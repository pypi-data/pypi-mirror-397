#!/usr/bin/env python
# ******************************************************************************
# Copyright 2024 Brainchip Holdings Ltd.
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

__all__ = ["convert_conv_to_gemm"]

import numpy as np
import onnx_ir as ir
from onnxscript.rewriter import RewriteRuleClassBase
from onnxscript.rewriter._basics import MatchResult

from ..model import ONNXModel
from .utils import safe_fail


class _ConvToGemmBase(RewriteRuleClassBase):
    def rewrite(self, op, x, out1, **_):
        conv_node = out1.producer()

        # Create Gemm weights from Conv
        conv_weights = conv_node.inputs[1].const_value.numpy()
        gemm_weights = np.reshape(conv_weights, (conv_weights.shape[0], -1))

        initializers = [op.initializer(ir.tensor(gemm_weights),
                                       name=conv_node.inputs[1].name)]
        # Check Bias
        if len(conv_node.inputs) > 2:
            conv_bias = conv_node.inputs[2].const_value.numpy()
            initializers.append(op.initializer(ir.tensor(conv_bias),
                                               name=conv_node.inputs[2].name))

        return op.Gemm(op.Flatten(x), *initializers, transB=1)

    def check(self, context, **_):
        # The checks performed are:
        # - Verifies that the input to the Conv node has a known shape
        #   and its spatial dimensions are (1, 1).
        # - Checks that the output of the Squeeze or Reshape node has a known shape
        #   and it is equal to (conv_input[0], filters)
        check_result = MatchResult()
        squeeze_or_reshape_node, conv_node = context.nodes

        # Check input
        conv_input = conv_node.inputs[0]
        if conv_input.shape is None:
            return check_result.fail(f"Unknown shape for Conv input ({conv_input.name}).")

        if conv_input.shape[-2:] != (1, 1):
            return check_result.fail(f"Conv input ({conv_input.name}) spatial "
                                     f"dimensions are not (1, 1).")
        # Check conv groups
        if (group := conv_node.attributes.get("group", ir.AttrInt64("group", 1)).as_int()) != 1:
            return check_result.fail(f"Conv group should be 1. Actual : {group}")

        # Check reshape output shape
        squeeze_or_reshape_output = squeeze_or_reshape_node.outputs[0]
        if squeeze_or_reshape_output.shape is None:
            return check_result.fail(f"Unknown shape for reshape/squeeze output "
                                     f"({squeeze_or_reshape_output}).")

        filters = conv_node.inputs[1].const_value.shape[0]
        if squeeze_or_reshape_output.shape != (conv_input.shape[0], filters):
            return check_result.fail(f"Reshape/squeeze output ({squeeze_or_reshape_output}) "
                                     f"is not equal to {(conv_input.shape[0], filters)}.")

        return check_result


class _ConvReshapeToGemm(_ConvToGemmBase):
    def pattern(self, op, x):
        return op.Reshape(op.Conv(x, _allow_other_inputs=True, _outputs=["out1"]),
                          _allow_other_inputs=True)


class _ConvSqueezeToGemm(_ConvToGemmBase):
    def pattern(self, op, x):
        return op.Squeeze(op.Conv(x, _allow_other_inputs=True, _outputs=["out1"]),
                          _allow_other_inputs=True)


@safe_fail
def convert_conv_to_gemm(model):
    """Transforms Conv + (Reshape/Squeeze) into Flatten + Gemm if both operation
    chains are compatible.

    Args:
        model (ONNXModel): The ONNX model to be processed.
    """

    assert isinstance(model, ONNXModel)
    model.rewrite([_ConvReshapeToGemm().rule(), _ConvSqueezeToGemm().rule()])
