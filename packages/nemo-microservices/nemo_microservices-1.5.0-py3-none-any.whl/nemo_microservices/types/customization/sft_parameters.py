# SPDX-FileCopyrightText: Copyright (c) 2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional

from ..._models import BaseModel

__all__ = ["SftParameters"]


class SftParameters(BaseModel):
    attention_dropout: Optional[float] = None
    """Dropout probability applied to attention weights in the self-attention
    mechanism.

    Randomly zeros a fraction of attention scores during training to improve
    generalization. Typical values range from 0.0 (no dropout) to 0.1. Set to None
    to use model defaults. Higher values can help prevent the model from
    over-relying on specific token relationships.
    """

    hidden_dropout: Optional[float] = None
    """Dropout probability applied to the hidden states in transformer layers.

    Randomly zeros a fraction of hidden state activations during training to prevent
    overfitting. Typical values range from 0.0 (no dropout) to 0.1. Set to None to
    use model defaults. Higher values increase regularization but may slow
    convergence.
    """
