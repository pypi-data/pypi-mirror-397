CONFIGURATION_FILE_TEMPLATE = """# Auto-generated configuration file
source_platform: {platform}
target_platform: Snowflake
output_directory_path: {output_directory_path}
max_threads: 1
{teradata_database}

source_connection:
{source_connection_details}

target_connection:
  mode: name
  name: default

validation_configuration:
  schema_validation: true
  metrics_validation: true
  row_validation: false

# database_mappings:
  # <DATABASE_SOURCE_NAME_PLACEHOLDER>: <DATABASE_TARGET_NAME_PLACEHOLDER>

# schema_mappings:
  # <SCHEMA_SOURCE_NAME_PLACEHOLDER>: <SCHEMA_TARGET_NAME_PLACEHOLDER>

tables:
{tables_configuration}
"""

TABLE_CONFIGURATION_TEMPLATE = """
  - fully_qualified_name: {database}.{schema}.{table}
    target_name: {target_table}
    use_column_selection_as_exclude_list: false
    column_selection_list: []

"""

TERADATA_TABLE_CONFIGURATION_TEMPLATE = """
  - fully_qualified_name: {schema}.{table}
    target_name: {target_table}
    use_column_selection_as_exclude_list: false
    column_selection_list: []

"""

REDSHIFT_TABLES_QUERY = """
SELECT
    CASE
        WHEN REGEXP_INSTR(tables.table_name, '[^a-zA-Z0-9_$]') = 0
            THEN tables.table_name
        ELSE QUOTE_IDENT(tables.table_name)
    END AS TableName
FROM
    information_schema.tables tables
WHERE
    tables.table_type = 'BASE TABLE'
    AND tables.table_catalog = '{database}'
    AND tables.table_schema = '{schema}'
ORDER BY
    tables.table_name;
"""

SQL_SERVER_TABLES_QUERY = r"""
SELECT
    IIF(
        PATINDEX(N'%[^a-zA-Z0-9\_@#]%', tables.TABLE_NAME) = 0,
        tables.TABLE_NAME,
        QUOTENAME(tables.TABLE_NAME)
        )
        AS TableName
FROM
    INFORMATION_SCHEMA.TABLES tables
WHERE
    tables.TABLE_TYPE = 'BASE TABLE'
    AND tables.TABLE_CATALOG = '{database}'
    AND tables.TABLE_SCHEMA = '{schema}'
ORDER BY
    tables.TABLE_NAME;
"""

TERADATA_TABLES_QUERY = """
SELECT
    CASE
        WHEN REGEXP_SIMILAR(tables.TableName, '.*[^A-Z0-9_].*', 'i') = 0
        THEN tables.TableName
        ELSE '"' || tables.TableName || '"'
    END AS TableName
FROM
    DBC.TablesV tables
WHERE
    tables.TableKind = 'T'
    AND tables.DatabaseName = '{database}'
ORDER BY
    tables.TableName;
"""
