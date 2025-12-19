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

from typing import Dict, Optional
from typing_extensions import Literal

from ..._models import BaseModel
from .model_cache_config import ModelCacheConfig

__all__ = ["GuardrailModel"]


class GuardrailModel(BaseModel):
    engine: str

    type: str

    api_key_env_var: Optional[str] = None
    """Optional environment variable with model's API Key. Do not include "$"."""

    cache: Optional[ModelCacheConfig] = None
    """Configuration for model caching."""

    mode: Optional[Literal["chat", "text"]] = None
    """Whether the mode is 'text' completion or 'chat' completion.

    Allowed values are 'chat' or 'text'.
    """

    model: Optional[str] = None
    """The name of the model.

    If not specified, it should be specified through the parameters attribute.
    """

    parameters: Optional[Dict[str, object]] = None
