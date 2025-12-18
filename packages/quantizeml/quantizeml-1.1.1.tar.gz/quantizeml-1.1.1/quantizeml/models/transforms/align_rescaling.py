#!/usr/bin/env python
# ******************************************************************************
# Copyright 2022 Brainchip Holdings Ltd.
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
"""
Rescaling transformation for quantized models.
"""

__all__ = ["align_rescaling"]

import numpy as np

from copy import deepcopy
from tf_keras.layers import Rescaling, Conv2D, Dense
from tf_keras.saving import serialize_keras_object

from .transforms_utils import get_layers_by_type, get_layers, safe_fail
from ..utils import apply_weights_to_model, requires_tf_keras_model
from ...layers.convolution import PaddedConv2D, QuantizedConv2D
from ...layers import BufferTempConv, DepthwiseBufferTempConv


def _find_rescaling_fold_target(rescaling):
    """ Find the folding target and check limitations.

    Args:
        rescaling (keras.layers.Layer): the rescaling layer

    Returns:
        keras.layers.Layer: the layer that follows the Rescaling if a valid candidate, None
        otherwise.
    """
    # Define layers that can accept Rescaling alignment
    supported_dst_layers = [Conv2D, Dense, BufferTempConv, DepthwiseBufferTempConv]

    scale_per_axis = isinstance(rescaling.scale, (list, tuple)) and len(rescaling.scale) > 1
    if isinstance(rescaling.offset, (list, tuple)):
        zero_offset = all(offset == 0 for offset in rescaling.offset)
    else:
        zero_offset = rescaling.offset == 0
    if not scale_per_axis and zero_offset:
        # Rescaling is already aligned: nothing to do
        return None
    # Alignment is limited to single outbound node Rescaling layers
    if len(rescaling.outbound_nodes) != 1:
        raise ValueError("Found a non-aligned Rescaling layer in the model with multiple outbounds "
                         "which is not supported.")
    # Retrieve the destination layer and check its type
    dst_layer = rescaling.outbound_nodes[0].layer
    if type(dst_layer) not in supported_dst_layers:
        raise ValueError(f"Layer type {type(dst_layer)} after Rescaling not supported, must be in "
                         f"{supported_dst_layers}.")
    return dst_layer


def _adapt_padding(model, dst_layer):
    """ Update padding scheme by replacing Conv2D with a PaddedConv2D.

    Args:
        model (keras.Model): the original model
        dst_layer (keras.layer): the layer where offset or scale will be folded

    Returns:
        keras.Model: the updated model
    """
    # Copy configuration before applying modifications
    config = deepcopy(model.get_config())
    # Fold rescaling by editing the model configuration
    dst_config = get_layers(config, [dst_layer.name])[0]
    # Force bias
    had_bias = dst_config['config']['use_bias']
    dst_config['config']['use_bias'] = True
    # Replace Conv2D with 'same' padding by PaddedConv2D
    if isinstance(dst_layer, Conv2D) and dst_layer.padding.lower() == 'same':
        new_config = PaddedConv2D.from_config(dst_config['config'])
        dst_config.update(serialize_keras_object(new_config))
        dst_config['config']['padding_value'] = [0.0]

    # Reconstruct model from the config
    aligned_model = model.from_config(config)

    # Restore model weights, setting bias to zero if they was created.
    variables_dict = {var.name: var for var in model.variables}
    apply_weights_to_model(aligned_model, variables_dict, False)
    if not had_bias:
        new_bias = aligned_model.get_layer(dst_layer.name).bias
        new_bias.assign_sub(new_bias)
    return aligned_model


def _fold_rescaling(rescaling_layer, dst_layer):
    """ Fold rescaling parameters into dst_layer weights and bias.

    Note that if scales are per-channel, there are folded in the weights.

    Args:
        rescaling_layer (keras.layers.Layer): the Rescaling layer
        dst_layer (keras.layers.Layer): the layer where Rescaling is folded
    """
    assert isinstance(dst_layer, (Conv2D, Dense, BufferTempConv, DepthwiseBufferTempConv))
    kernel = dst_layer.kernel
    assert (bias := dst_layer.bias) is not None, f"{dst_layer.name} must have a bias."

    # Fold offset in padding_value.
    offset = np.array(rescaling_layer.offset)
    if (isinstance(dst_layer, (PaddedConv2D, QuantizedConv2D)) and
            dst_layer.padding_value is not None):
        # Update previous padding value.
        dst_layer._padding_value = (np.array(dst_layer._padding_value) - offset).tolist()
        # Reduce to just one value if possible (improve inference runtime).
        if all(x == dst_layer._padding_value[0] for x in dst_layer._padding_value):
            dst_layer._padding_value = [dst_layer._padding_value[0]]

    # Fold offset in bias.
    vector_offset = (isinstance(rescaling_layer.offset, (list, tuple)) and
                     len(rescaling_layer.offset) > 1)
    if vector_offset and isinstance(dst_layer, BufferTempConv):
        # Reshape the offset
        offset = np.tile(offset, dst_layer.kernel_size)
    if not isinstance(dst_layer, DepthwiseBufferTempConv):
        offset = np.reshape(offset, newshape=(-1, 1))
    bias.assign_add(np.sum(kernel * offset, axis=tuple(range(np.ndim(kernel) - 1))))
    rescaling_layer.offset = 0

    # Fold scale in kernel when it is a vector.
    scale = rescaling_layer.scale
    vector_scale = isinstance(scale, (list, tuple)) and len(scale) > 1
    if vector_scale:
        rescaling_layer.scale = 1
        scale = np.array(scale)
        if isinstance(dst_layer, PaddedConv2D):
            # Also rescale the padding value
            padding_value = np.array(dst_layer._padding_value, dtype=np.float32)
            dst_layer._padding_value = list(padding_value / scale)
        elif isinstance(dst_layer, (BufferTempConv)):
            scale = np.tile(scale, dst_layer.kernel_size)
        if not isinstance(dst_layer, DepthwiseBufferTempConv):
            scale = np.reshape(scale, newshape=(-1, 1))

        kernel.assign(kernel * scale)


@safe_fail
@requires_tf_keras_model
def align_rescaling(model):
    """Aligns the Rescaling layer of the model to make it quantization ready.

    This folds the offset into the bias of next layer.

    The resulting Rescaling is therefore compatible with a quantization to a
    QuantizedRescaling.

    If the source model does not contain a Rescaling or if its Rescaling is already
    aligned, then the original model is returned.

    Args:
        model (keras.Model): the source Keras model

    Returns:
        keras.Model: the original model or a new model with Rescaling layer aligned
    """
    # Check if the model has a Rescaling layer and return the original model if not
    rescaling_layer = get_layers_by_type(model, Rescaling)
    if not rescaling_layer:
        return model

    # Limit alignment to the first rescaling layer (a model should only have one)
    rescaling_layer = rescaling_layer[0]

    # Find folding target and check limitations
    dst_layer = _find_rescaling_fold_target(rescaling_layer)

    # If no folding target was found return the original model
    if dst_layer is None:
        return model

    # There is a rescaling offset, dst_layer padding scheme must be updated
    aligned_model = _adapt_padding(model, dst_layer)

    # Fold Rescaling parameters into the new layer weights
    _fold_rescaling(aligned_model.get_layer(rescaling_layer.name),
                    aligned_model.get_layer(dst_layer.name))
    return aligned_model
