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
from typing_extensions import TypedDict

__all__ = ["ExportConfigParamParam"]


class ExportConfigParamParam(TypedDict, total=False):
    filters: Dict[str, object]
    """
    Filter criteria for selecting entries (namespace, app, task, thread_id,
    external_id, has_thumb, has_rating, longest_per_thread, etc.)
    """

    format_options: Dict[str, object]
    """Format options for the export (e.g., row_transformation)"""

    limit: int
    """Maximum number of entries to export. None means no limit."""

    search: Dict[str, object]
    """Search criteria for finding entries"""
