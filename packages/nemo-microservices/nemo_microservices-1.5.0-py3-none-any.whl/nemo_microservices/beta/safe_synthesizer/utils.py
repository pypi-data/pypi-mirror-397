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

from __future__ import annotations

import functools
import json
import time
from pathlib import Path
from typing import Any, Generator, Protocol

import numpy as np
import pandas as pd
from datasets import Dataset
from pandas import DataFrame
from tabulate import tabulate

from .data_processing.stats import Statistics
from .defaults import (
    LOG_PREFIX,
)
from .logging_utils import get_logger

logger = get_logger(__name__)


# This is being patched in here because outlines_core doesn't export it and outlines doesn't have it anymore
# past outlines==0.11.8
def _get_num_items_pattern(min_items, max_items, whitespace_pattern):
    # Helper function for arrays and objects
    min_items = int(min_items or 0)
    if max_items is None:
        return rf"{{{max(min_items - 1, 0)},}}"
    else:
        max_items = int(max_items)
        if max_items < 1:
            return None
        return rf"{{{max(min_items - 1, 0)},{max_items - 1}}}"


def create_schema_prompt(
    columns: list[str],
    instruction: str,
    prompt_template: str,
) -> str:
    """Create the schema prompt based on the given column names.

    Args:
        columns: List of column names.
        instruction: Instruction of the prompt.
        prompt_template: Template with variables for the instruction and schema.

    Returns:
        The schema prompt.
    """
    return prompt_template.format(instruction=instruction, schema=",".join([f'"{c}":<unk>' for c in columns]))


def get_random_number_generator(seed: int) -> np.random.Generator:
    """Return a random number generator with the given seed."""
    return np.random.default_rng(seed)


def has_length(obj: Any) -> bool:
    """Returns True if the given object has __len__ defined."""
    try:
        return len(obj) is not None
    except TypeError:
        return False


def log_stats(
    stats: Statistics | list[Statistics],
    headers: list[str] | None = None,
    table_format: str = "fancy_grid",
    use_print: bool = False,
) -> None:
    """Log the given aggregated statistics using tabulate.

    Args:
        stats: Single or list of statistics objects.
        headers: Column headers.
        table_format: Tabulate table format.
        use_print: If True, print the table instead of logging it.
    """
    headers = headers or ""
    stats = stats if isinstance(stats, list) else [stats]
    table = tabulate(
        [
            ["min"] + [round_number_if_float(s.min) for s in stats],
            ["max"] + [round_number_if_float(s.max) for s in stats],
            ["mean"] + [round_number_if_float(s.mean) for s in stats],
            ["stddev"] + [round_number_if_float(s.stddev) for s in stats],
        ],
        headers=headers,
        tablefmt=table_format,
        numalign="right",
    )
    if use_print:
        print(table)
    else:
        logger.info(f"\n{table}")


def log_training_example_stats(stats_dict: dict[str, Statistics], **kwargs) -> None:
    """Log training example statistics from the given dictionary."""
    logger.info(f"{LOG_PREFIX}Training Example Statistics:")
    stats = list(stats_dict.values())
    headers = list([name.replace("_", " ").capitalize() for name in stats_dict.keys()])
    log_stats(stats, headers=headers, **kwargs)


def round_number_if_float(number, precision=3):
    """Round the number to the given precision if it is a float."""
    return round(number, precision) if isinstance(number, float) else number


def smart_read_table(df_or_path: str | Path | pd.DataFrame) -> pd.DataFrame:
    """Load (if needed) and return tabular data set as a DataFrame

    Args:
        df_or_path: DataFrame or path to a table file.

    Returns:
        The tabular data as a DataFrame.
    """
    if isinstance(df_or_path, pd.DataFrame):
        return df_or_path

    path = str(df_or_path)
    if path.endswith(".csv"):
        df = pd.read_csv(path)
    elif path.endswith(".json"):
        try:
            df = pd.read_json(path)
        except Exception:
            df = pd.read_json(path, lines=True, orient="records")
    elif path.endswith(".jsonl"):
        df = pd.read_json(path, lines=True, orient="records")
    elif path.endswith(".parquet"):
        df = pd.read_parquet(path)
    else:
        raise ValueError(f"Unsupported file type: {path}")
    return df


def time_function(func):
    """Decorator to log the time taken by a function to execute."""

    @functools.wraps(func)
    def time_closure(*args, **kwargs):
        start = time.perf_counter()
        result = func(*args, **kwargs)
        time_elapsed = time.perf_counter() - start
        time_elapsed = f"{time_elapsed:.2f} sec" if time_elapsed <= 120 else f"{time_elapsed / 60:.2f} min"
        logger.info(f"⏱️  Function: {func.__name__}, Time: {time_elapsed}\n")
        return result

    return time_closure


def grouped_train_test_split(
    dataset: Dataset,
    test_size: float,
    group_by: str | list[str],
    seed: int | None = None,
) -> tuple[DataFrame, DataFrame | None]:
    """
    Currently unused, but this function supports multi_column split for future reference.

    Modified this to work with the Assemblers.
    Split a HuggingFace Dataset into train and test sets while ensuring that the groups stay together.

    Args:
        dataset: The HuggingFace Dataset to split.
        test_size: The size of the test set.
        group_by: Column name or list of column names to group by.
        seed: The random state to use for the split.

    Returns:
        A tuple of the train and test sets.
    """

    # Convert to pandas for group operations
    df = dataset.to_pandas()
    # importing like this to avoid a dep for testing on the sdk side
    from ..holdout import holdout as nss_holdout

    return nss_holdout.grouped_train_test_split(df=df, test_size=test_size, group_by=group_by, random_state=seed)


class DataActionsFn(Protocol):
    def __call__(self, batch: pd.DataFrame, df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]: ...


def debug_fmt(df: pd.DataFrame) -> str:
    """
    Format dataframes for the purposes of data actions debugging.
    """
    return df.head(5).to_json(orient="records", date_format="iso")


def merge_dicts(base: dict, new: dict) -> dict:
    """Merge two dictionaries. Will prefer values from the `new` dict and
    handles deeply nested dicts.
    """
    result = base.copy()
    for k, new_v in new.items():
        base_v = result.get(k)
        if isinstance(base_v, dict) and isinstance(new_v, dict):
            result[k] = merge_dicts(base_v, new_v)
        else:
            result[k] = new_v
    return result


def is_iterable(x: Any):
    """
    checks if the object is iterable. valid for items with __getitem__ iters.
    Rare cases of `__getitem__` not being iterable abound.
    """
    return hasattr(x, "__iter__") and hasattr(x, "__getitem__")


def flatten(iter) -> Generator:
    """
    Flatten an iterable that might contain other iterables.
    Note that this will break strings apart.
    """
    """Flattens a nested iterable."""
    if isinstance(iter, dict):
        logger.warning("Flattening a dictionary is not supported. Returning the dictionary as is.")
        yield iter
    for v in iter:
        if is_iterable(v) and not isinstance(v, str):
            yield from flatten(v)
        else:
            yield v


def all_equal_type(iter, type_, flatten_iter=True) -> bool:
    """
    check if all the values in an iterable.

    Args:
        iter: the iterable
        type_: type to check against
        flatten_iter: flatten the iterable's nested iterables - which includes strings.
    """

    def typecheck(x):
        return isinstance(x, type_)

    if flatten_iter:
        mapped = map(typecheck, flatten(iter))
    else:
        mapped = map(typecheck, iter)
    for i in mapped:
        if not i:
            return False
    return True


def write_json(
    data: dict,
    path: str | Path,
    encoding: str | None = None,
    indent: int | None = None,
) -> None:
    """
    Write the given dictionary to JSON.
    The directory is created if it does not yet exist.
    """
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding=encoding) as file:
        json.dump(data, file, indent=indent)


def load_json(path: str | Path, encoding: str | None = None) -> dict:
    """Load JSON file and return the content as a dict."""
    with Path(path).open(encoding=encoding) as file:
        return json.load(file)
