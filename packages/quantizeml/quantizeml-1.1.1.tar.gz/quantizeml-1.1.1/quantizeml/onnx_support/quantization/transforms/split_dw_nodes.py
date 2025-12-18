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

__all__ = ["split_dw_nodes"]

import numpy as np
import onnx_ir as ir
from onnxscript.rewriter._basics import MatchResult
from onnxscript.rewriter._rewrite_rule import RewriteRuleClassBase

from ..model import ONNXModel
from .utils import safe_fail, compute_conv_same_pads


@safe_fail
def split_dw_nodes(model):
    """Transforms depthwise convolution nodes with stride-2 and kernel sizes in (5x5 or 7x7)
    into an equivalent sequence of two depthwise convolutions:

    - A depthwise convolution with the same kernel size (5x5 or 7x7) and stride=1.
    - Followed by an identity depthwise convolution with a 3x3 kernel and stride=2.

    Args:
        model (ONNXModel): The ONNX model to be processed.
    """

    assert isinstance(model, ONNXModel)
    model.rewrite([_SplitDwNodes().rule()])


class _SplitDwNodes(RewriteRuleClassBase):
    def pattern(self, op, x, w):
        return op.Conv(x, w, _allow_other_inputs=True, _outputs=["conv"])

    def rewrite(self, op, w, conv, **_):
        ir_node = conv.producer()
        attributes = ir_node.attributes

        # Change strides to 1 and padding to SAME paddings
        attributes["strides"] = ir.AttrInt64s("strides", (1, 1))

        # Compute pads following SAME padding.
        # Note when stride=1, UPPER and LOWER modes produce the same pads.
        pads = compute_conv_same_pads(ir_node.inputs[0].shape[2:], w.shape[2:], (1, 1))
        attributes["pads"] = ir.AttrInt64s("pads", pads)
        dw_stride_1 = op.Conv(*ir_node.inputs, **attributes)

        # Compute SAME pads to apply in next conv.
        # Note we fix the mode to UPPER to have the same behavior than pads in Keras.
        new_pads = compute_conv_same_pads(ir_node.inputs[0].shape[2:], (3, 3), (2, 2), mode="UPPER")

        # Apply "identity" with kernel size=3 and strides=2.
        # The position of '1' within the kernel depends on the number of pads applied by the
        # first conv and the new ones to be applied with respect to the originals:
        # - if pads + new_pads == original_pads: '1' is placed in the left/top corner of the kernel
        # - if pads + new_pads == original_pads + 1: '1' is placed in the center
        # - if pads + new_pads == original_pads + 2: '1' is placed in the right/bottom corner
        coords = [p + n_p - o_p for p, n_p, o_p in zip(pads[:2], new_pads[:2], self.org_pads[:2])]
        identity_w = np.zeros((w.shape[0], 1, 3, 3), dtype="float32")
        identity_w[(np.arange(w.shape[0]), 0, *coords)] = 1
        identity_w = op.initializer(ir.tensor(identity_w), name=f"{ir_node.name}_identity_weights")

        # Create the second depthwise.
        dw_stride_2 = op.Conv(
            dw_stride_1,
            identity_w,
            kernel_shape=(3, 3),
            strides=(2, 2),
            pads=new_pads,
            group=w.shape[0],
        )
        return dw_stride_2

    def check(self, context, x, w, conv):
        del context  # Not used
        check_result = MatchResult()

        attributes = conv.producer().attributes
        group = attributes.get("group", ir.AttrInt64("group", 1))
        strides = attributes.get("strides", ir.AttrInt64s("strides", (1, 1)))
        self.org_pads = list(attributes.get("pads", ir.AttrInt64s("pads", (0, 0, 0, 0))).value)

        # Compute expected pads
        # Shape is needed to compute pads
        if x.shape is None:
            return check_result.fail(f"{x.name} shape is unknown.")
        expected_pads = [compute_conv_same_pads(x.shape[2:], w.shape[2:], strides.value, mode=m)
                         for m in ["LOWER", "UPPER"]]

        if not (
            group.value == w.shape[0]
            and w.shape[2:] in {(5, 5), (7, 7)}
            and list(strides.value) == [2, 2]
            and self.org_pads in expected_pads
        ):
            return check_result.fail(
                f"Invalid attributes. Expected group == in_channels ({w.shape[0]}), "
                f"kernel size in (5x5, 7x7), strides == (2, 2), and pads one of {expected_pads}; "
                f"got group={group.value}, kernel size={w.shape[2:]}, strides={strides.value} "
                f"pads={self.org_pads}."
            )

        return check_result
