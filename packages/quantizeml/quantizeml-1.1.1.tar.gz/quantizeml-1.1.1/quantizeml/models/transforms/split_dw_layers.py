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

__all__ = ["split_dw_layers"]

import tf_keras as keras
import numpy as np

from ..utils import apply_weights_to_model, requires_tf_keras_model
from .transforms_utils import get_layer_index, safe_fail
from .insert_layer import insert_in_config


@safe_fail
@requires_tf_keras_model
def split_dw_layers(model):
    """Transforms depthwise convolution layers with stride-2 and kernel sizes in (5x5 or 7x7)
    into an equivalent sequence of two depthwise convolutions:

    - A depthwise convolution with the same kernel size (5x5 or 7x7) and stride=1.
    - Followed by an identity depthwise convolution with a 3x3 kernel and stride=2.

    Args:
        model (keras.Model): a model

    Returns:
        keras.Model: the original model or the sanitized model.
    """
    target_layers = _find_target_dw_layers(model)

    # When there are no valid candidates, return the original model
    if len(target_layers) == 0:
        return model

    updated_model = _split_dw_layers(model, target_layers)
    return updated_model


def _find_target_dw_layers(model):
    def _has_expected_attributes(layer):
        stride = layer.strides[0]
        kernel_size = layer.kernel_size[0]
        padding = layer.padding

        return stride == 2 and kernel_size in {5, 7} and padding == "same"

    target_layers = []
    for layer in model.layers:
        if isinstance(layer, keras.layers.DepthwiseConv2D) and _has_expected_attributes(layer):
            target_layers.append(layer)

    return target_layers


def _split_dw_layers(model, target_layers):
    config = model.get_config()
    layers = config["layers"]
    variables_dict = {var.name: var for var in model.variables}

    for target_layer in target_layers:
        target_layer_index = get_layer_index(layers, target_layer.name)

        # Change strides to 1
        layers[target_layer_index]["config"]["strides"] = (1, 1)

        # Add dw with identity weights
        id_conv_name = f"{target_layer.name}_identity_dw_conv"
        identity_dw_conv = keras.layers.DepthwiseConv2D(
            kernel_size=(3, 3), strides=(2, 2), padding="same", use_bias=False, name=id_conv_name
        )

        insert_in_config(model, target_layer.name, identity_dw_conv, config)

        # Store weights of the identity depthwise convolution layer
        # (only the center element is 1, the rest are 0).
        in_channels = target_layer.weights[0].shape[2]
        identity_w = np.zeros((3, 3, in_channels, 1), dtype="float32")
        identity_w[1, 1, np.arange(in_channels), 0] = 1
        variables_dict[f"{id_conv_name}/depthwise_kernel:0"] = identity_w

    updated_model = model.from_config(config)
    apply_weights_to_model(updated_model, variables_dict)

    return updated_model
