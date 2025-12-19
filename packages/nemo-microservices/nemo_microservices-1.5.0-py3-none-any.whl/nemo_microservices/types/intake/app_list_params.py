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

from .app_sort_field import AppSortField
from .app_filter_param import AppFilterParam
from .app_search_param import AppSearchParam

__all__ = ["AppListParams"]


class AppListParams(TypedDict, total=False):
    filter: AppFilterParam
    """Filter apps on various criteria."""

    page: int
    """Page number."""

    page_size: int
    """Page size."""

    search: AppSearchParam
    """Search apps using substring matching.

    You can combine multiple search fields and filters.

    For example:

    - `?search[name]=chatbot`: searches all apps with 'chatbot' in the name.
    - `?search[namespace]=default`: searches all apps with 'default' in the
      namespace.
    - `?search[description]=support`: searches all apps with 'support' in the
      description.
    - `?search[updated_at][start]=2024-01-01T00:00:00` finds all apps updated on or
      after the start date
    """

    sort: AppSortField
    """Sort fields for Apps."""
