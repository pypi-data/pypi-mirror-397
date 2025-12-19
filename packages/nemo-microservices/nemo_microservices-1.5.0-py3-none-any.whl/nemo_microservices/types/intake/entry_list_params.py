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

from .entry_sort_field import EntrySortField
from .entry_filter_param import EntryFilterParam
from .entry_search_param import EntrySearchParam

__all__ = ["EntryListParams"]


class EntryListParams(TypedDict, total=False):
    filter: EntryFilterParam
    """Filter entries on various criteria.

    Examples:

    - `?filter[namespace]=default`: Filter by namespace
    - `?filter[app]=default/my-app`: Filter by app reference
    - `?filter[has_thumb]=true`: Filter entries with thumb feedback
    - `?filter[longest_per_thread]=true`: Return only longest entry per thread
    """

    page: int
    """Page number."""

    page_size: int
    """Page size."""

    search: EntrySearchParam
    """Search entries using substring matching."""

    sort: EntrySortField
    """Sort fields for Entries."""
