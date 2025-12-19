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

from typing_extensions import Required, TypedDict

from .task_sort_field import TaskSortField
from .task_filter_param import TaskFilterParam
from .task_search_param import TaskSearchParam

__all__ = ["TaskListParams"]


class TaskListParams(TypedDict, total=False):
    namespace: Required[str]

    filter: TaskFilterParam
    """Filter tasks on various criteria."""

    page: int
    """Page number."""

    page_size: int
    """Page size."""

    search: TaskSearchParam
    """Search tasks using substring matching.

    For example:

    - `?search[name]=chat`: searches all tasks with 'chat' in the name.
    - `?search[description]=support`: searches all tasks with 'support' in the
      description.
    """

    sort: TaskSortField
    """Sort fields for Tasks."""
