import os

from datetime import datetime

from snowflake.snowflake_data_validation.configuration.model.connection_types import (
    Connection,
)
from snowflake.snowflake_data_validation.utils.connector_factory import ConnectorFactory
from snowflake.snowflake_data_validation.utils.constants import Platform
from snowflake.snowflake_data_validation.utils.templates.configuration_file_templates import (
    CONFIGURATION_FILE_TEMPLATE,
    REDSHIFT_TABLES_QUERY,
    SQL_SERVER_TABLES_QUERY,
    TABLE_CONFIGURATION_TEMPLATE,
    TERADATA_TABLE_CONFIGURATION_TEMPLATE,
    TERADATA_TABLES_QUERY,
)


tables_query_template = {
    Platform.REDSHIFT: REDSHIFT_TABLES_QUERY,
    Platform.SQLSERVER: SQL_SERVER_TABLES_QUERY,
    Platform.TERADATA: TERADATA_TABLES_QUERY,
}


def generate_configuration_file(
    platform: Platform,
    credentials_connection: Connection,
    database: str,
    schema: str,
    output_path: str,
) -> bool:
    """Generate a configuration file for Snowflake Data Validation."""
    if not os.path.exists(path=output_path):
        raise Exception("Given output path does not exist")

    if not os.path.isdir(s=output_path):
        raise Exception("Given output path is not a directory")

    if not os.access(path=output_path, mode=os.W_OK):
        raise PermissionError("Given output path is not writable")

    datetime_str = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    file_output_path = os.path.join(output_path, f"configuration_{datetime_str}.yaml")

    connection = ConnectorFactory.create_connector(platform, credentials_connection)

    get_all_tables_query_template = tables_query_template[platform]
    tables_query = get_all_tables_query_template.format(
        database=database, schema=schema
    )
    result = connection.execute_query(query=tables_query)
    tables = _digest_query_result(result=result)
    tables_configuration_section = _generate_tables_configuration(
        platform=platform, database=database, schema=schema, tables=tables
    )
    configuration_file_generated = _generate_configuration_file(
        platform=platform,
        credentials_connection=credentials_connection,
        tables_configuration_section=tables_configuration_section,
        output_path=output_path,
        file_output_path=file_output_path,
    )

    return configuration_file_generated


def _digest_query_result(result: any) -> list[str]:
    """Digest query result into a list of table names."""
    _, metadata_info = result
    return metadata_info


def _generate_tables_configuration(
    platform: Platform, database: str, schema: str, tables: list[str]
) -> str:
    tables_configuration_section = ""

    for table in tables:
        if table is None or table[0] is None:
            continue

        escaped_table = _escape_quotes(table[0])
        target_table = _convert_to_snowflake_identifier(table[0])

        if platform == Platform.TERADATA:
            table_configuration = TERADATA_TABLE_CONFIGURATION_TEMPLATE.format(
                schema=schema, table=escaped_table, target_table=target_table
            )
        else:
            table_configuration = TABLE_CONFIGURATION_TEMPLATE.format(
                database=database,
                schema=schema,
                table=escaped_table,
                target_table=target_table,
            )

        tables_configuration_section += table_configuration

    return tables_configuration_section


def _generate_configuration_file(
    platform: Platform,
    credentials_connection: Connection,
    tables_configuration_section: str,
    output_path: str,
    file_output_path: str,
) -> bool:
    configuration_file_content = CONFIGURATION_FILE_TEMPLATE.format(
        platform=platform.value,
        teradata_database=(
            f"target_database: {credentials_connection.database}"
            if platform == Platform.TERADATA
            else ""
        ),
        output_directory_path=output_path,
        source_connection_details=credentials_connection.configuration_file_connection_string(),
        tables_configuration=tables_configuration_section,
    )

    with open(file_output_path, "w") as config_file:
        config_file.write(configuration_file_content)

    return os.path.exists(path=file_output_path)


def _escape_quotes(identifier: str) -> str:
    """
    Escapes double quotes in the given identifier string.

    Args:
        identifier (str): The identifier string to escape.

    Returns:
        str: The identifier string with double quotes escaped.

    """
    if identifier and identifier.startswith('"') and identifier.endswith('"'):
        return f'\\"{identifier[1:-1]}\\"'

    return identifier


def _convert_to_snowflake_identifier(identifier: str) -> str:
    """
    Convert the given identifier to Snowflake format.

    Args:
        identifier (str): The identifier string to convert.

    Returns:
        str: The identifier string in Snowflake format.

    """
    has_quotes = identifier and identifier.startswith('"') and identifier.endswith('"')
    has_brackets = (
        identifier and identifier.startswith("[") and identifier.endswith("]")
    )

    if has_quotes or has_brackets:
        return f'\\"{identifier[1:-1]}\\"'

    return identifier.upper()
