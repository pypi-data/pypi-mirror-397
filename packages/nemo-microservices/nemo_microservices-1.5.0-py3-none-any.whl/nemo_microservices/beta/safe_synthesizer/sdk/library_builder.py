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

import time
from typing import TYPE_CHECKING

import pandas as pd
from datasets import Dataset

from ..config import (
    SafeSynthesizerParameters,
)
from ..config.autoconfig import resolve_auto_config
from ..evaluation.evaluator import Evaluator
from ..generation.vllm_backend import VllmBackend
from ..holdout.holdout import Holdout
from ..llm.metadata import ModelMetadata
from ..logging_utils import get_logger
from ..pii_replacer.nemo_pii import NemoPII
from ..results import SafeSynthesizerResults, make_nss_results
from ..training.huggingface_backend import HuggingFaceBackend
from .config_builder import ConfigBuilder

logger = get_logger(__name__)

if TYPE_CHECKING:
    from ..data_processing.actions.data_actions import ActionExecutor
    from ..generation.backend import GeneratorBackend
    from ..training.backend import TrainingBackend


def _run_pii_replacer_only(config: SafeSynthesizerParameters, df: pd.DataFrame) -> SafeSynthesizerResults:
    total_start = time.monotonic()

    replacer = NemoPII(config.replace_pii)
    replacer.transform_df(df)

    evaluator = None
    if config.evaluation.enabled:
        evaluator = Evaluator(
            config=config,
            generate_results=replacer.result.transformed_df,
            pii_replacer_time=replacer.elapsed_time if replacer else None,
            column_statistics=replacer.result.column_statistics,
        )
        evaluator.evaluate()

    total_time_sec = time.monotonic() - total_start
    evaluation_time_sec = evaluator.evaluation_time if evaluator else None

    return make_nss_results(
        total_time=total_time_sec,
        evaluation_time=evaluation_time_sec,
        training_time=None,
        generation_time=None,
        generate_results=replacer.result.transformed_df,
        report=evaluator.report if evaluator else None,
    )


def _get_unsloth_backend_class() -> type[TrainingBackend]:
    """Get the Unsloth training backend class."""
    from ..training.unsloth_backend import UnslothTrainer

    return UnslothTrainer


def get_training_backend_class(config: SafeSynthesizerParameters) -> type[TrainingBackend]:
    """Get the training backend class for the given configuration.
    Args:
        config: SafeSynthesizerParameters object.

    Returns:
        The training backend class.
    """
    class_map = {
        "huggingface": HuggingFaceBackend,
        "unsloth": _get_unsloth_backend_class(),
    }
    logger.info(f"Use unsloth: {config.training.use_unsloth}")
    cls = "unsloth" if config.training.use_unsloth is True else "huggingface"
    cls = class_map.get(cls)
    if cls is None:
        raise ValueError(f"Unsupported training backend: {config.training.use_unsloth}")
    return cls


class SafeSynthesizer(ConfigBuilder):
    """Builder for package-only Safe Synthesizer workflows.

    This class provides a fluent interface for building Safe Synthesizer workflows.
    It allows you to configure all the parameters needed to create and run a Safe Synthesizer workflow.

    Each main parameter group method returns the builder instance to allow for method chaining, and most methods
    follow a common api:
        ```python
            >>> def with_<parameter_group>(self, config: ParamT | ParamDict | None = None, **kwargs) -> SafeSynthesizer: pass
        ```
        config: Optional configuration object or dictionary containing <parameter_group> parameters.
      **kwargs: Configuration parameters for <parameter_group>, that will override any overlapping parameters in config and model defaults.

    Examples:
        ```python
        >>> from nemo_safe_synthesizer.sdk.library_builder import SafeSynthesizer

        >>> builder = (
        >>>     SafeSynthesizer()
        >>>     .with_data_source("your_dataframe")
        >>>     .with_replace_pii()  # Uses default PII replacement settings
        >>>     .synthesize()  # Enables synthesis; not strictly needed if you are already calling training() or generation()
        >>>     .with_train(learning_rate=0.0001)  # Custom training settings
        >>>     .with_generate(num_records=10000)  # Custom generation settings
        >>>     .with_evaluate(enable=False)  # disable evaluation for this job
        >>> )
        >>> builder.run()
        >>> results = builder.results
        ```
    """

    trainer: TrainingBackend
    generator: GeneratorBackend
    evaluator: Evaluator
    results: SafeSynthesizerResults

    def __init__(self, config: SafeSynthesizerParameters | None = None):
        super().__init__(config=config)
        self._resolve_nss_config()

    def run(self) -> None:
        """Run the Safe Synthesizer workflow end to end."""
        total_start = time.monotonic()
        if not self._nss_config.enable_synthesis:
            if not self._nss_config.enable_replace_pii:
                raise ValueError("At least one of enable_replace_pii or enable_synthesis must be True.")
            if self._nss_config.replace_pii is not None:
                self.results = _run_pii_replacer_only(self._nss_config, self._data_source)
            else:
                raise ValueError("Pii replacement config is None but enable_replace_pii is True.")

        holdout = Holdout(self._nss_config)
        original_train_df, test_df = holdout.train_test_split(self._data_source)

        train_df = original_train_df
        column_statistics = None

        resolved_config = resolve_auto_config(train_df, self._nss_config)
        self._nss_config = resolved_config

        replacer = None
        if self._nss_config.enable_replace_pii:
            replacer = NemoPII(self._nss_config.replace_pii)
            replacer.transform_df(original_train_df)
            train_df = replacer.result.transformed_df
            column_statistics = replacer.result.column_statistics
            # We explicitly do not replace PII in the test set so that the
            # privacy metrics are valid.

        maybe_split_dataset: bool = True
        action_executor: ActionExecutor | None = None
        llm_metadata = ModelMetadata.from_config(self._nss_config)

        self.trainer = get_training_backend_class(self._nss_config)(
            params=self._nss_config,
            model_metadata=llm_metadata,
            training_dataset=Dataset.from_pandas(train_df),
            action_executor=action_executor,
            verbose_logging=True,
            maybe_split_dataset=maybe_split_dataset,
            artifact_path=None,
        )
        self.trainer.load_model()
        self.trainer.train()

        self.generator = VllmBackend(config=self._nss_config, model_metadata=llm_metadata)
        self.generator.initialize()
        self.generator.generate()

        self.evaluator = Evaluator(
            config=self._nss_config,
            generate_results=self.generator.gen_results,
            pii_replacer_time=replacer.elapsed_time if replacer else None,
            column_statistics=column_statistics,
            train_df=train_df,
            test_df=test_df,
        )
        self.evaluator.evaluate()

        self.results = make_nss_results(
            total_time=time.monotonic() - total_start,
            training_time=self.trainer.results.elapsed_time,
            generation_time=self.generator.gen_results.elapsed_time,
            evaluation_time=self.evaluator.evaluation_time,
            report=self.evaluator.report,
            generate_results=self.generator.gen_results,
        )
