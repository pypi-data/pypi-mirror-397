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

import pytest
import os

from snowflake.snowflake_data_validation.configuration.configuration_loader import (
    ConfigurationLoader,
)
from snowflake.snowflake_data_validation.configuration.model.table_configuration import (
    TableConfiguration,
)
from snowflake.snowflake_data_validation.configuration.singleton import Singleton
from snowflake.snowflake_data_validation.utils.configuration_file_editor import (
    ConfigurationFileEditor,
)


@pytest.fixture(autouse=True)
def reset_configuration_loader():
    """Reset ConfigurationLoader singleton before each test to ensure isolation."""
    # Save current state
    saved_instances = Singleton._instances.copy()
    saved_id_counter = TableConfiguration._id_counter

    # Clear only ConfigurationLoader for this test
    if ConfigurationLoader in Singleton._instances:
        del Singleton._instances[ConfigurationLoader]

    yield

    # Restore state after test
    Singleton._instances = saved_instances
    TableConfiguration._id_counter = saved_id_counter


SAMPLE_CONFIG = """\
source_platform: SQL server
target_platform: Snowflake
target_database: test_db
parallelization: false
output_directory_path: /test/reports

validation_configuration:
  schema_validation: true
  metrics_validation: true
  row_validation: false
  max_failed_rows_number: 50

comparison_configuration:
  tolerance: 0.01

tables:
  - fully_qualified_name: db.schema.table1
    use_column_selection_as_exclude_list: false
    column_selection_list: []
  - fully_qualified_name: db.schema.table2
    use_column_selection_as_exclude_list: true
    column_selection_list:
      - excluded_col
"""


@pytest.fixture
def temp_config_file(tmp_path):
    """Create a temporary configuration file for testing."""
    config_file = tmp_path / "test_config.yaml"
    config_file.write_text(SAMPLE_CONFIG)
    return str(config_file)


def test_file_not_found():
    """Test that FileNotFoundError is raised for non-existent file."""
    with pytest.raises(FileNotFoundError):
        ConfigurationFileEditor("/non/existent/path.yaml")


def test_is_directory_error(tmp_path):
    """Test that IsADirectoryError is raised when path is a directory."""
    with pytest.raises(IsADirectoryError):
        ConfigurationFileEditor(str(tmp_path))


def test_valid_file_loads_successfully(temp_config_file):
    """Test that a valid configuration file loads successfully."""
    editor = ConfigurationFileEditor(temp_config_file)
    assert editor.configuration_model is not None


def test_returns_source_connection(temp_config_file):
    """Test that get_connection_credentials returns the source connection (None if not defined)."""
    editor = ConfigurationFileEditor(temp_config_file)
    # source_connection is optional in config, so it can be None
    connection = editor.get_connection_credentials()
    assert connection is None  # Our sample config doesn't define source_connection


def test_returns_table_list(temp_config_file):
    """Test that get_table_collection returns a list of tables."""
    editor = ConfigurationFileEditor(temp_config_file)
    tables = editor.get_table_collection()

    assert isinstance(tables, list)
    assert len(tables) == 2


def test_table_fully_qualified_names(temp_config_file):
    """Test that tables have correct fully qualified names."""
    editor = ConfigurationFileEditor(temp_config_file)
    tables = editor.get_table_collection()

    fqn_list = [t.fully_qualified_name for t in tables]
    assert "db.schema.table1" in fqn_list
    assert "db.schema.table2" in fqn_list


def test_creates_new_file(temp_config_file):
    """Test that add_partitioned_table_configuration creates a new file."""
    editor = ConfigurationFileEditor(temp_config_file)

    new_content = """  - fully_qualified_name: db.schema.partitioned_table
    use_column_selection_as_exclude_list: false
    column_selection_list: []
    where_clause: ID >= 1 AND ID < 100
"""
    result = editor.add_partitioned_table_configuration(new_content)

    assert result is True

    # Verify file was created
    dir_path = os.path.dirname(temp_config_file)
    base_name = os.path.basename(temp_config_file).replace(".yaml", "")
    new_files = [
        f
        for f in os.listdir(dir_path)
        if f.startswith(base_name) and "_partitioned_" in f
    ]
    assert len(new_files) == 1


def test_new_file_contains_tables_section(temp_config_file):
    """Test that new file contains the tables section with new content."""
    editor = ConfigurationFileEditor(temp_config_file)

    new_content = """  - fully_qualified_name: db.schema.new_table
    use_column_selection_as_exclude_list: false
    column_selection_list: []
"""
    editor.add_partitioned_table_configuration(new_content)

    # Find the new file based on the original file's name
    dir_path = os.path.dirname(temp_config_file)
    base_name = os.path.basename(temp_config_file).replace(".yaml", "")
    new_files = [
        f
        for f in os.listdir(dir_path)
        if f.startswith(base_name) and "_partitioned_" in f
    ]

    assert len(new_files) == 1

    # Read and verify content
    new_file_path = os.path.join(dir_path, new_files[0])
    with open(new_file_path) as f:
        content = f.read()

    assert "tables:" in content
    assert "db.schema.new_table" in content
