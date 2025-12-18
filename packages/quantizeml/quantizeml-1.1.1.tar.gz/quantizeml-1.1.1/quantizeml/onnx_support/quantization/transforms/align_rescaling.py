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
__all__ = ["align_rescaling"]

import numpy as np

from onnxscript import ir, rewriter

from ..model import ONNXModel
from .utils import safe_fail


def _np_to_initializer(op, x, name):
    return op.initializer(ir.tensor(x), name=name)


def _fold_scale(kernel, scale):
    return scale * kernel


def _fold_offset(bias, offset, kernel=None):
    if kernel is not None:
        kernel = ir.convenience.get_const_tensor(kernel).numpy()
        N = kernel.ndim
        offset = np.reshape(offset, tuple(1 if i != 1 else -1 for i in range(N)))
        offset = (offset * kernel).sum(axis=tuple(range(1, N)))
    return bias + offset


class _AlignRescaleBase(rewriter.RewriteRuleClassBase):
    def __init__(self, op_type, before=True):
        super().__init__()
        self.op_type = op_type
        self.before = before

    def check(self, context, main_out, op_value, **__):
        check_result = rewriter.MatchResult()
        main_node = main_out.producer()

        # Check initializer constraints.
        bias = None
        if ir.convenience.get_const_tensor(kernel := main_node.inputs[1]) is None:
            return check_result.fail(f"{kernel.name} is expected to be constant.")
        if (len(main_node.inputs) > 2 and
                ir.convenience.get_const_tensor(bias := main_node.inputs[2]) is None):
            return check_result.fail(f"{bias.name} is expected to be constant.")
        if ir.convenience.get_const_tensor(op_value) is None:
            return check_result.fail(f"{op_value.name} is expected to be constant.")

        # Check broadcastable constraints.
        # Fulfill shape to have same dims than kernel.
        op_shape = np.broadcast_shapes(op_value.shape, (1,) * len(kernel.shape))
        # Constant variable could be a vector only in axis = 1.
        expected_channels = kernel.shape[1] if self.before else kernel.shape[0]
        if (any(op_shape[x] != 1 for x in [0] + list(range(2, len(op_shape)))) or
                op_shape[1] not in {expected_channels, 1}):
            return check_result.fail(f"{kernel.name} and {op_value.name} are not broadcastable.")

        # Store variables.
        self.kernel = kernel
        self.bias = bias
        self.attributes = main_node.attributes
        return check_result


class _AlignOpMul(_AlignRescaleBase):
    def pattern(self, op, x, op_value):
        main_op = getattr(op, self.op_type)
        if self.before:
            return main_op(op.Mul(x, op_value), _allow_other_inputs=True, _outputs=["main_out"])
        return op.Mul(main_op(x, _allow_other_inputs=True, _outputs=["main_out"]), op_value)

    def rewrite(self, op, x, op_value, **__):
        # Fold scale into kernel.
        scale = ir.convenience.get_const_tensor(op_value).numpy()
        if not self.before:
            # Fold scale in filter dimension.
            scale = np.expand_dims(scale, -1)
        kernel = _fold_scale(ir.convenience.get_const_tensor(self.kernel).numpy(), scale)
        op_inputs = [x, _np_to_initializer(op, kernel, name=self.kernel.name)]

        # Fold scale into bias (if required).
        if (bias := self.bias) is not None:
            if not self.before:
                bias = _fold_scale(ir.convenience.get_const_tensor(bias).numpy(), np.squeeze(scale))
                bias = _np_to_initializer(op, bias, name=self.bias.name)
            op_inputs.append(bias)
        return op.op(self.op_type, inputs=op_inputs, attributes=self.attributes)


class _AlignOpAdd(_AlignRescaleBase):
    def check(self, context, main_out, op_value, **__):
        if not ((check_result := super().check(context, main_out, op_value, **__)) and self.before):
            return check_result

        # Transform is only possible (when Add is before to Op) if there are not pads.
        target_node = main_out.producer()
        if any(x != 0 for x in target_node.attributes.get_ints("pads", [0])):
            return check_result.fail(f"{target_node.name} must have pads equal to zero.")

        return check_result

    def pattern(self, op, x, op_value):
        main_op = getattr(op, self.op_type)
        if self.before:
            return main_op(op.Add(x, op_value), _allow_other_inputs=True, _outputs=["main_out"])
        return op.Add(main_op(x, _allow_other_inputs=True, _outputs=["main_out"]), op_value)

    def rewrite(self, op, x, op_value, **__):
        offset = np.squeeze(ir.convenience.get_const_tensor(op_value).numpy())
        # Get bias (if exists).
        if self.bias is None:
            bias_name = f"{x.name}/bias"
            bias = 0
        else:
            bias_name = self.bias.name
            bias = ir.convenience.get_const_tensor(self.bias).numpy()
        # Fold offset into bias.
        bias = _fold_offset(bias, offset, self.kernel if self.before else None)
        bias = _np_to_initializer(op, np.broadcast_to(bias, self.kernel.shape[0]), name=bias_name)
        return op.op(self.op_type, inputs=[x, self.kernel, bias], attributes=self.attributes)


@safe_fail
def align_rescaling(model):
    """Aligns and folds rescaling operations into Conv and Gemm weights.

    This function rewrites the model in-place by searching for patterns where a 'Mul' operation
    is applied before or after a target node, and folds the factor directly into their weights.

    Args:
        model (ONNXModel): the ONNX model to optimize.
    """
    assert isinstance(model, ONNXModel)
    rules = []
    for op_type in ["Conv", "Gemm"]:
        rules.append(_AlignOpAdd.rule(op_type=op_type, before=True))
        rules.append(_AlignOpMul.rule(op_type=op_type, before=True))
        rules.append(_AlignOpMul.rule(op_type=op_type, before=False))
        rules.append(_AlignOpAdd.rule(op_type=op_type, before=False))
    model.rewrite(rules)
