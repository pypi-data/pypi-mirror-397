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

import logging
import random
import string
import tempfile
from pathlib import Path
from typing import TYPE_CHECKING

import pandas as pd
from huggingface_hub import HfApi
from typing_extensions import Self

from ..config import (
    SafeSynthesizerJobConfig,
)
from .config_builder import ConfigBuilder, ParamDict
from .datastore import DatastoreSettings
from .job import SafeSynthesizerJob

if TYPE_CHECKING:
    from nemo_microservices import NeMoMicroservices

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SafeSynthesizerJobBuilder(ConfigBuilder):
    """Builder for Safe Synthesizer Jobs ran with the Nemo Microservice Platform.

    This class provides a fluent interface for building Safe Synthesizer configurations.
    It allows you to configure all the parameters needed to create and run a Safe Synthesizer job
    as defined by the SafeSythesizerJobConfig class.

    Each main parameter group method returns the builder instance to allow for method chaining, and most methods
    follow a common api:
        ```python
            >>> def with_<parameter_group>(self, config: ParamT | ParamDict | None = None, **kwargs) -> SafeSynthesizerJobBuilder: pass
        ```
      config: Optional configuration object or dictionary containing <parameter_group> parameters.
      **kwargs: Configuration parameters for <parameter_group>, that will override any overlapping parameters in config and model defaults.

    Examples:
        ```python
        >>> from nemo_microservices import NeMoMicroservices
        >>> from nemo_microservices.beta.safe_synthesizer.sdk.job_builder import SafeSynthesizerJobBuilder

        >>> client = NeMoMicroservices(base_url=..., inference_base_url=...)
        >>> # Using default PII replacement settings
        >>> builder = (
        >>>     SafeSynthesizerJobBuilder(client)
        >>>     .with_data_source("your_dataframe")
        >>>     .with_datastore("your_datastore_settings")
        >>>     .with_replace_pii()  # Uses default PII replacement settings
        >>>     .synthesize()  # Enables synthesis; not strictly needed if you are already calling training() or generation()
        >>>     .with_train(learning_rate=0.0001)  # Custom training settings
        >>>     .with_generate(num_records=10000)  # Custom generation settings
        >>>     .with_evaluate(enable=False)  # disable evaluation for this job
        >>>     .resolve_job_config()  # Finalizes the job configuration - useful for debugging or logging for yourself
        >>> )
        >>> job = builder.create_job()  # Creates and starts the job
    """

    def __init__(self, client: NeMoMicroservices):
        super().__init__()
        self._client = client
        self._datastore: DatastoreSettings | None = None
        self._final_job_config: SafeSynthesizerJobConfig | None = None

    def with_datastore(self, config: DatastoreSettings | ParamDict | None = None, **kwargs) -> Self:
        """Set the datastore settings for uploading datasets.

        Args:
            config: Datastore settings or dictionary containing datastore configuration.

        Returns:
            The current Safe Synthesizer builder instance.
        """
        ds = self._resolve_config(values=config, cls=DatastoreSettings, **kwargs)
        if not ds:
            raise ValueError("Datastore settings must be provided")
        self._datastore = ds
        return self

    def _generate_random_string(self, length=6):
        """
        Generates a random string of a specified length using uppercase letters and digits.
        """
        characters = string.ascii_uppercase + string.digits
        random_string = "".join(random.choice(characters) for _ in range(length))
        return random_string

    def _resolve_datasource(self, **kwargs) -> None:
        try:
            match self._data_source:
                case pd.DataFrame():
                    pass
                case str(url):
                    self._data_source: pd.DataFrame = pd.read_csv(url, **kwargs)
                case _:
                    raise ValueError("Data source must be a pandas DataFrame or a URL")

            with tempfile.NamedTemporaryFile(mode="w+", suffix=".csv", delete=False) as temp_file:
                # Write the DataFrame to the temporary file
                self._data_source.to_csv(temp_file.name, index=False)
            # TODO: Have to have an option to give a filename somehow
            file_name = f"dataset{self._generate_random_string()}.csv"
            result = self._upload_to_hf_hub(
                dataset_path=temp_file.name,
                filename=file_name,
                repo_id="default/safe-synthesizer",
                datastore=self._datastore,
            )
            self._data_source_path = result
        finally:
            Path(temp_file.name).unlink(missing_ok=True)

    def _resolve_job_config(self):
        self._resolve_datasource()
        self._resolve_nss_config()
        if not self._enable_replace_pii and not self._enable_synthesis:
            raise ValueError("Data synthesis and/or replace PII must be enabled")

        if not self._data_source_path:
            raise ValueError("No data source path found after uploading dataset, check datastore settings")

        job_config = SafeSynthesizerJobConfig(
            data_source=f"hf://datasets/{self._data_source_path}",
            config=self._nss_config,
        )
        self._final_job_config = job_config

    def resolve_job_config(self) -> Self:
        """Generate the final job configuration.

        This method compiles all the configurations set through the builder methods
        into a final job configuration that can be used to create and execute a job.

        Returns:
            The final job configuration.
        """
        if self._final_job_config is None:
            self._resolve_job_config()
        return self

    def create_job(self, **kwargs) -> SafeSynthesizerJob:
        """Create and optionally execute the synthetic data generation job.

        Args:
            **kwargs: Additional job creation parameters.

        Returns:
            Job object that can be used to fetch results.

        """
        self._resolve_job_config()
        response = self._client.beta.safe_synthesizer.jobs.create(spec=self._final_job_config.model_dump(), **kwargs)
        return SafeSynthesizerJob(response.id, self._client)

    def _upload_to_hf_hub(
        self,
        dataset_path: str | Path,
        filename: str,
        repo_id: str,
        datastore: DatastoreSettings | None,
        **kwargs,
    ) -> str:
        datastore = self._datastore
        dataset_path = self._validate_dataset_path(dataset_path)
        if not datastore:
            raise Exception("Error uploading file, datastore location must be set using `with_datastore`")
        hfapi = HfApi(endpoint=datastore.endpoint, token=datastore.token)
        hfapi.create_repo(repo_id, exist_ok=True, repo_type="dataset")
        hfapi.upload_file(
            path_or_fileobj=dataset_path,
            path_in_repo=filename,
            repo_id=repo_id,
            repo_type="dataset",
            **kwargs,
        )
        return f"{repo_id}/{filename}"

    @staticmethod
    def _validate_dataset_path(dataset_path: str | Path) -> Path:
        if not Path(dataset_path).is_file():
            raise ValueError("🛑 To upload a dataset to the datastore, you must provide a valid file path.")
        if not Path(dataset_path).name.endswith((".parquet", ".csv", ".json", ".jsonl")):
            raise ValueError(
                "🛑 Dataset files must be in `parquet`, `csv`, or `json` (orient='records', lines=True) format."
            )
        return Path(dataset_path)
