# Copyright 2025 Snowflake Inc.
# SPDX-License-Identifier: Apache-2.0

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

# http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Source validation executor for extracting and saving source data as Parquet."""

import logging
import os

import pandas as pd

from snowflake.snowflake_data_validation.configuration.model.table_configuration import (
    TableConfiguration,
)
from snowflake.snowflake_data_validation.extractor.metadata_extractor_base import (
    MetadataExtractorBase,
)
from snowflake.snowflake_data_validation.script_writer.script_writer_base import (
    ScriptWriterBase,
)
from snowflake.snowflake_data_validation.utils.base_output_handler import (
    OutputMessageLevel,
)
from snowflake.snowflake_data_validation.utils.constants import Origin
from snowflake.snowflake_data_validation.utils.context import Context
from snowflake.snowflake_data_validation.utils.logging_utils import log
from snowflake.snowflake_data_validation.utils.model.table_column_metadata import (
    TableColumnMetadata,
)
from snowflake.snowflake_data_validation.utils.model.table_context import TableContext


LOGGER = logging.getLogger(__name__)


class SourceValidationExecutor:
    """Executor for source-only validation query execution.

    This executor executes validation queries on the source database only
    and saves the results as Parquet files for later validation without
    needing source database access.

    It does NOT perform any validation or comparison - just extracts and saves data.
    """

    @log
    def __init__(
        self,
        source_extractor: MetadataExtractorBase,
        context: Context,
    ):
        """Initialize the source validation executor.

        Args:
            source_extractor: Extractor for source metadata
            context: Validation context containing configuration and runtime info

        Raises:
            ValueError: If source_extractor is None
            TypeError: If source_extractor is a ScriptWriterBase instance

        """
        LOGGER.debug("Initializing SourceValidationExecutor")

        # Validate that source_extractor is not None
        if source_extractor is None:
            error_msg = "source_extractor cannot be None"
            LOGGER.error(error_msg)
            raise ValueError(error_msg)

        # Validate that source_extractor is not a ScriptWriterBase
        # ScriptWriterBase doesn't have the required extract_schema_metadata
        # and extract_metrics_metadata methods
        if isinstance(source_extractor, ScriptWriterBase):
            error_msg = (
                "SourceValidationExecutor requires a MetadataExtractorBase instance "
                "with extract_schema_metadata and extract_metrics_metadata methods. "
                "ScriptWriterBase instances are not supported as they only write "
                "queries to files without executing them."
            )
            LOGGER.error(error_msg)
            raise TypeError(error_msg)

        self.source_extractor = source_extractor
        self.context = context
        LOGGER.debug("SourceValidationExecutor initialized")

    @log
    def execute_source_validation(
        self,
        table_configuration: TableConfiguration,
        source_table_column_metadata: TableColumnMetadata,
    ) -> None:
        """Execute validation queries on source and save results as Parquet.

        Args:
            table_configuration: Configuration for the table
            source_table_column_metadata: Metadata for source table columns

        """
        LOGGER.info(
            "Executing source validation for table: %s",
            table_configuration.fully_qualified_name,
        )

        # Generate source table context
        source_table_context = self._generate_source_table_context(
            table_configuration, source_table_column_metadata
        )

        # Execute schema validation
        self._execute_and_save_schema(source_table_context)

        # Execute metrics validation
        self._execute_and_save_metrics(source_table_context)

        LOGGER.info(
            "Completed source validation for table: %s",
            table_configuration.fully_qualified_name,
        )

    def _generate_source_table_context(
        self,
        table_configuration: TableConfiguration,
        source_table_column_metadata: TableColumnMetadata,
    ) -> TableContext:
        """Generate table context for source validation.

        Args:
            table_configuration: Table configuration
            source_table_column_metadata: Source table column metadata

        Returns:
            TableContext: Generated table context for source

        """
        return TableContext(
            apply_metric_column_modifier=table_configuration.apply_metric_column_modifier,
            chunk_number=table_configuration.chunk_number,
            column_mappings=table_configuration.column_mappings,
            column_selection_list=source_table_column_metadata.column_selection_list,
            columns=source_table_column_metadata.columns,
            database_name=table_configuration.source_database,
            exclude_metrics=table_configuration.exclude_metrics,
            fully_qualified_name=table_configuration.fully_qualified_name,
            has_where_clause=table_configuration.has_where_clause,
            max_failed_rows_number=table_configuration.max_failed_rows_number,
            user_index_column_collection=table_configuration.index_column_list,
            id=table_configuration.id,
            is_case_sensitive=table_configuration.is_case_sensitive,
            is_exclusion_mode=table_configuration.use_column_selection_as_exclude_list,
            origin=Origin.SOURCE,
            platform=self.context.source_platform,
            row_count=source_table_column_metadata.row_count,
            run_id=self.context.run_id,
            run_start_time=self.context.run_start_time,
            schema_name=table_configuration.source_schema,
            sql_generator=self.context.sql_generator,
            table_name=table_configuration.source_table,
            templates_loader_manager=self.context.source_templates,
            where_clause=table_configuration.where_clause,
        )

    def _execute_and_save_schema(self, source_table_context: TableContext) -> None:
        """Execute schema query and save results as Parquet.

        Args:
            source_table_context: Source table context

        """
        LOGGER.info(
            "Executing schema query for source: %s",
            source_table_context.fully_qualified_name,
        )

        self.context.output_handler.handle_message(
            message=(
                f"Extracting schema metadata from: "
                f"{source_table_context.fully_qualified_name}"
            ),
            level=OutputMessageLevel.INFO,
        )

        # Execute schema query
        schema_df = self.source_extractor.extract_schema_metadata(
            table_context=source_table_context,
            output_handler=self.context.output_handler,
        )

        # Save as Parquet
        output_path = self._get_output_path("schema", source_table_context)
        self._save_dataframe_as_parquet(schema_df, output_path)

        self.context.output_handler.handle_message(
            header="Schema data extracted and saved.",
            message=(f"Saved {len(schema_df)} schema rows to: {output_path}"),
            level=OutputMessageLevel.SUCCESS,
        )

    def _execute_and_save_metrics(self, source_table_context: TableContext) -> None:
        """Execute metrics query and save results as Parquet.

        Args:
            source_table_context: Source table context

        """
        LOGGER.info(
            "Executing metrics query for source: %s",
            source_table_context.fully_qualified_name,
        )

        self.context.output_handler.handle_message(
            message=(
                f"Extracting metrics metadata from: "
                f"{source_table_context.fully_qualified_name}"
            ),
            level=OutputMessageLevel.INFO,
        )

        # Execute metrics query
        metrics_df = self.source_extractor.extract_metrics_metadata(
            table_context=source_table_context,
            output_handler=self.context.output_handler,
        )

        # Save as Parquet
        output_path = self._get_output_path("metrics", source_table_context)
        self._save_dataframe_as_parquet(metrics_df, output_path)

        self.context.output_handler.handle_message(
            header="Metrics data extracted and saved.",
            message=(f"Saved {len(metrics_df)} metrics rows to: {output_path}"),
            level=OutputMessageLevel.SUCCESS,
        )

    def _get_output_path(
        self, validation_type: str, table_context: TableContext
    ) -> str:
        """Get the output file path for Parquet file.

        Args:
            validation_type: Type of validation (schema or metrics)
            table_context: Table context

        Returns:
            str: Full path to output Parquet file

        """
        # Create directory structure: output_dir/source/{validation_type}/
        output_dir = os.path.join(self.context.report_path, "source", validation_type)
        os.makedirs(output_dir, exist_ok=True)

        # Filename: {table_fully_qualified_name}.parquet (dots replaced with underscores)
        filename = f"{table_context.normalized_fully_qualified_name}.parquet"
        return os.path.join(output_dir, filename)

    def _save_dataframe_as_parquet(self, df: pd.DataFrame, output_path: str) -> None:
        """Save DataFrame as Parquet file.

        Args:
            df: DataFrame to save
            output_path: Path to output file

        Note:
            Uses Snappy compression for optimal balance between speed and compression ratio,
            which is ideal for data that will be read frequently during validation.

        """
        LOGGER.debug("Saving DataFrame to Parquet: %s", output_path)
        try:
            df.to_parquet(
                output_path,
                engine="pyarrow",
                compression="snappy",  # Fast compression, good balance for validation data
                index=False,
            )
            LOGGER.debug("Successfully saved Parquet file: %s", output_path)
        except Exception as e:
            LOGGER.error(
                "Error saving DataFrame to Parquet file %s: %s", output_path, e
            )
            raise
