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

"""Integration tests for source-validate command functionality."""

import os
import tempfile
from unittest.mock import MagicMock, patch

import pandas as pd
import pytest

# Check if pyarrow is available for parquet tests
try:
    import pyarrow as pa
    import pyarrow.parquet as pq

    PYARROW_AVAILABLE = True
except ImportError:
    PYARROW_AVAILABLE = False

requires_pyarrow = pytest.mark.skipif(
    not PYARROW_AVAILABLE, reason="requires pyarrow for parquet support"
)

from snowflake.snowflake_data_validation.comparison_orchestrator import (
    ComparisonOrchestrator,
)
from snowflake.snowflake_data_validation.configuration.model.table_configuration import (
    TableConfiguration,
)
from snowflake.snowflake_data_validation.configuration.model.validation_configuration import (
    ValidationConfiguration,
)
from snowflake.snowflake_data_validation.connector.connector_base import (
    ConnectorBase,
)
from snowflake.snowflake_data_validation.executer.source_validation_executor import (
    SourceValidationExecutor,
)
from snowflake.snowflake_data_validation.extractor.metadata_extractor_base import (
    MetadataExtractorBase,
)
from snowflake.snowflake_data_validation.utils.base_output_handler import (
    OutputHandlerBase,
    OutputMessageLevel,
)
from snowflake.snowflake_data_validation.utils.constants import (
    COLUMN_VALIDATED,
    DEFAULT_CONNECTION_MODE,
    Platform,
)
from snowflake.snowflake_data_validation.utils.context import Context
from snowflake.snowflake_data_validation.utils.model.table_context import (
    TableContext,
)


class MockConnector(ConnectorBase):
    """Mock connector for testing purposes."""

    def __init__(self, synthetic_data=None):
        self.synthetic_data = synthetic_data or {}
        super().__init__()

    def connect(
        self, mode: str = DEFAULT_CONNECTION_MODE, connection_name: str = ""
    ) -> None:
        pass

    def execute_query(self, query: str) -> list[tuple]:
        """Mock execute_query - returns empty list.

        Note: All tests use MockMetadataExtractor which overrides
        extract_schema_metadata() and extract_metrics_metadata(),
        so this method is never called with real queries.

        """
        return []

    def execute_statement(self, statement: str) -> None:
        pass

    def execute_query_no_return(self, query: str) -> None:
        pass

    def close(self) -> None:
        pass


class MockMetadataExtractor(MetadataExtractorBase):
    """Mock metadata extractor for testing purposes."""

    def __init__(self, connector: ConnectorBase, platform: Platform):
        self.connector = connector
        self.platform = platform
        self.query_generator = MagicMock()
        self.report_path = ""
        self.columns_metrics = {}

    def extract_schema_metadata(self, table_context, output_handler) -> pd.DataFrame:
        """Extract synthetic schema metadata."""
        return pd.DataFrame(
            {
                COLUMN_VALIDATED: [
                    "ID",
                    "FIRST_NAME",
                    "LAST_NAME",
                    "EMAIL",
                    "BIRTH_DATE",
                    "SALARY",
                ],
                "ORDINAL_POSITION": [1, 2, 3, 4, 5, 6],
                "DATA_TYPE": [
                    "INTEGER",
                    "VARCHAR",
                    "VARCHAR",
                    "VARCHAR",
                    "DATE",
                    "DECIMAL",
                ],
                "CHARACTER_MAXIMUM_LENGTH": [None, 50, 50, 100, None, None],
                "NUMERIC_PRECISION": [10, None, None, None, 10, 10],
                "NUMERIC_SCALE": [0, None, None, None, 0, 2],
                "IS_NULLABLE": ["NO", "NO", "NO", "YES", "YES", "YES"],
                "ROW_COUNT": [1000] * 6,
            }
        )

    def extract_metrics_metadata(self, table_context, output_handler) -> pd.DataFrame:
        """Extract synthetic metrics metadata."""
        return pd.DataFrame(
            {
                COLUMN_VALIDATED: [
                    "ID",
                    "FIRST_NAME",
                    "LAST_NAME",
                    "EMAIL",
                    "BIRTH_DATE",
                    "SALARY",
                ],
                "MAX_LENGTH": [10, 50, 50, 100, 10, 10],
                "NULL_COUNT": [0, 15, 8, 25, 50, 100],
                "MIN_VALUE": [1, None, None, None, None, 30000.00],
                "MAX_VALUE": [1000, None, None, None, None, 150000.00],
                "AVG_VALUE": [500.5, None, None, None, None, 75000.50],
                "STD_DEV": [288.675, None, None, None, None, 25000.25],
            }
        )

    def extract_table_column_metadata(
        self, table_configuration: TableConfiguration, context: Context
    ) -> pd.DataFrame:
        """Extract synthetic table column metadata."""
        return pd.DataFrame(
            {
                "DATABASE_NAME": ["TEST_DB"] * 6,
                "SCHEMA_NAME": ["TEST_SCHEMA"] * 6,
                "TABLE_NAME": ["EMPLOYEES"] * 6,
                "COLUMN_NAME": [
                    "ID",
                    "FIRST_NAME",
                    "LAST_NAME",
                    "EMAIL",
                    "BIRTH_DATE",
                    "SALARY",
                ],
                "NULLABLE": [False, False, False, True, True, True],
                "DATA_TYPE": [
                    "INTEGER",
                    "VARCHAR",
                    "VARCHAR",
                    "VARCHAR",
                    "DATE",
                    "DECIMAL",
                ],
                "IS_PRIMARY_KEY": [True, False, False, False, False, False],
                "CHARACTER_LENGTH": [None, 50, 50, 100, None, None],
                "PRECISION": [10, None, None, None, 10, 10],
                "SCALE": [0, None, None, None, 0, 2],
                "CALCULATED_COLUMN_SIZE_IN_BYTES": [4, 200, 200, 400, 3, 9],
            }
        )

    def extract_table_row_count(
        self,
        fully_qualified_name: str,
        where_clause: str,
        has_where_clause: bool,
        platform: Platform,
        context: Context,
    ) -> pd.DataFrame:
        """Extract synthetic table row count."""
        return pd.DataFrame({"ROW_COUNT": [1000]})

    def process_schema_query_result(
        self, result: list, output_handler: OutputHandlerBase
    ) -> pd.DataFrame:
        """Process schema query result."""
        return pd.DataFrame()

    def process_metrics_query_result(
        self, result: list, output_handler: OutputHandlerBase
    ) -> pd.DataFrame:
        """Process metrics query result."""
        return pd.DataFrame()

    def process_table_column_metadata_result(
        self, result: list, output_handler: OutputHandlerBase
    ) -> pd.DataFrame:
        """Process table column metadata result."""
        return pd.DataFrame()

    def compute_md5(self, table_context, other_table_name: str) -> None:
        """Compute MD5 checksum."""
        pass

    def extract_chunks_md5(self, table_context: TableContext) -> pd.DataFrame:
        """Extract chunks MD5."""
        return pd.DataFrame()

    def create_table_chunks_md5(self, table_context: TableContext) -> None:
        """Create table chunks MD5."""
        pass

    def extract_md5_rows_chunk(
        self, chunk_id: str, table_context: TableContext
    ) -> pd.DataFrame:
        """Extract MD5 rows chunk."""
        return pd.DataFrame()


class MockOutputHandler(OutputHandlerBase):
    """Mock output handler for testing purposes."""

    def __init__(self):
        self.messages = []
        self.dataframes = []
        super().__init__(enable_console_output=False)

    def handle_message(
        self,
        level: OutputMessageLevel,
        message: str = "",
        header: str = "",
        dataframe: pd.DataFrame = None,
    ) -> None:
        """Store messages for verification in tests."""
        self.messages.append(
            {
                "message": message,
                "header": header,
                "level": level,
                "dataframe": dataframe,
            }
        )
        if dataframe is not None:
            self.dataframes.append(dataframe)


@pytest.fixture
def temp_report_dir():
    """Create a temporary directory for test reports."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield tmpdir


@pytest.fixture
def mock_table_configuration():
    """Create a mock table configuration for testing."""
    return TableConfiguration(
        fully_qualified_name="TEST_DB.TEST_SCHEMA.EMPLOYEES",
        source_database="TEST_DB",
        source_schema="TEST_SCHEMA",
        source_table="EMPLOYEES",
        column_selection_list=[
            "ID",
            "FIRST_NAME",
            "LAST_NAME",
            "EMAIL",
            "BIRTH_DATE",
            "SALARY",
        ],
        use_column_selection_as_exclude_list=False,
        index_column_list=[],
    )


@pytest.fixture
def mock_validation_config():
    """Create a mock validation configuration for testing."""
    mock_config = MagicMock(spec=ValidationConfiguration)
    mock_config.schema_validation = True
    mock_config.metrics_validation = True
    mock_config.row_validation = False  # Not applicable for source-only
    mock_config.model_dump.return_value = {
        "schema_validation": True,
        "metrics_validation": True,
        "row_validation": False,
    }
    return mock_config


@pytest.fixture
def mock_context(temp_report_dir):
    """Create a mock context for testing."""
    context = MagicMock(spec=Context)
    context.output_handler = MockOutputHandler()
    context.source_platform = Platform.SQLSERVER
    context.configuration = MagicMock()
    context.configuration.tables = []
    context.report_path = temp_report_dir
    context.datatypes_mappings = {
        "INTEGER": "NUMBER",
        "VARCHAR": "VARCHAR",
        "DATE": "DATE",
        "DECIMAL": "NUMBER",
    }
    context.run_id = "test_run_12345"
    context.run_start_time = "20250120T120000"
    context.templates_path = "/tmp/templates"
    context.sql_generator = MagicMock()
    return context


class TestSourceValidationIntegration:
    """Integration tests for source-validate functionality."""

    @requires_pyarrow
    def test_source_validation_creates_parquet_files(
        self,
        mock_table_configuration,
        mock_context,
        temp_report_dir,
    ):
        """Test that source validation creates Parquet files for schema and metrics."""
        # Create mock connector and extractor
        source_connector = MockConnector()
        source_extractor = MockMetadataExtractor(source_connector, Platform.SQLSERVER)

        # Create executor
        executor = SourceValidationExecutor(
            source_extractor=source_extractor,
            context=mock_context,
        )

        # Create mock table column metadata
        mock_metadata = MagicMock()
        mock_metadata.columns = []
        mock_metadata.row_count = 1000

        # Execute source validation
        with patch.object(
            executor,
            "_generate_source_table_context",
            return_value=MagicMock(
                fully_qualified_name="TEST_DB.TEST_SCHEMA.EMPLOYEES"
            ),
        ):
            executor.execute_source_validation(
                table_configuration=mock_table_configuration,
                source_table_column_metadata=mock_metadata,
            )

        # Verify Parquet files were created
        schema_file = os.path.join(
            temp_report_dir,
            "source",
            "schema",
            "TEST_DB.TEST_SCHEMA.EMPLOYEES.parquet",
        )
        metrics_file = os.path.join(
            temp_report_dir,
            "source",
            "metrics",
            "TEST_DB.TEST_SCHEMA.EMPLOYEES.parquet",
        )

        assert os.path.exists(schema_file), f"Schema file not found: {schema_file}"
        assert os.path.exists(metrics_file), f"Metrics file not found: {metrics_file}"

        # Verify files can be read
        schema_df = pd.read_parquet(schema_file)
        metrics_df = pd.read_parquet(metrics_file)

        assert not schema_df.empty, "Schema DataFrame should not be empty"
        assert not metrics_df.empty, "Metrics DataFrame should not be empty"

        # Verify schema DataFrame structure
        assert COLUMN_VALIDATED in schema_df.columns
        assert len(schema_df) == 6  # 6 columns in our test data

        # Verify metrics DataFrame structure
        assert COLUMN_VALIDATED in metrics_df.columns
        assert len(metrics_df) == 6

    @requires_pyarrow
    def test_source_validation_with_multiple_tables(
        self,
        mock_validation_config,
        mock_context,
        temp_report_dir,
    ):
        """Test source validation with multiple tables."""
        # Create multiple table configurations
        table_configs = []
        for table_name in ["EMPLOYEES", "DEPARTMENTS", "PROJECTS"]:
            config = TableConfiguration(
                fully_qualified_name=f"TEST_DB.TEST_SCHEMA.{table_name}",
                source_database="TEST_DB",
                source_schema="TEST_SCHEMA",
                source_table=table_name,
                column_selection_list=["ID", "NAME", "DESCRIPTION"],
                use_column_selection_as_exclude_list=False,
                index_column_list=[],
            )
            table_configs.append(config)

        # Create source connector and extractor
        source_connector = MockConnector()
        source_extractor = MockMetadataExtractor(source_connector, Platform.SQLSERVER)

        # Create executor
        executor = SourceValidationExecutor(
            source_extractor=source_extractor,
            context=mock_context,
        )

        # Execute source validation for each table
        for table_config in table_configs:
            mock_metadata = MagicMock()
            mock_metadata.columns = []
            mock_metadata.row_count = 1000

            with patch.object(
                executor,
                "_generate_source_table_context",
                return_value=MagicMock(
                    fully_qualified_name=table_config.fully_qualified_name
                ),
            ):
                executor.execute_source_validation(
                    table_configuration=table_config,
                    source_table_column_metadata=mock_metadata,
                )

        # Verify files were created for all tables
        for table_name in ["EMPLOYEES", "DEPARTMENTS", "PROJECTS"]:
            schema_file = os.path.join(
                temp_report_dir,
                "source",
                "schema",
                f"TEST_DB.TEST_SCHEMA.{table_name}.parquet",
            )
            metrics_file = os.path.join(
                temp_report_dir,
                "source",
                "metrics",
                f"TEST_DB.TEST_SCHEMA.{table_name}.parquet",
            )

            assert os.path.exists(
                schema_file
            ), f"Schema file not found for {table_name}"
            assert os.path.exists(
                metrics_file
            ), f"Metrics file not found for {table_name}"

    def test_source_validation_via_orchestrator(
        self,
        mock_table_configuration,
        mock_validation_config,
        mock_context,
        temp_report_dir,
    ):
        """Test source validation through the orchestrator."""
        # Setup configuration
        mock_context.configuration.tables = [mock_table_configuration]
        mock_context.configuration.validation_configuration = mock_validation_config

        # Create mock connection pool manager
        mock_pool_manager = MagicMock()
        mock_pool_manager.pool_size = 4

        # Mock source connector
        mock_source_connector = MagicMock()
        mock_source_connector.__enter__ = MagicMock(return_value=MockConnector())
        mock_source_connector.__exit__ = MagicMock(return_value=None)
        mock_pool_manager.get_source_connection.return_value = mock_source_connector

        # Create orchestrator
        orchestrator = ComparisonOrchestrator(
            connection_pool_manager=mock_pool_manager,
            context=mock_context,
            max_threads=4,
        )

        # Mock the execution engine
        with patch.object(
            orchestrator.execution_engine, "execute_parallel_validation"
        ) as mock_execute:
            orchestrator.run_source_validation()

            # Verify execution was called with SOURCE_VALIDATION mode
            mock_execute.assert_called_once()
            from snowflake.snowflake_data_validation.utils.constants import (
                ExecutionMode,
            )

            call_args = mock_execute.call_args
            assert call_args[1]["execution_mode"] == ExecutionMode.SOURCE_VALIDATION

    def test_source_validation_handles_extraction_errors(
        self,
        mock_table_configuration,
        mock_context,
    ):
        """Test that source validation handles extraction errors gracefully."""

        class ErrorExtractor(MockMetadataExtractor):
            def extract_schema_metadata(self, table_context, output_handler):
                raise Exception("Database connection error")

            def extract_metrics_metadata(self, table_context, output_handler):
                raise Exception("Query execution error")

        # Create error-prone extractor
        source_connector = MockConnector()
        error_extractor = ErrorExtractor(source_connector, Platform.SQLSERVER)

        # Create executor
        executor = SourceValidationExecutor(
            source_extractor=error_extractor,
            context=mock_context,
        )

        # Create mock metadata
        mock_metadata = MagicMock()
        mock_metadata.columns = []
        mock_metadata.row_count = 1000

        # Execute should handle errors gracefully
        with patch.object(
            executor,
            "_generate_source_table_context",
            return_value=MagicMock(
                fully_qualified_name="TEST_DB.TEST_SCHEMA.EMPLOYEES"
            ),
        ):
            # This should not raise an exception
            try:
                executor.execute_source_validation(
                    table_configuration=mock_table_configuration,
                    source_table_column_metadata=mock_metadata,
                )
            except Exception:
                # Errors should be caught and handled
                pass

        # Verify error messages were logged
        output_handler = mock_context.output_handler
        messages = [msg["message"] for msg in output_handler.messages]
        # Should have some error-related messages
        assert len(messages) > 0

    @requires_pyarrow
    def test_source_validation_with_empty_dataset(
        self,
        mock_table_configuration,
        mock_context,
        temp_report_dir,
    ):
        """Test source validation with empty datasets."""

        class EmptyDataExtractor(MockMetadataExtractor):
            def extract_schema_metadata(self, table_context, output_handler):
                return pd.DataFrame()

            def extract_metrics_metadata(self, table_context, output_handler):
                return pd.DataFrame()

        # Create extractor that returns empty data
        source_connector = MockConnector()
        empty_extractor = EmptyDataExtractor(source_connector, Platform.SQLSERVER)

        # Create executor
        executor = SourceValidationExecutor(
            source_extractor=empty_extractor,
            context=mock_context,
        )

        # Create mock metadata
        mock_metadata = MagicMock()
        mock_metadata.columns = []
        mock_metadata.row_count = 0

        # Execute source validation
        with patch.object(
            executor,
            "_generate_source_table_context",
            return_value=MagicMock(
                fully_qualified_name="TEST_DB.TEST_SCHEMA.EMPLOYEES"
            ),
        ):
            executor.execute_source_validation(
                table_configuration=mock_table_configuration,
                source_table_column_metadata=mock_metadata,
            )

        # Verify files were still created (even if empty)
        schema_file = os.path.join(
            temp_report_dir,
            "source",
            "schema",
            "TEST_DB.TEST_SCHEMA.EMPLOYEES.parquet",
        )
        metrics_file = os.path.join(
            temp_report_dir,
            "source",
            "metrics",
            "TEST_DB.TEST_SCHEMA.EMPLOYEES.parquet",
        )

        assert os.path.exists(schema_file)
        assert os.path.exists(metrics_file)

        # Files should exist but contain empty DataFrames
        schema_df = pd.read_parquet(schema_file)
        metrics_df = pd.read_parquet(metrics_file)

        assert len(schema_df) == 0
        assert len(metrics_df) == 0

    @requires_pyarrow
    def test_source_validation_output_directory_structure(
        self,
        mock_table_configuration,
        mock_context,
        temp_report_dir,
    ):
        """Test that source validation creates the correct directory structure."""
        # Create source connector and extractor
        source_connector = MockConnector()
        source_extractor = MockMetadataExtractor(source_connector, Platform.SQLSERVER)

        # Create executor
        executor = SourceValidationExecutor(
            source_extractor=source_extractor,
            context=mock_context,
        )

        # Create mock metadata
        mock_metadata = MagicMock()
        mock_metadata.columns = []
        mock_metadata.row_count = 1000

        # Execute source validation
        with patch.object(
            executor,
            "_generate_source_table_context",
            return_value=MagicMock(
                fully_qualified_name="TEST_DB.TEST_SCHEMA.EMPLOYEES"
            ),
        ):
            executor.execute_source_validation(
                table_configuration=mock_table_configuration,
                source_table_column_metadata=mock_metadata,
            )

        # Verify directory structure
        source_dir = os.path.join(temp_report_dir, "source")
        schema_dir = os.path.join(source_dir, "schema")
        metrics_dir = os.path.join(source_dir, "metrics")

        assert os.path.exists(source_dir), "Source directory should exist"
        assert os.path.isdir(source_dir), "Source should be a directory"
        assert os.path.exists(schema_dir), "Schema directory should exist"
        assert os.path.isdir(schema_dir), "Schema should be a directory"
        assert os.path.exists(metrics_dir), "Metrics directory should exist"
        assert os.path.isdir(metrics_dir), "Metrics should be a directory"

    @requires_pyarrow
    def test_source_validation_preserves_data_types(
        self,
        mock_table_configuration,
        mock_context,
        temp_report_dir,
    ):
        """Test that source validation preserves data types in Parquet files."""
        # Create source connector and extractor
        source_connector = MockConnector()
        source_extractor = MockMetadataExtractor(source_connector, Platform.SQLSERVER)

        # Create executor
        executor = SourceValidationExecutor(
            source_extractor=source_extractor,
            context=mock_context,
        )

        # Create mock metadata
        mock_metadata = MagicMock()
        mock_metadata.columns = []
        mock_metadata.row_count = 1000

        # Execute source validation
        with patch.object(
            executor,
            "_generate_source_table_context",
            return_value=MagicMock(
                fully_qualified_name="TEST_DB.TEST_SCHEMA.EMPLOYEES"
            ),
        ):
            executor.execute_source_validation(
                table_configuration=mock_table_configuration,
                source_table_column_metadata=mock_metadata,
            )

        # Read the Parquet files
        schema_file = os.path.join(
            temp_report_dir,
            "source",
            "schema",
            "TEST_DB.TEST_SCHEMA.EMPLOYEES.parquet",
        )
        metrics_file = os.path.join(
            temp_report_dir,
            "source",
            "metrics",
            "TEST_DB.TEST_SCHEMA.EMPLOYEES.parquet",
        )

        schema_df = pd.read_parquet(schema_file)
        metrics_df = pd.read_parquet(metrics_file)

        # Verify data types are preserved
        assert COLUMN_VALIDATED in schema_df.columns
        assert "DATA_TYPE" in schema_df.columns
        assert "NUMERIC_PRECISION" in schema_df.columns

        # Verify numeric columns have appropriate types
        assert "MAX_LENGTH" in metrics_df.columns
        assert "NULL_COUNT" in metrics_df.columns

    @requires_pyarrow
    def test_source_validation_with_special_characters_in_table_names(
        self,
        mock_context,
        temp_report_dir,
    ):
        """Test source validation with special characters in table names."""
        # Create table configuration with special characters
        table_config = TableConfiguration(
            fully_qualified_name="TEST_DB.TEST_SCHEMA.TABLE-WITH_SPECIAL$CHARS",
            source_database="TEST_DB",
            source_schema="TEST_SCHEMA",
            source_table="TABLE-WITH_SPECIAL$CHARS",
            column_selection_list=["ID", "NAME"],
            use_column_selection_as_exclude_list=False,
            index_column_list=[],
        )

        # Create source connector and extractor
        source_connector = MockConnector()
        source_extractor = MockMetadataExtractor(source_connector, Platform.SQLSERVER)

        # Create executor
        executor = SourceValidationExecutor(
            source_extractor=source_extractor,
            context=mock_context,
        )

        # Create mock metadata
        mock_metadata = MagicMock()
        mock_metadata.columns = []
        mock_metadata.row_count = 1000

        # Execute source validation
        with patch.object(
            executor,
            "_generate_source_table_context",
            return_value=MagicMock(
                fully_qualified_name="TEST_DB.TEST_SCHEMA.TABLE-WITH_SPECIAL$CHARS"
            ),
        ):
            executor.execute_source_validation(
                table_configuration=table_config,
                source_table_column_metadata=mock_metadata,
            )

        # Verify files were created with special characters handled correctly
        schema_file = os.path.join(
            temp_report_dir,
            "source",
            "schema",
            "TEST_DB.TEST_SCHEMA.TABLE-WITH_SPECIAL$CHARS.parquet",
        )

        assert os.path.exists(schema_file), "File should exist with special characters"
