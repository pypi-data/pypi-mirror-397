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
from typing_extensions import Literal, TypeAlias

from ..._models import BaseModel
from .validator_type import ValidatorType
from .code_validator_params import CodeValidatorParams
from .remote_validator_params import RemoteValidatorParams
from .local_callable_validator_params import LocalCallableValidatorParams

__all__ = ["ValidationColumnConfig", "ValidatorParams"]

ValidatorParams: TypeAlias = Union[CodeValidatorParams, LocalCallableValidatorParams, RemoteValidatorParams]


class ValidationColumnConfig(BaseModel):
    name: str

    target_columns: List[str]

    validator_params: ValidatorParams
    """Configuration for code validation. Supports Python and SQL code validation.

    Attributes: code_lang: The language of the code to validate. Supported values
    include: `python`, `sql:sqlite`, `sql:postgres`, `sql:mysql`, `sql:tsql`,
    `sql:bigquery`, `sql:ansi`.
    """

    validator_type: ValidatorType

    batch_size: Optional[int] = None
    """Number of records to process in each batch"""

    column_type: Optional[Literal["validation"]] = None

    drop: Optional[bool] = None
