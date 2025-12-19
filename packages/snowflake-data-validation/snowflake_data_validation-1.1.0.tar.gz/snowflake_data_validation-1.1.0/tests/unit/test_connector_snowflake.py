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

"""Tests for ConnectorSnowflake."""

import pytest
from unittest.mock import Mock, patch
from snowflake.snowflake_data_validation.snowflake.connector.connector_snowflake import (
    ConnectorSnowflake,
)
from snowflake.snowflake_data_validation.utils.constants import (
    CONNECTION_NOT_ESTABLISHED,
    CREDENTIALS_CONNECTION_MODE,
    DEFAULT_CONNECTION_MODE,
    FAILED_TO_EXECUTE_QUERY,
    INVALID_CONNECTION_MODE,
    NAME_CONNECTION_MODE,
)
from snowflake.snowflake_data_validation.configuration.singleton import Singleton


@pytest.fixture(autouse=True)
def reset_singleton():
    """Clear singleton instances before and after each test."""
    Singleton._instances = {}
    yield
    Singleton._instances = {}


class TestConnectorSnowflake:
    """Test cases for ConnectorSnowflake."""

    def setup_method(self):
        """Set up test fixtures."""
        self.connector = ConnectorSnowflake()

    def test_init(self):
        """Test ConnectorSnowflake initialization."""
        assert self.connector.connection is None

    @patch(
        "snowflake.snowflake_data_validation.snowflake.connector.connector_snowflake.snowflake.connector.connect"
    )
    @patch(
        "snowflake.snowflake_data_validation.snowflake.connector.connector_snowflake.toml"
    )
    @patch(
        "snowflake.snowflake_data_validation.snowflake.connector.connector_snowflake.Path"
    )
    def test_connect_default_mode_success(
        self, mock_path_class, mock_toml, mock_connect
    ):
        """Test successful connection in default mode."""
        mock_connection = Mock()
        mock_cursor = Mock()
        mock_connection.cursor.return_value = mock_cursor
        mock_cursor.fetchall.return_value = [(1,)]
        mock_connect.return_value = mock_connection

        # Mock Path to return a path that exists
        mock_config_path = Mock()
        mock_config_path.exists.return_value = True
        mock_config_path.__truediv__ = Mock(return_value=mock_config_path)

        mock_home_path = Mock()
        mock_home_path.__truediv__ = Mock(return_value=mock_config_path)

        mock_path_class.home.return_value = mock_home_path

        # Mock default connection in config.toml
        mock_toml.load.return_value = {
            "default_connection_name": "default",
            "connections": {
                "default": {
                    "account": "test_account",
                    "user": "test_user",
                    "password": "test_password",
                }
            },
        }

        self.connector.connect(mode=DEFAULT_CONNECTION_MODE)

        mock_connect.assert_called_once()
        mock_connection.cursor.assert_called()
        mock_cursor.execute.assert_called_with("SELECT 1")
        assert self.connector.connection == mock_connection

    @patch(
        "snowflake.snowflake_data_validation.snowflake.connector.connector_snowflake.snowflake.connector.connect"
    )
    @patch(
        "snowflake.snowflake_data_validation.snowflake.connector.connector_snowflake.toml"
    )
    @patch(
        "snowflake.snowflake_data_validation.snowflake.connector.connector_snowflake.Path"
    )
    def test_connect_name_mode_success(self, mock_path_class, mock_toml, mock_connect):
        """Test successful connection in name mode."""
        mock_connection = Mock()
        mock_cursor = Mock()
        mock_connection.cursor.return_value = mock_cursor
        mock_cursor.fetchall.return_value = [(1,)]
        mock_connect.return_value = mock_connection

        # Mock Path to return a path that exists and supports / operator
        mock_config_path = Mock()
        mock_config_path.exists.return_value = True
        mock_config_path.__truediv__ = Mock(
            return_value=mock_config_path
        )  # Chain returns itself

        mock_home_path = Mock()
        mock_home_path.__truediv__ = Mock(return_value=mock_config_path)

        mock_path_class.home.return_value = mock_home_path
        mock_path_class.cwd.return_value = mock_home_path  # cwd also needs to work

        # Mock config file
        mock_toml.load.return_value = {
            "connections": {
                "test_connection": {
                    "account": "test_account",
                    "user": "test_user",
                    "password": "test_password",
                }
            }
        }

        self.connector.connect(
            mode=NAME_CONNECTION_MODE, connection_name="test_connection"
        )

        mock_connect.assert_called_once()
        mock_connection.cursor.assert_called()
        mock_cursor.execute.assert_called_with("SELECT 1")
        assert self.connector.connection == mock_connection

    def test_connect_name_mode_missing_connection_name(self):
        """Test connection in name mode with missing connection name."""
        with pytest.raises(ConnectionError) as exc_info:
            self.connector.connect(mode=NAME_CONNECTION_MODE)

        assert "Connection name is required for 'name' mode" in str(exc_info.value)

    @patch(
        "snowflake.snowflake_data_validation.snowflake.connector.connector_snowflake.snowflake.connector.connect"
    )
    def test_connect_credentials_mode_success(self, mock_connect):
        """Test successful connection in credentials mode."""
        mock_connection = Mock()
        mock_cursor = Mock()
        mock_connection.cursor.return_value = mock_cursor
        mock_cursor.fetchall.return_value = [(1,)]
        mock_connect.return_value = mock_connection

        self.connector.connect(
            mode=CREDENTIALS_CONNECTION_MODE,
            account="test_account",
            username="test_user",
            database="test_db",
            warehouse="test_wh",
            schema="test_schema",
            role="test_role",
            password="test_pass",
            authenticator="snowflake",
        )

        expected_config = {
            "account": "test_account",
            "user": "test_user",
            "database": "test_db",
            "warehouse": "test_wh",
            "schema": "test_schema",
            "role": "test_role",
            "password": "test_pass",
            "authenticator": "snowflake",
        }

        mock_connect.assert_called_once_with(**expected_config)
        mock_connection.cursor.assert_called()
        mock_cursor.execute.assert_called_with("SELECT 1")
        assert self.connector.connection == mock_connection

    def test_connect_credentials_mode_missing_required_params(self):
        """Test connection in credentials mode with missing required parameters."""
        with pytest.raises(ConnectionError) as exc_info:
            self.connector.connect(
                mode=CREDENTIALS_CONNECTION_MODE,
                account="test_account",
                username="test_user",
                # Missing database and warehouse
                max_attempts=1,
                delay_seconds=0.01,
                delay_multiplier=1.0,
            )

        assert (
            "Account, username, database, and warehouse are required for 'credentials' mode"
            in str(exc_info.value)
        )

    def test_connect_invalid_mode(self):
        """Test connection with invalid mode."""
        with pytest.raises(ConnectionError) as exc_info:
            self.connector.connect(
                mode="invalid_mode",
                max_attempts=1,
                delay_seconds=0.01,
                delay_multiplier=1.0,
            )

        assert INVALID_CONNECTION_MODE in str(exc_info.value)
        assert "invalid_mode" in str(exc_info.value)

    @patch(
        "snowflake.snowflake_data_validation.snowflake.connector.connector_snowflake.snowflake.connector.connect"
    )
    @patch(
        "snowflake.snowflake_data_validation.snowflake.connector.connector_snowflake.toml"
    )
    @patch(
        "snowflake.snowflake_data_validation.snowflake.connector.connector_snowflake.Path"
    )
    def test_connect_connection_verification_fails(
        self, mock_path_class, mock_toml, mock_connect
    ):
        """Test connection when verification query fails."""
        # Mock Path to return a path that exists
        mock_config_path = Mock()
        mock_config_path.exists.return_value = True
        mock_config_path.__truediv__ = Mock(return_value=mock_config_path)

        mock_home_path = Mock()
        mock_home_path.__truediv__ = Mock(return_value=mock_config_path)

        mock_path_class.home.return_value = mock_home_path

        # Mock default connection
        mock_toml.load.return_value = {
            "default_connection_name": "default",
            "connections": {
                "default": {
                    "account": "test_account",
                    "user": "test_user",
                    "password": "test_password",
                }
            },
        }

        mock_connection = Mock()
        mock_cursor = Mock()
        mock_connection.cursor.return_value = mock_cursor
        mock_cursor.execute.side_effect = Exception("Connection test failed")
        mock_connect.return_value = mock_connection

        with pytest.raises(ConnectionError) as exc_info:
            # Use fast retry parameters for testing
            self.connector.connect(
                mode=DEFAULT_CONNECTION_MODE,
                max_attempts=1,
                delay_seconds=0.01,
                delay_multiplier=1.0,
            )

        assert "Failed to establish connection after" in str(exc_info.value)
        assert self.connector.connection is None

    @patch(
        "snowflake.snowflake_data_validation.snowflake.connector.connector_snowflake.snowflake.connector.connect"
    )
    @patch(
        "snowflake.snowflake_data_validation.snowflake.connector.connector_snowflake.toml"
    )
    @patch(
        "snowflake.snowflake_data_validation.snowflake.connector.connector_snowflake.Path"
    )
    def test_connect_import_error(self, mock_path_class, mock_toml, mock_connect):
        """Test connection when Snowflake dependencies are missing."""
        # Mock Path to return a path that exists
        mock_config_path = Mock()
        mock_config_path.exists.return_value = True
        mock_config_path.__truediv__ = Mock(return_value=mock_config_path)

        mock_home_path = Mock()
        mock_home_path.__truediv__ = Mock(return_value=mock_config_path)

        mock_path_class.home.return_value = mock_home_path

        # Mock default connection
        mock_toml.load.return_value = {
            "default_connection_name": "default",
            "connections": {
                "default": {
                    "account": "test_account",
                    "user": "test_user",
                    "password": "test_password",
                }
            },
        }

        mock_connect.side_effect = ImportError("No module named 'snowflake'")

        with pytest.raises(ConnectionError) as exc_info:
            # Use fast retry parameters for testing
            self.connector.connect(
                mode=DEFAULT_CONNECTION_MODE,
                max_attempts=1,
                delay_seconds=0.01,
                delay_multiplier=1.0,
            )

        assert "No module named 'snowflake'" in str(exc_info.value)

    @patch(
        "snowflake.snowflake_data_validation.snowflake.connector.connector_snowflake.snowflake.connector.connect"
    )
    @patch(
        "snowflake.snowflake_data_validation.snowflake.connector.connector_snowflake.toml"
    )
    @patch(
        "snowflake.snowflake_data_validation.snowflake.connector.connector_snowflake.Path"
    )
    def test_connect_generic_exception(self, mock_path_class, mock_toml, mock_connect):
        """Test connection when generic exception occurs."""
        # Mock Path to return a path that exists
        mock_config_path = Mock()
        mock_config_path.exists.return_value = True
        mock_config_path.__truediv__ = Mock(return_value=mock_config_path)

        mock_home_path = Mock()
        mock_home_path.__truediv__ = Mock(return_value=mock_config_path)

        mock_path_class.home.return_value = mock_home_path

        # Mock default connection
        mock_toml.load.return_value = {
            "default_connection_name": "default",
            "connections": {
                "default": {
                    "account": "test_account",
                    "user": "test_user",
                    "password": "test_password",
                }
            },
        }

        mock_connect.side_effect = Exception("Generic error")

        with pytest.raises(ConnectionError) as exc_info:
            # Use fast retry parameters for testing
            self.connector.connect(
                mode=DEFAULT_CONNECTION_MODE,
                max_attempts=1,
                delay_seconds=0.01,
                delay_multiplier=1.0,
            )

        assert "Generic error" in str(exc_info.value)

    @patch(
        "snowflake.snowflake_data_validation.snowflake.connector.connector_snowflake.snowflake.connector.DictCursor"
    )
    def test_execute_query_success(self, mock_dict_cursor):
        """Test successful query execution."""
        mock_connection = Mock()
        mock_cursor = Mock()
        mock_results = [{"col1": "result1"}, {"col1": "result2"}]
        mock_cursor.fetchall.return_value = mock_results
        mock_connection.cursor.return_value = mock_cursor

        self.connector.connection = mock_connection

        result = self.connector.execute_query("SELECT * FROM test_table")

        mock_connection.cursor.assert_called_once_with(mock_dict_cursor)
        mock_cursor.execute.assert_called_once_with("SELECT * FROM test_table")
        mock_cursor.fetchall.assert_called_once()
        mock_cursor.close.assert_called_once()
        assert result == mock_results

    def test_execute_query_no_connection(self):
        """Test query execution without established connection."""
        with pytest.raises(Exception) as exc_info:
            self.connector.execute_query("SELECT 1")

        assert CONNECTION_NOT_ESTABLISHED in str(exc_info.value)

    @patch(
        "snowflake.snowflake_data_validation.snowflake.connector.connector_snowflake.snowflake.connector.DictCursor"
    )
    def test_execute_query_execution_fails(self, mock_dict_cursor):
        """Test query execution when query fails."""
        mock_connection = Mock()
        mock_cursor = Mock()
        mock_cursor.execute.side_effect = Exception("Query failed")
        mock_connection.cursor.return_value = mock_cursor

        self.connector.connection = mock_connection

        with pytest.raises(Exception) as exc_info:
            self.connector.execute_query("SELECT * FROM test_table")

        assert FAILED_TO_EXECUTE_QUERY in str(exc_info.value)
        mock_connection.cursor.assert_called_once_with(mock_dict_cursor)

    def test_close_with_connection(self):
        """Test closing connection when connection exists."""
        mock_connection = Mock()
        self.connector.connection = mock_connection

        self.connector.close()

        mock_connection.close.assert_called_once()

    def test_close_without_connection(self):
        """Test closing connection when no connection exists."""
        self.connector.connection = None

        # Should not raise any exception
        self.connector.close()

    def test_execute_query_no_return(self):
        mock_connection = Mock()
        mock_cursor = Mock()
        mock_connection.cursor.return_value = mock_cursor

        self.connector.connection = mock_connection

        self.connector.execute_query_no_return("CREATE TABLE test_table (id INT)")

        mock_connection.cursor.assert_called_once()
        mock_cursor.execute.assert_called_once_with("CREATE TABLE test_table (id INT)")
        mock_cursor.close.assert_called_once()

    def test_execute_query_no_return_exception(self):
        mock_connection = Mock()

        self.connector.connection = mock_connection

        with pytest.raises(Exception) as exc_info:
            self.connector.execute_query("CREATE TABLE test_table (id INT)")

        assert FAILED_TO_EXECUTE_QUERY in str(exc_info.value)

    def test_execute_query_no_return_no_connection(self):
        with pytest.raises(Exception) as exc_info:
            self.connector.execute_query("CREATE TABLE test_table (id INT)")

        assert CONNECTION_NOT_ESTABLISHED in str(exc_info.value)
