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

from typing import Dict, Union, Iterable
from typing_extensions import Required, TypeAlias, TypedDict

from .entry_data_param import EntryDataParam
from .user_rating_param import UserRatingParam
from .entry_context_param import EntryContextParam
from .user_action_event_param import UserActionEventParam
from ..shared_params.ownership import Ownership
from .user_feedback_event_param import UserFeedbackEventParam
from .reviewer_annotation_event_param import ReviewerAnnotationEventParam

__all__ = ["EntryCreateParams", "Event"]


class EntryCreateParams(TypedDict, total=False):
    context: Required[EntryContextParam]
    """Contextual metadata attached to every entry record.

    Keeping these grouped in a dedicated object avoids polluting the top-level
    namespace and makes it trivial to extend without breaking compatibility.
    """

    data: Required[EntryDataParam]
    """Entry data containing the request and response for an LLM interaction."""

    custom_fields: Dict[str, object]
    """A set of custom fields that the user can define and use for various purposes."""

    description: str
    """The description of the entity."""

    events: Iterable[Event]
    """All events associated with this entry."""

    external_id: str
    """
    Optional client-provided identifier (e.g., completion_id from an LLM provider
    like OpenAI or NIM). Must be globally unique if provided—attempting to create an
    entry with a duplicate external_id will fail with a 409 error. If your service
    provides unique IDs (like 'chatcmpl-abc123'), you should use them here for
    easier lookups. Entries can be retrieved using external_id via the prefix
    syntax: GET /entries/external:chatcmpl-abc123
    """

    namespace: str
    """The namespace of the entity.

    This can be missing for namespace entities or in deployments that don't use
    namespaces.
    """

    ownership: Ownership
    """Information about ownership of an entity.

    If the entity is a namespace, the `access_policies` will typically apply to all
    entities inside the namespace.
    """

    project: str
    """The URN of the project associated with this entity."""

    user_rating: UserRatingParam
    """User's rating/evaluation of an AI response.

    This captures various forms of end-user feedback about a model's response,
    including binary thumbs up/down ratings, numeric scores, free-text opinions,
    suggested rewrites, and structured category ratings.

    Either `thumb` or `rating` should be provided (they are mutually exclusive), but
    all fields are optional to accommodate different feedback collection patterns.
    """


Event: TypeAlias = Union[UserFeedbackEventParam, UserActionEventParam, ReviewerAnnotationEventParam]
