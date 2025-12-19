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

from typing import Dict, Iterable

import httpx

from .events import (
    EventsResource,
    AsyncEventsResource,
    EventsResourceWithRawResponse,
    AsyncEventsResourceWithRawResponse,
    EventsResourceWithStreamingResponse,
    AsyncEventsResourceWithStreamingResponse,
)
from ...._types import Body, Omit, Query, Headers, NoneType, NotGiven, omit, not_given
from ...._utils import maybe_transform, async_maybe_transform
from ...._compat import cached_property
from ...._resource import SyncAPIResource, AsyncAPIResource
from ...._response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from ....pagination import SyncDefaultPagination, AsyncDefaultPagination
from ...._base_client import AsyncPaginator, make_request_options
from ....types.intake import (
    EntryDataParam,
    EntrySortField,
    entry_list_params,
    entry_create_params,
    entry_update_params,
)
from ....types.intake.entry import Entry
from ....types.intake.entry_data_param import EntryDataParam
from ....types.intake.entry_sort_field import EntrySortField
from ....types.shared_params.ownership import Ownership
from ....types.intake.user_rating_param import UserRatingParam
from ....types.intake.entry_filter_param import EntryFilterParam
from ....types.intake.entry_search_param import EntrySearchParam
from ....types.intake.entry_context_param import EntryContextParam

__all__ = ["EntriesResource", "AsyncEntriesResource"]


class EntriesResource(SyncAPIResource):
    @cached_property
    def events(self) -> EventsResource:
        return EventsResource(self._client)

    @cached_property
    def with_raw_response(self) -> EntriesResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://docs.nvidia.com/nemo/microservices/latest/pysdk/index.html#accessing-raw-response-data-e-g-headers
        """
        return EntriesResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> EntriesResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://docs.nvidia.com/nemo/microservices/latest/pysdk/index.html#with_streaming_response
        """
        return EntriesResourceWithStreamingResponse(self)

    def create(
        self,
        *,
        context: EntryContextParam,
        data: EntryDataParam,
        custom_fields: Dict[str, object] | Omit = omit,
        description: str | Omit = omit,
        events: Iterable[entry_create_params.Event] | Omit = omit,
        external_id: str | Omit = omit,
        namespace: str | Omit = omit,
        ownership: Ownership | Omit = omit,
        project: str | Omit = omit,
        user_rating: UserRatingParam | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> Entry:
        """
        Create a new entry.

        Apps and tasks referenced in the entry context will be auto-created if they
        don't exist.

        Args:
          context: Contextual metadata attached to every entry record.

              Keeping these grouped in a dedicated object avoids polluting the top-level
              namespace and makes it trivial to extend without breaking compatibility.

          data: Entry data containing the request and response for an LLM interaction.

          custom_fields: A set of custom fields that the user can define and use for various purposes.

          description: The description of the entity.

          events: All events associated with this entry.

          external_id: Optional client-provided identifier (e.g., completion_id from an LLM provider
              like OpenAI or NIM). Must be globally unique if provided—attempting to create an
              entry with a duplicate external_id will fail with a 409 error. If your service
              provides unique IDs (like 'chatcmpl-abc123'), you should use them here for
              easier lookups. Entries can be retrieved using external_id via the prefix
              syntax: GET /entries/external:chatcmpl-abc123

          namespace: The namespace of the entity. This can be missing for namespace entities or in
              deployments that don't use namespaces.

          ownership: Information about ownership of an entity.

              If the entity is a namespace, the `access_policies` will typically apply to all
              entities inside the namespace.

          project: The URN of the project associated with this entity.

          user_rating: User's rating/evaluation of an AI response.

              This captures various forms of end-user feedback about a model's response,
              including binary thumbs up/down ratings, numeric scores, free-text opinions,
              suggested rewrites, and structured category ratings.

              Either `thumb` or `rating` should be provided (they are mutually exclusive), but
              all fields are optional to accommodate different feedback collection patterns.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/v1/intake/entries",
            body=maybe_transform(
                {
                    "context": context,
                    "data": data,
                    "custom_fields": custom_fields,
                    "description": description,
                    "events": events,
                    "external_id": external_id,
                    "namespace": namespace,
                    "ownership": ownership,
                    "project": project,
                    "user_rating": user_rating,
                },
                entry_create_params.EntryCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=Entry,
        )

    def retrieve(
        self,
        entry_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> Entry:
        """
        Get a specific entry by ID or external_id.

        Use `external:{external_id}` to get by external_id. Example:
        `/v1/intake/entries/external:chatcmpl-abc123`

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not entry_id:
            raise ValueError(f"Expected a non-empty value for `entry_id` but received {entry_id!r}")
        return self._get(
            f"/v1/intake/entries/{entry_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=Entry,
        )

    def update(
        self,
        entry_id: str,
        *,
        context: EntryContextParam | Omit = omit,
        custom_fields: Dict[str, object] | Omit = omit,
        data: EntryDataParam | Omit = omit,
        description: str | Omit = omit,
        events: Iterable[entry_update_params.Event] | Omit = omit,
        ownership: Ownership | Omit = omit,
        project: str | Omit = omit,
        user_rating: UserRatingParam | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> Entry:
        """
        Update an existing entry by ID or external_id.

        Use `external:{external_id}` to update by external_id. Example:
        `/v1/intake/entries/external:chatcmpl-abc123`

        Args:
          context: Contextual metadata attached to every entry record.

              Keeping these grouped in a dedicated object avoids polluting the top-level
              namespace and makes it trivial to extend without breaking compatibility.

          custom_fields: A set of custom fields that the user can define and use for various purposes.

          data: Entry data containing the request and response for an LLM interaction.

          description: The description of the entity.

          events: All events associated with this entry.

          ownership: Information about ownership of an entity.

              If the entity is a namespace, the `access_policies` will typically apply to all
              entities inside the namespace.

          project: The URN of the project associated with this entity.

          user_rating: User's rating/evaluation of an AI response.

              This captures various forms of end-user feedback about a model's response,
              including binary thumbs up/down ratings, numeric scores, free-text opinions,
              suggested rewrites, and structured category ratings.

              Either `thumb` or `rating` should be provided (they are mutually exclusive), but
              all fields are optional to accommodate different feedback collection patterns.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not entry_id:
            raise ValueError(f"Expected a non-empty value for `entry_id` but received {entry_id!r}")
        return self._patch(
            f"/v1/intake/entries/{entry_id}",
            body=maybe_transform(
                {
                    "context": context,
                    "custom_fields": custom_fields,
                    "data": data,
                    "description": description,
                    "events": events,
                    "ownership": ownership,
                    "project": project,
                    "user_rating": user_rating,
                },
                entry_update_params.EntryUpdateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=Entry,
        )

    def list(
        self,
        *,
        filter: EntryFilterParam | Omit = omit,
        page: int | Omit = omit,
        page_size: int | Omit = omit,
        search: EntrySearchParam | Omit = omit,
        sort: EntrySortField | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> SyncDefaultPagination[Entry]:
        """
        List all entries with filtering and search capabilities.

        When longest_per_thread=true is set in filters, returns only the longest entry
        (by message count) for each unique thread_id.

        Args:
          filter: Filter entries on various criteria.

              Examples:

              - `?filter[namespace]=default`: Filter by namespace
              - `?filter[app]=default/my-app`: Filter by app reference
              - `?filter[has_thumb]=true`: Filter entries with thumb feedback
              - `?filter[longest_per_thread]=true`: Return only longest entry per thread

          page: Page number.

          page_size: Page size.

          search: Search entries using substring matching.

          sort: Sort fields for Entries.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._get_api_list(
            "/v1/intake/entries",
            page=SyncDefaultPagination[Entry],
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "filter": filter,
                        "page": page,
                        "page_size": page_size,
                        "search": search,
                        "sort": sort,
                    },
                    entry_list_params.EntryListParams,
                ),
            ),
            model=Entry,
        )

    def delete(
        self,
        entry_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> None:
        """
        Delete an entry by ID or external_id.

        Use `external:{external_id}` to delete by external_id. Example:
        `/v1/intake/entries/external:chatcmpl-abc123`

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not entry_id:
            raise ValueError(f"Expected a non-empty value for `entry_id` but received {entry_id!r}")
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        return self._delete(
            f"/v1/intake/entries/{entry_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=NoneType,
        )


class AsyncEntriesResource(AsyncAPIResource):
    @cached_property
    def events(self) -> AsyncEventsResource:
        return AsyncEventsResource(self._client)

    @cached_property
    def with_raw_response(self) -> AsyncEntriesResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://docs.nvidia.com/nemo/microservices/latest/pysdk/index.html#accessing-raw-response-data-e-g-headers
        """
        return AsyncEntriesResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncEntriesResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://docs.nvidia.com/nemo/microservices/latest/pysdk/index.html#with_streaming_response
        """
        return AsyncEntriesResourceWithStreamingResponse(self)

    async def create(
        self,
        *,
        context: EntryContextParam,
        data: EntryDataParam,
        custom_fields: Dict[str, object] | Omit = omit,
        description: str | Omit = omit,
        events: Iterable[entry_create_params.Event] | Omit = omit,
        external_id: str | Omit = omit,
        namespace: str | Omit = omit,
        ownership: Ownership | Omit = omit,
        project: str | Omit = omit,
        user_rating: UserRatingParam | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> Entry:
        """
        Create a new entry.

        Apps and tasks referenced in the entry context will be auto-created if they
        don't exist.

        Args:
          context: Contextual metadata attached to every entry record.

              Keeping these grouped in a dedicated object avoids polluting the top-level
              namespace and makes it trivial to extend without breaking compatibility.

          data: Entry data containing the request and response for an LLM interaction.

          custom_fields: A set of custom fields that the user can define and use for various purposes.

          description: The description of the entity.

          events: All events associated with this entry.

          external_id: Optional client-provided identifier (e.g., completion_id from an LLM provider
              like OpenAI or NIM). Must be globally unique if provided—attempting to create an
              entry with a duplicate external_id will fail with a 409 error. If your service
              provides unique IDs (like 'chatcmpl-abc123'), you should use them here for
              easier lookups. Entries can be retrieved using external_id via the prefix
              syntax: GET /entries/external:chatcmpl-abc123

          namespace: The namespace of the entity. This can be missing for namespace entities or in
              deployments that don't use namespaces.

          ownership: Information about ownership of an entity.

              If the entity is a namespace, the `access_policies` will typically apply to all
              entities inside the namespace.

          project: The URN of the project associated with this entity.

          user_rating: User's rating/evaluation of an AI response.

              This captures various forms of end-user feedback about a model's response,
              including binary thumbs up/down ratings, numeric scores, free-text opinions,
              suggested rewrites, and structured category ratings.

              Either `thumb` or `rating` should be provided (they are mutually exclusive), but
              all fields are optional to accommodate different feedback collection patterns.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/v1/intake/entries",
            body=await async_maybe_transform(
                {
                    "context": context,
                    "data": data,
                    "custom_fields": custom_fields,
                    "description": description,
                    "events": events,
                    "external_id": external_id,
                    "namespace": namespace,
                    "ownership": ownership,
                    "project": project,
                    "user_rating": user_rating,
                },
                entry_create_params.EntryCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=Entry,
        )

    async def retrieve(
        self,
        entry_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> Entry:
        """
        Get a specific entry by ID or external_id.

        Use `external:{external_id}` to get by external_id. Example:
        `/v1/intake/entries/external:chatcmpl-abc123`

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not entry_id:
            raise ValueError(f"Expected a non-empty value for `entry_id` but received {entry_id!r}")
        return await self._get(
            f"/v1/intake/entries/{entry_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=Entry,
        )

    async def update(
        self,
        entry_id: str,
        *,
        context: EntryContextParam | Omit = omit,
        custom_fields: Dict[str, object] | Omit = omit,
        data: EntryDataParam | Omit = omit,
        description: str | Omit = omit,
        events: Iterable[entry_update_params.Event] | Omit = omit,
        ownership: Ownership | Omit = omit,
        project: str | Omit = omit,
        user_rating: UserRatingParam | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> Entry:
        """
        Update an existing entry by ID or external_id.

        Use `external:{external_id}` to update by external_id. Example:
        `/v1/intake/entries/external:chatcmpl-abc123`

        Args:
          context: Contextual metadata attached to every entry record.

              Keeping these grouped in a dedicated object avoids polluting the top-level
              namespace and makes it trivial to extend without breaking compatibility.

          custom_fields: A set of custom fields that the user can define and use for various purposes.

          data: Entry data containing the request and response for an LLM interaction.

          description: The description of the entity.

          events: All events associated with this entry.

          ownership: Information about ownership of an entity.

              If the entity is a namespace, the `access_policies` will typically apply to all
              entities inside the namespace.

          project: The URN of the project associated with this entity.

          user_rating: User's rating/evaluation of an AI response.

              This captures various forms of end-user feedback about a model's response,
              including binary thumbs up/down ratings, numeric scores, free-text opinions,
              suggested rewrites, and structured category ratings.

              Either `thumb` or `rating` should be provided (they are mutually exclusive), but
              all fields are optional to accommodate different feedback collection patterns.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not entry_id:
            raise ValueError(f"Expected a non-empty value for `entry_id` but received {entry_id!r}")
        return await self._patch(
            f"/v1/intake/entries/{entry_id}",
            body=await async_maybe_transform(
                {
                    "context": context,
                    "custom_fields": custom_fields,
                    "data": data,
                    "description": description,
                    "events": events,
                    "ownership": ownership,
                    "project": project,
                    "user_rating": user_rating,
                },
                entry_update_params.EntryUpdateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=Entry,
        )

    def list(
        self,
        *,
        filter: EntryFilterParam | Omit = omit,
        page: int | Omit = omit,
        page_size: int | Omit = omit,
        search: EntrySearchParam | Omit = omit,
        sort: EntrySortField | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> AsyncPaginator[Entry, AsyncDefaultPagination[Entry]]:
        """
        List all entries with filtering and search capabilities.

        When longest_per_thread=true is set in filters, returns only the longest entry
        (by message count) for each unique thread_id.

        Args:
          filter: Filter entries on various criteria.

              Examples:

              - `?filter[namespace]=default`: Filter by namespace
              - `?filter[app]=default/my-app`: Filter by app reference
              - `?filter[has_thumb]=true`: Filter entries with thumb feedback
              - `?filter[longest_per_thread]=true`: Return only longest entry per thread

          page: Page number.

          page_size: Page size.

          search: Search entries using substring matching.

          sort: Sort fields for Entries.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._get_api_list(
            "/v1/intake/entries",
            page=AsyncDefaultPagination[Entry],
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "filter": filter,
                        "page": page,
                        "page_size": page_size,
                        "search": search,
                        "sort": sort,
                    },
                    entry_list_params.EntryListParams,
                ),
            ),
            model=Entry,
        )

    async def delete(
        self,
        entry_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> None:
        """
        Delete an entry by ID or external_id.

        Use `external:{external_id}` to delete by external_id. Example:
        `/v1/intake/entries/external:chatcmpl-abc123`

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not entry_id:
            raise ValueError(f"Expected a non-empty value for `entry_id` but received {entry_id!r}")
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        return await self._delete(
            f"/v1/intake/entries/{entry_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=NoneType,
        )


class EntriesResourceWithRawResponse:
    def __init__(self, entries: EntriesResource) -> None:
        self._entries = entries

        self.create = to_raw_response_wrapper(
            entries.create,
        )
        self.retrieve = to_raw_response_wrapper(
            entries.retrieve,
        )
        self.update = to_raw_response_wrapper(
            entries.update,
        )
        self.list = to_raw_response_wrapper(
            entries.list,
        )
        self.delete = to_raw_response_wrapper(
            entries.delete,
        )

    @cached_property
    def events(self) -> EventsResourceWithRawResponse:
        return EventsResourceWithRawResponse(self._entries.events)


class AsyncEntriesResourceWithRawResponse:
    def __init__(self, entries: AsyncEntriesResource) -> None:
        self._entries = entries

        self.create = async_to_raw_response_wrapper(
            entries.create,
        )
        self.retrieve = async_to_raw_response_wrapper(
            entries.retrieve,
        )
        self.update = async_to_raw_response_wrapper(
            entries.update,
        )
        self.list = async_to_raw_response_wrapper(
            entries.list,
        )
        self.delete = async_to_raw_response_wrapper(
            entries.delete,
        )

    @cached_property
    def events(self) -> AsyncEventsResourceWithRawResponse:
        return AsyncEventsResourceWithRawResponse(self._entries.events)


class EntriesResourceWithStreamingResponse:
    def __init__(self, entries: EntriesResource) -> None:
        self._entries = entries

        self.create = to_streamed_response_wrapper(
            entries.create,
        )
        self.retrieve = to_streamed_response_wrapper(
            entries.retrieve,
        )
        self.update = to_streamed_response_wrapper(
            entries.update,
        )
        self.list = to_streamed_response_wrapper(
            entries.list,
        )
        self.delete = to_streamed_response_wrapper(
            entries.delete,
        )

    @cached_property
    def events(self) -> EventsResourceWithStreamingResponse:
        return EventsResourceWithStreamingResponse(self._entries.events)


class AsyncEntriesResourceWithStreamingResponse:
    def __init__(self, entries: AsyncEntriesResource) -> None:
        self._entries = entries

        self.create = async_to_streamed_response_wrapper(
            entries.create,
        )
        self.retrieve = async_to_streamed_response_wrapper(
            entries.retrieve,
        )
        self.update = async_to_streamed_response_wrapper(
            entries.update,
        )
        self.list = async_to_streamed_response_wrapper(
            entries.list,
        )
        self.delete = async_to_streamed_response_wrapper(
            entries.delete,
        )

    @cached_property
    def events(self) -> AsyncEventsResourceWithStreamingResponse:
        return AsyncEventsResourceWithStreamingResponse(self._entries.events)
