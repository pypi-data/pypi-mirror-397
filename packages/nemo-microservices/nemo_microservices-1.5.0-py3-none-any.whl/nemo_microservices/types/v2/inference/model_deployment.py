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
from datetime import datetime

from ...._compat import PYDANTIC_V1, ConfigDict
from ...._models import BaseModel
from .model_deployment_status import ModelDeploymentStatus

__all__ = ["ModelDeployment"]


class ModelDeployment(BaseModel):
    config: str
    """Reference to the ModelDeploymentConfig name"""

    config_version: int
    """Reference to the specific ModelDeploymentConfig version"""

    entity_version: int
    """Version of this deployment. Automatically managed."""

    name: str
    """Name of the entity. Name/namespace combo must be unique across all entities."""

    namespace: str
    """The namespace of the entity."""

    id: Optional[str] = None
    """Unique identifier for the deployment"""

    created_at: Optional[datetime] = None

    hf_token_secret_id: Optional[str] = None
    """Reference to the Hugging Face token secret stored in the Secrets service."""

    model_provider_id: Optional[str] = None
    """
    Optional reference to the auto-created ModelProvider namespace/name (format:
    namespace/name)
    """

    project: Optional[str] = None
    """The URN of the project associated with this entity."""

    status: Optional[ModelDeploymentStatus] = None
    """Status enum for ModelDeployment objects."""

    status_message: Optional[str] = None
    """Detailed status message, populated by models controller"""

    updated_at: Optional[datetime] = None

    if not PYDANTIC_V1:
        # allow fields with a `model_` prefix
        model_config = ConfigDict(protected_namespaces=tuple())
