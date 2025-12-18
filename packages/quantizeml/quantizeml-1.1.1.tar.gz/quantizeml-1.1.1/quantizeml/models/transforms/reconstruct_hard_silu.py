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
"""
Helper that reconstructs hard silu activation if it's hardcoded.
"""
from copy import deepcopy
from tf_keras.layers import ReLU, Multiply
from tf_keras.src.layers import TFOpLambda

from .transforms_utils import get_layers_by_type, get_layer_index, update_inbound, safe_fail
from ..transforms.insert_layer import insert_in_config
from ...layers import Activation


__all__ = ["reconstruct_hard_silu"]


def _relu_after_layer(layer):
    """Check whether the next outbound layer is a ReLU layer with max_value = 6.0."""
    if (len(layer.outbound_nodes) == 1
       and isinstance(next_layer := layer.outbound_nodes[0].layer, ReLU)
       and next_layer.max_value == 6.0):
        return next_layer
    return None


def _multiply_or_div_op_after_layer(layer, config):
    """Check whether the next outbound layer is a TFOpLambda multiply or div op
        and check its factor.
    """
    if len(layer.outbound_nodes) == 1 and isinstance(
       next_layer := layer.outbound_nodes[0].layer, TFOpLambda):
        layer_index = get_layer_index(config['layers'], next_layer.name)
        layer_config = config['layers'][layer_index]
        if ((layer_config['config']['function'] == 'math.multiply'
             and 1 / 6 in layer_config['inbound_nodes'][0][3].values())
           or (layer_config['config']['function'] == 'math.truediv'
               and 6 in layer_config['inbound_nodes'][0][3].values())):
            return next_layer
    return None


def _mulitply_layer_after_layer(layer):
    """Check whether the next outbound layer is a keras.layers.Multiply."""
    if len(layer.outbound_nodes) == 1 and isinstance(
       next_layer := layer.outbound_nodes[0].layer, Multiply):
        return next_layer
    return None


def _get_outbound_if_inbound_matches(layer, config, inbound_node_name):
    """Return outbound nodes if the layer has a specific inbound connection.

    Args:
        layer (keras.layers.Layer): the layer to inspect.
        config (dict): the model configuration dictionary.
        inbound_node_name (str): the name of the inbound node to check for.

    Returns:
        list[keras.engine.node.Node] or None: the outbound nodes if the inbound
        connection matches, otherwise None.
    """
    layer_index = get_layer_index(config['layers'], layer.name)
    layer_config = config['layers'][layer_index]
    if (len(layer_config['inbound_nodes']) == 1
       and len(layer_config['inbound_nodes'][0]) == 2
       and any(x[0] == inbound_node_name for x in layer_config['inbound_nodes'][0])):
        return layer.outbound_nodes
    return None


def _remove_layers_from_config(layer_names, config):
    for layer_name in layer_names:
        layer_index = get_layer_index(config['layers'], layer_name)
        config['layers'].pop(layer_index)


def _fetch_candidates(layers, config):
    """Identify candidate subgraphs in a Keras model configuration that match
    a specific Hard-SiLU pattern (add + ReLU + multiply/divide operations).
    """
    candidates = []

    while layers:
        layer = layers.pop()
        layer_index = get_layer_index(config['layers'], layer.name)
        layer_config = config['layers'][layer_index]

        if (layer_config['config']['function'] in ['math.add', '__operators__.add']
           and 3.0 in layer_config['inbound_nodes'][0][3].values()):

            inbound_node_name = layer_config['inbound_nodes'][0][0]

            if ((relu := _relu_after_layer(layer))
               and (multiply_or_div := _multiply_or_div_op_after_layer(relu, config))
               and (multiply_layer := _mulitply_layer_after_layer(multiply_or_div))
               and (hard_silu_outbound_nodes := _get_outbound_if_inbound_matches(
                   multiply_layer, config, inbound_node_name)) is not None):

                hard_silu_outbound_nodes_names = [
                    node.layer.name for node in hard_silu_outbound_nodes]

                candidates.append((inbound_node_name, layer.name, relu.name, multiply_or_div.name,
                                   multiply_layer.name, hard_silu_outbound_nodes_names))

                if multiply_or_div in layers:
                    layers.remove(multiply_or_div)

    return candidates


@safe_fail
def reconstruct_hard_silu(model):
    """Reconstruct a model by replacing subgraphs that implement Hard-SiLU
    with a single Activation layer.

    This function scans the model configuration for patterns that emulate
    the Hard-SiLU activation (using Add → ReLU → multiply/div → Multiply) assuming that multiply ops
    that have two layers as inbound were replaced by a Multiply layer, removes the redundant layers,
    and inserts a single `Activation('hard_silu')` layer instead.

    Args:
        model (keras.Model): the input model.

    Returns:
        keras.Model: the original model or a new model where Hard-SiLU patterns are replaced by a
        dedicated Hard-SiLU activation layer.
    """

    # Copy configuration before applying modifications
    config = deepcopy(model.get_config())

    layers = get_layers_by_type(model, TFOpLambda)

    candidates = _fetch_candidates(layers, config)

    if not candidates:
        return model

    for candidate in candidates:

        inbound_name, add, relu, multiply_or_div, multiply_layer, outbound_names = candidate

        # Collect outbound layer names and update their inbound references
        for outbound_name in outbound_names:
            layer_index = get_layer_index(config['layers'], outbound_name)
            layer_config = config['layers'][layer_index]
            update_inbound(layer_config, multiply_layer, inbound_name)

        # Remove the original sequence of layers that emulates Hard-SiLU
        _remove_layers_from_config(
            [add, relu, multiply_or_div, multiply_layer], config)

        # Create a single Hard-SiLU activation layer
        new_layer = Activation(activation='hard_silu')

        # Replace the second Multiply with Hard-SiLU in config['output_layers'] if found
        for layer_config in config['output_layers']:
            if layer_config[0] == multiply_layer:
                layer_config[0] = new_layer.name

        # Insert new layer
        insert_in_config(model, inbound_name, new_layer, config, outbound_names)

    # Reconstruct model from the config
    updated_model = model.from_config(config)

    # Restore model weights
    updated_model.set_weights(model.get_weights())
    return updated_model
