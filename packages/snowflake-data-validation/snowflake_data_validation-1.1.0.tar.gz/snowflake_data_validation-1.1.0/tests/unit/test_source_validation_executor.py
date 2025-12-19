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

"""Unit tests for SourceValidationExecutor."""

import os
from unittest.mock import MagicMock, patch

import pandas as pd
import pytest

from snowflake.snowflake_data_validation.configuration.model.table_configuration import (
    TableConfiguration,
)
from snowflake.snowflake_data_validation.executer.source_validation_executor import (
    SourceValidationExecutor,
)
from snowflake.snowflake_data_validation.script_writer.script_writer_base import (
    ScriptWriterBase,
)
from snowflake.snowflake_data_validation.utils.model.table_column_metadata import (
    TableColumnMetadata,
)


@pytest.fixture
def mock_source_extractor():
    """Create a mock source extractor."""
    extractor = MagicMock()
    return extractor


@pytest.fixture
def mock_context(tmp_path):
    """Create a mock context with temp directory."""
    context = MagicMock()
    context.report_path = str(tmp_path)
    context.output_handler = MagicMock()
    context.source_templates = MagicMock()
    context.sql_generator = MagicMock()
    return context


@pytest.fixture
def table_configuration():
    """Create a test table configuration."""
    config = TableConfiguration(
        fully_qualified_name="testdb.testschema.testtable",
        source_database="testdb",
        source_schema="testschema",
        source_table="testtable",
        column_selection_list=["col1", "col2", "col3"],
        use_column_selection_as_exclude_list=False,
        index_column_list=[],
    )
    return config


@pytest.fixture
def table_column_metadata():
    """Create test table column metadata."""
    # Create a mock TableColumnMetadata object
    metadata = MagicMock(spec=TableColumnMetadata)
    metadata.columns = [
        MagicMock(name="col1", data_type="INTEGER", nullable=False),
        MagicMock(name="col2", data_type="VARCHAR", nullable=True),
        MagicMock(name="col3", data_type="DATE", nullable=False),
    ]
    metadata.column_selection_list = ["col1", "col2", "col3"]
    metadata.row_count = 1000
    return metadata


class TestSourceValidationExecutorInitialization:
    """Tests for SourceValidationExecutor initialization."""

    def test_initialization(self, mock_source_extractor, mock_context):
        """Test that executor initializes correctly."""
        executor = SourceValidationExecutor(
            source_extractor=mock_source_extractor,
            context=mock_context,
        )

        assert executor.source_extractor == mock_source_extractor
        assert executor.context == mock_context

    def test_initialization_rejects_none_extractor(self, mock_context):
        """Test that initialization raises ValueError when None extractor is passed."""
        # Verify that ValueError is raised with appropriate message
        with pytest.raises(ValueError) as exc_info:
            SourceValidationExecutor(
                source_extractor=None,
                context=mock_context,
            )

        # Check the error message content
        assert str(exc_info.value) == "source_extractor cannot be None"

    def test_initialization_rejects_script_writer(self, mock_context):
        """Test that initialization raises TypeError when ScriptWriterBase is passed."""
        # Create a mock ScriptWriterBase instance
        mock_script_writer = MagicMock(spec=ScriptWriterBase)

        # Verify that TypeError is raised with appropriate message
        with pytest.raises(TypeError) as exc_info:
            SourceValidationExecutor(
                source_extractor=mock_script_writer,
                context=mock_context,
            )

        # Check the error message content
        expected_error = (
            "SourceValidationExecutor requires a MetadataExtractorBase instance "
            "with extract_schema_metadata and extract_metrics_metadata methods. "
            "ScriptWriterBase instances are not supported as they only write "
            "queries to files without executing them."
        )
        assert str(exc_info.value) == expected_error


class TestExecuteSourceValidation:
    """Tests for execute_source_validation method."""

    @patch.object(SourceValidationExecutor, "_execute_and_save_schema")
    @patch.object(SourceValidationExecutor, "_execute_and_save_metrics")
    @patch.object(SourceValidationExecutor, "_generate_source_table_context")
    def test_execute_source_validation_success(
        self,
        mock_generate_context,
        mock_execute_metrics,
        mock_execute_schema,
        mock_source_extractor,
        mock_context,
        table_configuration,
        table_column_metadata,
    ):
        """Test successful source validation execution."""
        # Setup mocks
        mock_table_context = MagicMock()
        mock_generate_context.return_value = mock_table_context

        executor = SourceValidationExecutor(
            source_extractor=mock_source_extractor,
            context=mock_context,
        )

        # Execute
        executor.execute_source_validation(
            table_configuration=table_configuration,
            source_table_column_metadata=table_column_metadata,
        )

        # Verify context generation was called
        mock_generate_context.assert_called_once_with(
            table_configuration, table_column_metadata
        )

        # Verify schema and metrics extraction were called
        mock_execute_schema.assert_called_once_with(mock_table_context)
        mock_execute_metrics.assert_called_once_with(mock_table_context)


class TestGetOutputPath:
    """Tests for _get_output_path method."""

    def test_get_output_path_schema(
        self,
        mock_source_extractor,
        mock_context,
    ):
        """Test output path generation for schema files."""
        executor = SourceValidationExecutor(
            source_extractor=mock_source_extractor,
            context=mock_context,
        )

        # Create mock table context
        mock_table_context = MagicMock()
        mock_table_context.fully_qualified_name = "testdb.testschema.testtable"
        mock_table_context.normalized_fully_qualified_name = (
            "testdb_testschema_testtable"
        )

        output_path = executor._get_output_path("schema", mock_table_context)

        # Verify full path structure: {report_path}/source/schema/{table_name}.parquet
        expected_path = os.path.join(
            mock_context.report_path,
            "source",
            "schema",
            "testdb_testschema_testtable.parquet",
        )
        assert (
            output_path == expected_path
        ), f"Expected path '{expected_path}', got: {output_path}"

    def test_get_output_path_metrics(
        self,
        mock_source_extractor,
        mock_context,
    ):
        """Test output path generation for metrics files."""
        executor = SourceValidationExecutor(
            source_extractor=mock_source_extractor,
            context=mock_context,
        )

        # Create mock table context
        mock_table_context = MagicMock()
        mock_table_context.fully_qualified_name = "testdb.testschema.testtable"
        mock_table_context.normalized_fully_qualified_name = (
            "testdb_testschema_testtable"
        )

        output_path = executor._get_output_path("metrics", mock_table_context)

        # Verify full path structure: {report_path}/source/metrics/{table_name}.parquet
        expected_path = os.path.join(
            mock_context.report_path,
            "source",
            "metrics",
            "testdb_testschema_testtable.parquet",
        )
        assert (
            output_path == expected_path
        ), f"Expected path '{expected_path}', got: {output_path}"

    def test_get_output_path_creates_directory(
        self,
        mock_source_extractor,
        mock_context,
    ):
        """Test that output directory is created if it doesn't exist."""
        executor = SourceValidationExecutor(
            source_extractor=mock_source_extractor,
            context=mock_context,
        )

        # Create mock table context
        mock_table_context = MagicMock()
        mock_table_context.fully_qualified_name = "testdb.testschema.testtable"
        mock_table_context.normalized_fully_qualified_name = (
            "testdb_testschema_testtable"
        )

        output_path = executor._get_output_path("schema", mock_table_context)

        # Verify directory was created
        output_dir = os.path.dirname(output_path)
        assert os.path.exists(output_dir)


class TestSaveDataframeAsParquet:
    """Tests for _save_dataframe_as_parquet method."""

    @patch("pandas.DataFrame.to_parquet")
    def test_save_dataframe_as_parquet(
        self,
        mock_to_parquet,
        mock_source_extractor,
        mock_context,
    ):
        """Test saving DataFrame as Parquet file."""
        executor = SourceValidationExecutor(
            source_extractor=mock_source_extractor,
            context=mock_context,
        )

        # Create test DataFrame
        df = pd.DataFrame(
            {
                "col1": [1, 2, 3],
                "col2": ["a", "b", "c"],
            }
        )

        output_path = "/fake/path/test.parquet"

        # Save DataFrame
        executor._save_dataframe_as_parquet(df, output_path)

        # Verify to_parquet was called with correct parameters
        mock_to_parquet.assert_called_once_with(
            output_path, engine="pyarrow", compression="snappy", index=False
        )

    @patch("pandas.DataFrame.to_parquet")
    def test_save_empty_dataframe_as_parquet(
        self,
        mock_to_parquet,
        mock_source_extractor,
        mock_context,
    ):
        """Test saving empty DataFrame as Parquet file."""
        executor = SourceValidationExecutor(
            source_extractor=mock_source_extractor,
            context=mock_context,
        )

        # Create empty DataFrame with schema
        df = pd.DataFrame(columns=["col1", "col2"])

        output_path = "/fake/path/test.parquet"

        # Save DataFrame
        executor._save_dataframe_as_parquet(df, output_path)

        # Verify to_parquet was called
        mock_to_parquet.assert_called_once()


class TestExecuteAndSaveSchema:
    """Tests for _execute_and_save_schema method."""

    @patch.object(SourceValidationExecutor, "_save_dataframe_as_parquet")
    @patch.object(SourceValidationExecutor, "_get_output_path")
    def test_execute_and_save_schema_success(
        self,
        mock_get_path,
        mock_save,
        mock_source_extractor,
        mock_context,
    ):
        """Test successful schema extraction and save."""
        # Setup mock data
        schema_df = pd.DataFrame(
            {
                "COLUMN_VALIDATED": ["col1", "col2"],
                "DATA_TYPE": ["INTEGER", "VARCHAR"],
            }
        )
        mock_source_extractor.extract_schema_metadata.return_value = schema_df
        mock_get_path.return_value = "/fake/path/schema.parquet"

        executor = SourceValidationExecutor(
            source_extractor=mock_source_extractor,
            context=mock_context,
        )

        # Create mock table context
        mock_table_context = MagicMock()

        executor._execute_and_save_schema(mock_table_context)

        # Verify extractor was called
        mock_source_extractor.extract_schema_metadata.assert_called_once_with(
            table_context=mock_table_context,
            output_handler=mock_context.output_handler,
        )

        # Verify save was called
        mock_save.assert_called_once()

        # Verify output messages
        assert mock_context.output_handler.handle_message.call_count >= 2

    @patch.object(SourceValidationExecutor, "_get_output_path")
    def test_execute_and_save_schema_with_error(
        self,
        mock_get_path,
        mock_source_extractor,
        mock_context,
    ):
        """Test schema extraction with error."""
        # Setup mock to raise error
        mock_source_extractor.extract_schema_metadata.side_effect = Exception(
            "Database error"
        )
        mock_get_path.return_value = "/fake/path/schema.parquet"

        executor = SourceValidationExecutor(
            source_extractor=mock_source_extractor,
            context=mock_context,
        )

        # Create mock table context
        mock_table_context = MagicMock()

        # Should raise exception
        with pytest.raises(Exception, match="Database error"):
            executor._execute_and_save_schema(mock_table_context)


class TestExecuteAndSaveMetrics:
    """Tests for _execute_and_save_metrics method."""

    @patch.object(SourceValidationExecutor, "_save_dataframe_as_parquet")
    @patch.object(SourceValidationExecutor, "_get_output_path")
    def test_execute_and_save_metrics_success(
        self,
        mock_get_path,
        mock_save,
        mock_source_extractor,
        mock_context,
    ):
        """Test successful metrics extraction and save."""
        # Setup mock data
        metrics_df = pd.DataFrame(
            {
                "COLUMN_VALIDATED": ["col1", "col2"],
                "min": [1, 0],
                "max": [100, 50],
            }
        )
        mock_source_extractor.extract_metrics_metadata.return_value = metrics_df
        mock_get_path.return_value = "/fake/path/metrics.parquet"

        executor = SourceValidationExecutor(
            source_extractor=mock_source_extractor,
            context=mock_context,
        )

        # Create mock table context
        mock_table_context = MagicMock()

        executor._execute_and_save_metrics(mock_table_context)

        # Verify extractor was called
        mock_source_extractor.extract_metrics_metadata.assert_called_once_with(
            table_context=mock_table_context,
            output_handler=mock_context.output_handler,
        )

        # Verify save was called
        mock_save.assert_called_once()

        # Verify output messages
        assert mock_context.output_handler.handle_message.call_count >= 2


class TestGenerateSourceTableContext:
    """Tests for _generate_source_table_context method."""

    @patch(
        "snowflake.snowflake_data_validation.executer.source_validation_executor.TableContext"
    )
    def test_generate_source_table_context(
        self,
        mock_table_context_class,
        mock_source_extractor,
        mock_context,
        table_configuration,
        table_column_metadata,
    ):
        """Test table context generation."""
        executor = SourceValidationExecutor(
            source_extractor=mock_source_extractor,
            context=mock_context,
        )

        executor._generate_source_table_context(
            table_configuration, table_column_metadata
        )

        # Verify TableContext was instantiated (not from_table_column_metadata)
        mock_table_context_class.assert_called_once()

        # Verify correct parameters passed to TableContext constructor
        call_kwargs = mock_table_context_class.call_args[1]
        assert (
            call_kwargs["fully_qualified_name"]
            == table_configuration.fully_qualified_name
        )
        assert call_kwargs["database_name"] == table_configuration.source_database
        assert call_kwargs["schema_name"] == table_configuration.source_schema
        assert call_kwargs["platform"] == mock_context.source_platform
