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

__all__ = ["invert_batchnorm_pooling"]

import numpy as np
import onnx_ir as ir
from onnxscript.rewriter._basics import MatchResult
from onnxscript.rewriter._rewrite_rule import RewriteRuleClassBase

from ..model import ONNXModel
from .utils import safe_fail


@safe_fail
def invert_batchnorm_pooling(model):
    """Inverts pooling and BatchNormalization nodes in a model to have BN node before pooling.

    Note:
        Inversion of nodes is equivalent only if the scales (gammas) of BN nodes are positive.

    Args:
        model (ONNXModel): The ONNX model to be processed.
    """

    assert isinstance(model, ONNXModel)
    model.rewrite([_InvertBatchnormMaxPool().rule(), _InvertBatchnormGap().rule()])


class _InvertBatchnormPoolingBase(RewriteRuleClassBase):
    def rewrite(self, op, x, batchnorm_out, pool_out):
        pool_node = pool_out.producer()
        batchnorm_node = batchnorm_out.producer()

        y = op.BatchNormalization(x, *batchnorm_node.inputs[1:])
        return op.op(self.op_type, inputs=[y],
                     attributes=pool_node.attributes)

    def check(self, context, x, batchnorm_out, **_):
        del context  # Not used
        check_result = MatchResult()

        if x.shape is None or len(x.shape) != 4:
            return check_result.fail(f"{x.name} must have a known shape of rank 4")

        batchnorm_node = batchnorm_out.producer()
        for bn_param in batchnorm_node.inputs[1:]:
            if ir.convenience.get_const_tensor(bn_param) is None:
                return check_result.fail(f"{bn_param.name} is not a constant.")

        return check_result


class _InvertBatchnormMaxPool(_InvertBatchnormPoolingBase):
    op_type = "MaxPool"

    def check_scales(self, _, node):
        # It is impossible to invert MaxPool->BN with scales (gamma) <= 0
        scales = node.inputs[1]
        return ir.convenience.get_const_tensor(scales) is not None and \
            np.all(scales.const_value.numpy() > 0)

    def pattern(self, op, x):
        return op.BatchNormalization(op.MaxPool(x, _outputs=["pool_out"]),
                                     _allow_other_inputs=True,
                                     _check=self.check_scales,
                                     _outputs=["batchnorm_out"])


class _InvertBatchnormGap(_InvertBatchnormPoolingBase):
    op_type = "GlobalAveragePool"

    def pattern(self, op, x):
        return op.BatchNormalization(op.GlobalAveragePool(x, _outputs=["pool_out"]),
                                     _allow_other_inputs=True,
                                     _outputs=["batchnorm_out"])
