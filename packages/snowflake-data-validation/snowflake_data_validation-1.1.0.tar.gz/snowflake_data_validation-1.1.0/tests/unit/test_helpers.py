# Copyright 2025 Snowflake Inc.
# SPDX-License-Identifier: Apache-2.0
from unittest.mock import MagicMock

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
from deepdiff import DeepDiff

from snowflake.snowflake_data_validation.utils.helper import Helper
from snowflake.snowflake_data_validation.utils.helpers.helper_database import (
    HelperDatabase,
)

ASSETS_DIRECTORY_NAME = "assets"
DUMMY_CONFIGURATION_JSON_FILE_NAME = "dummy_configuration_file.json"
DUMMY_METRICS_TEMPLATE_YAML_FILE_NAME = "dummy_metrics_template.yaml"
DUMMY_METRICS_TEMPLATE_DATATYPES_YAML_FILE_NAME = (
    "dummy_metrics_template_datatypes.yaml"
)
DUMMY_DATATYPES_TEMPLATE_YAML_FILE_NAME = "dummy_datatypes_template.yaml"
DUMMY_DATATYPES_NORMALIZATION_TEMPLATE_YAML_FILE_NAME = (
    "dummy_datatypes_normalization_template.yaml"
)
NOT_EXISTS_TEMPLATE_YAML_FILE_NAME = "not_exists.yaml"
NOT_VALID_FORMAT_TEMPLATE_YAML_FILE_NAME = "not_valid_format.yaml"
TEST_HELPERS_DIRECTORY_NAME = "test_helpers"


def test_get_decomposed_fully_qualified_name():

    assert Helper.get_decomposed_fully_qualified_name("database.schema.table") == (
        "database",
        "schema",
        "table",
    )


def test_test_get_decomposed_fully_qualified_name_exception():
    with pytest.raises(ValueError) as ex_info:
        Helper.get_decomposed_fully_qualified_name("123")

    assert (
        "Invalid fully qualified name: 123. Expected format: 'database.schema.table' or 'schema.table'"
        == str(ex_info.value)
    )


def test_copy_templates_to_temp_dir():
    from pathlib import Path
    import os
    import tempfile

    source_templates_path = (
        Path(__file__)
        .parent.joinpath(ASSETS_DIRECTORY_NAME)
        .joinpath(TEST_HELPERS_DIRECTORY_NAME)
    )
    core_templates_path = source_templates_path
    expected_files_copied_path_collection = sorted(os.listdir(source_templates_path))

    with tempfile.TemporaryDirectory() as temp_dir:
        Helper.copy_templates_to_temp_dir(
            str(source_templates_path), str(core_templates_path), str(temp_dir)
        )

        files_copied_collection = sorted(os.listdir(temp_dir))
        assert files_copied_collection == expected_files_copied_path_collection


def test_load_metrics_templates_from_yaml():
    from pathlib import Path
    import pandas as pd

    file_path = (
        Path(__file__)
        .parent.joinpath(ASSETS_DIRECTORY_NAME)
        .joinpath(TEST_HELPERS_DIRECTORY_NAME)
        .joinpath(DUMMY_METRICS_TEMPLATE_YAML_FILE_NAME)
    )

    datatypes_normalization_templates = {
        "TYPE1": "TO_CHAR({{ metric_query }}, 'N4')",
        "TYPE2": "TO_CHAR({{ metric_query }})",
        "TYPE3": "TO_CHAR({{ metric_query }}, 'N1')",
    }

    df = Helper.load_metrics_templates_from_yaml(
        file_path, datatypes_normalization_templates
    )

    expected_df = pd.DataFrame(
        {
            "type": ["TYPE1", "TYPE1", "TYPE2"],
            "metric": ["METRIC1", "METRIC2", "METRIC1"],
            "template": [
                'METRIC1("{{ col_name }}")',
                'METRIC2("{{ col_name }}")',
                'METRIC1("{{ col_name }}")',
            ],
            "normalization": [
                "TO_CHAR({{ metric_query }}, 'N4')",
                "TO_CHAR({{ metric_query }}, 'N4')",
                "TO_CHAR({{ metric_query }})",
            ],
            "column_modifier": [None, None, None],
        }
    )
    assert df.equals(expected_df)


def test_load_metrics_templates_datatypes_from_yaml():
    from pathlib import Path
    import pandas as pd

    file_path = (
        Path(__file__)
        .parent.joinpath(ASSETS_DIRECTORY_NAME)
        .joinpath(TEST_HELPERS_DIRECTORY_NAME)
        .joinpath(DUMMY_METRICS_TEMPLATE_DATATYPES_YAML_FILE_NAME)
    )

    datatypes_normalization_templates = {
        "TYPE1": "TO_CHAR({{ metric_query }}, 'N4')",
        "TYPE2": "TO_CHAR({{ metric_query }})",
        "TYPE3": "TO_CHAR({{ metric_query }}, 'YYYY-DD-MM')",
    }

    df = Helper.load_metrics_templates_from_yaml(
        file_path, datatypes_normalization_templates
    )

    expected_df = pd.DataFrame(
        {
            "type": ["TYPE1", "TYPE1", "TYPE2"],
            "metric": ["METRIC1", "METRIC2", "METRIC1"],
            "template": [
                'METRIC1("{{ col_name }}")',
                'METRIC2("{{ col_name }}")',
                'METRIC1("{{ col_name }}")',
            ],
            "normalization": [
                "TO_CHAR({{ metric_query }}, 'N4')",
                "TO_CHAR({{ metric_query }})",
                "TO_CHAR({{ metric_query }}, 'YYYY-DD-MM')",
            ],
            "column_modifier": ["% 10", None, None],
        }
    )
    assert df.equals(expected_df)


def test_load_metrics_templates_from_yaml_file_not_found_exception():
    from pathlib import Path

    with pytest.raises(FileNotFoundError) as ex_info:
        file_path = (
            Path(__file__)
            .parent.joinpath(ASSETS_DIRECTORY_NAME)
            .joinpath(TEST_HELPERS_DIRECTORY_NAME)
            .joinpath(NOT_EXISTS_TEMPLATE_YAML_FILE_NAME)
        )
        Helper.load_metrics_templates_from_yaml(file_path, {})

    assert (str(ex_info.value)).startswith("Template file not found at:")


def test_load_metrics_templates_from_yaml_missing_datatype_key_exception():
    from pathlib import Path

    with pytest.raises(RuntimeError) as ex_info:
        file_path = (
            Path(__file__)
            .parent.joinpath(ASSETS_DIRECTORY_NAME)
            .joinpath(TEST_HELPERS_DIRECTORY_NAME)
            .joinpath(DUMMY_METRICS_TEMPLATE_DATATYPES_YAML_FILE_NAME)
        )
        Helper.load_metrics_templates_from_yaml(file_path, {})

    assert (
        str(ex_info.value) == "Missing TYPE1 datatype in datatypes normalization file."
    )


def test_load_metrics_templates_from_yaml_not_valid_format_exception():
    yaml_content = r"""key1: value1
key2
  - value2
key3: [value3, value4"""

    with pytest.raises(RuntimeError) as ex_info:
        file_path = MagicMock()
        file_path.read_text.return_value = yaml_content
        file_path.name = "not_valid_format.yaml"
        Helper.load_metrics_templates_from_yaml(file_path, {})

    expected_error_message = r"""Error in the format of not_valid_format.yaml. Please check the following:
Incorrect indentation: YAML relies heavily on consistent indentation using spaces (not tabs).
Invalid characters: Certain characters might need to be quoted.
Syntax errors in lists or dictionaries: Incorrect use of hyphens for list items or nested structures.
Special characters not quoted: If a string contains special characters it might need to be enclosed in quotes."""

    assert expected_error_message == str(ex_info.value)


def test_reformat_metrics_yaml_data():
    import yaml
    from pathlib import Path

    file_path = (
        Path(__file__)
        .parent.joinpath(ASSETS_DIRECTORY_NAME)
        .joinpath(TEST_HELPERS_DIRECTORY_NAME)
        .joinpath(DUMMY_METRICS_TEMPLATE_YAML_FILE_NAME)
    )

    datatypes_normalization_templates = {
        "TYPE1": "TO_CHAR({{ metric_query }}, 'N4')",
        "TYPE2": "TO_CHAR({{ metric_query }})",
    }

    file_content = file_path.read_text()
    yaml_data = yaml.safe_load(file_content)
    yaml_data_reformatted = Helper._reformat_metrics_yaml_data(
        yaml_data, datatypes_normalization_templates
    )

    expected_model = {
        "type": ["TYPE1", "TYPE1", "TYPE2"],
        "metric": ["METRIC1", "METRIC2", "METRIC1"],
        "template": [
            'METRIC1("{{ col_name }}")',
            'METRIC2("{{ col_name }}")',
            'METRIC1("{{ col_name }}")',
        ],
        "normalization": [
            "TO_CHAR({{ metric_query }}, 'N4')",
            "TO_CHAR({{ metric_query }}, 'N4')",
            "TO_CHAR({{ metric_query }})",
        ],
        "column_modifier": [None, None, None],
    }

    diff = DeepDiff(
        expected_model,
        yaml_data_reformatted,
        ignore_order=True,
    )

    assert diff == {}


def test_load_datatypes_templates_from_yaml():
    from pathlib import Path
    import pandas as pd

    file_path = (
        Path(__file__)
        .parent.joinpath(ASSETS_DIRECTORY_NAME)
        .joinpath(TEST_HELPERS_DIRECTORY_NAME)
        .joinpath(DUMMY_DATATYPES_TEMPLATE_YAML_FILE_NAME)
    )
    df = Helper.load_datatypes_templates_from_yaml(file_path, "some_dialect")

    expected_df = pd.DataFrame(
        {
            "some_dialect": ["TYPE1", "TYPE2"],
            "DIALECT1": ["TYPE1_DIALECT1", "TYPE2_DIALECT1"],
        }
    )
    assert df.equals(expected_df)


def test_load_datatypes_templates_from_yaml_file_not_found_exception():
    from pathlib import Path

    with pytest.raises(FileNotFoundError) as ex_info:
        file_path = (
            Path(__file__)
            .parent.joinpath(ASSETS_DIRECTORY_NAME)
            .joinpath(TEST_HELPERS_DIRECTORY_NAME)
            .joinpath(NOT_EXISTS_TEMPLATE_YAML_FILE_NAME)
        )
        Helper.load_datatypes_templates_from_yaml(file_path, "some_dialect")

    assert (str(ex_info.value)).startswith("Template file not found at:")


def test_load_datatypes_templates_from_yaml_not_valid_format_exception():
    yaml_content = r"""key1: value1
key2
  - value2
key3: [value3, value4"""

    with pytest.raises(RuntimeError) as ex_info:
        file_path = MagicMock()
        file_path.read_text.return_value = yaml_content
        file_path.name = "not_valid_format.yaml"
        Helper.load_metrics_templates_from_yaml(file_path, {})

    expected_error_message = r"""Error in the format of not_valid_format.yaml. Please check the following:
Incorrect indentation: YAML relies heavily on consistent indentation using spaces (not tabs).
Invalid characters: Certain characters might need to be quoted.
Syntax errors in lists or dictionaries: Incorrect use of hyphens for list items or nested structures.
Special characters not quoted: If a string contains special characters it might need to be enclosed in quotes."""

    assert expected_error_message == str(ex_info.value)


def test_reformat_datatypes_yaml_data():
    import yaml
    from pathlib import Path

    file_path = (
        Path(__file__)
        .parent.joinpath(ASSETS_DIRECTORY_NAME)
        .joinpath(TEST_HELPERS_DIRECTORY_NAME)
        .joinpath(DUMMY_DATATYPES_TEMPLATE_YAML_FILE_NAME)
    )

    file_content = file_path.read_text()
    yaml_data = yaml.safe_load(file_content)
    yaml_data_reformatted = Helper._reformat_datatypes_yaml_data(
        yaml_data, "some_dialect"
    )

    expected_model = {
        "some_dialect": ["TYPE1", "TYPE2"],
        "DIALECT1": ["TYPE1_DIALECT1", "TYPE2_DIALECT1"],
    }

    diff = DeepDiff(
        expected_model,
        yaml_data_reformatted,
        ignore_order=True,
    )

    assert diff == {}


def test_load_datatypes_normalization_templates_from_yaml():
    from pathlib import Path

    file_path = (
        Path(__file__)
        .parent.joinpath(ASSETS_DIRECTORY_NAME)
        .joinpath(TEST_HELPERS_DIRECTORY_NAME)
        .joinpath(DUMMY_DATATYPES_NORMALIZATION_TEMPLATE_YAML_FILE_NAME)
    )
    model = Helper.load_datatypes_normalization_templates_from_yaml(file_path)

    expected_model = {
        "TYPE1": "TO_CHAR({{ metric_query }}, 'N4')",
        "TYPE2": "TO_CHAR({{ metric_query }})",
        "TYPE3": "TO_CHAR({{ metric_query }}, 'N1')",
    }

    diff = DeepDiff(
        expected_model,
        model,
        ignore_order=True,
    )

    assert diff == {}


def test_load_datatypes_normalization_templates_from_yaml_file_not_found_exception():
    from pathlib import Path

    with pytest.raises(FileNotFoundError) as ex_info:
        file_path = (
            Path(__file__)
            .parent.joinpath(ASSETS_DIRECTORY_NAME)
            .joinpath(TEST_HELPERS_DIRECTORY_NAME)
            .joinpath(NOT_EXISTS_TEMPLATE_YAML_FILE_NAME)
        )
        Helper.load_datatypes_normalization_templates_from_yaml(file_path)

    assert (str(ex_info.value)).startswith("Template file not found at:")


def test_load_datatypes_normalization_templates_from_yaml_not_valid_format_exception():
    yaml_content = r"""key1: value1
key2
  - value2
key3: [value3, value4"""

    with pytest.raises(RuntimeError) as ex_info:
        file_path = MagicMock()
        file_path.read_text.return_value = yaml_content
        file_path.name = "not_valid_format.yaml"
        Helper.load_datatypes_normalization_templates_from_yaml(file_path)

    expected_error_message = r"""Error in the format of not_valid_format.yaml. Please check the following:
Incorrect indentation: YAML relies heavily on consistent indentation using spaces (not tabs).
Invalid characters: Certain characters might need to be quoted.
Syntax errors in lists or dictionaries: Incorrect use of hyphens for list items or nested structures.
Special characters not quoted: If a string contains special characters it might need to be enclosed in quotes."""

    assert expected_error_message == str(ex_info.value)


def test_normalize_identifier_remove_brackets():
    """Test normalize_identifier removes square brackets from identifiers."""
    from snowflake.snowflake_data_validation.utils.helpers.helper_misc import HelperMisc

    # Test removing brackets
    assert HelperDatabase.normalize_identifier("[table_name]") == "table_name"
    assert HelperDatabase.normalize_identifier("[database]") == "database"
    assert HelperDatabase.normalize_identifier("[schema_name]") == "schema_name"


def test_normalize_identifier_remove_double_quotes():
    """Test normalize_identifier removes double quotes from identifiers."""
    from snowflake.snowflake_data_validation.utils.helpers.helper_misc import HelperMisc

    # Test removing double quotes
    assert HelperDatabase.normalize_identifier('"table_name"') == "table_name"
    assert HelperDatabase.normalize_identifier('"database"') == "database"
    assert HelperDatabase.normalize_identifier('"schema_name"') == "schema_name"


def test_normalize_identifier_no_enclosing_characters():
    """Test normalize_identifier with identifiers that have no enclosing characters."""
    from snowflake.snowflake_data_validation.utils.helpers.helper_misc import HelperMisc

    # Test identifiers without brackets or quotes
    assert HelperDatabase.normalize_identifier("table_name") == "table_name"
    assert HelperDatabase.normalize_identifier("database") == "database"
    assert HelperDatabase.normalize_identifier("schema_name") == "schema_name"


def test_normalize_identifier_partial_brackets():
    """Test normalize_identifier with partial brackets (only opening or closing)."""
    from snowflake.snowflake_data_validation.utils.helpers.helper_misc import HelperMisc

    # Test partial brackets - should not be removed
    assert HelperDatabase.normalize_identifier("[table_name") == "[table_name"
    assert HelperDatabase.normalize_identifier("table_name]") == "table_name]"
    assert HelperDatabase.normalize_identifier("]table_name[") == "]table_name["


def test_normalize_identifier_partial_quotes():
    """Test normalize_identifier with partial quotes (only opening or closing)."""
    from snowflake.snowflake_data_validation.utils.helpers.helper_misc import HelperMisc

    # Test partial quotes - should not be removed
    assert HelperDatabase.normalize_identifier('"table_name') == '"table_name'
    assert HelperDatabase.normalize_identifier('table_name"') == 'table_name"'
    assert HelperDatabase.normalize_identifier("\"table_name'") == "\"table_name'"


def test_normalize_identifier_special_characters_inside():
    """Test normalize_identifier with special characters inside brackets/quotes."""
    from snowflake.snowflake_data_validation.utils.helpers.helper_misc import HelperMisc

    # Test with spaces and special characters
    assert (
        HelperDatabase.normalize_identifier("[table name with spaces]")
        == "table name with spaces"
    )
    assert HelperDatabase.normalize_identifier('"table-name_123"') == "table-name_123"
    assert (
        HelperDatabase.normalize_identifier("[table$name@domain]")
        == "table$name@domain"
    )


def test_normalize_identifier_nested_brackets_quotes():
    """Test normalize_identifier with nested or multiple brackets/quotes."""
    from snowflake.snowflake_data_validation.utils.helpers.helper_misc import HelperMisc

    # Test nested characters (should only remove outer ones)
    assert HelperDatabase.normalize_identifier('["inner"]') == '"inner"'
    assert HelperDatabase.normalize_identifier("[table[name]]") == "table[name]"
    assert HelperDatabase.normalize_identifier('"table"name""') == 'table"name"'


def test_remove_escape_quotes_with_escaped_quotes():
    """Test remove_escape_quotes removes escaped quotes from start and end."""
    assert HelperDatabase.remove_escape_quotes('\\"value\\"') == "value"
    assert HelperDatabase.remove_escape_quotes('\\"table name\\"') == "table name"
    assert HelperDatabase.remove_escape_quotes('\\"Column Name\\"') == "Column Name"


def test_remove_escape_quotes_empty_and_none():
    """Test remove_escape_quotes with empty string and None."""
    assert HelperDatabase.remove_escape_quotes("") == ""
    assert HelperDatabase.remove_escape_quotes('\\"\\"') == ""


def test_normalize_to_snowflake_identifier_uppercase():
    """Test normalize_to_snowflake_identifier converts lowercase to uppercase."""
    assert HelperDatabase.normalize_to_snowflake_identifier("database") == "DATABASE"
    assert HelperDatabase.normalize_to_snowflake_identifier("schema") == "SCHEMA"
    assert (
        HelperDatabase.normalize_to_snowflake_identifier("table_name") == "TABLE_NAME"
    )


def test_normalize_to_snowflake_identifier_already_uppercase():
    """Test normalize_to_snowflake_identifier with already uppercase values."""
    assert HelperDatabase.normalize_to_snowflake_identifier("DATABASE") == "DATABASE"
    assert HelperDatabase.normalize_to_snowflake_identifier("SCHEMA") == "SCHEMA"


def test_normalize_to_snowflake_identifier_escaped_quotes():
    """Test normalize_to_snowflake_identifier with escaped quotes."""
    assert (
        HelperDatabase.normalize_to_snowflake_identifier('\\"my_table\\"')
        == '"my_table"'
    )
    assert (
        HelperDatabase.normalize_to_snowflake_identifier('\\"MyDatabase\\"')
        == '"MyDatabase"'
    )


def test_normalize_to_snowflake_identifier_none_value():
    """Test normalize_to_snowflake_identifier with None value returns None."""
    assert HelperDatabase.normalize_to_snowflake_identifier(None) is None


def test_normalize_to_snowflake_identifier_empty_string():
    """Test normalize_to_snowflake_identifier with empty string returns empty string."""
    assert HelperDatabase.normalize_to_snowflake_identifier("") == ""


def test_normalize_to_snowflake_identifier_mixed_case():
    """Test normalize_to_snowflake_identifier with mixed case identifiers."""
    assert (
        HelperDatabase.normalize_to_snowflake_identifier("MyDatabase") == "MYDATABASE"
    )
    assert HelperDatabase.normalize_to_snowflake_identifier("mySchema") == "MYSCHEMA"
    assert (
        HelperDatabase.normalize_to_snowflake_identifier("Table_Name") == "TABLE_NAME"
    )
