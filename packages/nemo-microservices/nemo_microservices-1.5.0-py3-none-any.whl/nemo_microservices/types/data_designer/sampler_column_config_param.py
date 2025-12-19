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

from typing import Dict, Union
from typing_extensions import Literal, Required, TypeAlias, TypedDict

from .sampler_type import SamplerType
from .uuid_sampler_params_param import UuidSamplerParamsParam
from .scipy_sampler_params_param import ScipySamplerParamsParam
from .person_sampler_params_param import PersonSamplerParamsParam
from .poisson_sampler_params_param import PoissonSamplerParamsParam
from .uniform_sampler_params_param import UniformSamplerParamsParam
from .binomial_sampler_params_param import BinomialSamplerParamsParam
from .category_sampler_params_param import CategorySamplerParamsParam
from .datetime_sampler_params_param import DatetimeSamplerParamsParam
from .gaussian_sampler_params_param import GaussianSamplerParamsParam
from .bernoulli_sampler_params_param import BernoulliSamplerParamsParam
from .time_delta_sampler_params_param import TimeDeltaSamplerParamsParam
from .subcategory_sampler_params_param import SubcategorySamplerParamsParam
from .bernoulli_mixture_sampler_params_param import BernoulliMixtureSamplerParamsParam
from .person_from_faker_sampler_params_param import PersonFromFakerSamplerParamsParam

__all__ = ["SamplerColumnConfigParam", "Params", "ConditionalParams"]

Params: TypeAlias = Union[
    SubcategorySamplerParamsParam,
    CategorySamplerParamsParam,
    DatetimeSamplerParamsParam,
    PersonSamplerParamsParam,
    PersonFromFakerSamplerParamsParam,
    TimeDeltaSamplerParamsParam,
    UuidSamplerParamsParam,
    BernoulliSamplerParamsParam,
    BernoulliMixtureSamplerParamsParam,
    BinomialSamplerParamsParam,
    GaussianSamplerParamsParam,
    PoissonSamplerParamsParam,
    UniformSamplerParamsParam,
    ScipySamplerParamsParam,
]

ConditionalParams: TypeAlias = Union[
    SubcategorySamplerParamsParam,
    CategorySamplerParamsParam,
    DatetimeSamplerParamsParam,
    PersonSamplerParamsParam,
    PersonFromFakerSamplerParamsParam,
    TimeDeltaSamplerParamsParam,
    UuidSamplerParamsParam,
    BernoulliSamplerParamsParam,
    BernoulliMixtureSamplerParamsParam,
    BinomialSamplerParamsParam,
    GaussianSamplerParamsParam,
    PoissonSamplerParamsParam,
    UniformSamplerParamsParam,
    ScipySamplerParamsParam,
]


class SamplerColumnConfigParam(TypedDict, total=False):
    name: Required[str]

    params: Required[Params]
    """Parameters for subcategory sampling conditioned on a parent category column.

    Samples subcategory values based on the value of a parent category column. Each
    parent category value maps to its own list of possible subcategory values,
    enabling hierarchical or conditional sampling patterns.

    Attributes: category: Name of the parent category column that this subcategory
    depends on. The parent column must be generated before this subcategory column.
    values: Mapping from each parent category value to a list of possible
    subcategory values. Each key must correspond to a value that appears in the
    parent category column.
    """

    sampler_type: Required[SamplerType]

    column_type: Literal["sampler"]

    conditional_params: Dict[str, ConditionalParams]

    convert_to: str

    drop: bool
