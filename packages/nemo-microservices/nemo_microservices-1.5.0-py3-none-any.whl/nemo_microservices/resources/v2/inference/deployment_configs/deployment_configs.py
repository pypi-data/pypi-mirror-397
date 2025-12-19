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

from typing import Optional

import httpx

from .versions import (
    VersionsResource,
    AsyncVersionsResource,
    VersionsResourceWithRawResponse,
    AsyncVersionsResourceWithRawResponse,
    VersionsResourceWithStreamingResponse,
    AsyncVersionsResourceWithStreamingResponse,
)
from ....._types import Body, Omit, Query, Headers, NoneType, NotGiven, omit, not_given
from ....._utils import maybe_transform, async_maybe_transform
from ....._compat import cached_property
from ....._resource import SyncAPIResource, AsyncAPIResource
from ....._response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from ....._base_client import make_request_options
from .....types.v2.inference import (
    deployment_config_list_params,
    deployment_config_create_params,
    deployment_config_update_params,
    deployment_config_list_namespace_params,
)
from .....types.v2.inference.nim_deployment_param import NIMDeploymentParam
from .....types.v2.inference.model_deployment_config import ModelDeploymentConfig
from .....types.v2.inference.deployment_config_list_response import DeploymentConfigListResponse
from .....types.v2.inference.deployment_config_list_namespace_response import DeploymentConfigListNamespaceResponse

__all__ = ["DeploymentConfigsResource", "AsyncDeploymentConfigsResource"]


class DeploymentConfigsResource(SyncAPIResource):
    @cached_property
    def versions(self) -> VersionsResource:
        return VersionsResource(self._client)

    @cached_property
    def with_raw_response(self) -> DeploymentConfigsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://docs.nvidia.com/nemo/microservices/latest/pysdk/index.html#accessing-raw-response-data-e-g-headers
        """
        return DeploymentConfigsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> DeploymentConfigsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://docs.nvidia.com/nemo/microservices/latest/pysdk/index.html#with_streaming_response
        """
        return DeploymentConfigsResourceWithStreamingResponse(self)

    def create(
        self,
        *,
        name: str,
        nim_deployment: NIMDeploymentParam,
        description: str | Omit = omit,
        model_entity_id: str | Omit = omit,
        namespace: str | Omit = omit,
        project: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ModelDeploymentConfig:
        """
        Create a new ModelDeploymentConfig (version 1).

        Args:
          name: Name of the deployment configuration

          nim_deployment: Configuration for NIM-based model deployment.

          description: Optional description of the deployment configuration

          model_entity_id: Optional reference to the base model entity ID for this deployment

          namespace: The namespace of the deployment configuration

          project: The URN of the project associated with this deployment configuration

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/v2/inference/deployment-configs",
            body=maybe_transform(
                {
                    "name": name,
                    "nim_deployment": nim_deployment,
                    "description": description,
                    "model_entity_id": model_entity_id,
                    "namespace": namespace,
                    "project": project,
                },
                deployment_config_create_params.DeploymentConfigCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ModelDeploymentConfig,
        )

    def retrieve(
        self,
        deployment_config_name: str,
        *,
        namespace: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ModelDeploymentConfig:
        """
        Get the latest version of a ModelDeploymentConfig.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not namespace:
            raise ValueError(f"Expected a non-empty value for `namespace` but received {namespace!r}")
        if not deployment_config_name:
            raise ValueError(
                f"Expected a non-empty value for `deployment_config_name` but received {deployment_config_name!r}"
            )
        return self._get(
            f"/v2/inference/deployment-configs/{namespace}/{deployment_config_name}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ModelDeploymentConfig,
        )

    def update(
        self,
        deployment_config_name: str,
        *,
        namespace: str,
        nim_deployment: NIMDeploymentParam,
        description: str | Omit = omit,
        model_entity_id: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ModelDeploymentConfig:
        """
        Update a ModelDeploymentConfig (creates a new immutable version).

        Args:
          nim_deployment: Configuration for NIM-based model deployment.

          description: Optional description of the deployment configuration

          model_entity_id: Optional reference to the base model entity ID for this deployment

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not namespace:
            raise ValueError(f"Expected a non-empty value for `namespace` but received {namespace!r}")
        if not deployment_config_name:
            raise ValueError(
                f"Expected a non-empty value for `deployment_config_name` but received {deployment_config_name!r}"
            )
        return self._post(
            f"/v2/inference/deployment-configs/{namespace}/{deployment_config_name}",
            body=maybe_transform(
                {
                    "nim_deployment": nim_deployment,
                    "description": description,
                    "model_entity_id": model_entity_id,
                },
                deployment_config_update_params.DeploymentConfigUpdateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ModelDeploymentConfig,
        )

    def list(
        self,
        *,
        namespace: Optional[str] | Omit = omit,
        project: Optional[str] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> DeploymentConfigListResponse:
        """List all ModelDeploymentConfigs with optional filtering.

        Returns only the latest
        version of each config.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._get(
            "/v2/inference/deployment-configs",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "namespace": namespace,
                        "project": project,
                    },
                    deployment_config_list_params.DeploymentConfigListParams,
                ),
            ),
            cast_to=DeploymentConfigListResponse,
        )

    def delete(
        self,
        deployment_config_name: str,
        *,
        namespace: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> None:
        """
        Delete all versions of a ModelDeploymentConfig.

        This operation will fail with 409 Conflict if any ModelDeployments currently
        reference this config. Delete the dependent deployments first.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not namespace:
            raise ValueError(f"Expected a non-empty value for `namespace` but received {namespace!r}")
        if not deployment_config_name:
            raise ValueError(
                f"Expected a non-empty value for `deployment_config_name` but received {deployment_config_name!r}"
            )
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        return self._delete(
            f"/v2/inference/deployment-configs/{namespace}/{deployment_config_name}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=NoneType,
        )

    def list_namespace(
        self,
        namespace: str,
        *,
        project: Optional[str] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> DeploymentConfigListNamespaceResponse:
        """List ModelDeploymentConfigs for a specific namespace.

        Returns only the latest
        version of each config.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not namespace:
            raise ValueError(f"Expected a non-empty value for `namespace` but received {namespace!r}")
        return self._get(
            f"/v2/inference/deployment-configs/{namespace}",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {"project": project}, deployment_config_list_namespace_params.DeploymentConfigListNamespaceParams
                ),
            ),
            cast_to=DeploymentConfigListNamespaceResponse,
        )


class AsyncDeploymentConfigsResource(AsyncAPIResource):
    @cached_property
    def versions(self) -> AsyncVersionsResource:
        return AsyncVersionsResource(self._client)

    @cached_property
    def with_raw_response(self) -> AsyncDeploymentConfigsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://docs.nvidia.com/nemo/microservices/latest/pysdk/index.html#accessing-raw-response-data-e-g-headers
        """
        return AsyncDeploymentConfigsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncDeploymentConfigsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://docs.nvidia.com/nemo/microservices/latest/pysdk/index.html#with_streaming_response
        """
        return AsyncDeploymentConfigsResourceWithStreamingResponse(self)

    async def create(
        self,
        *,
        name: str,
        nim_deployment: NIMDeploymentParam,
        description: str | Omit = omit,
        model_entity_id: str | Omit = omit,
        namespace: str | Omit = omit,
        project: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ModelDeploymentConfig:
        """
        Create a new ModelDeploymentConfig (version 1).

        Args:
          name: Name of the deployment configuration

          nim_deployment: Configuration for NIM-based model deployment.

          description: Optional description of the deployment configuration

          model_entity_id: Optional reference to the base model entity ID for this deployment

          namespace: The namespace of the deployment configuration

          project: The URN of the project associated with this deployment configuration

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/v2/inference/deployment-configs",
            body=await async_maybe_transform(
                {
                    "name": name,
                    "nim_deployment": nim_deployment,
                    "description": description,
                    "model_entity_id": model_entity_id,
                    "namespace": namespace,
                    "project": project,
                },
                deployment_config_create_params.DeploymentConfigCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ModelDeploymentConfig,
        )

    async def retrieve(
        self,
        deployment_config_name: str,
        *,
        namespace: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ModelDeploymentConfig:
        """
        Get the latest version of a ModelDeploymentConfig.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not namespace:
            raise ValueError(f"Expected a non-empty value for `namespace` but received {namespace!r}")
        if not deployment_config_name:
            raise ValueError(
                f"Expected a non-empty value for `deployment_config_name` but received {deployment_config_name!r}"
            )
        return await self._get(
            f"/v2/inference/deployment-configs/{namespace}/{deployment_config_name}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ModelDeploymentConfig,
        )

    async def update(
        self,
        deployment_config_name: str,
        *,
        namespace: str,
        nim_deployment: NIMDeploymentParam,
        description: str | Omit = omit,
        model_entity_id: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ModelDeploymentConfig:
        """
        Update a ModelDeploymentConfig (creates a new immutable version).

        Args:
          nim_deployment: Configuration for NIM-based model deployment.

          description: Optional description of the deployment configuration

          model_entity_id: Optional reference to the base model entity ID for this deployment

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not namespace:
            raise ValueError(f"Expected a non-empty value for `namespace` but received {namespace!r}")
        if not deployment_config_name:
            raise ValueError(
                f"Expected a non-empty value for `deployment_config_name` but received {deployment_config_name!r}"
            )
        return await self._post(
            f"/v2/inference/deployment-configs/{namespace}/{deployment_config_name}",
            body=await async_maybe_transform(
                {
                    "nim_deployment": nim_deployment,
                    "description": description,
                    "model_entity_id": model_entity_id,
                },
                deployment_config_update_params.DeploymentConfigUpdateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ModelDeploymentConfig,
        )

    async def list(
        self,
        *,
        namespace: Optional[str] | Omit = omit,
        project: Optional[str] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> DeploymentConfigListResponse:
        """List all ModelDeploymentConfigs with optional filtering.

        Returns only the latest
        version of each config.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._get(
            "/v2/inference/deployment-configs",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {
                        "namespace": namespace,
                        "project": project,
                    },
                    deployment_config_list_params.DeploymentConfigListParams,
                ),
            ),
            cast_to=DeploymentConfigListResponse,
        )

    async def delete(
        self,
        deployment_config_name: str,
        *,
        namespace: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> None:
        """
        Delete all versions of a ModelDeploymentConfig.

        This operation will fail with 409 Conflict if any ModelDeployments currently
        reference this config. Delete the dependent deployments first.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not namespace:
            raise ValueError(f"Expected a non-empty value for `namespace` but received {namespace!r}")
        if not deployment_config_name:
            raise ValueError(
                f"Expected a non-empty value for `deployment_config_name` but received {deployment_config_name!r}"
            )
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        return await self._delete(
            f"/v2/inference/deployment-configs/{namespace}/{deployment_config_name}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=NoneType,
        )

    async def list_namespace(
        self,
        namespace: str,
        *,
        project: Optional[str] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> DeploymentConfigListNamespaceResponse:
        """List ModelDeploymentConfigs for a specific namespace.

        Returns only the latest
        version of each config.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not namespace:
            raise ValueError(f"Expected a non-empty value for `namespace` but received {namespace!r}")
        return await self._get(
            f"/v2/inference/deployment-configs/{namespace}",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {"project": project}, deployment_config_list_namespace_params.DeploymentConfigListNamespaceParams
                ),
            ),
            cast_to=DeploymentConfigListNamespaceResponse,
        )


class DeploymentConfigsResourceWithRawResponse:
    def __init__(self, deployment_configs: DeploymentConfigsResource) -> None:
        self._deployment_configs = deployment_configs

        self.create = to_raw_response_wrapper(
            deployment_configs.create,
        )
        self.retrieve = to_raw_response_wrapper(
            deployment_configs.retrieve,
        )
        self.update = to_raw_response_wrapper(
            deployment_configs.update,
        )
        self.list = to_raw_response_wrapper(
            deployment_configs.list,
        )
        self.delete = to_raw_response_wrapper(
            deployment_configs.delete,
        )
        self.list_namespace = to_raw_response_wrapper(
            deployment_configs.list_namespace,
        )

    @cached_property
    def versions(self) -> VersionsResourceWithRawResponse:
        return VersionsResourceWithRawResponse(self._deployment_configs.versions)


class AsyncDeploymentConfigsResourceWithRawResponse:
    def __init__(self, deployment_configs: AsyncDeploymentConfigsResource) -> None:
        self._deployment_configs = deployment_configs

        self.create = async_to_raw_response_wrapper(
            deployment_configs.create,
        )
        self.retrieve = async_to_raw_response_wrapper(
            deployment_configs.retrieve,
        )
        self.update = async_to_raw_response_wrapper(
            deployment_configs.update,
        )
        self.list = async_to_raw_response_wrapper(
            deployment_configs.list,
        )
        self.delete = async_to_raw_response_wrapper(
            deployment_configs.delete,
        )
        self.list_namespace = async_to_raw_response_wrapper(
            deployment_configs.list_namespace,
        )

    @cached_property
    def versions(self) -> AsyncVersionsResourceWithRawResponse:
        return AsyncVersionsResourceWithRawResponse(self._deployment_configs.versions)


class DeploymentConfigsResourceWithStreamingResponse:
    def __init__(self, deployment_configs: DeploymentConfigsResource) -> None:
        self._deployment_configs = deployment_configs

        self.create = to_streamed_response_wrapper(
            deployment_configs.create,
        )
        self.retrieve = to_streamed_response_wrapper(
            deployment_configs.retrieve,
        )
        self.update = to_streamed_response_wrapper(
            deployment_configs.update,
        )
        self.list = to_streamed_response_wrapper(
            deployment_configs.list,
        )
        self.delete = to_streamed_response_wrapper(
            deployment_configs.delete,
        )
        self.list_namespace = to_streamed_response_wrapper(
            deployment_configs.list_namespace,
        )

    @cached_property
    def versions(self) -> VersionsResourceWithStreamingResponse:
        return VersionsResourceWithStreamingResponse(self._deployment_configs.versions)


class AsyncDeploymentConfigsResourceWithStreamingResponse:
    def __init__(self, deployment_configs: AsyncDeploymentConfigsResource) -> None:
        self._deployment_configs = deployment_configs

        self.create = async_to_streamed_response_wrapper(
            deployment_configs.create,
        )
        self.retrieve = async_to_streamed_response_wrapper(
            deployment_configs.retrieve,
        )
        self.update = async_to_streamed_response_wrapper(
            deployment_configs.update,
        )
        self.list = async_to_streamed_response_wrapper(
            deployment_configs.list,
        )
        self.delete = async_to_streamed_response_wrapper(
            deployment_configs.delete,
        )
        self.list_namespace = async_to_streamed_response_wrapper(
            deployment_configs.list_namespace,
        )

    @cached_property
    def versions(self) -> AsyncVersionsResourceWithStreamingResponse:
        return AsyncVersionsResourceWithStreamingResponse(self._deployment_configs.versions)
