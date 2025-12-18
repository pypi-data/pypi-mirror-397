#!/usr/bin/env python
# ******************************************************************************
# Copyright 2025 Brainchip Holdings Ltd.
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

__all__ = ["InputQuantizer", "Dequantizer"]

import tensorflow as tf
import tf_keras as keras

from tf_keras.layers import Layer

from ..tensors import QTensor, QFloat, FixedPoint
from ..debugging import assert_less_equal
from .recorders import TensorRecorder, QFloatRecorder
from .layers_base import check_arg_constraints, QuantizedLayer


@keras.saving.register_keras_serializable()
class InputQuantizer(QuantizedLayer):
    """Quantizer layer for input tensors.

    This layer quantizes input tensors to a q-tensor representation using a specified bitwidth,
    supporting signed and axis quantization.

    Args:
        bitwidth (int, optional): the quantization bitwidth. Defaults to 8.
        signed (bool, optional): whether the quantizer expects signed values or unsigned.
            Defaults to True.
        axis (str, optional): the quantization range is a scalar ('per-tensor') or a vector
            corresponding to the last axis ('per-axis'). Defaults to 'per-tensor'.

    Example:
        >>> quantizer = InputQuantizer(bitwidth=8, signed=True)
        >>> quantized = quantizer(tf.constant([[1.0, -2.0], [3.0, 4.0]]))
    """
    arg_constraints = {'axis': lambda: ["per-tensor", "per-axis"]}

    def __init__(self, bitwidth=8, signed=True, axis="per-tensor", **kwargs):
        super().__init__(**kwargs)
        self.axis = axis
        self.bitwidth = bitwidth
        self.signed = signed
        self.frac_bits = TensorRecorder()
        check_arg_constraints(self, self.get_config())

    @property
    def value_bits(self):
        return self.bitwidth - 1 if self.signed else self.bitwidth

    def build(self, input_shape):
        super().build(input_shape)
        # Convert axis to a list of int.
        if self.axis == "per-axis":
            ndims = len(input_shape)
            if ndims < 3:
                raise ValueError(f"'{self.name}' (InputQuantizer) cannot quantize per-axis "
                                 "tensors with 2 dimensions or less.")
            range_axis = list(range(len(input_shape) - 1))
        else:
            range_axis = None

        # Declares the constant/vector that will store the maximum values and zero point.
        self.range_min = self.add_weight(
            name="range_min",
            shape=input_shape[-1] if range_axis is not None else (),
            dtype=tf.float32,
            initializer="zeros",
            synchronization=tf.VariableSynchronization.ON_READ,
            trainable=False,
            aggregation=tf.VariableAggregation.MEAN,
            experimental_autocast=False,
        )
        self.range_max = self.add_weight(
            name="range_max",
            shape=input_shape[-1] if range_axis is not None else (),
            dtype=tf.float32,
            initializer="ones",
            synchronization=tf.VariableSynchronization.ON_READ,
            trainable=False,
            aggregation=tf.VariableAggregation.MEAN,
            experimental_autocast=False,
        )

    def call(self, inputs):
        """Quantize the inputs according to the quantizer configuration.

        This method calculates the scale and zero point from the calibration ranges provided
        to project the input to integer values.

        Args:
            inputs (tf.Tensor): the input tensor to be quantized.

        Returns:
            QFloat: the quantized tensor.
        """
        if not isinstance(inputs, tf.Tensor):
            raise TypeError(f"{self.__class__.__name__} only accepts {tf.Tensor} inputs. "
                            f"Receives {type(inputs)} inputs.")
        if inputs.dtype.is_integer:
            raise TypeError(f"{self.__class__.__name__} only accepts float inputs. "
                            f"Receives {inputs.dtype} inputs.")
        inputs = tf.cast(inputs, tf.float32)

        # Compute range/zero_point.
        assert_less_equal(self.range_min,
                          self.range_max,
                          message="range_max must be higher or equal than range_min.")
        if self.signed:
            # When signed is true, zero point is not required.
            range_abs = tf.maximum(tf.abs(self.range_max), tf.abs(self.range_min))
        else:
            # We cannot handle negative zero point (HW constraint).
            # That is why we reject positive range_min.
            # In other words, a positive min_range refers to inputs that do not require
            # a zero point, since quantization already produces unsigned values.
            assert_less_equal(self.range_min, tf.zeros_like(self.range_min),
                              message="range_min > 0 is not allowed (HW constraint).")
            range_abs = self.range_max - self.range_min
            range_min = self.range_min

            # Build recorder object for zero point.
            with tf.init_scope():
                self.zero_points = QFloatRecorder(name="zero_point")

        # Compute the frac_bits to quantize the inputs.
        frac_bits = tf.stop_gradient(FixedPoint.max_frac_bits(self.value_bits, range_abs))
        self.frac_bits(frac_bits)
        # Quantize the inputs.
        q_inputs = FixedPoint.quantize(inputs, self.value_bits, frac_bits)
        # Change output signature depending on signed parameter.
        if not self.signed:
            q_inputs = QFloat(q_inputs, 1.0)
            # When the output is unsigned, a zero point is needed to shift the range
            # to an entirely positive one.
            q_zero_points = QFloat.quantize(-range_min, self.value_bits, q_inputs.scales, frac_bits)
            q_inputs = q_inputs + q_zero_points
            # Record zero point.
            self.zero_points(q_zero_points)
        return q_inputs

    def get_config(self):
        """Get the config of the layer.

        Returns:
            dict: the config of the layer.
        """
        config = super().get_config()
        config.update({"bitwidth": self.bitwidth})
        config.update({"signed": self.signed})
        config.update({"axis": self.axis})
        return config


@keras.saving.register_keras_serializable()
class Dequantizer(Layer):
    """ Layer that allows to dequantize its inputs.
    """
    scales: list = None
    frac_bits: list = None

    def _build_records(self, inputs):
        def _build(x):
            record_fb = record_scale = None
            # from tf_keras documentation, any variable creation taking place
            # in call should be wrapped with tf.init_scope
            with tf.init_scope():
                if isinstance(x, QTensor):
                    record_fb = TensorRecorder(self.name + "/record_fb")
                if isinstance(x, QFloat):
                    record_scale = TensorRecorder(self.name + "/record_scale")
            return record_fb, record_scale

        if self.frac_bits is not None:
            # Nothing to do
            return
        if not isinstance(inputs, (tuple, list)):
            # Manage single inputs
            self.frac_bits, self.scales = _build(inputs)
            return

        self.frac_bits = []
        self.scales = []
        with tf.init_scope():
            for x in inputs:
                frac_bits, scales = _build(x)
                self.frac_bits.append(frac_bits)
                self.scales.append(scales)

    def call(self, inputs):
        """Convert QTensor inputs to float.

        Args:
            inputs (tf.Tensor or :obj:`QTensor`): the inputs tensor(s).

        Returns:
            tf.Tensor: the dequantized tensor(s).
        """

        def dequantize(x, frac_bits_recorder=None, scales_recorder=None):
            if isinstance(x, QTensor):
                if frac_bits_recorder is not None:
                    frac_bits_recorder(x.fp.frac_bits if isinstance(x, QFloat) else x.frac_bits)
                if scales_recorder is not None:
                    scales_recorder(x.scales)
                return x.to_float()
            return x

        # Build records
        self._build_records(inputs)

        # Apply dequantizer
        if isinstance(inputs, (list, tuple)):
            return [dequantize(x, fb, scales) for x, fb, scales in
                    zip(inputs, self.frac_bits, self.scales)]

        return dequantize(inputs, self.frac_bits, self.scales)
