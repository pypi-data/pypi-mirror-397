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

"""Main CLI application for Snowflake Data Validation."""

import logging
import sys

import typer

from snowflake.snowflake_data_validation.__version__ import __version__
from snowflake.snowflake_data_validation.redshift.redshift_cli import redshift_app
from snowflake.snowflake_data_validation.snowflake.snowflake_cli import snowflake_app
from snowflake.snowflake_data_validation.sqlserver.sqlserver_cli import sqlserver_app
from snowflake.snowflake_data_validation.teradata.teradata_cli import teradata_app
from snowflake.snowflake_data_validation.utils.logging_config import setup_logging


LOGGER = logging.getLogger(__name__)

# Only set up logging if this is not a help or version command
# Check for help and version flags in command line arguments
_is_help_command = any(
    arg in ("--help", "-h", "help", "--version", "-v") for arg in sys.argv
)

if not _is_help_command:
    # Set up logging for all CLI commands
    setup_logging()
    LOGGER.info("Starting Snowflake Data Validation CLI application")


def version_callback(value: bool) -> None:
    """Display the version of the package."""
    if value:
        typer.echo(f"snowflake-data-validation {__version__}")
        raise typer.Exit()


# Create main data validation app
data_validation_app = typer.Typer(
    add_completion=False,
    pretty_exceptions_show_locals=False,
    invoke_without_command=True,
)


@data_validation_app.callback(invoke_without_command=True)
def main(
    ctx: typer.Context,
    version: bool = typer.Option(
        None,
        "--version",
        "-v",
        help="Show the application version and exit.",
        callback=version_callback,
        is_eager=True,
    ),
) -> None:
    """Snowflake Data Validation CLI - Validate data migrations to Snowflake."""
    # If no subcommand is provided, show help
    if ctx.invoked_subcommand is None and not version:
        typer.echo(ctx.get_help())
        raise typer.Exit()


# Add dialect-specific subcommands
data_validation_app.add_typer(
    sqlserver_app, name="sqlserver", help="SQL Server dialect commands"
)

data_validation_app.add_typer(
    redshift_app, name="redshift", help="Redshift dialect commands"
)
data_validation_app.add_typer(
    snowflake_app, name="snowflake", help="Snowflake dialect commands"
)
data_validation_app.add_typer(
    teradata_app, name="teradata", help="Teradata dialect commands"
)

if not _is_help_command:
    LOGGER.info("Snowflake Data Validation CLI application initialized")
