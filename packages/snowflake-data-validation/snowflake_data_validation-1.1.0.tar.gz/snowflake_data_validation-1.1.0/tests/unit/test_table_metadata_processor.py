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

from unittest.mock import MagicMock

import pandas as pd
import pytest

from snowflake.snowflake_data_validation.configuration.model.table_configuration import (
    TableConfiguration,
)
from snowflake.snowflake_data_validation.orchestration.table_metadata_processor import (
    TableMetadataProcessor,
)
from snowflake.snowflake_data_validation.utils.constants import (
    CALCULATED_COLUMN_SIZE_IN_BYTES_KEY,
    CHARACTER_LENGTH_KEY,
    COLUMN_DATATYPE,
    COLUMN_NAME_KEY,
    DATABASE_NAME_KEY,
    IS_PRIMARY_KEY_KEY,
    NULLABLE_KEY,
    PRECISION_KEY,
    ROW_COUNT_KEY,
    SCALE_KEY,
    SCHEMA_NAME_KEY,
    TABLE_NAME_KEY,
    Platform,
)


class TestTableMetadataProcessor:
    """Test class for TableMetadataProcessor."""

    def setup_method(self):
        self.processor = TableMetadataProcessor()

        self.mock_context = MagicMock()
        self.mock_context.source_platform = Platform.REDSHIFT
        self.mock_context.target_platform = Platform.SNOWFLAKE
        self.mock_context.output_handler = MagicMock()

        self.processor.context = self.mock_context

    def test_map_column_datatype_with_existing_mapping(self):
        column_datatype = "VARCHAR"
        datatypes_mappings = {"VARCHAR": "STRING", "INTEGER": "NUMBER"}
        column_name = "test_column"

        result = self.processor._map_column_datatype(
            column_datatype, datatypes_mappings, column_name
        )

        assert result == "STRING"
        self.mock_context.output_handler.handle_message.assert_not_called()

    def test_map_column_datatype_with_missing_mapping(self):
        column_datatype = "CUSTOM_TYPE"
        datatypes_mappings = {"VARCHAR": "STRING", "INTEGER": "NUMBER"}
        column_name = "custom_column"

        result = self.processor._map_column_datatype(
            column_datatype, datatypes_mappings, column_name
        )

        assert result == column_datatype
        self.mock_context.output_handler.handle_message.assert_called_once()

    def test_generate_target_table_column_metadata_without_column_mappings(self):
        """Test _generate_target_table_column_metadata with no column mappings."""
        source_df = pd.DataFrame(
            {
                COLUMN_NAME_KEY: ["id", "name", "email"],
                COLUMN_DATATYPE: ["INTEGER", "VARCHAR", "VARCHAR"],
                NULLABLE_KEY: [False, True, True],
                IS_PRIMARY_KEY_KEY: [True, False, False],
                CALCULATED_COLUMN_SIZE_IN_BYTES_KEY: [8, 50, 100],
                DATABASE_NAME_KEY: ["source_db", "source_db", "source_db"],
                SCHEMA_NAME_KEY: ["source_schema", "source_schema", "source_schema"],
                TABLE_NAME_KEY: ["source_table", "source_table", "source_table"],
                CHARACTER_LENGTH_KEY: [None, None, None],
                PRECISION_KEY: [None, None, None],
                SCALE_KEY: [None, None, None],
            }
        )

        table_config = TableConfiguration(
            fully_qualified_name="source_db.source_schema.source_table",
            target_database="target_db",
            target_schema="target_schema",
            target_name="target_table",
            use_column_selection_as_exclude_list=False,
            column_selection_list=["id", "name"],
            column_mappings={},  # No column mappings
            is_case_sensitive=False,
        )

        row_count_df = pd.DataFrame({ROW_COUNT_KEY: [500]})
        case_sensitive_df = pd.DataFrame()
        datatypes_mappings = {"INTEGER": "NUMBER", "VARCHAR": "STRING"}

        result = self.processor._generate_target_table_column_metadata(
            table_column_metadata_from_source_df=source_df,
            table_configuration=table_config,
            datatypes_mappings=datatypes_mappings,
            table_row_count_df=row_count_df,
            case_sensitive_columns_df=case_sensitive_df,
        )

        assert len(result.columns) == 3
        assert result.columns[0].name == "ID"
        assert result.columns[1].name == "NAME"
        assert result.columns[2].name == "EMAIL"

        assert len(result.column_selection_list) == 2
        assert result.column_selection_list[0] == "ID"
        assert result.column_selection_list[1] == "NAME"

    def test_generate_target_table_column_metadata_with_empty_column_selection_list(
        self,
    ):
        """Test _generate_target_table_column_metadata with empty column_selection_list."""
        source_df = pd.DataFrame(
            {
                COLUMN_NAME_KEY: ["id", "name", "email", "age"],
                COLUMN_DATATYPE: ["INTEGER", "VARCHAR", "VARCHAR", "INTEGER"],
                NULLABLE_KEY: [False, True, True, False],
                IS_PRIMARY_KEY_KEY: [True, False, False, False],
                CALCULATED_COLUMN_SIZE_IN_BYTES_KEY: [8, 50, 100, 4],
                DATABASE_NAME_KEY: ["source_db", "source_db", "source_db", "source_db"],
                SCHEMA_NAME_KEY: [
                    "source_schema",
                    "source_schema",
                    "source_schema",
                    "source_schema",
                ],
                TABLE_NAME_KEY: [
                    "source_table",
                    "source_table",
                    "source_table",
                    "source_table",
                ],
                CHARACTER_LENGTH_KEY: [None, None, None, None],
                PRECISION_KEY: [None, None, None, None],
                SCALE_KEY: [None, None, None, None],
            }
        )

        table_config = TableConfiguration(
            fully_qualified_name="source_db.source_schema.source_table",
            target_database="target_db",
            target_schema="target_schema",
            target_name="target_table",
            use_column_selection_as_exclude_list=False,
            column_selection_list=[],  # Empty column selection list
            column_mappings={},  # No column mappings
            is_case_sensitive=False,
        )

        row_count_df = pd.DataFrame({ROW_COUNT_KEY: [500]})
        case_sensitive_df = pd.DataFrame()
        datatypes_mappings = {"INTEGER": "NUMBER", "VARCHAR": "STRING"}

        result = self.processor._generate_target_table_column_metadata(
            table_column_metadata_from_source_df=source_df,
            table_configuration=table_config,
            datatypes_mappings=datatypes_mappings,
            table_row_count_df=row_count_df,
            case_sensitive_columns_df=case_sensitive_df,
        )

        # Verify all columns are present
        assert len(result.columns) == 4
        assert result.columns[0].name == "ID"
        assert result.columns[1].name == "NAME"
        assert result.columns[2].name == "EMAIL"
        assert result.columns[3].name == "AGE"

        assert len(result.column_selection_list) == 0

    def test_generate_target_table_column_metadata_with_column_mappings(self):
        """Test _generate_target_table_column_metadata with column mappings."""
        source_df = pd.DataFrame(
            {
                COLUMN_NAME_KEY: ["id", "full_name"],
                COLUMN_DATATYPE: ["INTEGER", "VARCHAR"],
                NULLABLE_KEY: [False, True],
                IS_PRIMARY_KEY_KEY: [True, False],
                CALCULATED_COLUMN_SIZE_IN_BYTES_KEY: [8, 100],
                DATABASE_NAME_KEY: ["source_db", "source_db"],
                SCHEMA_NAME_KEY: ["source_schema", "source_schema"],
                TABLE_NAME_KEY: ["source_table", "source_table"],
                CHARACTER_LENGTH_KEY: [None, None],
                PRECISION_KEY: [None, None],
                SCALE_KEY: [None, None],
            }
        )

        table_config = TableConfiguration(
            fully_qualified_name="source_db.source_schema.source_table",
            target_database="target_db",
            target_schema="target_schema",
            target_name="target_table",
            use_column_selection_as_exclude_list=False,
            column_selection_list=["full_name"],
            column_mappings={"FULL_NAME": "name"},
            is_case_sensitive=False,
        )

        row_count_df = pd.DataFrame({ROW_COUNT_KEY: [500]})
        case_sensitive_df = pd.DataFrame()
        datatypes_mappings = {"INTEGER": "NUMBER", "VARCHAR": "STRING"}

        result = self.processor._generate_target_table_column_metadata(
            table_column_metadata_from_source_df=source_df,
            table_configuration=table_config,
            datatypes_mappings=datatypes_mappings,
            table_row_count_df=row_count_df,
            case_sensitive_columns_df=case_sensitive_df,
        )

        assert len(result.columns) == 2
        assert result.columns[1].name == "NAME"
        assert len(result.column_selection_list) == 1
        assert result.column_selection_list[0] == "NAME"

    @pytest.mark.parametrize(
        "is_case_sensitive, column_selection_list, column_mappings, expected_names, expected_column_selection_list",
        [
            (  # Case 1: Original mappings, lowercase source
                False,
                ["id", "beautifool c*lumn", "$pecial column", "test column"],
                {
                    "BEAUTIFOOL C*LUMN": "beautifool_c_lumn",
                    "$PECIAL COLUMN": "_pecial_column",
                },
                ["ID", "BEAUTIFOOL_C_LUMN", "_PECIAL_COLUMN", "TEST COLUMN"],
                ["ID", "BEAUTIFOOL_C_LUMN", "_PECIAL_COLUMN", "TEST COLUMN"],
            ),
            (  # Case 2: Original mappings, uppercase source
                False,
                [
                    s.upper()
                    for s in [
                        "id",
                        "beautifool c*lumn",
                        "$pecial column",
                        "test column",
                    ]
                ],
                {
                    "BEAUTIFOOL C*LUMN": "beautifool_c_lumn",
                    "$PECIAL COLUMN": "_pecial_column",
                },
                ["ID", "BEAUTIFOOL_C_LUMN", "_PECIAL_COLUMN", "TEST COLUMN"],
                ["ID", "BEAUTIFOOL_C_LUMN", "_PECIAL_COLUMN", "TEST COLUMN"],
            ),
            (  # Case 3: Original mappings, everything lowercase
                False,
                ["id", "beautifool c*lumn", "$pecial column", "test column"],
                {
                    "beautifool c*lumn": "beautifool_c_lumn",
                    "$pecial column": "_pecial_column",
                },
                ["ID", "BEAUTIFOOL_C_LUMN", "_PECIAL_COLUMN", "TEST COLUMN"],
                ["ID", "BEAUTIFOOL_C_LUMN", "_PECIAL_COLUMN", "TEST COLUMN"],
            ),
            (  # Case 4: is_case_sensitive = True
                True,
                ["id", "beautifool c*lumn", "$pecial column", "test column"],
                {
                    "beautifool c*lumn": "beautifool_c_lumn",
                    "$pecial column": "_pecial_column",
                },
                ["ID", "beautifool_c_lumn", "_pecial_column", "TEST COLUMN"],
                ["ID", "beautifool_c_lumn", "_pecial_column", "TEST COLUMN"],
            ),
        ],
    )
    def test_generate_target_table_column_metadata_with_special_characters_in_mappings(
        self,
        is_case_sensitive,
        column_selection_list,
        column_mappings,
        expected_names,
        expected_column_selection_list,
    ):
        """Test _generate_target_table_column_metadata with special characters in column mappings."""
        source_df = pd.DataFrame(
            {
                COLUMN_NAME_KEY: [
                    "id",
                    "beautifool c*lumn",
                    "$pecial column",
                    "test column",
                ],
                COLUMN_DATATYPE: ["INTEGER", "VARCHAR", "VARCHAR", "INTEGER"],
                NULLABLE_KEY: [False, True, True, False],
                IS_PRIMARY_KEY_KEY: [True, False, False, False],
                CALCULATED_COLUMN_SIZE_IN_BYTES_KEY: [8, 100, 50, 4],
                DATABASE_NAME_KEY: ["source_db", "source_db", "source_db", "source_db"],
                SCHEMA_NAME_KEY: [
                    "source_schema",
                    "source_schema",
                    "source_schema",
                    "source_schema",
                ],
                TABLE_NAME_KEY: [
                    "source_table",
                    "source_table",
                    "source_table",
                    "source_table",
                ],
                CHARACTER_LENGTH_KEY: [None, None, None, None],
                PRECISION_KEY: [None, None, None, None],
                SCALE_KEY: [None, None, None, None],
            }
        )

        table_config = TableConfiguration(
            fully_qualified_name="source_db.source_schema.source_table",
            target_database="target_db",
            target_schema="target_schema",
            target_name="target_table",
            use_column_selection_as_exclude_list=False,
            column_selection_list=column_selection_list,
            column_mappings=column_mappings,
            is_case_sensitive=is_case_sensitive,
        )

        row_count_df = pd.DataFrame({ROW_COUNT_KEY: [600]})
        case_sensitive_df = pd.DataFrame()
        datatypes_mappings = {"INTEGER": "NUMBER", "VARCHAR": "STRING"}

        result = self.processor._generate_target_table_column_metadata(
            table_column_metadata_from_source_df=source_df,
            table_configuration=table_config,
            datatypes_mappings=datatypes_mappings,
            table_row_count_df=row_count_df,
            case_sensitive_columns_df=case_sensitive_df,
        )

        assert [col.name for col in result.columns] == expected_names
        assert result.column_selection_list == expected_column_selection_list

    def test_generate_target_table_column_metadata_with_brackets_in_mappings(
        self,
    ):
        """Test _generate_target_table_column_metadata with special characters in column mappings."""
        source_df = pd.DataFrame(
            {
                COLUMN_NAME_KEY: [
                    "id",
                    "[beautifool c*lumn]",
                    "[$pecial column]",
                    "test column",
                ],
                COLUMN_DATATYPE: ["INTEGER", "VARCHAR", "VARCHAR", "INTEGER"],
                NULLABLE_KEY: [False, True, True, False],
                IS_PRIMARY_KEY_KEY: [True, False, False, False],
                CALCULATED_COLUMN_SIZE_IN_BYTES_KEY: [8, 100, 50, 4],
                DATABASE_NAME_KEY: ["source_db", "source_db", "source_db", "source_db"],
                SCHEMA_NAME_KEY: [
                    "source_schema",
                    "source_schema",
                    "source_schema",
                    "source_schema",
                ],
                TABLE_NAME_KEY: [
                    "source_table",
                    "source_table",
                    "source_table",
                    "source_table",
                ],
                CHARACTER_LENGTH_KEY: [None, None, None, None],
                PRECISION_KEY: [None, None, None, None],
                SCALE_KEY: [None, None, None, None],
            }
        )

        table_config = TableConfiguration(
            fully_qualified_name="source_db.source_schema.source_table",
            target_database="target_db",
            target_schema="target_schema",
            target_name="target_table",
            use_column_selection_as_exclude_list=False,
            column_selection_list=[
                "id",
                "[beautifool c*lumn]",
                "[$pecial column]",
                "test column",
            ],
            column_mappings={
                "[BEAUTIFOOL C*LUMN]": "[beautifool_c_lumn]",
                "[$PECIAL COLUMN]": "[_pecial_column]",
            },
            is_case_sensitive=False,
        )

        row_count_df = pd.DataFrame({ROW_COUNT_KEY: [600]})
        case_sensitive_df = pd.DataFrame()
        datatypes_mappings = {"INTEGER": "NUMBER", "VARCHAR": "STRING"}

        result = self.processor._generate_target_table_column_metadata(
            table_column_metadata_from_source_df=source_df,
            table_configuration=table_config,
            datatypes_mappings=datatypes_mappings,
            table_row_count_df=row_count_df,
            case_sensitive_columns_df=case_sensitive_df,
        )

        assert len(result.columns) == 4
        assert result.columns[0].name == "ID"
        assert result.columns[1].name == "[BEAUTIFOOL_C_LUMN]"
        assert result.columns[2].name == "[_PECIAL_COLUMN]"
        assert result.columns[3].name == "TEST COLUMN"
        assert len(result.column_selection_list) == 4
        assert result.column_selection_list[0] == "ID"
        assert result.column_selection_list[1] == "[BEAUTIFOOL_C_LUMN]"
        assert result.column_selection_list[2] == "[_PECIAL_COLUMN]"
        assert result.column_selection_list[3] == "TEST COLUMN"

    def test_extract_and_generate_target_metadata_uses_passed_source_dataframe(self):
        """Test that _extract_and_generate_target_metadata uses the passed source DataFrame.

        This test verifies that the target metadata generation uses the source DataFrame
        passed as parameter, rather than re-extracting from the target database.
        This is critical because target column metadata should be derived from source
        columns (with mappings applied), not from the target database directly.
        """
        # Create source DataFrame with specific columns
        source_df = pd.DataFrame(
            {
                COLUMN_NAME_KEY: ["source_col_a", "source_col_b"],
                COLUMN_DATATYPE: ["INTEGER", "VARCHAR"],
                NULLABLE_KEY: [False, True],
                IS_PRIMARY_KEY_KEY: [True, False],
                CALCULATED_COLUMN_SIZE_IN_BYTES_KEY: [8, 100],
                DATABASE_NAME_KEY: ["source_db", "source_db"],
                SCHEMA_NAME_KEY: ["source_schema", "source_schema"],
                TABLE_NAME_KEY: ["source_table", "source_table"],
                CHARACTER_LENGTH_KEY: [None, None],
                PRECISION_KEY: [None, None],
                SCALE_KEY: [None, None],
            }
        )

        table_config = TableConfiguration(
            fully_qualified_name="source_db.source_schema.source_table",
            target_database="target_db",
            target_schema="target_schema",
            target_name="target_table",
            use_column_selection_as_exclude_list=False,
            column_selection_list=[],
            column_mappings={},
            is_case_sensitive=False,
        )

        # Mock target extractor
        mock_target_extractor = MagicMock()
        mock_target_extractor.platform = Platform.SNOWFLAKE
        mock_target_extractor.extract_table_row_count.return_value = pd.DataFrame(
            {ROW_COUNT_KEY: [100]}
        )
        mock_target_extractor.extract_case_sensitive_columns.return_value = (
            pd.DataFrame()
        )

        # Set up context with datatypes mappings
        self.mock_context.datatypes_mappings = {
            "INTEGER": "NUMBER",
            "VARCHAR": "STRING",
        }

        # Call _extract_and_generate_target_metadata with the source DataFrame
        result = self.processor._extract_and_generate_target_metadata(
            table_configuration=table_config,
            table_column_metadata_from_source_df=source_df,
            target_extractor=mock_target_extractor,
            context=self.mock_context,
        )

        # Verify that the result contains columns from the SOURCE DataFrame
        # (not re-extracted from target)
        assert len(result.columns) == 2
        assert result.columns[0].name == "SOURCE_COL_A"
        assert result.columns[1].name == "SOURCE_COL_B"

        # Verify that _extract_table_column_metadata_from_source was NOT called
        # on the target_extractor (it should use the passed DataFrame)
        assert (
            not hasattr(mock_target_extractor, "extract_table_column_metadata")
            or not mock_target_extractor.extract_table_column_metadata.called
        )
