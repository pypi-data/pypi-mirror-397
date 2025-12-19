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

import pandas as pd

from snowflake.snowflake_data_validation.configuration.model.table_configuration import (
    TableConfiguration,
)
from snowflake.snowflake_data_validation.extractor.metadata_extractor_base import (
    MetadataExtractorBase,
)
from snowflake.snowflake_data_validation.script_writer.script_writer_base import (
    ScriptWriterBase,
)
from snowflake.snowflake_data_validation.utils.base_output_handler import (
    OutputMessageLevel,
)
from snowflake.snowflake_data_validation.utils.constants import (
    COLUMN_DATATYPE,
    COLUMN_NAME_KEY,
    DATABASE_NAME_KEY,
    IS_DATA_TYPE_SUPPORTED_KEY,
    ROW_COUNT_KEY,
    SCHEMA_NAME_KEY,
    TABLE_NAME_KEY,
    Platform,
)
from snowflake.snowflake_data_validation.utils.context import Context
from snowflake.snowflake_data_validation.utils.logging_utils import log
from snowflake.snowflake_data_validation.utils.model.table_column_metadata import (
    TableColumnMetadata,
)


LOGGER = logging.getLogger(__name__)


class TableMetadataProcessor:
    """Handles table metadata extraction and processing operations."""

    @log
    def generate_table_column_metadata(
        self,
        table_configuration: TableConfiguration,
        source_extractor: MetadataExtractorBase | ScriptWriterBase,
        target_extractor: MetadataExtractorBase | ScriptWriterBase,
        context: Context,
    ) -> tuple[TableColumnMetadata, TableColumnMetadata]:
        """Generate source and target table column metadata.

        This method handles the extraction of table column metadata from the source database
        and mapping it to the target. If the target is Snowflake, it will also extract
        case-sensitive column information to ensure proper column name matching between
        SQL Server and Snowflake.

        Args:
            table_configuration: Table configuration containing all necessary metadata
            source_extractor: Source extractor for metadata extraction
            target_extractor: Target extractor for metadata extraction
            context: Validation context

        Returns:
            Tuple[TableColumnMetadata, TableColumnMetadata]: Source and target metadata

        """
        self.context = context
        LOGGER.info(
            "Loading table column metadata model for: %s",
            table_configuration.fully_qualified_name,
        )

        # Extract source metadata
        source_table_column_metadata, table_column_metadata_from_source_df = (
            self._extract_and_generate_source_metadata(
                table_configuration=table_configuration,
                source_extractor=source_extractor,
                context=context,
            )
        )

        LOGGER.debug("Successfully generated source table column metadata model")

        # Extract target metadata
        target_table_column_metadata = self._extract_and_generate_target_metadata(
            table_configuration=table_configuration,
            table_column_metadata_from_source_df=table_column_metadata_from_source_df,
            target_extractor=target_extractor,
            context=context,
        )

        LOGGER.debug("Successfully generated target table column metadata model")

        LOGGER.info(
            "Successfully loaded table column metadata model for: %s",
            table_configuration.fully_qualified_name,
        )

        return source_table_column_metadata, target_table_column_metadata

    @log
    def generate_source_table_column_metadata(
        self,
        table_configuration: TableConfiguration,
        source_extractor: MetadataExtractorBase | ScriptWriterBase,
        context: Context,
    ) -> TableColumnMetadata:
        """Generate source-only table column metadata.

        This method is used for source-only validation where only source metadata
        is needed without any target comparison.

        Args:
            table_configuration: Table configuration containing all necessary metadata
            source_extractor: Source extractor for metadata extraction
            context: Validation context

        Returns:
            TableColumnMetadata: Source table column metadata

        """
        self.context = context
        LOGGER.info(
            "Loading source-only table column metadata for: %s",
            table_configuration.fully_qualified_name,
        )

        source_table_column_metadata, _ = self._extract_and_generate_source_metadata(
            table_configuration=table_configuration,
            source_extractor=source_extractor,
            context=context,
        )

        LOGGER.info(
            "Successfully loaded source-only table column metadata for: %s",
            table_configuration.fully_qualified_name,
        )

        return source_table_column_metadata

    def _extract_and_generate_source_metadata(
        self,
        table_configuration: TableConfiguration,
        source_extractor: MetadataExtractorBase | ScriptWriterBase,
        context: Context,
    ) -> tuple[TableColumnMetadata, pd.DataFrame]:
        """Extract and generate source table column metadata.

        Args:
            table_configuration: Table configuration containing all necessary metadata
            source_extractor: Source extractor for metadata extraction
            context: Validation context

        Returns:
            tuple[TableColumnMetadata, pd.DataFrame]: A tuple containing:
                - TableColumnMetadata: Source table column metadata model
                - pd.DataFrame: Raw source table column metadata DataFrame,
                  used for generating target metadata with proper column mappings

        """
        table_column_metadata_from_source_df: pd.DataFrame = (
            self._extract_table_column_metadata_from_source(
                table_configuration, source_extractor, context
            )
        )

        # TODO: Implement row count extraction in ScriptWriterBase or define what needs to be done
        source_table_row_count_df: pd.DataFrame = (
            source_extractor.extract_table_row_count(
                fully_qualified_name=table_configuration.fully_qualified_name,
                where_clause=table_configuration.where_clause,
                has_where_clause=bool(table_configuration.where_clause),
                platform=context.source_platform,
                context=context,
            )
        )

        LOGGER.debug(
            "Successfully loaded table row count for table: %s in platform: %s",
            table_configuration.fully_qualified_name,
            context.source_platform,
        )

        source_table_column_metadata: TableColumnMetadata = (
            self._generate_source_table_column_metadata(
                table_column_metadata_from_source_df=table_column_metadata_from_source_df,
                table_row_count_df=source_table_row_count_df,
                datatypes_mappings=context.datatypes_mappings,
                column_selection_list=table_configuration.column_selection_list,
            )
        )

        return source_table_column_metadata, table_column_metadata_from_source_df

    def _extract_and_generate_target_metadata(
        self,
        table_configuration: TableConfiguration,
        table_column_metadata_from_source_df: pd.DataFrame,
        target_extractor: MetadataExtractorBase | ScriptWriterBase,
        context: Context,
    ) -> TableColumnMetadata:
        """Extract and generate target table column metadata.

        Args:
            table_configuration: Table configuration containing all necessary metadata
            table_column_metadata_from_source_df: Source table column metadata DataFrame,
                used to derive target column names with proper mappings applied
            target_extractor: Target extractor for metadata extraction
            context: Validation context

        Returns:
            TableColumnMetadata: Target table column metadata

        """
        target_table_row_count_df: pd.DataFrame = (
            target_extractor.extract_table_row_count(
                fully_qualified_name=table_configuration.target_fully_qualified_name,
                where_clause=table_configuration.target_where_clause,
                has_where_clause=table_configuration.has_target_where_clause,
                platform=context.target_platform,
                context=context,
            )
        )

        # If the target is Snowflake, extract case-sensitive column information
        case_sensitive_columns_df = pd.DataFrame()
        if (
            hasattr(target_extractor, "extract_case_sensitive_columns")
            and target_extractor.platform == Platform.SNOWFLAKE
        ):
            try:
                case_sensitive_columns_df = (
                    target_extractor.extract_case_sensitive_columns(
                        table_configuration=table_configuration, context=context
                    )
                )
                LOGGER.info(
                    "Found case-sensitive columns information for Snowflake target"
                )
            except Exception as e:
                LOGGER.warning(
                    f"Could not extract case-sensitive column information: {str(e)}"
                )
                case_sensitive_columns_df = pd.DataFrame()

        LOGGER.debug(
            "Successfully loaded table row count for table: %s in platform: %s",
            table_configuration.target_fully_qualified_name,
            context.target_platform,
        )

        target_table_column_metadata: TableColumnMetadata = (
            self._generate_target_table_column_metadata(
                table_column_metadata_from_source_df=table_column_metadata_from_source_df,
                table_configuration=table_configuration,
                datatypes_mappings=context.datatypes_mappings,
                table_row_count_df=target_table_row_count_df,
                case_sensitive_columns_df=case_sensitive_columns_df,
            )
        )

        return target_table_column_metadata

    def _generate_source_table_column_metadata(
        self,
        table_column_metadata_from_source_df: pd.DataFrame,
        table_row_count_df: pd.DataFrame,
        datatypes_mappings: dict[str, str],
        column_selection_list: list[str],
    ) -> TableColumnMetadata:
        """Generate source table column metadata model.

        Args:
            table_column_metadata_from_source_df: Source table metadata DataFrame
            table_row_count_df: Table row count DataFrame
            datatypes_mappings: Data type mappings
            column_selection_list: List of columns to include in the metadata
        Returns:
            TableColumnMetadata: Source table metadata model

        """
        try:
            table_column_metadata_from_source_df[IS_DATA_TYPE_SUPPORTED_KEY] = (
                table_column_metadata_from_source_df[COLUMN_DATATYPE].apply(
                    lambda datatype_key: datatype_key in datatypes_mappings
                )
            )

            table_column_metadata_from_source_df[ROW_COUNT_KEY] = table_row_count_df[
                ROW_COUNT_KEY
            ]

            table_column_metadata_model = TableColumnMetadata(
                table_column_metadata_df=table_column_metadata_from_source_df,
                column_selection_list=column_selection_list,
            )

            return table_column_metadata_model

        except Exception as e:
            LOGGER.error(
                "Error generating source table column metadata model: %s", str(e)
            )
            raise ValueError(
                "Failed to generate source table column metadata model"
            ) from e

    def _extract_table_column_metadata_from_source(
        self,
        table_configuration: TableConfiguration,
        extractor: MetadataExtractorBase | ScriptWriterBase,
        context: Context,
    ) -> pd.DataFrame:
        """Extract table column metadata from the source.

        Args:
            table_configuration: Table configuration containing all necessary metadata
            extractor: The extractor to use for extracting metadata
            context: Validation context

        Returns:
            pd.DataFrame: DataFrame containing the table column metadata

        """
        table_column_metadata_df: pd.DataFrame = (
            extractor.extract_table_column_metadata(
                table_configuration=table_configuration,
                context=context,
            )
        )

        return table_column_metadata_df

    def _get_target_cols(
        self,
        table_configuration: TableConfiguration,
        case_sensitive_dict: dict,
        cols: list[str],
    ) -> list[str]:
        """
        Resolve the target column names based on column mappings, case sensitivity, and fallback rules.

        The resolution order for each column is as follows:
            1. If the column name exists in table_configuration.column_mappings, use the mapped value.
            2. If not case sensitive and column.upper() exists in column_mappings, use the mapped value.
            3. If the uppercase column name exists in case_sensitive_dict, use the value from case_sensitive_dict.
            4. Use the original column name if case_sensitive_dict is provided, else use the uppercase column name.

        Args:
            table_configuration (TableConfiguration): Contains column mappings and case sensitivity flag.
            case_sensitive_dict (dict): Dictionary mapping uppercase column names to their case-sensitive counterparts.
            cols (list[str]): List of source column names to resolve.

        Returns:
            list[str]: List of resolved target column names, in the same order as `cols`.

        """
        res = []
        for col in cols:
            n_col = (
                col if case_sensitive_dict else col.upper()
            )  # default if nothing else found
            if col in table_configuration.column_mappings:
                n_col = table_configuration.column_mappings.get(col)
            elif (
                not table_configuration.is_case_sensitive
                and col.upper() in table_configuration.column_mappings
            ):
                n_col = table_configuration.column_mappings.get(col.upper())
            elif col.upper() in case_sensitive_dict:
                n_col = case_sensitive_dict.get(col.upper())
            res.append(n_col)
        return res

    def _generate_target_table_column_metadata(
        self,
        table_column_metadata_from_source_df: pd.DataFrame,
        table_configuration: TableConfiguration,
        datatypes_mappings: dict[str, str],
        table_row_count_df: pd.DataFrame,
        case_sensitive_columns_df: pd.DataFrame,
    ) -> TableColumnMetadata:
        """Generate target table column metadata model.

        Args:
            table_column_metadata_from_source_df: Source table metadata DataFrame
            table_configuration: Table configuration
            datatypes_mappings: Data type mappings
            table_row_count_df: Table row count DataFrame
            case_sensitive_columns_df: DataFrame containing case-sensitive column information from Snowflake

        Returns:
            TableColumnMetadata: Target table metadata model

        """
        try:
            local_df: pd.DataFrame = table_column_metadata_from_source_df.copy()
            local_df[DATABASE_NAME_KEY] = table_configuration.target_database
            local_df[SCHEMA_NAME_KEY] = table_configuration.target_schema
            local_df[TABLE_NAME_KEY] = table_configuration.target_name
            local_df[IS_DATA_TYPE_SUPPORTED_KEY] = local_df[COLUMN_DATATYPE].apply(
                lambda datatype_key: datatype_key in datatypes_mappings
            )
            local_df[COLUMN_DATATYPE] = local_df.apply(
                lambda row: self._map_column_datatype(
                    row[COLUMN_DATATYPE], datatypes_mappings, row[COLUMN_NAME_KEY]
                ),
                axis=1,
            )

            # Create case-sensitive dictionary if available, otherwise use empty dict
            case_sensitive_dict = {}
            if (
                case_sensitive_columns_df is not None
                and not case_sensitive_columns_df.empty
            ):
                LOGGER.info("Using case-sensitive column information from Snowflake")
                LOGGER.debug(
                    "case_sensitive_columns_df columns: %s",
                    case_sensitive_columns_df.columns.tolist(),
                )
                LOGGER.debug(
                    "case_sensitive_columns_df shape: %s",
                    case_sensitive_columns_df.shape,
                )

                # Handle both uppercase and lowercase column names
                column_name_key = "COLUMN_NAME"

                case_sensitive_dict = dict(
                    zip(
                        case_sensitive_columns_df[column_name_key].str.upper(),
                        case_sensitive_columns_df[column_name_key],
                        strict=False,
                    )
                )
            # Apply column name mappings with unified logic
            local_df[COLUMN_NAME_KEY] = self._get_target_cols(
                table_configuration, case_sensitive_dict, local_df[COLUMN_NAME_KEY]
            )
            local_df[ROW_COUNT_KEY] = table_row_count_df[ROW_COUNT_KEY]

            column_selection_list = None
            if table_configuration.column_selection_list:
                column_selection_list = table_configuration.column_selection_list.copy()
                # Apply column mappings to convert source column names to target column names
                column_selection_list = self._get_target_cols(
                    table_configuration, case_sensitive_dict, column_selection_list
                )
            table_column_metadata_model: TableColumnMetadata = TableColumnMetadata(
                local_df, column_selection_list=column_selection_list
            )
            return table_column_metadata_model

        except Exception as e:
            LOGGER.error(
                "Error generating target table column metadata model: %s", str(e)
            )
            raise ValueError(
                "Failed to generate target table column metadata model"
            ) from e

    # pylint: disable=consider-using-f-string
    # ruff: noqa: UP031
    def _map_column_datatype(
        self, column_datatype: str, datatypes_mappings: dict[str, str], column_name: str
    ) -> str:
        """Map the column datatype to the target datatype.

        Args:
            column_datatype: The column datatype to map
            datatypes_mappings: The datatypes mappings
            column_name: The column name for logging purposes

        Returns:
            str: The mapped column datatype

        """
        if column_datatype in datatypes_mappings:
            return datatypes_mappings[column_datatype]
        else:
            platform_name = self.context.source_platform.value
            LOGGER.warning(
                "Datatype %s not found in datatypes mappings. "
                "Column: %s will be skipped. "
                "Please define it in the %s_datatypes_mapping_template.yaml file.",
                column_datatype,
                column_name,
                platform_name,
            )
            self.context.output_handler.handle_message(
                header="Column datatype not found in datatypes mappings",
                message=(
                    "Datatype %s not found in datatypes mappings. "
                    "Column: %s will be skipped. "
                    "Please define it in the %s_datatypes_mapping_template.yaml file."
                    % (column_datatype, column_name, platform_name)
                ),
                level=OutputMessageLevel.WARNING,
            )
            return column_datatype
