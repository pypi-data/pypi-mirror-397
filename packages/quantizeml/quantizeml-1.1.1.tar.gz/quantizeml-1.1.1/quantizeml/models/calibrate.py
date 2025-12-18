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

__all__ = ["calibrate"]

import numpy as np
import tensorflow as tf

from copy import deepcopy
from tf_keras.layers import (Conv2D, Conv2DTranspose, SeparableConv2D, DepthwiseConv2D, Dense,
                             Dropout, Reshape, Flatten, MaxPool2D, GlobalAvgPool2D, Rescaling)

from .random import generate_keras_random_samples
from .transforms.insert_layer import insert_in_config
from .transforms.transforms_utils import get_layers_by_type, get_layer_index
from .transforms.align_rescaling import _fold_rescaling
from .utils import apply_weights_to_model
from ..layers import (InputObserver, OutputObserver, PaddedConv2D, DepthwiseConv2DTranspose,
                      BufferTempConv, DepthwiseBufferTempConv, StatefulRecurrent,
                      StatefulProjection, InputQuantizer, Dequantizer, update_batch_size)
from ..tensors import FixedPoint, floor_log2


def _get_calibration_model(model, qmodel):
    """Builds a calibration model with Observers added.

    Args:
        model (keras.Model): input model
        qmodel (keras.Model): quantized model

    Returns:
        keras.Model, dict: the calibration ready model and mapping of layer names with its Observer.
    """
    # Get model config to edit
    config = deepcopy(model.get_config())

    # Insert Observers
    end_of_blocks = {}
    for layer in qmodel.layers:
        if getattr(layer, 'out_quantizer', None):
            # Build an observer and store it for future use
            observer = OutputObserver(layer.out_quantizer.axis)
            end_of_blocks[layer.name] = observer.name
            # Insert observer in config
            insert_in_config(model, layer.name, observer, config)
        elif isinstance(layer, InputQuantizer):
            # Search layer linked to InputQuantizer.
            input_layer = layer.inbound_nodes[0].inbound_layers
            # Build an observer and store it for future use.
            # Note we specified its input shape in cases it is the first layer.
            observer = InputObserver(axis=layer.axis, input_shape=input_layer.input_shape[0][1:])
            end_of_blocks[layer.name] = observer.name
            # Verify that model contains input_layer in config.
            # Otherwise, InputObserver will be set in the input.
            if (layer_id := get_layer_index(config["layers"], input_layer.name)) >= 0:
                input_layer_name = config["layers"][layer_id]["config"]["name"]
            else:
                input_layer_name = None
            insert_in_config(model, input_layer_name, observer, config)

    # Build the calibration model from the config
    calibration_model = model.from_config(config)

    # Load original weights
    variables_dict = {var.name: var for var in model.variables}
    apply_weights_to_model(calibration_model, variables_dict, False)
    return calibration_model, end_of_blocks


def _get_next_layer(layer, supported_layers, skippable_layers=(), reshape_ops=[]):
    """ Finds the layer following a target layer.

    Args:
        layer (keras.Layer): the layer of interest
        supported_layers (tuple): layer types that will support equalization.
        skippable_layers (tuple, optional): layer types that can be skipped. Defaults to ().
        reshape_ops (list, optional): list of reshape operation encountered as
            [(input_shape,), (output_shape,)]. Defaults to [].

    Returns:
        keras.Layer: the layer following the layer of interest if valid, None otherwise
    """
    # Limit support to single outbound
    outbounds = layer.outbound_nodes
    if len(outbounds) != 1:
        return None
    next_layer = outbounds[0].layer

    # StatefulProjection with downshape or upshape is not supported by CLE
    if isinstance(next_layer, StatefulProjection) and (next_layer.downshape or next_layer.upshape):
        return None
    # If the layer is supported, it is a valid candidate
    if isinstance(next_layer, supported_layers):
        return next_layer
    # If the next layer can be skipped, recursively call the function
    elif isinstance(next_layer, skippable_layers):
        return _get_next_layer(next_layer, supported_layers, skippable_layers, reshape_ops)
    # If the next layer is a Reshape or Flatten store the performed ops and continue (limit reshape
    # ops to a single layer)
    elif isinstance(next_layer, (Reshape, Flatten)) and len(reshape_ops) == 0:
        reshape_ops.append([next_layer.input_shape[1:], next_layer.output_shape[1:]])
        return _get_next_layer(next_layer, supported_layers, skippable_layers, reshape_ops)

    # If next layer is not supported, alignment cannot happen
    return None


def _set_and_equalize(qmodel, layer_name, range_max):
    """ Set 'layer_name' output quantizer range_max to the ideal value.

    The ideal range_max is computed from the maximum value the target layer OutputQuantizer's
    can represent given it's bitwidth, and the float calibrated range_max.

    The ratio between the calibrated value and the ideal value is stored in the OutputQuantizer and
    will be applied when the scale_out operation happens. Equalization happens by dividing weights
    of the next layer by the ratio to preserve global outputs.

    Args:
        qmodel (keras.Model): quantized keras model
        layer_name (str): layer name where to set the range_max
        range_max (tf.Tensor): the float calibrated range_max
    """
    # First set the calibrated range_max in the target OutputQuantizer
    target_layer = qmodel.get_layer(layer_name)
    target_layer.out_quantizer.range_max.assign(range_max)

    # Skip layers that only perform out_shift since rescaling rate needs a scale out to be applied
    if not hasattr(target_layer.out_quantizer, 'qscales'):
        return

    # Define layers that will support or can be skipped when equalizing
    supported_layers = (Conv2D, PaddedConv2D, Conv2DTranspose, SeparableConv2D, DepthwiseConv2D,
                        Dense, DepthwiseConv2DTranspose, BufferTempConv, DepthwiseBufferTempConv)
    skippable_layers = (Dropout, MaxPool2D, GlobalAvgPool2D, Dequantizer)
    # When quantized per-tensor, Reshaping layers can be skipped as the rescaling rate single value
    # will be used during equalization on all weights values
    if target_layer.out_quantizer.axis == 'per-tensor':
        skippable_layers += (Reshape, Flatten)

    # Retrieve next_layer: if there is no candidate layer following layer_name, equalization cannot
    # happen
    reshape_ops = []
    next_layer = _get_next_layer(target_layer, supported_layers, skippable_layers, reshape_ops)
    # For now cross layer equalization for (Dephwise)BufferTempConvLayers is possible only if their
    # input is quantized per-tensor.
    # cross layer equalization is not applied on conv2d when groups is greater than 1 and when
    # data_format is 'channels_first'
    if (next_layer is None
        or (isinstance(next_layer, (BufferTempConv, DepthwiseBufferTempConv))
            and target_layer.out_quantizer.axis == 'per-axis')
            or getattr(next_layer, 'groups', 1) != 1
            or getattr(next_layer, 'data_format', 'channels_last') == 'channels_first'):
        return

    # Compute ideal range_max
    bitwidth = target_layer.out_quantizer.bitwidth
    frac_bits = bitwidth - floor_log2(range_max)
    int_max = FixedPoint.int_max(bitwidth)
    ideal_range_max = FixedPoint(int_max, bitwidth, frac_bits).to_float().numpy()

    # Check that values are different
    if np.all(ideal_range_max == range_max):
        return

    # Set ideal_range_max into the target OutputQuantizer
    target_layer.out_quantizer.range_max.assign(ideal_range_max)

    # range_max can be approximately 0 on some channels (eg. a ReLU where an input channel
    # had all negative values). When that happens, range_max set on output quantizer
    # (ideal_range_max) is exactly zero. In that case rescaling_rate is forced to 1
    # so that cross-layer equalization does nothing.
    if target_layer.out_quantizer.axis == 'per-axis':
        range_max = range_max.numpy()
        range_max[ideal_range_max == 0] = 1
        ideal_range_max[ideal_range_max == 0] = 1

    # Compute the rescaling rate
    rescaling_rate = ideal_range_max / range_max

    # Set rate in the target OutputQuantizer
    target_layer.out_quantizer.rescaling_rate.assign(rescaling_rate)

    # Divide weights of the next layer by the rescaling rate
    next_weights = next_layer.get_weights()
    new_weights = next_weights[0]

    # Apply reshape ops
    if reshape_ops:
        # Supporting a single reshape ops
        reshape_ops = reshape_ops[0]
        # Check that last dimension is unchanged by the reshape ops, if that's not the case, the op
        # needs to be undone on weights, eg. for Flatten: X*Y*C, F -> X, Y, C, F
        if reshape_ops[0][-1] != reshape_ops[1][-1]:
            F = (new_weights.shape[-1], )
            new_weights = np.reshape(new_weights, reshape_ops[0] + F)
        # Invert last two dimensions (input and output channels), eg. for flatten:
        # X, Y, C, F -> X, Y, F, C
        axes = list(range(0, len(new_weights.shape)))
        assert len(axes) > 1
        axes[-2], axes[-1] = axes[-1], axes[-2]
        new_weights = np.transpose(new_weights, axes)
    elif not isinstance(next_layer, Conv2DTranspose):
        # Expand dims to allow broadcasting on the expected dimension. Skipping Conv2dTranspose
        # since their kernel is (H, W, F, C), where C is the dimension of rescaling_rate
        rescaling_rate = np.expand_dims(rescaling_rate, -1)

    # Apply rescaling rate
    new_weights /= rescaling_rate

    # Undo reshape ops
    if reshape_ops:
        # Revert last dimensions swap, eg. for Flatten: X, Y, F, C -> X, Y, C, F
        new_weights = np.transpose(new_weights, axes)
        # Undo the reshape op on weights when last dimension is changed, eg. for Flatten:
        # X, Y, C, F -> X*Y*C, F
        if reshape_ops[0][-1] != reshape_ops[1][-1]:
            F = (new_weights.shape[-1], )
            new_weights = np.reshape(new_weights, reshape_ops[1] + F)

    next_weights[0] = new_weights
    next_layer.set_weights(next_weights)


def _set_and_fold_zero_point(qmodel, layer_name, range_min, range_max):
    quantizer = qmodel.get_layer(layer_name)

    # Update range_min if required.
    if not quantizer.signed:
        range_min = tf.where(range_min > 0.0, 0.0, range_min)

    # Set ranges in quantizer.
    quantizer.range_min.assign(range_min)
    quantizer.range_max.assign(range_max)

    # Stop procedure if all range_min are zero (zero point folding is not required).
    if tf.reduce_all(range_min == 0.0) or quantizer.signed:
        return qmodel

    # Retrieve next_layer.
    skippable_layers = (Rescaling,)
    next_layer = quantizer
    while (len(outbounds := next_layer.outbound_nodes) == 1 and
           isinstance((next_layer := outbounds[0].layer), skippable_layers)):
        # Update value to fold depending of next layer.
        if isinstance(next_layer, Rescaling):
            range_min = range_min * next_layer.scale

    # Fold zero point into bias of next layer.
    try:
        fake_rescaling_layer = Rescaling(scale=1.0, offset=range_min)
        _fold_rescaling(fake_rescaling_layer, next_layer)
    except Exception as e:
        raise RuntimeError("During calibration, impossible to fold zero point in "
                           f"{next_layer.name}.") from e


def calibrate(model, qmodel, samples=None, num_samples=1024, batch_size=None, epochs=1):
    """Calibrates the model using the provided samples.

    With TENN models only np.array samples are supported for calibration. Those should have
    a temporally coherent data, which means that their expected shape is
    [batch_size*Seq, dim_0,, ..., dim_n] for spatiotemporal TENNs where:

        - batch_size is the same batch_size provided to the calibration.
        - Seq is a dataset parameter that defines the temporally coherent data (eg number of frames
          per video clips).

    and [batch_size, (model.input_shape)] for recurrent TENNs.

    When no samples are provided, random samples are generated.

    Args:
        model (keras.Model): the original model
        qmodel (keras.Model): the quantized model to calibrate
        samples (tf.Dataset, np.array or generator, optional): calibration samples. When no samples
            are provided, random samples are generated. Defaults to None.
        num_samples (int, optional): number of samples to use in the provided samples or number of
            samples to generate. Defaults to 1024.
        batch_size (int, optional): the batch size. Defaults to None.
        epochs (int, optional): the number of epochs. Defaults to 1.

    """
    # Build a calibration model which is a float model with Observers at locations where the
    # quantized model has InputQuantizers/OutputQuantizers.
    calibration_model, end_of_blocks = _get_calibration_model(model, qmodel)

    if samples is None:
        # Generate random samples.
        # Note we use the float model since the quantized model has not yet been calibrated.
        samples = generate_keras_random_samples(model, num_samples)

    # Extract number of (Depthwise)BufferTempConv and StatefulRecurrent layers
    buf_layers = get_layers_by_type(calibration_model, (BufferTempConv, DepthwiseBufferTempConv))
    rec_layers = get_layers_by_type(calibration_model, StatefulRecurrent)
    if buf_layers or rec_layers:
        if not isinstance(samples, np.ndarray):
            raise TypeError("TENN models calibration is only possible with np.array samples."
                            f" Received {type(samples)}. Please convert them to a compatible"
                            " format before the calibration. \n"
                            " Spatiotemporal expects the following shape:"
                            " [batch_size*Seq, dim_0,, ..., dim_n] where:"
                            " - batch_size is the same batch_size provided to the calibration."
                            " - Seq is a dataset parameter that defines the temporally coherent"
                            " data (eg number of frames per video clips). \n"
                            " Recurrent expects [batch_size, (model.input_shape)] array.")
        if buf_layers:
            # With ST TENN models, the number of samples is infered from the provided samples
            num_samples = len(samples)
            if batch_size is None:
                raise ValueError("batch_size not specified. With spatiotemporal TENN models "
                                 "batch_size must be given for the calibration, otherwise the "
                                 "result is unpredictible. Refer to 'calibrate' function docstring "
                                 "for more details.")

            # The number of samples must be a multiple of the batch_size to prevent a reset of the
            # FIFO
            if num_samples % batch_size != 0:
                raise ValueError("When calibrating spatiotemporal TENN, num_samples must be a "
                                 f"multiple of batch_size, got num_samples={num_samples} and "
                                 f"batch_size={batch_size}.")

    # Compute step value otherwise 'predict' will run until samples are exhausted (ie. indefinitely
    # if samples is a dataset with repeat enabled)
    if batch_size is None:
        steps = num_samples
    else:
        assert batch_size > 0, "The batch size should be strictly positive."
        steps = np.ceil(num_samples / batch_size)

    for i in range(epochs):
        if rec_layers:
            calibration_model = update_batch_size(calibration_model, samples.shape[0])
            # Ensure graph execution
            model_func = tf.function(calibration_model)
            in_shape = calibration_model.input_shape[1]
            # Allow to "cut" the calibration samples in portions compatible with
            # the stateful model input shape.
            assert samples.shape[1] % in_shape == 0, (
                f"Each sample length {samples.shape[1]} "
                f"should be a multiple of the model input size {in_shape}.")
            in_step = samples.shape[1] // in_shape
            for i in range(in_step):
                model_func(samples[:, i * in_shape:(i + 1) * in_shape])
        else:
            calibration_model.predict(
                x=samples, steps=steps, batch_size=batch_size)

    # Update quantized model calibration ranges using Observers calibrated values.
    for eob, observer in end_of_blocks.items():
        if isinstance(observer := calibration_model.get_layer(observer), OutputObserver):
            _set_and_equalize(qmodel, eob, observer.range_max)
        else:
            _set_and_fold_zero_point(qmodel, eob, observer.range_min, observer.range_max)
