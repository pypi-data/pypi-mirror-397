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

from ..._types import Body, Omit, Query, Headers, NoneType, NotGiven, SequenceNotStr, omit, not_given
from ..._utils import maybe_transform, async_maybe_transform
from ..._compat import cached_property
from ..._resource import SyncAPIResource, AsyncAPIResource
from ..._response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from ..._base_client import make_request_options
from ...types.v2.models import ModelEntitySortField, model_list_params, model_create_params, model_update_params
from ...types.v2.models.model_entity import ModelEntity
from ...types.shared_params.model_spec import ModelSpec
from ...types.shared_params.prompt_data import PromptData
from ...types.shared_params.model_artifact import ModelArtifact
from ...types.v2.models.model_list_response import ModelListResponse
from ...types.shared_params.api_endpoint_data import APIEndpointData
from ...types.v2.models.model_entity_sort_field import ModelEntitySortField
from ...types.shared_params.guardrail_config_param import GuardrailConfigParam
from ...types.shared_params.parameter_efficient_finetuning_data import ParameterEfficientFinetuningData

__all__ = ["ModelsResource", "AsyncModelsResource"]


class ModelsResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> ModelsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://docs.nvidia.com/nemo/microservices/latest/pysdk/index.html#accessing-raw-response-data-e-g-headers
        """
        return ModelsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> ModelsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://docs.nvidia.com/nemo/microservices/latest/pysdk/index.html#with_streaming_response
        """
        return ModelsResourceWithStreamingResponse(self)

    def create(
        self,
        *,
        name: str,
        api_endpoint: APIEndpointData | Omit = omit,
        artifact: ModelArtifact | Omit = omit,
        base_model: str | Omit = omit,
        custom_fields: Dict[str, object] | Omit = omit,
        description: str | Omit = omit,
        guardrails: GuardrailConfigParam | Omit = omit,
        model_providers: SequenceNotStr[str] | Omit = omit,
        namespace: str | Omit = omit,
        ownership: Dict[str, object] | Omit = omit,
        peft: ParameterEfficientFinetuningData | Omit = omit,
        project: str | Omit = omit,
        prompt: PromptData | Omit = omit,
        spec: ModelSpec | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ModelEntity:
        """
        Create a new model entity.

        This endpoint creates a new Model Entity in the Models service database. The
        Model Entity will be registered for use within the platform.

        Args:
          name: Name of the model entity

          api_endpoint: Data about an API endpoint.

          artifact: Data about a model artifact (a set of checkpoint files, configs, and other
              auxiliary info).

              The `files_url` field can point to a DataStore location.

              Example:

              - nds://models/rdinu/my-lora-customization

              The `rdinu/my-lora-customization` part above is the actual repository.

              If a specific revision needs to be referred, the HuggingFace syntax is used.

              - nds://models/rdinu/my-lora-customization@v1
              - nds://models/rdinu/my-lora-customization@8df79a8

          base_model: Link to another model which is used as a base for the current model

          custom_fields: Custom fields for additional metadata

          description: Optional description of the model

          guardrails: A guardrail configuration

          model_providers: List of ModelProvider namespace/name resource names that provide inference for
              this Model Entity

          namespace: The namespace of the model entity

          ownership: Ownership information for the model

          peft: Data about a parameter-efficient finetuning.

          project: The URN of the project associated with this model entity

          prompt: Prompt engineering data.

          spec: Detailed specification about a model.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/v2/models",
            body=maybe_transform(
                {
                    "name": name,
                    "api_endpoint": api_endpoint,
                    "artifact": artifact,
                    "base_model": base_model,
                    "custom_fields": custom_fields,
                    "description": description,
                    "guardrails": guardrails,
                    "model_providers": model_providers,
                    "namespace": namespace,
                    "ownership": ownership,
                    "peft": peft,
                    "project": project,
                    "prompt": prompt,
                    "spec": spec,
                },
                model_create_params.ModelCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ModelEntity,
        )

    def retrieve(
        self,
        model_name: str,
        *,
        namespace: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ModelEntity:
        """
        Get Model by Namespace and Name.

        Returns the details of a specific model entity identified by its namespace and
        name.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not namespace:
            raise ValueError(f"Expected a non-empty value for `namespace` but received {namespace!r}")
        if not model_name:
            raise ValueError(f"Expected a non-empty value for `model_name` but received {model_name!r}")
        return self._get(
            f"/v2/models/{namespace}/{model_name}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ModelEntity,
        )

    def update(
        self,
        model_name: str,
        *,
        namespace: str,
        api_endpoint: APIEndpointData | Omit = omit,
        artifact: ModelArtifact | Omit = omit,
        base_model: str | Omit = omit,
        custom_fields: Dict[str, object] | Omit = omit,
        description: str | Omit = omit,
        guardrails: GuardrailConfigParam | Omit = omit,
        model_providers: SequenceNotStr[str] | Omit = omit,
        ownership: Dict[str, object] | Omit = omit,
        peft: ParameterEfficientFinetuningData | Omit = omit,
        prompt: PromptData | Omit = omit,
        spec: ModelSpec | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ModelEntity:
        """Update Model metadata.

        Updates the metadata of an existing model entity.

        If the request body has an
        empty field, the old value is kept.

        Args:
          api_endpoint: Data about an API endpoint.

          artifact: Data about a model artifact (a set of checkpoint files, configs, and other
              auxiliary info).

              The `files_url` field can point to a DataStore location.

              Example:

              - nds://models/rdinu/my-lora-customization

              The `rdinu/my-lora-customization` part above is the actual repository.

              If a specific revision needs to be referred, the HuggingFace syntax is used.

              - nds://models/rdinu/my-lora-customization@v1
              - nds://models/rdinu/my-lora-customization@8df79a8

          base_model: Link to another model which is used as a base for the current model

          custom_fields: Custom fields for additional metadata

          description: Optional description of the model

          guardrails: A guardrail configuration

          model_providers: List of ModelProvider namespace/name resource names that provide inference for
              this Model Entity

          ownership: Ownership information for the model

          peft: Data about a parameter-efficient finetuning.

          prompt: Prompt engineering data.

          spec: Detailed specification about a model.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not namespace:
            raise ValueError(f"Expected a non-empty value for `namespace` but received {namespace!r}")
        if not model_name:
            raise ValueError(f"Expected a non-empty value for `model_name` but received {model_name!r}")
        return self._patch(
            f"/v2/models/{namespace}/{model_name}",
            body=maybe_transform(
                {
                    "api_endpoint": api_endpoint,
                    "artifact": artifact,
                    "base_model": base_model,
                    "custom_fields": custom_fields,
                    "description": description,
                    "guardrails": guardrails,
                    "model_providers": model_providers,
                    "ownership": ownership,
                    "peft": peft,
                    "prompt": prompt,
                    "spec": spec,
                },
                model_update_params.ModelUpdateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ModelEntity,
        )

    def list(
        self,
        *,
        page: int | Omit = omit,
        page_size: int | Omit = omit,
        sort: ModelEntitySortField | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ModelListResponse:
        """
        List Models endpoint with filtering, search, pagination, and sorting.

        Supports filter parameters for various criteria (including peft, custom fields),
        search parameters for substring matching (name, base_model, peft,
        custom_property), pagination (page, page_size), sorting, and namespace filtering
        via query parameter.

        Args:
          page: Page number.

          page_size: Page size.

          sort: Sort fields for Model Entity queries.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._get(
            "/v2/models",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "page": page,
                        "page_size": page_size,
                        "sort": sort,
                    },
                    model_list_params.ModelListParams,
                ),
            ),
            cast_to=ModelListResponse,
        )

    def delete(
        self,
        model_name: str,
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
        Delete Model entity.

        Permanently deletes a model entity from the platform.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not namespace:
            raise ValueError(f"Expected a non-empty value for `namespace` but received {namespace!r}")
        if not model_name:
            raise ValueError(f"Expected a non-empty value for `model_name` but received {model_name!r}")
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        return self._delete(
            f"/v2/models/{namespace}/{model_name}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=NoneType,
        )


class AsyncModelsResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncModelsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://docs.nvidia.com/nemo/microservices/latest/pysdk/index.html#accessing-raw-response-data-e-g-headers
        """
        return AsyncModelsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncModelsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://docs.nvidia.com/nemo/microservices/latest/pysdk/index.html#with_streaming_response
        """
        return AsyncModelsResourceWithStreamingResponse(self)

    async def create(
        self,
        *,
        name: str,
        api_endpoint: APIEndpointData | Omit = omit,
        artifact: ModelArtifact | Omit = omit,
        base_model: str | Omit = omit,
        custom_fields: Dict[str, object] | Omit = omit,
        description: str | Omit = omit,
        guardrails: GuardrailConfigParam | Omit = omit,
        model_providers: SequenceNotStr[str] | Omit = omit,
        namespace: str | Omit = omit,
        ownership: Dict[str, object] | Omit = omit,
        peft: ParameterEfficientFinetuningData | Omit = omit,
        project: str | Omit = omit,
        prompt: PromptData | Omit = omit,
        spec: ModelSpec | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ModelEntity:
        """
        Create a new model entity.

        This endpoint creates a new Model Entity in the Models service database. The
        Model Entity will be registered for use within the platform.

        Args:
          name: Name of the model entity

          api_endpoint: Data about an API endpoint.

          artifact: Data about a model artifact (a set of checkpoint files, configs, and other
              auxiliary info).

              The `files_url` field can point to a DataStore location.

              Example:

              - nds://models/rdinu/my-lora-customization

              The `rdinu/my-lora-customization` part above is the actual repository.

              If a specific revision needs to be referred, the HuggingFace syntax is used.

              - nds://models/rdinu/my-lora-customization@v1
              - nds://models/rdinu/my-lora-customization@8df79a8

          base_model: Link to another model which is used as a base for the current model

          custom_fields: Custom fields for additional metadata

          description: Optional description of the model

          guardrails: A guardrail configuration

          model_providers: List of ModelProvider namespace/name resource names that provide inference for
              this Model Entity

          namespace: The namespace of the model entity

          ownership: Ownership information for the model

          peft: Data about a parameter-efficient finetuning.

          project: The URN of the project associated with this model entity

          prompt: Prompt engineering data.

          spec: Detailed specification about a model.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/v2/models",
            body=await async_maybe_transform(
                {
                    "name": name,
                    "api_endpoint": api_endpoint,
                    "artifact": artifact,
                    "base_model": base_model,
                    "custom_fields": custom_fields,
                    "description": description,
                    "guardrails": guardrails,
                    "model_providers": model_providers,
                    "namespace": namespace,
                    "ownership": ownership,
                    "peft": peft,
                    "project": project,
                    "prompt": prompt,
                    "spec": spec,
                },
                model_create_params.ModelCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ModelEntity,
        )

    async def retrieve(
        self,
        model_name: str,
        *,
        namespace: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ModelEntity:
        """
        Get Model by Namespace and Name.

        Returns the details of a specific model entity identified by its namespace and
        name.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not namespace:
            raise ValueError(f"Expected a non-empty value for `namespace` but received {namespace!r}")
        if not model_name:
            raise ValueError(f"Expected a non-empty value for `model_name` but received {model_name!r}")
        return await self._get(
            f"/v2/models/{namespace}/{model_name}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ModelEntity,
        )

    async def update(
        self,
        model_name: str,
        *,
        namespace: str,
        api_endpoint: APIEndpointData | Omit = omit,
        artifact: ModelArtifact | Omit = omit,
        base_model: str | Omit = omit,
        custom_fields: Dict[str, object] | Omit = omit,
        description: str | Omit = omit,
        guardrails: GuardrailConfigParam | Omit = omit,
        model_providers: SequenceNotStr[str] | Omit = omit,
        ownership: Dict[str, object] | Omit = omit,
        peft: ParameterEfficientFinetuningData | Omit = omit,
        prompt: PromptData | Omit = omit,
        spec: ModelSpec | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ModelEntity:
        """Update Model metadata.

        Updates the metadata of an existing model entity.

        If the request body has an
        empty field, the old value is kept.

        Args:
          api_endpoint: Data about an API endpoint.

          artifact: Data about a model artifact (a set of checkpoint files, configs, and other
              auxiliary info).

              The `files_url` field can point to a DataStore location.

              Example:

              - nds://models/rdinu/my-lora-customization

              The `rdinu/my-lora-customization` part above is the actual repository.

              If a specific revision needs to be referred, the HuggingFace syntax is used.

              - nds://models/rdinu/my-lora-customization@v1
              - nds://models/rdinu/my-lora-customization@8df79a8

          base_model: Link to another model which is used as a base for the current model

          custom_fields: Custom fields for additional metadata

          description: Optional description of the model

          guardrails: A guardrail configuration

          model_providers: List of ModelProvider namespace/name resource names that provide inference for
              this Model Entity

          ownership: Ownership information for the model

          peft: Data about a parameter-efficient finetuning.

          prompt: Prompt engineering data.

          spec: Detailed specification about a model.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not namespace:
            raise ValueError(f"Expected a non-empty value for `namespace` but received {namespace!r}")
        if not model_name:
            raise ValueError(f"Expected a non-empty value for `model_name` but received {model_name!r}")
        return await self._patch(
            f"/v2/models/{namespace}/{model_name}",
            body=await async_maybe_transform(
                {
                    "api_endpoint": api_endpoint,
                    "artifact": artifact,
                    "base_model": base_model,
                    "custom_fields": custom_fields,
                    "description": description,
                    "guardrails": guardrails,
                    "model_providers": model_providers,
                    "ownership": ownership,
                    "peft": peft,
                    "prompt": prompt,
                    "spec": spec,
                },
                model_update_params.ModelUpdateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ModelEntity,
        )

    async def list(
        self,
        *,
        page: int | Omit = omit,
        page_size: int | Omit = omit,
        sort: ModelEntitySortField | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ModelListResponse:
        """
        List Models endpoint with filtering, search, pagination, and sorting.

        Supports filter parameters for various criteria (including peft, custom fields),
        search parameters for substring matching (name, base_model, peft,
        custom_property), pagination (page, page_size), sorting, and namespace filtering
        via query parameter.

        Args:
          page: Page number.

          page_size: Page size.

          sort: Sort fields for Model Entity queries.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._get(
            "/v2/models",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {
                        "page": page,
                        "page_size": page_size,
                        "sort": sort,
                    },
                    model_list_params.ModelListParams,
                ),
            ),
            cast_to=ModelListResponse,
        )

    async def delete(
        self,
        model_name: str,
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
        Delete Model entity.

        Permanently deletes a model entity from the platform.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not namespace:
            raise ValueError(f"Expected a non-empty value for `namespace` but received {namespace!r}")
        if not model_name:
            raise ValueError(f"Expected a non-empty value for `model_name` but received {model_name!r}")
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        return await self._delete(
            f"/v2/models/{namespace}/{model_name}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=NoneType,
        )


class ModelsResourceWithRawResponse:
    def __init__(self, models: ModelsResource) -> None:
        self._models = models

        self.create = to_raw_response_wrapper(
            models.create,
        )
        self.retrieve = to_raw_response_wrapper(
            models.retrieve,
        )
        self.update = to_raw_response_wrapper(
            models.update,
        )
        self.list = to_raw_response_wrapper(
            models.list,
        )
        self.delete = to_raw_response_wrapper(
            models.delete,
        )


class AsyncModelsResourceWithRawResponse:
    def __init__(self, models: AsyncModelsResource) -> None:
        self._models = models

        self.create = async_to_raw_response_wrapper(
            models.create,
        )
        self.retrieve = async_to_raw_response_wrapper(
            models.retrieve,
        )
        self.update = async_to_raw_response_wrapper(
            models.update,
        )
        self.list = async_to_raw_response_wrapper(
            models.list,
        )
        self.delete = async_to_raw_response_wrapper(
            models.delete,
        )


class ModelsResourceWithStreamingResponse:
    def __init__(self, models: ModelsResource) -> None:
        self._models = models

        self.create = to_streamed_response_wrapper(
            models.create,
        )
        self.retrieve = to_streamed_response_wrapper(
            models.retrieve,
        )
        self.update = to_streamed_response_wrapper(
            models.update,
        )
        self.list = to_streamed_response_wrapper(
            models.list,
        )
        self.delete = to_streamed_response_wrapper(
            models.delete,
        )


class AsyncModelsResourceWithStreamingResponse:
    def __init__(self, models: AsyncModelsResource) -> None:
        self._models = models

        self.create = async_to_streamed_response_wrapper(
            models.create,
        )
        self.retrieve = async_to_streamed_response_wrapper(
            models.retrieve,
        )
        self.update = async_to_streamed_response_wrapper(
            models.update,
        )
        self.list = async_to_streamed_response_wrapper(
            models.list,
        )
        self.delete = async_to_streamed_response_wrapper(
            models.delete,
        )
