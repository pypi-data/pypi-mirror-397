import copy
import math

from snowflake.snowflake_data_validation.configuration.model.connection_types import (
    Connection,
)
from snowflake.snowflake_data_validation.configuration.model.table_configuration import (
    TableConfiguration,
)
from snowflake.snowflake_data_validation.utils.connector_factory import ConnectorFactory
from snowflake.snowflake_data_validation.utils.constants import NEWLINE, Platform


GET_PARTITIONS_TEMPLATE = """
WITH DV_PARTITIONS AS (
    SELECT
        ROW_NUMBER() OVER (ORDER BY {partition_column}) AS ROW_NUMBER_IDX,
        {partition_column}
    FROM {table_fully_qualified_name}
)
SELECT {partition_column}
FROM DV_PARTITIONS
WHERE ROW_NUMBER_IDX IN ({indexes_collection})"""


def row_partitioning(
    platform: Platform,
    credentials_connection: Connection,
    partition_column: str,
    number_of_partitions: int,
    is_str_partition_column: bool,
    table_configuration: TableConfiguration,
) -> str:
    """Generate partitioned table configurations based on the specified partitioning strategy.

    Args:
        platform (Platform): The source platform.
        credentials_connection (Connection): The connection details for the source platform.
        partition_column (str): The column used for partitioning.
        number_of_partitions (int): The number of partitions to create.
        is_str_partition_column (bool): Indicates if the partition column is of string type.
        table_configuration (TableConfiguration): The table configuration details.

    Returns:
        str: The generated partitioned table configurations.

    """
    connection = ConnectorFactory.create_connector(platform, credentials_connection)
    table_row_count = _get_table_row_count(
        connection, table_configuration.fully_qualified_name
    )
    number_of_rows_per_partition = math.ceil(table_row_count / number_of_partitions)

    table_partitions = _generate_partitions(
        connection=connection,
        table_fully_qualified_name=table_configuration.fully_qualified_name,
        partition_column=partition_column,
        table_row_count=table_row_count,
        number_of_partitions=number_of_partitions,
        number_of_rows_per_partition=number_of_rows_per_partition,
    )

    partitioned_table_config = _generate_partitioned_table(
        table_partitions=table_partitions,
        partition_column=partition_column,
        is_str_partition_column=is_str_partition_column,
        table_configuration=table_configuration,
    )

    return partitioned_table_config


def _get_table_row_count(
    connection: Connection, table_fully_qualified_name: str
) -> int:
    result = connection.execute_query(
        f"SELECT COUNT(*) FROM {table_fully_qualified_name}"
    )
    _, metadata_info = result
    table_row_count = metadata_info[0][0]
    return table_row_count


def _generate_indexes_collection(
    table_row_count: int,
    number_of_partitions: int,
    number_of_rows_per_partition: int,
) -> str:
    index = 1
    indexes = [index]
    for partition in range(number_of_partitions):
        if partition == number_of_partitions - 1:
            index = table_row_count
        else:
            index += number_of_rows_per_partition
        indexes.append(index)
    return ", ".join(map(str, indexes))


def _generate_partitions(
    connection: Connection,
    table_fully_qualified_name: str,
    partition_column: str,
    table_row_count: int,
    number_of_partitions: int,
    number_of_rows_per_partition: int,
):

    indexes_collection = _generate_indexes_collection(
        table_row_count, number_of_partitions, number_of_rows_per_partition
    )

    query = GET_PARTITIONS_TEMPLATE.format(
        table_fully_qualified_name=table_fully_qualified_name,
        partition_column=partition_column,
        indexes_collection=indexes_collection,
    )
    result = connection.execute_query(query)
    _, metadata_info = result
    return metadata_info


def _generate_partitioned_table(
    table_partitions: list[tuple],
    partition_column: str,
    is_str_partition_column: bool,
    table_configuration: TableConfiguration,
) -> str:
    tables = []
    partition_template = (
        "{partition_column} >= '{start_value}' AND {partition_column} < '{end_value}'"
        if is_str_partition_column
        else "{partition_column} >= {start_value} AND {partition_column} < {end_value}"
    )

    for i in range(len(table_partitions) - 1):
        start_value = table_partitions[i][0]
        end_value = table_partitions[i + 1][0]

        where_clause = partition_template.format(
            partition_column=partition_column,
            start_value=start_value,
            end_value=end_value,
        )

        # Use <= for the last partition
        if i == len(table_partitions) - 2:
            where_clause = where_clause.replace("<", "<=")

        target_where_clause = where_clause
        for column_source in table_configuration.column_mappings.keys():
            target_where_clause = target_where_clause.replace(
                column_source, table_configuration.column_mappings[column_source]
            )

        new_table_configuration = copy.deepcopy(table_configuration)
        new_table_configuration.where_clause = where_clause
        new_table_configuration.target_where_clause = target_where_clause

        tables.append(str(new_table_configuration) + NEWLINE)

    return NEWLINE.join(tables)
