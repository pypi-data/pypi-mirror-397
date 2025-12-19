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

"""Collection of default settings for the Navigator FT implementation."""

from pathlib import Path

# logging parameters
LOG_PREFIX = "<<  Nemo Safe Synthesizer  >> "
LOG_DASHES = "-" * 100
LOG_NUM_ERRORS = 10
MAX_ERR_COL_WIDTH = 80
# Human-readable JSON error messages, particularly for general schema validation
# categories in prod. Schema validation messages are based on
# https://json-schema.org/draft/2020-12/json-schema-validation#name-a-vocabulary-for-structural
HUMAN_READABLE_ERR_MSGS = {
    # JSON schema errors
    "type": "Invalid field type",
    "enum": "Invalid field value",
    "const": "Invalid field value",
    "multipleOf": "Field value must be a multiple of a given number",
    "maximum": "Field value must be less than or equal to a given number",
    "exclusiveMaximum": "Field value must be less than a given number",
    "minimum": "Field value must be greater than or equal to a given number",
    "exclusiveMinimum": "Field value must be greater than a given number",
    "maxLength": "Field value must be at most a given length",
    "minLength": "Field value must be at least a given length",
    "pattern": "Field value must match a given pattern",
    "maxItems": "Field value must have at most a given number of items",
    "minItems": "Field value must have at least a given number of items",
    "uniqueItems": "Field value must have unique items",
    "maxContains": "Field value must contain at most a given number of items",
    "minContains": "Field value must contain at least a given number of items",
    "maxProperties": "Field value must have at most a given number of properties",
    "minProperties": "Field value must have at least a given number of properties",
    "required": "Missing required field",
    "dependentRequired": "Missing required field based on another field",
    # JSON decode errors
    "Invalid JSON: Unterminated string starting at": "Invalid JSON: Unterminated string",
    # Groupby errors
    "groupby": "Groupby generation failed",
}

# project paths
PACKAGE_PATH = Path(__file__).parent
PROJECT_PATH = PACKAGE_PATH.parent
DEFAULT_BASE_OUTPUT_PATH = PACKAGE_PATH.parent / "local_data"

# evaluation parameters
EVAL_STEPS = 0.3
DEFAULT_VALID_RECORD_EVAL_BATCH_SIZE = 16
NUM_EVAL_BATCHES_TABULAR = 1
NUM_EVAL_BATCHES_GROUPED = 1


# training +  parameters
DEFAULT_PRETRAINED_MODEL_NAME = "TinyLlama-1.1B-Chat-v1.0"
PROMPT_TEMPLATE = "[INST] {instruction} {schema} [/INST]"
DEFAULT_INSTRUCTION = "Generate a JSONL dataset with the following columns: "
DEFAULT_SAMPLING_PARAMETERS = {
    "repetition_penalty": 1.0,
    "temperature": 0.9,
    "top_k": 0,
    "top_p": 1,
}
MAX_NUM_PROMPTS_PER_BATCH = 100
TRAIN_SET_SIZE_BUFFER = 100

# training examples
NUM_OVERLAP_RECORDS = 3

FIXED_RUNTIME_LORA_ARGS = {"use_rslora": True}
FIXED_RUNTIME_GENERATE_ARGS = {"top_k": -1, "min_p": 0}
RUNTIME_MODEL_ARCHIVE_NAME = "safe-synthesizer-model"
RUNTIME_MODEL_CONFIG_NAME = "safe-synthesizer-config"

# miscellaneous
EPS = 1e-15
NUM_SPECIAL_TOKENS = 2
DEFAULT_CACHE_PREFIX = "safe-synthesizer-dataset-cache"
