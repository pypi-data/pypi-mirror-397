import pytest

from snowflake.snowflake_data_validation.configuration.model.table_configuration import (
    TableConfiguration,
)
from snowflake.snowflake_data_validation.utils.configuration_file_editor import (
    ConfigurationFileEditor,
)
from snowflake.snowflake_data_validation.utils.row_partitioning_strategy import (
    _generate_indexes_collection,
    _generate_partitioned_table,
)


@pytest.fixture
def sample_table_configuration():
    """Create a sample TableConfiguration for testing."""
    return TableConfiguration(
        fully_qualified_name="test_db.test_schema.test_table",
        use_column_selection_as_exclude_list=False,
        column_selection_list=[],
        column_mappings={},
    )


def test_two_partitions():
    """Test generating WHERE clause for 2 partitions."""
    result = _generate_indexes_collection(
        table_row_count=100,
        number_of_partitions=2,
        number_of_rows_per_partition=50,
    )

    assert "1, 51, 100" == result


def test_three_partitions():
    """Test generating WHERE clause for 3 partitions."""
    result = _generate_indexes_collection(
        table_row_count=99,
        number_of_partitions=3,
        number_of_rows_per_partition=33,
    )

    assert "1, 34, 67, 99" == result


def test_single_partition():
    """Test generating WHERE clause for 1 partition."""
    result = _generate_indexes_collection(
        table_row_count=50,
        number_of_partitions=1,
        number_of_rows_per_partition=50,
    )

    assert "1, 50" == result


def test_numeric_partition_column(sample_table_configuration):
    """Test generating partitions for numeric partition column."""
    table_partitions = [(1,), (100,), (200,)]

    result = _generate_partitioned_table(
        table_partitions=table_partitions,
        partition_column="ID",
        is_str_partition_column=False,
        table_configuration=sample_table_configuration,
    )

    assert "ID >= 1 AND ID < 100" in result
    assert "ID >= 100 AND ID <= 200" in result


def test_string_partition_column(sample_table_configuration):
    """Test generating partitions for string partition column."""
    table_partitions = [("A",), ("M",), ("Z",)]

    result = _generate_partitioned_table(
        table_partitions=table_partitions,
        partition_column="NAME",
        is_str_partition_column=True,
        table_configuration=sample_table_configuration,
    )

    assert "NAME >= 'A' AND NAME < 'M'" in result
    assert "NAME >= 'M' AND NAME <= 'Z'" in result


def test_column_mappings_applied():
    """Test that column mappings are applied to target where clause."""
    table_config = TableConfiguration(
        fully_qualified_name="test_db.test_schema.test_table",
        use_column_selection_as_exclude_list=False,
        column_selection_list=[],
        column_mappings={"SOURCE_COL": "TARGET_COL"},
    )
    table_partitions = [(1,), (100,)]

    result = _generate_partitioned_table(
        table_partitions=table_partitions,
        partition_column="SOURCE_COL",
        is_str_partition_column=False,
        table_configuration=table_config,
    )

    # Source where clause should use SOURCE_COL
    assert "SOURCE_COL >= 1" in result
    # Target where clause should use TARGET_COL
    assert "TARGET_COL >= 1" in result


def test_multiple_partitions_output(sample_table_configuration):
    """Test that multiple partitions generate multiple table configurations."""
    table_partitions = [(0,), (100,), (200,), (300,)]

    result = _generate_partitioned_table(
        table_partitions=table_partitions,
        partition_column="ID",
        is_str_partition_column=False,
        table_configuration=sample_table_configuration,
    )

    # Should generate 3 partitions (n-1 from partition boundaries)
    assert "ID >= 0 AND ID < 100" in result
    assert "ID >= 100 AND ID < 200" in result
    assert "ID >= 200 AND ID <= 300" in result
