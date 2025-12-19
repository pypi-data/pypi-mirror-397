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

from typing import List, Union, Optional
from typing_extensions import Annotated, TypeAlias

from ..._utils import PropertyInfo
from ..._compat import PYDANTIC_V1, ConfigDict
from ..._models import BaseModel
from .seed_config import SeedConfig
from .processor_config import ProcessorConfig
from .model_config_param import ModelConfigParam
from .sampler_column_config import SamplerColumnConfig
from .llm_code_column_config import LlmCodeColumnConfig
from .llm_text_column_config import LlmTextColumnConfig
from .llm_judge_column_config import LlmJudgeColumnConfig
from .expression_column_config import ExpressionColumnConfig
from .validation_column_config import ValidationColumnConfig
from .seed_dataset_column_config import SeedDatasetColumnConfig
from .judge_score_profiler_config import JudgeScoreProfilerConfig
from .column_inequality_constraint import ColumnInequalityConstraint
from .llm_structured_column_config import LlmStructuredColumnConfig
from .scalar_inequality_constraint import ScalarInequalityConstraint

__all__ = ["DataDesignerConfig", "Column", "Constraint"]

Column: TypeAlias = Annotated[
    Union[
        ExpressionColumnConfig,
        LlmCodeColumnConfig,
        LlmJudgeColumnConfig,
        LlmStructuredColumnConfig,
        LlmTextColumnConfig,
        SamplerColumnConfig,
        SeedDatasetColumnConfig,
        ValidationColumnConfig,
    ],
    PropertyInfo(discriminator="column_type"),
]

Constraint: TypeAlias = Union[ScalarInequalityConstraint, ColumnInequalityConstraint]


class DataDesignerConfig(BaseModel):
    columns: List[Column]

    constraints: Optional[List[Constraint]] = None

    model_configs: Optional[List[ModelConfigParam]] = None

    processors: Optional[List[ProcessorConfig]] = None

    profilers: Optional[List[JudgeScoreProfilerConfig]] = None

    seed_config: Optional[SeedConfig] = None
    """Configuration for sampling data from a seed dataset.

    Args: dataset: Path or identifier for the seed dataset. sampling_strategy:
    Strategy for how to sample rows from the dataset. - ORDERED: Read rows
    sequentially in their original order. - SHUFFLE: Randomly shuffle rows before
    sampling. When used with selection_strategy, shuffling occurs within the
    selected range/partition. selection_strategy: Optional strategy to select a
    subset of the dataset. - IndexRange: Select a specific range of indices (e.g.,
    rows 100-200). - PartitionBlock: Select a partition by splitting the dataset
    into N equal parts. Partition indices are zero-based (index=0 is the first
    partition, index=1 is the second, etc.).

    Examples: Read rows sequentially from start to end:
    SeedConfig(dataset="my_data.parquet",
    sampling_strategy=SamplingStrategy.ORDERED)

        Read rows in random order:
            SeedConfig(dataset="my_data.parquet", sampling_strategy=SamplingStrategy.SHUFFLE)

        Read specific index range (rows 100-199):
            SeedConfig(
                dataset="my_data.parquet",
                sampling_strategy=SamplingStrategy.ORDERED,
                selection_strategy=IndexRange(start=100, end=199)
            )

        Read random rows from a specific index range (shuffles within rows 100-199):
            SeedConfig(
                dataset="my_data.parquet",
                sampling_strategy=SamplingStrategy.SHUFFLE,
                selection_strategy=IndexRange(start=100, end=199)
            )

        Read from partition 2 (3rd partition, zero-based) of 5 partitions (20% of dataset):
            SeedConfig(
                dataset="my_data.parquet",
                sampling_strategy=SamplingStrategy.ORDERED,
                selection_strategy=PartitionBlock(index=2, num_partitions=5)
            )

        Read shuffled rows from partition 0 of 10 partitions (shuffles within the partition):
            SeedConfig(
                dataset="my_data.parquet",
                sampling_strategy=SamplingStrategy.SHUFFLE,
                selection_strategy=PartitionBlock(index=0, num_partitions=10)
            )
    """

    if not PYDANTIC_V1:
        # allow fields with a `model_` prefix
        model_config = ConfigDict(protected_namespaces=tuple())
