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

import math
from dataclasses import dataclass
from typing import Union


@dataclass
class Statistics:
    """Container for basic statistical measures."""

    count: int = 0
    mean: float = 0
    sum_sq_diffs: float = 0
    min: int | float = float("inf")
    max: int | float = float("-inf")

    @property
    def stddev(self) -> float:
        return 0 if self.count <= 1 else math.sqrt(self.sum_sq_diffs / (self.count - 1))


@dataclass
class RunningStatistics(Statistics):
    """Class to calculate the running mean and variance using Welford's method.

    This class allows for the calculation of statistics on-the-fly without the need
    for the entire dataset to be loaded into memory.
    """

    def update(self, x: Union[int, float]) -> None:
        """Update statistics with new value `x`."""
        self.count += 1
        self.min = min(self.min, x)
        self.max = max(self.max, x)
        new_mean = self.mean + (x - self.mean) * 1.0 / self.count
        new_var = self.sum_sq_diffs + (x - self.mean) * (x - new_mean)
        self.mean, self.sum_sq_diffs = new_mean, new_var

    def reset(self) -> None:
        """Reset the running statistics."""
        self.count = 0
        self.mean = 0
        self.sum_sq_diffs = 0
        self.min = float("inf")
        self.max = float("-inf")
