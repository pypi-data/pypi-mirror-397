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

"""Shared CLI partitioning functions for data validation."""

import logging

import typer

from snowflake.snowflake_data_validation.utils.column_partitioning_strategy import (
    column_partitioning_strategy,
)
from snowflake.snowflake_data_validation.utils.configuration_file_editor import (
    ConfigurationFileEditor,
)
from snowflake.snowflake_data_validation.utils.constants import (
    NEWLINE,
    Platform,
)
from snowflake.snowflake_data_validation.utils.row_partitioning_strategy import (
    row_partitioning,
)


LOGGER = logging.getLogger(__name__)


def run_row_partitioning_helper(platform: Platform) -> None:
    """Run the interactive row partitioning helper for a given platform.

    This function processes each table in the configuration file,
    allowing users to either skip row partitioning or specify row partitioning
    parameters for each table.

    Args:
        platform: The source platform (SQLSERVER, TERADATA, REDSHIFT, etc.)

    """
    platform_name = platform.value.title()

    typer.secho(
        f"Generate a configuration file for {platform_name} row partitioning. "
        "This interactive helper function processes each table in the "
        "configuration file, allowing users to either skip row partitioning or "
        "specify row partitioning parameters for each table.",
        fg=typer.colors.WHITE,
    )

    try:
        configuration_file_path = typer.prompt("Configuration file path", type=str)
        configuration_file_editor = ConfigurationFileEditor(configuration_file_path)
        configuration_file_table_collection = (
            configuration_file_editor.get_table_collection()
        )
        connection_credentials = configuration_file_editor.get_connection_credentials()

        tables = []
        for table_configuration in configuration_file_table_collection:
            apply_partitioning = typer.confirm(
                f"Apply partitioning for {table_configuration.fully_qualified_name}?",
                default=True,
            )

            if not apply_partitioning:
                table = str(table_configuration) + NEWLINE
                tables.append(table)
                continue

            partition_column = typer.prompt(
                f"Write the partition column for "
                f"{table_configuration.fully_qualified_name}",
                type=str,
            )
            is_str_partition_column = typer.confirm(
                f"Is '{partition_column}' column a string type?", default=False
            )
            number_of_partitions = typer.prompt(
                f"Write the number of partitions for "
                f"{table_configuration.fully_qualified_name}",
                type=int,
            )

            table = row_partitioning(
                platform=platform,
                credentials_connection=connection_credentials,
                partition_column=partition_column,
                number_of_partitions=number_of_partitions,
                is_str_partition_column=is_str_partition_column,
                table_configuration=table_configuration,
            )
            tables.append(table)

        tables_str = NEWLINE.join(tables)
        success = configuration_file_editor.add_partitioned_table_configuration(
            tables_str
        )

        if success:
            typer.secho(
                "Table partitioning configuration file generated successfully!",
                fg=typer.colors.GREEN,
            )
            LOGGER.info("Table partitioning configuration file generated successfully.")
        else:
            typer.secho(
                "Failed to generate table partitioning configuration file.",
                fg=typer.colors.RED,
            )
            LOGGER.error("Failed to generate table partitioning configuration file.")

    except Exception as e:
        runtime_error_msg = (
            f"Failed to generate table partitioning configuration file: {e}"
        )
        LOGGER.error(runtime_error_msg)
        typer.secho(runtime_error_msg, fg=typer.colors.RED)


def run_column_partitioning_helper(platform: Platform) -> None:
    """Run the interactive column partitioning helper for a given platform.

    This function processes each table in the configuration file,
    allowing users to either skip column partitioning or specify column
    partitioning parameters for each table.

    Args:
        platform: The source platform (SQLSERVER, TERADATA, REDSHIFT, etc.)

    """
    platform_name = platform.value.title()

    typer.secho(
        f"Generate a configuration file for {platform_name} column partitioning. "
        "This interactive helper function processes each table in the "
        "configuration file, allowing users to either skip column partitioning or "
        "specify column partitioning parameters for each table.",
        fg=typer.colors.WHITE,
    )

    try:
        configuration_file_path = typer.prompt("Configuration file path", type=str)
        configuration_file_editor = ConfigurationFileEditor(configuration_file_path)
        configuration_file_table_collection = (
            configuration_file_editor.get_table_collection()
        )
        connection_credentials = configuration_file_editor.get_connection_credentials()

        tables = []
        for table_configuration in configuration_file_table_collection:
            apply_partitioning = typer.confirm(
                f"Apply column partitioning for {table_configuration.fully_qualified_name}?",
                default=True,
            )

            if not apply_partitioning:
                table = str(table_configuration) + NEWLINE
                tables.append(table)
                continue

            number_of_partitions = typer.prompt(
                f"Write the number of partitions for "
                f"{table_configuration.fully_qualified_name}",
                type=int,
            )

            table = column_partitioning_strategy(
                platform=platform,
                credentials_connection=connection_credentials,
                number_of_partitions=number_of_partitions,
                table_configuration=table_configuration,
            )
            tables.append(table)

        tables_str = NEWLINE.join(tables)
        success = configuration_file_editor.add_partitioned_table_configuration(
            tables_str
        )

        if success:
            typer.secho(
                "Column partitioning configuration file generated successfully!",
                fg=typer.colors.GREEN,
            )
            LOGGER.info(
                "Column partitioning configuration file generated successfully."
            )
        else:
            typer.secho(
                "Failed to generate table partitioning configuration file.",
                fg=typer.colors.RED,
            )
            LOGGER.error("Failed to generate column partitioning configuration file.")

    except Exception as e:
        runtime_error_msg = (
            f"Failed to generate column partitioning configuration file: {e}"
        )
        LOGGER.error(runtime_error_msg)
        typer.secho(runtime_error_msg, fg=typer.colors.RED)
