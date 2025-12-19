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

__all__ = ["CompCodingEnvironmentParam"]


class CompCodingEnvironmentParam(TypedDict, total=False):
    name: Literal["comp_coding"]
    """
    Name of the task-specific environment that the dataset schema is designed to be
    used with. This field is automatically added to Dataset Rows based on the
    Environment selection.
    """

    num_processes: int
    """The number of concurrent processes running tests for verification."""

    unit_test_timeout_secs: int
    """How long to allow each test case to run before terminating the test."""
