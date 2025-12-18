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

__all__ = ["Quantizer"]

from tf_keras.layers import Layer


class Quantizer(Layer):
    """The base class for all quantizers.

    The bitwidth defines the number of quantization levels on which the
    values will be quantized.
    For a quantizer that accepts unsigned values, the maximum quantization
    level is :math:`2 ^ {bitwidth} - 1`.
    For a quantizer that accepts signed values, we lose one bit of precision to
    store the sign.
    When the quantizer is signed, the quantization interval is asymmetric around
    zero (i.e range: :math:`[- 2 ^ {bitwidth - 1}, 2 ^ {bitwidth - 1} - 1]`).

    Args:
        bitwidth (int): the quantization bitwidth.
        signed (bool, optional): whether the quantizer expects signed values or unsigned.
            Defaults to True.
    """

    def __init__(self, bitwidth, signed=True, **kwargs):
        min_bitwidth = 2 if signed else 1
        if not isinstance(bitwidth, int) or bitwidth < min_bitwidth:
            raise ValueError(
                f"Bitwidth should be an int >= {min_bitwidth}, currently {bitwidth}")
        self.bitwidth = bitwidth
        self.signed = signed
        self.value_bits = bitwidth - 1 if signed else bitwidth
        super().__init__(**kwargs)

    def get_config(self):
        """Get the config of the layer.

        Returns:
            dict: the config of the layer.
        """
        config = super().get_config()
        config.update({"bitwidth": self.bitwidth})
        config.update({"signed": self.signed})
        return config
