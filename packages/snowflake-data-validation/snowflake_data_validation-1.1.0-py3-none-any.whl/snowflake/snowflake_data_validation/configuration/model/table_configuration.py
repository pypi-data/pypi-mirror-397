import logging

from typing import ClassVar

from pydantic import BaseModel, model_validator
from typing_extensions import Self

from snowflake.snowflake_data_validation.configuration.model.validation_configuration import (
    ValidationConfiguration,
)
from snowflake.snowflake_data_validation.utils.constants import NEWLINE
from snowflake.snowflake_data_validation.utils.helper import Helper
from snowflake.snowflake_data_validation.utils.helpers.helper_database import (
    HelperDatabase,
)


LOGGER = logging.getLogger(__name__)

MANDATORY_PROPERTIES: set[str] = {
    "target_name",
    "use_column_selection_as_exclude_list",
    "column_selection_list",
}

VISIBLE_PROPERTIES: set[str] = {
    "apply_metric_column_modifier",
    "chunk_number",
    "column_mappings",
    "exclude_metrics",
    "index_column_list",
    "is_case_sensitive",
    "max_failed_rows_number",
    "target_database",
    "target_index_column_list",
    "target_schema",
    "target_where_clause",
    "where_clause",
}


class TableConfiguration(BaseModel):
    """Table configuration model.

    Args:
        pydantic.BaseModel (pydantic.BaseModel): pydantic BaseModel

    """

    _id_counter: ClassVar[int] = 0
    id: int | None = None

    fully_qualified_name: str
    use_column_selection_as_exclude_list: bool
    column_selection_list: list[str]
    validation_configuration: ValidationConfiguration | None = None

    source_database: str | None = None
    source_schema: str | None = None
    source_table: str | None = None
    target_name: str | None = None

    target_fully_qualified_name: str = ""
    where_clause: str = ""
    target_where_clause: str = ""
    has_where_clause: bool = False
    has_target_where_clause: bool = False
    target_database: str | None = None
    target_schema: str | None = None
    index_column_list: list[str] = []
    target_index_column_list: list[str] = []
    is_case_sensitive: bool = False
    chunk_number: int | None = None
    column_mappings: dict[str, str] = {}
    max_failed_rows_number: int | None = None
    exclude_metrics: bool | None = None
    apply_metric_column_modifier: bool | None = None

    @model_validator(mode="after")
    def load(self) -> Self:
        self._assign_id()
        self._load_source_decomposed_fully_qualified_name()
        self._load_target_fully_qualified_name()
        self._set_has_where_clause()
        self._set_has_target_where_clause()
        self._normalize_where_clause()
        self._set_target_index_column_list()
        self._check_chunk_number()
        self._check_target_where_clause()
        self._set_column_mappings()
        self._check_max_failed_rows_number()
        self._normalize_column_selection_list()
        return self

    def _assign_id(self) -> None:
        if self.id is None:
            TableConfiguration._id_counter += 1
            self.id = TableConfiguration._id_counter

    def _load_source_decomposed_fully_qualified_name(self) -> None:
        self.fully_qualified_name = self.fully_qualified_name.replace('\\"', '"')

        decomposed_tuple = Helper.get_decomposed_fully_qualified_name(
            self.fully_qualified_name
        )

        if len(decomposed_tuple) == 2:
            self.source_database = None
            self.source_schema = decomposed_tuple[0]
            self.source_table = decomposed_tuple[1]

        else:
            self.source_database = decomposed_tuple[0]
            self.source_schema = decomposed_tuple[1]
            self.source_table = decomposed_tuple[2]

    def _load_target_fully_qualified_name(self) -> None:
        if self.target_database is None:
            self.target_database = HelperDatabase.normalize_to_snowflake_identifier(
                self.source_database
            )
        else:
            self.target_database = HelperDatabase.normalize_to_snowflake_identifier(
                self.target_database
            )

        if self.target_schema is None:
            self.target_schema = HelperDatabase.normalize_to_snowflake_identifier(
                self.source_schema
            )
        else:
            self.target_schema = HelperDatabase.normalize_to_snowflake_identifier(
                self.target_schema
            )

        if self.target_name is None:
            self.target_name = HelperDatabase.normalize_to_snowflake_identifier(
                self.source_table
            )
        else:
            self.target_name = HelperDatabase.normalize_to_snowflake_identifier(
                self.target_name
            )

        self.target_fully_qualified_name = (
            f"{self.target_database}.{self.target_schema}.{self.target_name}"
        )

    def _set_has_where_clause(self) -> None:
        self.has_where_clause = self.where_clause != ""

    def _set_has_target_where_clause(self) -> None:
        self.has_target_where_clause = self.target_where_clause != ""

    def _check_target_where_clause(self) -> None:
        if self.has_where_clause and not self.has_target_where_clause:
            LOGGER.warning(
                "Target where clause was not set for table %s. This may lead to unexpected results.",
                self.target_fully_qualified_name,
            )

    def _set_target_index_column_list(self) -> None:
        if self.target_index_column_list == []:
            self.target_index_column_list = self.index_column_list.copy()

        local_target_index_column_list = []
        for target_column_name in self.target_index_column_list:
            new_column_name = self.column_mappings.get(
                target_column_name, target_column_name
            )
            local_target_index_column_list.append(new_column_name)

        self.target_index_column_list = local_target_index_column_list

    def _check_chunk_number(self) -> None:
        if self.chunk_number is None:
            return
        elif self.chunk_number < 1:
            raise ValueError("Chunk number must be greater than or equal to 1.")

    def _set_column_mappings(self) -> None:
        """Normalize the keys and values of the column mappings dictionary to uppercase."""
        local_column_mapping = {}
        for key in self.column_mappings.keys():
            if self.is_case_sensitive:
                local_column_mapping[key] = self.column_mappings[key]
            else:
                local_column_mapping[key.upper()] = self.column_mappings[key].upper()
        self.column_mappings = local_column_mapping

    def _check_max_failed_rows_number(self) -> None:
        # Accept None, because it will be overwritten by ConfigurationModel
        # based on the value of ValidationConfiguration model.
        if self.max_failed_rows_number is None:
            return
        elif self.max_failed_rows_number < 1:
            raise ValueError(
                f"Invalid value for max failed rows number in table f{self.fully_qualified_name}. "
                "Value must be greater than or equal to 1."
            )

    def _normalize_where_clause(self) -> None:
        if self.has_where_clause:
            self.where_clause = HelperDatabase.remove_escape_quotes(self.where_clause)

        if self.has_target_where_clause:
            self.target_where_clause = HelperDatabase.remove_escape_quotes(
                self.target_where_clause
            )

    def _normalize_column_selection_list(self) -> None:
        self.column_selection_list = [
            HelperDatabase.remove_escape_quotes(col)
            for col in self.column_selection_list
        ]

    def __str__(self) -> str:
        """Return a formatted string representation of the table configuration."""
        properties = []

        # Add mandatory properties
        for attr in MANDATORY_PROPERTIES:
            properties.append(f"    {attr}: {getattr(self, attr)}")

        # Add visible properties with non-empty values
        for attr in VISIBLE_PROPERTIES:
            value = getattr(self, attr)
            if value not in (None, [], {}, "", 0):
                properties.append(f"    {attr}: {value}")

        properties.sort()
        properties_str = NEWLINE.join(properties)
        return f"  - fully_qualified_name: {self.fully_qualified_name}{NEWLINE}{properties_str}"
