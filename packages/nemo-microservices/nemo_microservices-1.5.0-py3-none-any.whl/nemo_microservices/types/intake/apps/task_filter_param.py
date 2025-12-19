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

from typing_extensions import TypedDict

from ...updated_at_filter_param import UpdatedAtFilterParam
from ...created_at_filter_op_param import CreatedAtFilterOpParam

__all__ = ["TaskFilterParam"]


class TaskFilterParam(TypedDict, total=False):
    app: str
    """Filter by app reference (namespace/name)."""

    created_at: CreatedAtFilterOpParam
    """Filter for created_at timestamp."""

    name: str
    """Filter by task name."""

    namespace: str
    """Filter by namespace id."""

    project: str
    """Filter by project name."""

    updated_at: UpdatedAtFilterParam
    """Filter for updated_at timestamp."""
