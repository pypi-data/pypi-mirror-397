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

from typing import Dict, List, Union, Optional
from datetime import datetime
from typing_extensions import Annotated, TypeAlias

from ..._utils import PropertyInfo
from ..._models import BaseModel
from .entry_data import EntryData
from .user_rating import UserRating
from .entry_context import EntryContext
from ..shared.ownership import Ownership
from .user_action_event import UserActionEvent
from .user_feedback_event import UserFeedbackEvent
from .reviewer_annotation_event import ReviewerAnnotationEvent

__all__ = ["Entry", "Event"]

Event: TypeAlias = Annotated[
    Union[UserFeedbackEvent, UserActionEvent, ReviewerAnnotationEvent], PropertyInfo(discriminator="event_type")
]


class Entry(BaseModel):
    context: EntryContext
    """Contextual metadata attached to every entry record.

    Keeping these grouped in a dedicated object avoids polluting the top-level
    namespace and makes it trivial to extend without breaking compatibility.
    """

    data: EntryData
    """Entry data containing the request and response for an LLM interaction."""

    id: Optional[str] = None
    """The ID of the entity.

    With the exception of namespaces, this is always a semantically-prefixed
    base58-encoded uuid4 [<prefix>-base58(uuid4())].
    """

    created_at: Optional[datetime] = None
    """Timestamp for when the entity was created."""

    custom_fields: Optional[Dict[str, object]] = None
    """A set of custom fields that the user can define and use for various purposes."""

    description: Optional[str] = None
    """The description of the entity."""

    events: Optional[List[Event]] = None
    """All events associated with this entry."""

    external_id: Optional[str] = None
    """
    Optional client-provided identifier (e.g., completion_id from an LLM provider
    like OpenAI or NIM). Must be globally unique if provided—attempting to create an
    entry with a duplicate external_id will fail with a 409 error. If your service
    provides unique IDs (like 'chatcmpl-abc123'), you should use them here for
    easier lookups. Entries can be retrieved using external_id via the prefix
    syntax: GET /entries/external:chatcmpl-abc123
    """

    namespace: Optional[str] = None
    """The namespace of the entity.

    This can be missing for namespace entities or in deployments that don't use
    namespaces.
    """

    ownership: Optional[Ownership] = None
    """Information about ownership of an entity.

    If the entity is a namespace, the `access_policies` will typically apply to all
    entities inside the namespace.
    """

    project: Optional[str] = None
    """The URN of the project associated with this entity."""

    schema_version: Optional[str] = None
    """The version of the schema for the object. Internal use only."""

    updated_at: Optional[datetime] = None
    """Timestamp for when the entity was last updated."""

    user_rating: Optional[UserRating] = None
    """User's rating/evaluation of an AI response.

    This captures various forms of end-user feedback about a model's response,
    including binary thumbs up/down ratings, numeric scores, free-text opinions,
    suggested rewrites, and structured category ratings.

    Either `thumb` or `rating` should be provided (they are mutually exclusive), but
    all fields are optional to accommodate different feedback collection patterns.
    """
