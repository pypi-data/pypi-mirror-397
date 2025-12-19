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
from typing_extensions import Literal, TypedDict

from ..._types import SequenceNotStr

__all__ = ["PersonSamplerParamsParam"]


class PersonSamplerParamsParam(TypedDict, total=False):
    age_range: Iterable[int]
    """If specified, then only synthetic people within this age range will be sampled."""

    city: Union[str, SequenceNotStr[str]]
    """If specified, then only synthetic people from these cities will be sampled."""

    locale: str
    """
    Locale that determines the language and geographic location that a synthetic
    person will be sampled from. Must be a locale supported by a managed Nemotron
    Personas dataset. Managed datasets exist for the following locales: en_US,
    ja_JP, en_IN, hi_IN.
    """

    sampler_type: Literal["person"]

    select_field_values: Dict[str, SequenceNotStr[str]]
    """Sample synthetic people with the specified field values.

    This is meant to be a flexible argument for selecting a subset of the population
    from the managed dataset. Note that this sampler does not support rare
    combinations of field values and will likely fail if your desired subset is not
    well-represented in the managed Nemotron Personas dataset. We generally
    recommend using the `sex`, `city`, and `age_range` arguments to filter the
    population when possible.
    """

    sex: str
    """If specified, then only synthetic people of the specified sex will be sampled."""

    with_synthetic_personas: bool
    """If True, then append synthetic persona columns to each generated person."""
