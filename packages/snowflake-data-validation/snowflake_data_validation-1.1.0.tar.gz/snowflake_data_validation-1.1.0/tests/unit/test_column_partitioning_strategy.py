import pytest
from unittest.mock import MagicMock, patch

from snowflake.snowflake_data_validation.configuration.model.table_configuration import (
    TableConfiguration,
)
from snowflake.snowflake_data_validation.configuration.singleton import Singleton
from snowflake.snowflake_data_validation.utils.column_partitioning_strategy import (
    column_partitioning_strategy,
    _get_table_column_name,
    _generate_partitions,
    _generate_partitioned_table,
)
from snowflake.snowflake_data_validation.utils.constants import Platform


@pytest.fixture(autouse=True)
def reset_singletons():
    """Reset singleton instances and TableConfiguration counter before each test."""
    Singleton._instances = {}
    TableConfiguration._id_counter = 0


@pytest.fixture
def sample_table_configuration():
    """Create a sample TableConfiguration for testing."""
    return TableConfiguration(
        fully_qualified_name="test_db.test_schema.test_table",
        use_column_selection_as_exclude_list=False,
        column_selection_list=[],
        column_mappings={},
    )


@pytest.fixture
def mock_connection():
    """Create a mock database connection."""
    return MagicMock()


def test_get_table_column_name_returns_column_names_redshift(mock_connection):
    """Test that column names are correctly extracted for Redshift."""
    mock_connection.execute_query.return_value = (
        None,
        [("ID",), ("NAME",), ("EMAIL",)],
    )

    result = _get_table_column_name(
        Platform.REDSHIFT, mock_connection, "test_db.test_schema.test_table"
    )

    assert result == ["ID", "NAME", "EMAIL"]
    mock_connection.execute_query.assert_called_once()
    call_args = mock_connection.execute_query.call_args[0][0]
    assert "SVV_COLUMNS" in call_args


def test_get_table_column_name_returns_column_names_sqlserver(mock_connection):
    """Test that column names are correctly extracted for SQL Server."""
    mock_connection.execute_query.return_value = (
        None,
        [("COL1",), ("COL2",)],
    )

    result = _get_table_column_name(
        Platform.SQLSERVER, mock_connection, "test_db.test_schema.test_table"
    )

    assert result == ["COL1", "COL2"]
    call_args = mock_connection.execute_query.call_args[0][0]
    assert "INFORMATION_SCHEMA.COLUMNS" in call_args


def test_get_table_column_name_raises_error_when_no_columns(mock_connection):
    """Test that ValueError is raised when no columns are found."""
    mock_connection.execute_query.return_value = (None, [])

    with pytest.raises(ValueError) as exc_info:
        _get_table_column_name(
            Platform.REDSHIFT, mock_connection, "test_db.test_schema.empty_table"
        )

    assert "No columns found for table" in str(exc_info.value)


def test_get_table_column_name_lowercases_table_for_redshift(mock_connection):
    """Test that table name is lowercased for Redshift."""
    mock_connection.execute_query.return_value = (
        None,
        [("ID",)],
    )

    _get_table_column_name(
        Platform.REDSHIFT, mock_connection, "test_db.test_schema.MY_TABLE"
    )

    call_args = mock_connection.execute_query.call_args[0][0]
    assert "my_table" in call_args


def test_get_table_column_name_preserves_case_for_sqlserver(mock_connection):
    """Test that table name case is preserved for SQL Server."""
    mock_connection.execute_query.return_value = (
        None,
        [("ID",)],
    )

    _get_table_column_name(
        Platform.SQLSERVER, mock_connection, "test_db.test_schema.MY_TABLE"
    )

    call_args = mock_connection.execute_query.call_args[0][0]
    assert "MY_TABLE" in call_args


def test_generate_partitions_two_partitions():
    """Test generating 2 partitions from 4 columns."""
    columns = ["COL1", "COL2", "COL3", "COL4"]

    result = _generate_partitions(columns, number_of_partitions=2)

    assert result == [["COL1", "COL2"], ["COL3", "COL4"]]


def test_generate_partitions_three_partitions():
    """Test generating 3 partitions from 6 columns."""
    columns = ["A", "B", "C", "D", "E", "F"]

    result = _generate_partitions(columns, number_of_partitions=3)

    assert result == [["A", "B"], ["C", "D"], ["E", "F"]]


def test_generate_partitions_uneven_split():
    """Test partitioning when columns don't divide evenly."""
    columns = ["COL1", "COL2", "COL3", "COL4", "COL5"]

    result = _generate_partitions(columns, number_of_partitions=2)

    # 5 columns / 2 partitions = ceil(2.5) = 3 columns per partition
    assert result == [["COL1", "COL2", "COL3"], ["COL4", "COL5"]]


def test_generate_partitions_single_partition():
    """Test generating single partition."""
    columns = ["COL1", "COL2", "COL3"]

    result = _generate_partitions(columns, number_of_partitions=1)

    assert result == [["COL1", "COL2", "COL3"]]


def test_generate_partitioned_table_sets_column_selection(sample_table_configuration):
    """Test that partitioned table sets column_selection_list correctly."""
    table_partitions = [["COL1", "COL2"], ["COL3", "COL4"]]

    result = _generate_partitioned_table(
        table_partitions=table_partitions,
        table_configuration=sample_table_configuration,
    )

    assert "COL1" in result
    assert "COL2" in result
    assert "COL3" in result
    assert "COL4" in result


def test_generate_partitioned_table_preserves_fully_qualified_name(
    sample_table_configuration,
):
    """Test that the table fully qualified name is preserved in output."""
    table_partitions = [["COL1"]]

    result = _generate_partitioned_table(
        table_partitions=table_partitions,
        table_configuration=sample_table_configuration,
    )

    assert "test_db.test_schema.test_table" in result


def test_generate_partitioned_table_sets_exclude_list_false(sample_table_configuration):
    """Test that use_column_selection_as_exclude_list is set to False."""
    sample_table_configuration.use_column_selection_as_exclude_list = True
    table_partitions = [["COL1", "COL2"]]

    result = _generate_partitioned_table(
        table_partitions=table_partitions,
        table_configuration=sample_table_configuration,
    )

    assert "use_column_selection_as_exclude_list: False" in result


@patch(
    "snowflake.snowflake_data_validation.utils.column_partitioning_strategy.ConnectorFactory"
)
def test_column_partitioning_strategy_integration(
    mock_connector_factory, sample_table_configuration
):
    """Test the complete column partitioning flow with mocked dependencies."""
    mock_connection = MagicMock()
    mock_connector_factory.create_connector.return_value = mock_connection

    mock_connection.execute_query.return_value = (
        None,
        [("ID",), ("NAME",), ("EMAIL",), ("AGE",)],
    )

    mock_credentials = MagicMock()

    result = column_partitioning_strategy(
        platform=Platform.REDSHIFT,
        credentials_connection=mock_credentials,
        number_of_partitions=2,
        table_configuration=sample_table_configuration,
    )

    # Verify the result contains expected columns in partitions
    assert "ID" in result
    assert "NAME" in result
    assert "EMAIL" in result
    assert "AGE" in result
    assert "test_db.test_schema.test_table" in result
