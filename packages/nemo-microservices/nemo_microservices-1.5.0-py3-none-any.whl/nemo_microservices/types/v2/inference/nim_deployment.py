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

from ...._compat import PYDANTIC_V1, ConfigDict
from ...._models import BaseModel
from .model_type import ModelType
from .k8s_nim_operator_config import K8sNIMOperatorConfig

__all__ = ["NIMDeployment"]


class NIMDeployment(BaseModel):
    gpu: int
    """Number of GPUs required for the deployment"""

    additional_envs: Optional[Dict[str, object]] = None
    """Additional environment variables for the deployment"""

    disk_size: Optional[str] = None
    """Disk size for the deployment"""

    image_name: Optional[str] = None
    """Container image name from NGC. If not specified, defaults to multi-llm"""

    image_tag: Optional[str] = None
    """Container image tag from NGC"""

    k8s_nim_operator_config: Optional[K8sNIMOperatorConfig] = None
    """Kubernetes configuration for NIM deployment via k8s-nim-operator.

    These fields provide typed access to commonly-used NIMService Spec fields and
    are applied before override_config in the compilation precedence.
    """

    lora_enabled: Optional[bool] = None
    """Whether to enable LoRA support"""

    model_name: Optional[str] = None
    """Model name - HF style for HuggingFace, NMP name for NMP models"""

    model_namespace: Optional[str] = None
    """Model namespace - HF style for HuggingFace, NMP namespace for NMP models"""

    model_provider: Optional[str] = None
    """Model provider: 'hf' for HuggingFace or 'nmp' for NMP"""

    model_revision: Optional[str] = None
    """Model revision (branch, tag, or commit).

    If not specified, parsed from model_name @revision suffix or defaults to 'main'
    """

    model_type: Optional[ModelType] = None
    """Model type enum for NIM deployments."""

    override_config: Optional[Dict[str, object]] = None
    """Raw NIMService spec configuration that takes precedence over generated config.

    Allows end users to provide advanced configuration options directly.
    """

    if not PYDANTIC_V1:
        # allow fields with a `model_` prefix
        model_config = ConfigDict(protected_namespaces=tuple())
