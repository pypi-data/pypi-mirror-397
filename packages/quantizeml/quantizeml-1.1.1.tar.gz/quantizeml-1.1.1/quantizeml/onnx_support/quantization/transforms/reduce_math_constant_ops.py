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
__all__ = ["reduce_math_constant_ops"]

import numpy as np

import onnx_ir as ir
import onnx_ir.passes.common as common_passes

from ..model import ONNXModel
from .utils import safe_fail


SUPPORTED_OPS = ("Mul", "Add", "Sub", "Div")


def _np_to_value(x, name):
    return ir.Value(const_value=ir.tensor(x, name=name), name=name)


def _check_valid_node(node):
    # Special case for Div: if input is in second position, the operation is no longer linear.
    if node.op_type == "Div" and node.inputs[1].const_value is None:
        return False
    return node.op_type in SUPPORTED_OPS and any(x.const_value is not None for x in node.inputs)


def _search_max_supported_ops_sequence(node):
    sequence = []
    while _check_valid_node(node):
        sequence.append(node)
        if len(node.outputs[0].consumers()) != 1:
            break
        node = node.outputs[0].consumers()[0]
    return sequence


def _compute_linear_factors(sequence):
    # Apply transformation to current values
    scale, offset = 1, 0
    for node in sequence:
        # Apply transformation to current values
        # Note that it does not make sense for both inputs
        # to be initializers (the graph would be disconnected).
        new_value = (node.inputs[0].const_value or node.inputs[1].const_value).numpy()
        if node.op_type == "Mul":
            scale = scale * new_value
            offset = offset * new_value
        elif node.op_type == "Div":
            scale = scale / new_value
            offset = offset / new_value
        elif node.op_type == "Add":
            scale = np.array(scale, new_value.dtype)
            offset = offset + new_value
        elif node.op_type == "Sub":
            # The operation changes according to the position of the initializer
            if node.inputs[0].const_value is None:
                # y = (scale*X + offset) - new_value = scale*X + offset - new_value
                offset = offset - new_value
                scale = np.array(scale, new_value.dtype)
            else:
                # y = new_value - (scale*X + offset) = -scale*X + new_value - offset
                offset = new_value - offset
                scale = -1 * scale
    return scale, offset


def _update_graph(graph, old_nodes, scale, offset):
    x = old_nodes[0].inputs[0]
    if x.const_value is not None:
        x = old_nodes[0].inputs[1]

    # Build a sequence of nodes to develop the scale and offset.
    new_nodes = []
    mul_x = x
    if np.any(scale != 1.0):
        scale = _np_to_value(scale, name=f"{x.name}/scale")
        graph.register_initializer(scale)
        new_nodes.append(ir.node("Mul", [x, scale]))
        mul_x = new_nodes[-1].outputs[0]
    if np.any(offset != 0.0):
        offset = _np_to_value(offset, name=f"{x.name}/offset")
        graph.register_initializer(offset)
        new_nodes.append(ir.node("Add", [mul_x, offset]))

    # Disconnect the sequence of the graph.
    old_nodes[0].replace_input_with(old_nodes[0].inputs.index(x), None)

    # Update graph with the new sequence.
    y = old_nodes[-1].outputs[0]
    new_y = x if len(new_nodes) == 0 else new_nodes[-1].outputs[0]
    ir.convenience.replace_nodes_and_values(graph, old_nodes[0], old_nodes, new_nodes, [y], [new_y])


class ReduceMathConstantOpsPass(ir.passes.InPlacePass):
    def call(self, model):
        modified = False
        nodes = list(model.graph)
        while nodes:
            node = nodes.pop(0)

            # Search a target sequence.
            if not (sequence := _search_max_supported_ops_sequence(node)):
                continue
            [nodes.remove(n) for n in sequence[1:]]

            # Compute the reduce form of ops.
            scale, offset = _compute_linear_factors(sequence)

            # Check if the graph needs to be modified.
            expected_op_types = []
            if np.any(scale != 1.0):
                expected_op_types.append("Mul")
            if np.any(offset != 0.0):
                expected_op_types.append("Add")
            if [n.op_type for n in sequence] == expected_op_types:
                continue

            # Update graph with the new ops: Add(Mul(x, scale), offset).
            _update_graph(model.graph, sequence, scale, offset)
            modified = True
        return ir.passes.PassResult(model, modified)


@safe_fail(infer_shapes=False)
def reduce_math_constant_ops(model):
    """Optimizes an ONNX model by reducing sequences of constant math operations to a minimal form.

    This function searches for chains of supported math operations (Mul, Add, Sub, Div) involving
    constant initializers, and replaces them with a simplified equivalent sequence
    (at most one Mul and one Add).

    Args:
        model (ONNXModel): the ONNX model to optimize.
    """
    assert isinstance(model, ONNXModel)

    model_ir = ir.from_proto(model.model)
    optimizer_pass = ir.passes.Sequential(ReduceMathConstantOpsPass(),
                                          common_passes.RemoveUnusedNodesPass())
    result = optimizer_pass(model_ir)
    if result.modified:
        model.model.CopyFrom(ir.to_proto(result.model))
