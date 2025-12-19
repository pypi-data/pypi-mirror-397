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
from ..updated_at_filter import UpdatedAtFilter
from .entry_context_filter import EntryContextFilter
from ..created_at_filter_op import CreatedAtFilterOp
from .entry_user_rating_filter import EntryUserRatingFilter

__all__ = ["EntryFilter"]


class EntryFilter(BaseModel):
    context: Optional[EntryContextFilter] = None
    """Filter for entry context fields."""

    created_at: Optional[CreatedAtFilterOp] = None
    """Filter for created_at timestamp."""

    external_id: Optional[str] = None
    """Filter by external ID (e.g., completion_id)."""

    has_events: Optional[bool] = None
    """Filter by presence of any events."""

    has_opinion: Optional[bool] = None
    """Filter by presence of opinion."""

    has_rating: Optional[bool] = None
    """Filter by presence of rating."""

    has_rewrite: Optional[bool] = None
    """Filter by presence of rewrite."""

    has_thumb: Optional[bool] = None
    """Filter by presence of thumb feedback."""

    longest_per_thread: Optional[bool] = None
    """If true, return only the longest entry per thread (based on message count)."""

    namespace: Optional[str] = None
    """Filter by namespace id."""

    project: Optional[str] = None
    """Filter by project name."""

    updated_at: Optional[UpdatedAtFilter] = None
    """Filter for updated_at timestamp."""

    user_rating: Optional[EntryUserRatingFilter] = None
    """Filter for entry user rating fields."""
