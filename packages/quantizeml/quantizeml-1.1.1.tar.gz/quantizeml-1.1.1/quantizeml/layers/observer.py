#!/usr/bin/env python
# ******************************************************************************
# Copyright 2023 Brainchip Holdings Ltd.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ******************************************************************************

__all__ = ["InputObserver", "OutputObserver"]

import tensorflow as tf
import tf_keras as keras

from tf_keras.layers import Layer

from .layers_base import check_arg_constraints


class Observer(Layer):
    """ Abstract calibration layer.

    This layer tracks the inputs over time using an exponential moving average.

    Args:
        axis (str, optional): the quantization range is a scalar ('per-tensor') or a vector
            corresponding to the last axis ('per-axis'). Defaults to 'per-tensor'.
        momentum (float, optional): the momentum for the moving average. Defaults to 0.9.
    """
    arg_constraints = {'axis': lambda: ["per-tensor", "per-axis"]}

    def __init__(self, axis="per-tensor", momentum=0.9, **kwargs):
        super().__init__(**kwargs)
        self.axis = axis
        self.momentum = momentum
        self._decay = tf.convert_to_tensor(1.0 - momentum, name="decay")
        check_arg_constraints(self, self.get_config())

    def build(self, input_shape):
        """Build the layer.

        Args:
            input_shape (list): the shape of input tensor.
        """
        super().build(input_shape)
        # Convert axis to a list of int
        if self.axis == "per-axis":
            ndims = len(input_shape)
            if ndims < 3:
                raise ValueError("OutputObserver cannot quantize per-axis tensors "
                                 " with 2 dimensions or less.")
            self._axis = list(range(len(input_shape) - 1))
        else:
            self._axis = None

    def update_variable(self, variable, new_value):
        """Updates a TensorFlow variable using a moving average algorithm.

        If the variable has never been updated (i.e., all values are 1), it is set directly
        to the new value. Otherwise, the variable is updated using an exponential moving average
        with the decay factor specified by the observer's momentum.

        Args:
            variable (tf.Variable): the variable to update.
            new_value (tf.Tensor): the new value to incorporate.
        """
        # If variables was never updated set their newly computed values otherwise update with
        # moving average algorithm.
        if tf.reduce_any(tf.math.not_equal(variable, tf.constant(1.))):
            # The new value is just the multiplication by decay.
            old_value = variable
            update_delta = (old_value - tf.cast(new_value, old_value.dtype)) * self._decay
            new_value = old_value - update_delta
        variable.assign(new_value)

    def get_config(self):
        """Get the config of the layer.

        Returns:
            dict: the config of the layer.
        """
        config = super().get_config()
        config.update({"axis": self.axis, "momentum": self.momentum})
        return config


@keras.saving.register_keras_serializable()
class InputObserver(Observer):
    """ Calibration layer.

    This layer is used to compute the future `range_max` and `range_min` of the
    equivalent InputQuantizer in the quantized model. It is placed where the InputQuantizer
    will be inserted and accumulates the observed maximum and minimum values (with momentum)
    for input in the float model.

    Args:
        axis (str, optional): the quantization range is a scalar ('per-tensor') or a vector
            corresponding to the last axis ('per-axis'). Defaults to 'per-tensor'.
        momentum (float, optional): the momentum for the moving average. Defaults to 0.9.
    """

    def build(self, input_shape):
        super().build(input_shape)

        # Declares the constant/vector that will store the maximum values of the input.
        self.range_max = self.add_weight(
            name="range_max",
            shape=input_shape[-1] if self._axis is not None else (),
            dtype=tf.float32,
            initializer="ones",
            synchronization=tf.VariableSynchronization.ON_READ,
            trainable=False,
            aggregation=tf.VariableAggregation.MEAN,
            experimental_autocast=False,
        )
        self.range_min = self.add_weight(
            name="range_min",
            shape=input_shape[-1] if self._axis is not None else (),
            dtype=tf.float32,
            initializer="ones",
            synchronization=tf.VariableSynchronization.ON_READ,
            trainable=False,
            aggregation=tf.VariableAggregation.MEAN,
            experimental_autocast=False,
        )

    def call(self, inputs):
        """ Observe inputs and update the maximum value with momentum.

        Args:
            inputs (tf.Tensor): the inputs tensor.

        Returns:
            tf.Tensor: unchanged inputs
        """
        # Compute the new ranges from inputs.
        range_max = tf.math.reduce_max(inputs, self._axis)
        range_min = tf.math.reduce_min(inputs, self._axis)

        # Update variables.
        self.update_variable(self.range_max, range_max)
        self.update_variable(self.range_min, range_min)
        return inputs


@keras.saving.register_keras_serializable()
class OutputObserver(Observer):
    """ Calibration layer.

    This layer is used to compute the future `range_max` of the equivalent OutputQuantizer in the
    quantized model. It is placed where the OutputQuantizer will be inserted (end of blocks) and
    accumulates the observed maximum values (with momentum) for input in the float model.

    Args:
        axis (str, optional): the quantization range is a scalar ('per-tensor') or a vector
            corresponding to the last axis ('per-axis'). Defaults to 'per-tensor'.
        momentum (float, optional): the momentum for the moving average. Defaults to 0.9.
    """

    def build(self, input_shape):
        super().build(input_shape)

        # Declares the constant/vector that will store the maximum values of the input.
        self.range_max = self.add_weight(
            name="range_max",
            shape=input_shape[-1] if self._axis is not None else (),
            dtype=tf.float32,
            initializer="ones",
            synchronization=tf.VariableSynchronization.ON_READ,
            trainable=False,
            aggregation=tf.VariableAggregation.MEAN,
            experimental_autocast=False,
        )

    def call(self, inputs):
        """ Observe inputs and update the maximum value with momentum.

        Args:
            inputs (tf.Tensor): the inputs tensor.

        Returns:
            tf.Tensor: unchanged inputs
        """
        # Compute the new range_max from inputs
        range_max = tf.math.reduce_max(tf.math.abs(inputs), self._axis)

        # Update variables.
        self.update_variable(self.range_max, range_max)
        return inputs
