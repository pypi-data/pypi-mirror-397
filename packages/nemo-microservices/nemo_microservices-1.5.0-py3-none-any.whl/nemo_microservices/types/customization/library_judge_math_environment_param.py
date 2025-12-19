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

from typing_extensions import Literal, TypedDict

__all__ = ["LibraryJudgeMathEnvironmentParam"]


class LibraryJudgeMathEnvironmentParam(TypedDict, total=False):
    judge_temperature: float
    """Sampling temperature for judge responses.

    Higher values (e.g., 1.0) increase randomness, lower values (e.g., 0.1) make
    output more deterministic. Temperature of 0 is equivalent to greedy sampling.
    """

    judge_top_p: float
    """Nucleus sampling parameter (top-p) for judge responses.

    Only tokens with cumulative probability >= top_p are considered. 1.0 means no
    filtering; lower values (e.g., 0.9) increase quality by filtering unlikely
    tokens.
    """

    name: Literal["library_judge_math"]
    """
    Name of the task-specific environment that the dataset schema is designed to be
    used with. This field is automatically added to Dataset Rows based on the
    Environment selection.
    """

    should_use_judge: bool
    """Whether to use a judge for the responses."""
