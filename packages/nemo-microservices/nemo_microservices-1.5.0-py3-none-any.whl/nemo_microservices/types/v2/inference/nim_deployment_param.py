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

from __future__ import annotations

from typing import Dict
from typing_extensions import Required, TypedDict

from .model_type import ModelType
from .k8s_nim_operator_config_param import K8sNIMOperatorConfigParam

__all__ = ["NIMDeploymentParam"]


class NIMDeploymentParam(TypedDict, total=False):
    gpu: Required[int]
    """Number of GPUs required for the deployment"""

    additional_envs: Dict[str, object]
    """Additional environment variables for the deployment"""

    disk_size: str
    """Disk size for the deployment"""

    image_name: str
    """Container image name from NGC. If not specified, defaults to multi-llm"""

    image_tag: str
    """Container image tag from NGC"""

    k8s_nim_operator_config: K8sNIMOperatorConfigParam
    """Kubernetes configuration for NIM deployment via k8s-nim-operator.

    These fields provide typed access to commonly-used NIMService Spec fields and
    are applied before override_config in the compilation precedence.
    """

    lora_enabled: bool
    """Whether to enable LoRA support"""

    model_name: str
    """Model name - HF style for HuggingFace, NMP name for NMP models"""

    model_namespace: str
    """Model namespace - HF style for HuggingFace, NMP namespace for NMP models"""

    model_provider: str
    """Model provider: 'hf' for HuggingFace or 'nmp' for NMP"""

    model_revision: str
    """Model revision (branch, tag, or commit).

    If not specified, parsed from model_name @revision suffix or defaults to 'main'
    """

    model_type: ModelType
    """Model type enum for NIM deployments."""

    override_config: Dict[str, object]
    """Raw NIMService spec configuration that takes precedence over generated config.

    Allows end users to provide advanced configuration options directly.
    """
