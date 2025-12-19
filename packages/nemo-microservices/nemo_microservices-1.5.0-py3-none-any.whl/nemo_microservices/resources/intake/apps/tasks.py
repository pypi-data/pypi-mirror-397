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

import httpx

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
from ....types.intake.apps import (
    TaskSortField,
    task_list_params,
    task_create_params,
    task_update_params,
)
from ....types.intake.apps.task import Task
from ....types.shared_params.ownership import Ownership
from ....types.intake.apps.task_sort_field import TaskSortField
from ....types.intake.apps.task_filter_param import TaskFilterParam
from ....types.intake.apps.task_search_param import TaskSearchParam

__all__ = ["TasksResource", "AsyncTasksResource"]


class TasksResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> TasksResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://docs.nvidia.com/nemo/microservices/latest/pysdk/index.html#accessing-raw-response-data-e-g-headers
        """
        return TasksResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> TasksResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://docs.nvidia.com/nemo/microservices/latest/pysdk/index.html#with_streaming_response
        """
        return TasksResourceWithStreamingResponse(self)

    def create(
        self,
        app_name: str,
        *,
        namespace: str,
        custom_fields: Dict[str, object] | Omit = omit,
        description: str | Omit = omit,
        locked: bool | Omit = omit,
        name: str | Omit = omit,
        ownership: Ownership | Omit = omit,
        project: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> Task:
        """
        Create a new task.

        Args:
          custom_fields: A set of custom fields that the user can define and use for various purposes.

          description: The description of the entity.

          locked: If true, this record cannot be automatically updated when entries are ingested.
              When an entry is created, the system normally auto-updates the task's metadata
              (name, description). Set locked=true to prevent these automatic updates and
              preserve manually curated information. The record can still be modified via
              explicit PATCH requests.

          name: The name of the entity. Must be unique inside the namespace. If not specified,
              it will be the same as the automatically generated id.

          ownership: Information about ownership of an entity.

              If the entity is a namespace, the `access_policies` will typically apply to all
              entities inside the namespace.

          project: The URN of the project associated with this entity.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not namespace:
            raise ValueError(f"Expected a non-empty value for `namespace` but received {namespace!r}")
        if not app_name:
            raise ValueError(f"Expected a non-empty value for `app_name` but received {app_name!r}")
        return self._post(
            f"/v1/intake/apps/{namespace}/{app_name}/tasks",
            body=maybe_transform(
                {
                    "custom_fields": custom_fields,
                    "description": description,
                    "locked": locked,
                    "name": name,
                    "ownership": ownership,
                    "project": project,
                },
                task_create_params.TaskCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=Task,
        )

    def retrieve(
        self,
        task_name: str,
        *,
        namespace: str,
        app_name: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> Task:
        """
        Get a specific task.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not namespace:
            raise ValueError(f"Expected a non-empty value for `namespace` but received {namespace!r}")
        if not app_name:
            raise ValueError(f"Expected a non-empty value for `app_name` but received {app_name!r}")
        if not task_name:
            raise ValueError(f"Expected a non-empty value for `task_name` but received {task_name!r}")
        return self._get(
            f"/v1/intake/apps/{namespace}/{app_name}/tasks/{task_name}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=Task,
        )

    def update(
        self,
        task_name: str,
        *,
        namespace: str,
        app_name: str,
        custom_fields: Dict[str, object] | Omit = omit,
        description: str | Omit = omit,
        locked: bool | Omit = omit,
        ownership: Ownership | Omit = omit,
        project: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> Task:
        """
        Update an existing task.

        Args:
          custom_fields: A set of custom fields that the user can define and use for various purposes.

          description: The description of the entity.

          locked: If true, this record cannot be automatically updated when entries are ingested.
              When an entry is created, the system normally auto-updates the task's metadata
              (name, description). Set locked=true to prevent these automatic updates and
              preserve manually curated information. The record can still be modified via
              explicit PATCH requests.

          ownership: Information about ownership of an entity.

              If the entity is a namespace, the `access_policies` will typically apply to all
              entities inside the namespace.

          project: The URN of the project associated with this entity.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not namespace:
            raise ValueError(f"Expected a non-empty value for `namespace` but received {namespace!r}")
        if not app_name:
            raise ValueError(f"Expected a non-empty value for `app_name` but received {app_name!r}")
        if not task_name:
            raise ValueError(f"Expected a non-empty value for `task_name` but received {task_name!r}")
        return self._patch(
            f"/v1/intake/apps/{namespace}/{app_name}/tasks/{task_name}",
            body=maybe_transform(
                {
                    "custom_fields": custom_fields,
                    "description": description,
                    "locked": locked,
                    "ownership": ownership,
                    "project": project,
                },
                task_update_params.TaskUpdateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=Task,
        )

    def list(
        self,
        app_name: str,
        *,
        namespace: str,
        filter: TaskFilterParam | Omit = omit,
        page: int | Omit = omit,
        page_size: int | Omit = omit,
        search: TaskSearchParam | Omit = omit,
        sort: TaskSortField | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> SyncDefaultPagination[Task]:
        """
        List all tasks for a specific app.

        Args:
          filter: Filter tasks on various criteria.

          page: Page number.

          page_size: Page size.

          search: Search tasks using substring matching.

              For example:

              - `?search[name]=chat`: searches all tasks with 'chat' in the name.
              - `?search[description]=support`: searches all tasks with 'support' in the
                description.

          sort: Sort fields for Tasks.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not namespace:
            raise ValueError(f"Expected a non-empty value for `namespace` but received {namespace!r}")
        if not app_name:
            raise ValueError(f"Expected a non-empty value for `app_name` but received {app_name!r}")
        return self._get_api_list(
            f"/v1/intake/apps/{namespace}/{app_name}/tasks",
            page=SyncDefaultPagination[Task],
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
                    task_list_params.TaskListParams,
                ),
            ),
            model=Task,
        )

    def delete(
        self,
        task_name: str,
        *,
        namespace: str,
        app_name: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> None:
        """
        Delete a task.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not namespace:
            raise ValueError(f"Expected a non-empty value for `namespace` but received {namespace!r}")
        if not app_name:
            raise ValueError(f"Expected a non-empty value for `app_name` but received {app_name!r}")
        if not task_name:
            raise ValueError(f"Expected a non-empty value for `task_name` but received {task_name!r}")
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        return self._delete(
            f"/v1/intake/apps/{namespace}/{app_name}/tasks/{task_name}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=NoneType,
        )


class AsyncTasksResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncTasksResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://docs.nvidia.com/nemo/microservices/latest/pysdk/index.html#accessing-raw-response-data-e-g-headers
        """
        return AsyncTasksResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncTasksResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://docs.nvidia.com/nemo/microservices/latest/pysdk/index.html#with_streaming_response
        """
        return AsyncTasksResourceWithStreamingResponse(self)

    async def create(
        self,
        app_name: str,
        *,
        namespace: str,
        custom_fields: Dict[str, object] | Omit = omit,
        description: str | Omit = omit,
        locked: bool | Omit = omit,
        name: str | Omit = omit,
        ownership: Ownership | Omit = omit,
        project: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> Task:
        """
        Create a new task.

        Args:
          custom_fields: A set of custom fields that the user can define and use for various purposes.

          description: The description of the entity.

          locked: If true, this record cannot be automatically updated when entries are ingested.
              When an entry is created, the system normally auto-updates the task's metadata
              (name, description). Set locked=true to prevent these automatic updates and
              preserve manually curated information. The record can still be modified via
              explicit PATCH requests.

          name: The name of the entity. Must be unique inside the namespace. If not specified,
              it will be the same as the automatically generated id.

          ownership: Information about ownership of an entity.

              If the entity is a namespace, the `access_policies` will typically apply to all
              entities inside the namespace.

          project: The URN of the project associated with this entity.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not namespace:
            raise ValueError(f"Expected a non-empty value for `namespace` but received {namespace!r}")
        if not app_name:
            raise ValueError(f"Expected a non-empty value for `app_name` but received {app_name!r}")
        return await self._post(
            f"/v1/intake/apps/{namespace}/{app_name}/tasks",
            body=await async_maybe_transform(
                {
                    "custom_fields": custom_fields,
                    "description": description,
                    "locked": locked,
                    "name": name,
                    "ownership": ownership,
                    "project": project,
                },
                task_create_params.TaskCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=Task,
        )

    async def retrieve(
        self,
        task_name: str,
        *,
        namespace: str,
        app_name: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> Task:
        """
        Get a specific task.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not namespace:
            raise ValueError(f"Expected a non-empty value for `namespace` but received {namespace!r}")
        if not app_name:
            raise ValueError(f"Expected a non-empty value for `app_name` but received {app_name!r}")
        if not task_name:
            raise ValueError(f"Expected a non-empty value for `task_name` but received {task_name!r}")
        return await self._get(
            f"/v1/intake/apps/{namespace}/{app_name}/tasks/{task_name}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=Task,
        )

    async def update(
        self,
        task_name: str,
        *,
        namespace: str,
        app_name: str,
        custom_fields: Dict[str, object] | Omit = omit,
        description: str | Omit = omit,
        locked: bool | Omit = omit,
        ownership: Ownership | Omit = omit,
        project: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> Task:
        """
        Update an existing task.

        Args:
          custom_fields: A set of custom fields that the user can define and use for various purposes.

          description: The description of the entity.

          locked: If true, this record cannot be automatically updated when entries are ingested.
              When an entry is created, the system normally auto-updates the task's metadata
              (name, description). Set locked=true to prevent these automatic updates and
              preserve manually curated information. The record can still be modified via
              explicit PATCH requests.

          ownership: Information about ownership of an entity.

              If the entity is a namespace, the `access_policies` will typically apply to all
              entities inside the namespace.

          project: The URN of the project associated with this entity.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not namespace:
            raise ValueError(f"Expected a non-empty value for `namespace` but received {namespace!r}")
        if not app_name:
            raise ValueError(f"Expected a non-empty value for `app_name` but received {app_name!r}")
        if not task_name:
            raise ValueError(f"Expected a non-empty value for `task_name` but received {task_name!r}")
        return await self._patch(
            f"/v1/intake/apps/{namespace}/{app_name}/tasks/{task_name}",
            body=await async_maybe_transform(
                {
                    "custom_fields": custom_fields,
                    "description": description,
                    "locked": locked,
                    "ownership": ownership,
                    "project": project,
                },
                task_update_params.TaskUpdateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=Task,
        )

    def list(
        self,
        app_name: str,
        *,
        namespace: str,
        filter: TaskFilterParam | Omit = omit,
        page: int | Omit = omit,
        page_size: int | Omit = omit,
        search: TaskSearchParam | Omit = omit,
        sort: TaskSortField | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> AsyncPaginator[Task, AsyncDefaultPagination[Task]]:
        """
        List all tasks for a specific app.

        Args:
          filter: Filter tasks on various criteria.

          page: Page number.

          page_size: Page size.

          search: Search tasks using substring matching.

              For example:

              - `?search[name]=chat`: searches all tasks with 'chat' in the name.
              - `?search[description]=support`: searches all tasks with 'support' in the
                description.

          sort: Sort fields for Tasks.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not namespace:
            raise ValueError(f"Expected a non-empty value for `namespace` but received {namespace!r}")
        if not app_name:
            raise ValueError(f"Expected a non-empty value for `app_name` but received {app_name!r}")
        return self._get_api_list(
            f"/v1/intake/apps/{namespace}/{app_name}/tasks",
            page=AsyncDefaultPagination[Task],
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
                    task_list_params.TaskListParams,
                ),
            ),
            model=Task,
        )

    async def delete(
        self,
        task_name: str,
        *,
        namespace: str,
        app_name: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> None:
        """
        Delete a task.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not namespace:
            raise ValueError(f"Expected a non-empty value for `namespace` but received {namespace!r}")
        if not app_name:
            raise ValueError(f"Expected a non-empty value for `app_name` but received {app_name!r}")
        if not task_name:
            raise ValueError(f"Expected a non-empty value for `task_name` but received {task_name!r}")
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        return await self._delete(
            f"/v1/intake/apps/{namespace}/{app_name}/tasks/{task_name}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=NoneType,
        )


class TasksResourceWithRawResponse:
    def __init__(self, tasks: TasksResource) -> None:
        self._tasks = tasks

        self.create = to_raw_response_wrapper(
            tasks.create,
        )
        self.retrieve = to_raw_response_wrapper(
            tasks.retrieve,
        )
        self.update = to_raw_response_wrapper(
            tasks.update,
        )
        self.list = to_raw_response_wrapper(
            tasks.list,
        )
        self.delete = to_raw_response_wrapper(
            tasks.delete,
        )


class AsyncTasksResourceWithRawResponse:
    def __init__(self, tasks: AsyncTasksResource) -> None:
        self._tasks = tasks

        self.create = async_to_raw_response_wrapper(
            tasks.create,
        )
        self.retrieve = async_to_raw_response_wrapper(
            tasks.retrieve,
        )
        self.update = async_to_raw_response_wrapper(
            tasks.update,
        )
        self.list = async_to_raw_response_wrapper(
            tasks.list,
        )
        self.delete = async_to_raw_response_wrapper(
            tasks.delete,
        )


class TasksResourceWithStreamingResponse:
    def __init__(self, tasks: TasksResource) -> None:
        self._tasks = tasks

        self.create = to_streamed_response_wrapper(
            tasks.create,
        )
        self.retrieve = to_streamed_response_wrapper(
            tasks.retrieve,
        )
        self.update = to_streamed_response_wrapper(
            tasks.update,
        )
        self.list = to_streamed_response_wrapper(
            tasks.list,
        )
        self.delete = to_streamed_response_wrapper(
            tasks.delete,
        )


class AsyncTasksResourceWithStreamingResponse:
    def __init__(self, tasks: AsyncTasksResource) -> None:
        self._tasks = tasks

        self.create = async_to_streamed_response_wrapper(
            tasks.create,
        )
        self.retrieve = async_to_streamed_response_wrapper(
            tasks.retrieve,
        )
        self.update = async_to_streamed_response_wrapper(
            tasks.update,
        )
        self.list = async_to_streamed_response_wrapper(
            tasks.list,
        )
        self.delete = async_to_streamed_response_wrapper(
            tasks.delete,
        )
