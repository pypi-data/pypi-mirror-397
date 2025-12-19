import pytest
from unittest.mock import MagicMock, patch

from snowflake.snowflake_data_validation.configuration.model.table_configuration import (
    TableConfiguration,
)
from snowflake.snowflake_data_validation.configuration.singleton import Singleton
from snowflake.snowflake_data_validation.utils.row_partitioning_strategy import (
    row_partitioning,
    _get_table_row_count,
    _generate_indexes_collection,
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


def test_get_table_row_count_returns_row_count(mock_connection):
    """Test that row count is correctly extracted from query result."""
    mock_connection.execute_query.return_value = (None, [(500,)])

    result = _get_table_row_count(mock_connection, "db.schema.table")

    assert result == 500
    mock_connection.execute_query.assert_called_once_with(
        "SELECT COUNT(*) FROM db.schema.table"
    )


def test_get_table_row_count_returns_zero_for_empty_table(mock_connection):
    """Test handling of empty table."""
    mock_connection.execute_query.return_value = (None, [(0,)])

    result = _get_table_row_count(mock_connection, "db.schema.empty_table")

    assert result == 0


def test_generate_indexes_collection_four_partitions():
    """Test generating indexes for 4 partitions."""
    result = _generate_indexes_collection(
        table_row_count=200,
        number_of_partitions=4,
        number_of_rows_per_partition=50,
    )

    assert result == "1, 51, 101, 151, 200"


def test_generate_indexes_collection_five_partitions():
    """Test generating indexes for 5 partitions."""
    result = _generate_indexes_collection(
        table_row_count=500,
        number_of_partitions=5,
        number_of_rows_per_partition=100,
    )

    assert result == "1, 101, 201, 301, 401, 500"


def test_generate_partitions_generates_query_and_returns_results(mock_connection):
    """Test that partition query is generated and executed correctly."""
    mock_connection.execute_query.return_value = (None, [(1,), (50,), (100,)])

    result = _generate_partitions(
        connection=mock_connection,
        table_fully_qualified_name="db.schema.table",
        partition_column="ID",
        table_row_count=100,
        number_of_partitions=2,
        number_of_rows_per_partition=50,
    )

    assert result == [(1,), (50,), (100,)]
    mock_connection.execute_query.assert_called_once()

    # Verify the query contains expected elements
    call_args = mock_connection.execute_query.call_args[0][0]
    assert "ID" in call_args
    assert "db.schema.table" in call_args


def test_generate_partitioned_table_last_partition_uses_less_than_or_equal(
    sample_table_configuration,
):
    """Test that the last partition uses <= instead of <."""
    table_partitions = [(10,), (50,), (100,)]

    result = _generate_partitioned_table(
        table_partitions=table_partitions,
        partition_column="ID",
        is_str_partition_column=False,
        table_configuration=sample_table_configuration,
    )

    # First partition uses <
    assert "ID >= 10 AND ID < 50" in result
    # Last partition uses <=
    assert "ID >= 50 AND ID <= 100" in result


def test_generate_partitioned_table_preserves_fully_qualified_name(
    sample_table_configuration,
):
    """Test that the table fully qualified name is preserved in output."""
    table_partitions = [(1,), (100,)]

    result = _generate_partitioned_table(
        table_partitions=table_partitions,
        partition_column="ID",
        is_str_partition_column=False,
        table_configuration=sample_table_configuration,
    )

    assert "test_db.test_schema.test_table" in result


@patch(
    "snowflake.snowflake_data_validation.utils.row_partitioning_strategy.ConnectorFactory"
)
def test_row_partitioning_integration(
    mock_connector_factory, sample_table_configuration
):
    """Test the complete row partitioning flow with mocked dependencies."""
    mock_connection = MagicMock()
    mock_connector_factory.create_connector.return_value = mock_connection

    # Mock row count query
    mock_connection.execute_query.side_effect = [
        (None, [(100,)]),  # Row count query
        (None, [(1,), (51,), (100,)]),  # Partition query
    ]

    mock_credentials = MagicMock()

    result = row_partitioning(
        platform=Platform.SNOWFLAKE,
        credentials_connection=mock_credentials,
        partition_column="ID",
        number_of_partitions=2,
        is_str_partition_column=False,
        table_configuration=sample_table_configuration,
    )

    # Verify the result contains expected partition clauses
    assert "ID >= 1 AND ID < 51" in result
    assert "ID >= 51 AND ID <= 100" in result


@patch(
    "snowflake.snowflake_data_validation.utils.row_partitioning_strategy.ConnectorFactory"
)
def test_row_partitioning_with_string_column(
    mock_connector_factory, sample_table_configuration
):
    """Test row partitioning with string partition column."""
    mock_connection = MagicMock()
    mock_connector_factory.create_connector.return_value = mock_connection

    mock_connection.execute_query.side_effect = [
        (None, [(60,)]),  # Row count
        (None, [("AAA",), ("MMM",), ("ZZZ",)]),  # Partition values
    ]

    mock_credentials = MagicMock()

    result = row_partitioning(
        platform=Platform.SNOWFLAKE,
        credentials_connection=mock_credentials,
        partition_column="CODE",
        number_of_partitions=2,
        is_str_partition_column=True,
        table_configuration=sample_table_configuration,
    )

    # Verify string values are quoted
    assert "CODE >= 'AAA' AND CODE < 'MMM'" in result
    assert "CODE >= 'MMM' AND CODE <= 'ZZZ'" in result
