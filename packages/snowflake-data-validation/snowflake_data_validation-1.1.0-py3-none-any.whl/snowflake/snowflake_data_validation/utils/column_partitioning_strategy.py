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
from snowflake.snowflake_data_validation.utils.helper import Helper


REDSHIFT_COUNT_COLUMNS_QUERY_TEMPLATE = """SELECT
    column_name AS NAME
FROM
    SVV_COLUMNS
WHERE
    table_name = '{table_name}'
    AND table_schema = '{schema_name}'
ORDER BY
    column_name;"""


SQL_SERVER_COUNT_COLUMNS_QUERY_TEMPLATE = """SELECT
    COLUMN_NAME AS NAME
FROM
    INFORMATION_SCHEMA.COLUMNS
WHERE
    TABLE_NAME = '{table_name}'
    AND TABLE_SCHEMA = '{schema_name}'
ORDER BY
    COLUMN_NAME;"""


TERADATA_COUNT_COLUMNS_QUERY_TEMPLATE = """SELECT
    TRIM(ColumnName) AS NAME
FROM
    DBC.Columns
WHERE
    TRIM(TableName) = '{table_name}'
    AND TRIM(DatabaseName) = '{schema_name}'
ORDER BY
    ColumnName;
"""

columns_query_template = {
    Platform.REDSHIFT: REDSHIFT_COUNT_COLUMNS_QUERY_TEMPLATE,
    Platform.SQLSERVER: SQL_SERVER_COUNT_COLUMNS_QUERY_TEMPLATE,
    Platform.TERADATA: TERADATA_COUNT_COLUMNS_QUERY_TEMPLATE,
}


def column_partitioning_strategy(
    platform: Platform,
    credentials_connection: Connection,
    number_of_partitions: int,
    table_configuration: TableConfiguration,
) -> str:
    """Generate partitioned table configurations based on the specified partitioning strategy.

    Args:
        platform (Platform): The database platform.
        credentials_connection (Connection): The connection credentials.
        number_of_partitions (int): The number of partitions to create.
        table_configuration (TableConfiguration): The table configuration.

    Returns:
        str: The generated partitioned table configurations.

    """
    connection = ConnectorFactory.create_connector(platform, credentials_connection)
    table_column_names = _get_table_column_name(
        platform, connection, table_configuration.fully_qualified_name
    )

    table_partitions = _generate_partitions(
        table_column_names=table_column_names,
        number_of_partitions=number_of_partitions,
    )

    partitioned_table_config = _generate_partitioned_table(
        table_partitions=table_partitions,
        table_configuration=table_configuration,
    )

    return partitioned_table_config


def _get_table_column_name(
    platform: Platform, connection: Connection, table_fully_qualified_name: str
) -> list[str]:
    _, schema, table = Helper.get_decomposed_fully_qualified_name(
        table_fully_qualified_name
    )

    if platform == Platform.REDSHIFT:
        table = table.lower()

    query_template = columns_query_template[platform]

    query = query_template.format(
        table_name=table,
        schema_name=schema,
    )

    result = connection.execute_query(query)
    _, metadata_info = result

    if len(metadata_info) == 0:
        raise ValueError(f"No columns found for table {table_fully_qualified_name}.")

    table_column_names = [row[0] for row in metadata_info]
    return table_column_names


def _generate_partitions(
    table_column_names: list[str], number_of_partitions: int
) -> list[list[str]]:
    number_of_columns_per_partition = math.ceil(
        len(table_column_names) / number_of_partitions
    )
    partitions = []
    for i in range(0, len(table_column_names), number_of_columns_per_partition):
        partitions.append(table_column_names[i : i + number_of_columns_per_partition])

    return partitions


def _generate_partitioned_table(
    table_partitions: list[list[str]],
    table_configuration: TableConfiguration,
):
    tables = []
    for partition_column_collection in table_partitions:
        new_table_configuration = copy.deepcopy(table_configuration)
        new_table_configuration.use_column_selection_as_exclude_list = False
        new_table_configuration.column_selection_list = partition_column_collection

        tables.append(str(new_table_configuration) + NEWLINE)

    return NEWLINE.join(tables)
