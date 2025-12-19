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

import logging
import os

from pathlib import Path

import toml
import typer

import snowflake.connector

from snowflake.connector.errors import DatabaseError, ProgrammingError
from snowflake.snowflake_data_validation.connector.connector_base import (
    ConnectorBase as BaseConnector,
)
from snowflake.snowflake_data_validation.utils.constants import (
    COLUMN_VALUES_CONCATENATED_ERROR_SNOWFLAKE,
    CONNECTION_NOT_ESTABLISHED,
    CREDENTIALS_CONNECTION_MODE,
    DEFAULT_CONNECTION_MODE,
    EXCEED_MAX_STRING_LENGHT_SNOWFLAKE_ERROR_CODE,
    FAILED_TO_EXECUTE_QUERY,
    FAILED_TO_EXECUTE_STATEMENT,
    INVALID_CONNECTION_MODE,
    NAME_CONNECTION_MODE,
    TABLE_NOT_FOUND_ERROR_CODE_SNOWFLAKE,
)
from snowflake.snowflake_data_validation.utils.logging_utils import log


LOGGER = logging.getLogger(__name__)


class ConnectorSnowflake(BaseConnector):
    """A class to manage connections and queries to a Snowflake database."""

    @log
    def __init__(self) -> None:
        """Initialize the SnowflakeConnector class."""
        super().__init__()
        self.connection: snowflake.connector.SnowflakeConnection | None = None

    @log(log_args=False)
    def connect(
        self,
        mode: str = DEFAULT_CONNECTION_MODE,
        connection_name: str = "",
        account: str = "",
        username: str = "",
        database: str = "",
        schema: str = "",
        warehouse: str = "",
        role: str = "",
        password: str = "",
        authenticator: str = "",
        private_key_file: str | None = None,
        private_key_passphrase: str | None = None,
        max_attempts: int = 3,
        delay_seconds: float = 1.0,
        delay_multiplier: float = 2.0,
    ) -> None:
        """Establish a connection to the Snowflake database.

        Args:
            mode (str): The mode of connection. Defaults to "default".
                        - "default": Connects using the default session configuration.
                        - "name": Connects using a named connection configuration.
                        - "credentials": Connects using the provided credentials.
            connection_name (str): The name of the connection configuration to use
                when mode is "name". Defaults to an empty string.
            account (str): The Snowflake account name.
            username (str): The username for the Snowflake account.
            database (str): The name of the database to connect to.
            schema (str): The schema within the database to use.
            warehouse (str): The name of the warehouse to use.
            role (str): The role to assume for the session.
            password (str): The password for the Snowflake account.
            authenticator (str): The authenticator to use for the Snowflake connection.
            private_key_file (Optional[str]): The path to the private key file for authentication.
            private_key_passphrase (Optional[str]): The passphrase for the private key file, if required.
            max_attempts (int): Maximum number of connection attempts. Defaults to 3.
            delay_seconds (float): Initial delay between retries in seconds. Defaults to 1.0.
            delay_multiplier (float): Multiplier for exponential backoff. Defaults to 2.0.

        Returns:
            None: Returns a Snowflake session object.

        Raises:
            ConnectionError: If the connection cannot be established.
            typer.BadParameter: If invalid parameters are provided.
            ImportError: If Snowflake connector dependencies are missing.

        """
        try:
            self.connect_with_retry(
                self._attempt_connection_and_verify,
                max_attempts,
                delay_seconds,
                delay_multiplier,
                self._internal_connect,
                mode,
                connection_name,
                account,
                username,
                database,
                schema,
                warehouse,
                role,
                password,
                authenticator,
                private_key_file,
                private_key_passphrase,
            )

        except ImportError as e:
            LOGGER.error("Failed to import Snowflake dependencies: %s", str(e))
            raise ImportError(
                f"Failed to import Snowflake dependencies: {e}. "
                "Please ensure snowflake-connector-python is installed."
            ) from e
        except typer.BadParameter:
            raise
        except ConnectionError:
            raise
        except Exception as e:
            LOGGER.error("Failed to establish Snowflake connection: %s", str(e))
            raise ConnectionError(
                f"Failed to establish Snowflake connection: {e}"
            ) from e

    def _load_named_connection(self, connection_name: str) -> dict:
        """Load connection parameters from config.toml or connections.toml file.

        Args:
            connection_name: Name of the connection in the config file

        Returns:
            Dictionary of connection parameters

        Raises:
            typer.BadParameter: If connection not found or file doesn't exist

        """
        # Check standard locations for config.toml (new) and connections.toml (legacy)
        config_paths = [
            Path.home() / ".snowflake" / "config.toml",
            Path.home() / ".snowflake" / "connections.toml",
            Path.cwd() / "config.toml",
            Path.cwd() / "connections.toml",
        ]

        for config_path in config_paths:
            if config_path.exists():
                try:
                    config = toml.load(config_path)
                    # Check for nested structure (config.toml format): connections.name
                    if (
                        "connections" in config
                        and connection_name in config["connections"]
                    ):
                        LOGGER.debug(
                            "Loaded connection '%s' from %s (nested)",
                            connection_name,
                            config_path,
                        )
                        return config["connections"][connection_name]
                    # Check for flat structure (legacy format): name
                    elif connection_name in config:
                        LOGGER.debug(
                            "Loaded connection '%s' from %s (flat)",
                            connection_name,
                            config_path,
                        )
                        return config[connection_name]
                except Exception as e:
                    LOGGER.warning("Failed to load config from %s: %s", config_path, e)

        raise typer.BadParameter(
            f"Connection '{connection_name}' not found in config.toml or connections.toml. "
            f"Searched locations: {', '.join(str(p) for p in config_paths)}"
        )

    def _get_default_connection_params(self) -> dict:
        """Get default connection parameters from environment or config.

        Returns:
            Dictionary of connection parameters

        Raises:
            typer.BadParameter: If default connection cannot be determined

        """
        # Try to load default connection from config.toml (new) or connections.toml (legacy)
        try:
            config_paths = [
                Path.home() / ".snowflake" / "config.toml",
                Path.home() / ".snowflake" / "connections.toml",
            ]
            for config_path in config_paths:
                if config_path.exists():
                    config = toml.load(config_path)

                    # Check for default_connection_name (config.toml format)
                    if "default_connection_name" in config and "connections" in config:
                        default_name = config["default_connection_name"]
                        if default_name in config["connections"]:
                            LOGGER.debug("Using default connection: %s", default_name)
                            return config["connections"][default_name]

                    # Check for nested connections structure
                    if "connections" in config and config["connections"]:
                        # Look for 'default' connection or use first available
                        if "default" in config["connections"]:
                            return config["connections"]["default"]
                        else:
                            # Use first available connection
                            first_conn = next(iter(config["connections"].keys()))
                            LOGGER.debug(
                                "Using first available connection: %s", first_conn
                            )
                            return config["connections"][first_conn]

                    # Fall back to flat structure (legacy)
                    elif "default" in config:
                        return config["default"]
                    elif config:
                        # Use first available connection
                        first_conn = next(iter(config.keys()))
                        LOGGER.debug("Using first available connection: %s", first_conn)
                        return config[first_conn]
        except Exception as e:
            LOGGER.debug("Could not load default connection from config: %s", e)

        # Fall back to environment variables if available
        env_params = {}

        # Map common environment variables
        env_mapping = {
            "SNOWFLAKE_ACCOUNT": "account",
            "SNOWFLAKE_USER": "user",
            "SNOWFLAKE_PASSWORD": "password",
            "SNOWFLAKE_DATABASE": "database",
            "SNOWFLAKE_SCHEMA": "schema",
            "SNOWFLAKE_WAREHOUSE": "warehouse",
            "SNOWFLAKE_ROLE": "role",
            "SNOWFLAKE_AUTHENTICATOR": "authenticator",
        }

        for env_var, param in env_mapping.items():
            value = os.getenv(env_var)
            if value:
                env_params[param] = value

        if env_params:
            LOGGER.debug("Using connection parameters from environment variables")
            return env_params

        raise typer.BadParameter(
            "No default connection found. Please provide a config.toml or connections.toml file "
            "at ~/.snowflake/config.toml or ~/.snowflake/connections.toml or set environment variables "
            "(SNOWFLAKE_ACCOUNT, SNOWFLAKE_USER, etc.)"
        )

    def _internal_connect(
        self,
        mode: str = DEFAULT_CONNECTION_MODE,
        connection_name: str = "",
        account: str = "",
        username: str = "",
        database: str = "",
        schema: str = "",
        warehouse: str = "",
        role: str = "",
        password: str = "",
        authenticator: str = "",
        private_key_file: str | None = None,
        private_key_passphrase: str | None = None,
    ) -> None:
        """Establish the actual connection. Default implementation without retry logic.

        Args:
            mode (str): The mode of connection. Defaults to "default".
            connection_name (str): The name of the connection configuration to use
                when mode is "name". Defaults to an empty string.
            account (str): The Snowflake account name.
            username (str): The username for the Snowflake account.
            database (str): The name of the database to connect to.
            schema (str): The schema within the database to use.
            warehouse (str): The name of the warehouse to use.
            role (str): The role to assume for the session.
            password (str): The password for the Snowflake account.
            authenticator (str): The authenticator to use for the Snowflake connection.
            private_key_file (Optional[str]): The path to the private key file for authentication.
            private_key_passphrase (Optional[str]): The passphrase for the private key file, if required.

        Raises:
            ConnectionError: If the connection cannot be established.
            typer.BadParameter: If invalid parameters are provided.

        """
        connection_config = {}

        if mode == DEFAULT_CONNECTION_MODE:
            # Use default connection from config or environment
            connection_config = self._get_default_connection_params()

        elif mode == NAME_CONNECTION_MODE:
            if not connection_name:
                raise typer.BadParameter("Connection name is required for 'name' mode")
            # Load named connection from connections.toml
            connection_config = self._load_named_connection(connection_name)

        elif mode == CREDENTIALS_CONNECTION_MODE:
            if not all([account, username, database, warehouse]):
                raise typer.BadParameter(
                    "Account, username, database, and warehouse are required for 'credentials' mode"
                )

            # Build connection configuration
            connection_config = {
                "account": account,
                "user": username,
                "database": database,
                "warehouse": warehouse,
            }

            if schema:
                connection_config["schema"] = schema
            if role:
                connection_config["role"] = role
            if password:
                connection_config["password"] = password
            if authenticator:
                connection_config["authenticator"] = authenticator
            if private_key_file:
                # Load private key for key-pair authentication
                try:
                    from cryptography.hazmat.primitives import serialization

                    with open(private_key_file, "rb") as key_file:
                        if private_key_passphrase:
                            passphrase = private_key_passphrase.encode()
                        else:
                            passphrase = None

                        private_key = serialization.load_pem_private_key(
                            key_file.read(),
                            password=passphrase,
                        )

                        pkb = private_key.private_bytes(
                            encoding=serialization.Encoding.DER,
                            format=serialization.PrivateFormat.PKCS8,
                            encryption_algorithm=serialization.NoEncryption(),
                        )
                        connection_config["private_key"] = pkb
                except Exception as e:
                    LOGGER.error("Failed to load private key: %s", e)
                    raise typer.BadParameter(
                        f"Failed to load private key from {private_key_file}: {e}"
                    ) from e

        else:
            raise typer.BadParameter(
                message=f"{INVALID_CONNECTION_MODE}. Selected mode: {mode}. "
                f"Valid modes are 'default', 'name', or 'credentials'."
            )

        # Establish connection using snowflake.connector
        LOGGER.debug("Connecting to Snowflake with mode: %s", mode)
        self.connection = snowflake.connector.connect(**connection_config)
        LOGGER.debug("Snowflake connection established successfully")

    def _verify_connection(self) -> None:
        """Verify the connection by executing a simple test query.

        Raises:
            ConnectionError: If connection verification fails

        """
        try:
            LOGGER.debug("Verifying Snowflake connection")
            if self.connection is None:
                raise ConnectionError("Connection is None")

            cursor = self.connection.cursor()
            try:
                cursor.execute("SELECT 1")
                cursor.fetchone()
                LOGGER.debug("Snowflake connection verified successfully")
            finally:
                cursor.close()

        except Exception as e:
            LOGGER.error("Failed to verify Snowflake connection: %s", str(e))
            self.connection = None
            raise ConnectionError(f"Failed to verify Snowflake connection: {e}") from e

    @log
    def execute_statement(self, statement: str) -> bool:
        """Execute a SQL statement that doesn't return results.

        Args:
            statement: SQL statement to execute

        Returns:
            True if successful

        Raises:
            Exception: If connection not established or execution fails

        """
        if self.connection is None:
            LOGGER.error("Database connection not established")
            raise Exception(CONNECTION_NOT_ESTABLISHED)

        try:
            LOGGER.debug("Executing Snowflake statement: %s", statement)
            cursor = self.connection.cursor()
            try:
                cursor.execute(statement)
                LOGGER.debug("Statement executed successfully")
                return True
            finally:
                cursor.close()
        except Exception as e:
            LOGGER.error("Failed to execute statement: %s", str(e))
            raise Exception(
                FAILED_TO_EXECUTE_STATEMENT.format(statement=statement)
            ) from e

    @log
    def execute_query_no_return(self, query: str) -> None:
        """Execute a query without expecting results (for side effects).

        Args:
            query: SQL query to execute

        Raises:
            Exception: If connection not established or execution fails

        """
        if self.connection is None:
            LOGGER.error("Database connection not established")
            raise Exception(CONNECTION_NOT_ESTABLISHED)

        try:
            LOGGER.debug("Executing Snowflake query: %s", query)
            cursor = self.connection.cursor()
            try:
                cursor.execute(query)
                LOGGER.debug("Query executed successfully, returned 0 rows")
            finally:
                cursor.close()
        except Exception as e:
            error_message = str(e)

            is_concatenation_error = (
                EXCEED_MAX_STRING_LENGHT_SNOWFLAKE_ERROR_CODE in error_message
            )
            if is_concatenation_error:
                error_message = COLUMN_VALUES_CONCATENATED_ERROR_SNOWFLAKE
                LOGGER.error(error_message)
                raise Exception(error_message) from e

            LOGGER.error("Failed to execute query: %s", error_message)
            raise Exception(FAILED_TO_EXECUTE_QUERY) from e

    @log
    def execute_query(self, query: str) -> list[dict]:
        """Execute a given SQL query using the Snowflake connector and return the results.

        Args:
            query (str): The SQL query to be executed.

        Returns:
            list[dict]: A list of dictionaries containing the query results with column names as keys.

        Raises:
            Exception: If the connector is not established or if the query execution fails.

        """
        if self.connection is None:
            LOGGER.error("Database connection not established")
            raise Exception(CONNECTION_NOT_ESTABLISHED)

        try:
            cursor = self.connection.cursor(snowflake.connector.DictCursor)
            try:
                cursor.execute(query)
                results = cursor.fetchall()
                LOGGER.debug(
                    "Query executed successfully, returned %d rows", len(results)
                )
                return results
            finally:
                cursor.close()

        except ProgrammingError as e:
            # ProgrammingError is the connector equivalent of SnowparkSQLException
            if e.errno == TABLE_NOT_FOUND_ERROR_CODE_SNOWFLAKE:
                LOGGER.error(
                    "Snowflake table not found or you do not have access to it: %s",
                    str(e),
                )
            LOGGER.error("Failed to execute query: %s", str(e))
            raise Exception(FAILED_TO_EXECUTE_QUERY) from e
        except DatabaseError as e:
            LOGGER.error("Failed to execute query: %s", str(e))
            raise Exception(FAILED_TO_EXECUTE_QUERY) from e
        except Exception as e:
            LOGGER.error("Failed to execute query: %s", str(e))
            raise Exception(FAILED_TO_EXECUTE_QUERY) from e

    @log
    def close(self) -> None:
        """Close the connection to the Snowflake database."""
        if self.connection:
            try:
                self.connection.close()
                LOGGER.info("Snowflake connection closed successfully")
            except Exception as e:
                LOGGER.warning("Error closing connection: %s", str(e))
        else:
            LOGGER.debug("No active connection to close")
