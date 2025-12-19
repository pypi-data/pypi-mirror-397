import os

from datetime import datetime
from pathlib import Path

from snowflake.snowflake_data_validation.configuration.configuration_loader import (
    ConfigurationLoader,
)
from snowflake.snowflake_data_validation.configuration.model.connection_types import (
    Connection,
)
from snowflake.snowflake_data_validation.configuration.model.table_configuration import (
    TableConfiguration,
)
from snowflake.snowflake_data_validation.utils.constants import NEWLINE


class ConfigurationFileEditor:
    """Class to edit and manage configuration files for data validation."""

    def __init__(self, file_path: str):
        """
        Initialize the ConfigurationFileEditor with a configuration file path.

        This constructor validates the provided file path and loads the configuration model.
        It performs several checks to ensure the file is accessible and has proper permissions.

        Args:
            file_path (str): Path to the configuration file to be edited.

        Raises:
            FileNotFoundError: If the configuration file does not exist at the specified path.
            IsADirectoryError: If the provided path points to a directory instead of a file.
            PermissionError: If the configuration file is not readable or not writable.

        Attributes:
            file_path (Path): Path object representing the configuration file location.
            configuration_model: The loaded configuration model from the file.

        """
        self.file_path: Path = Path(file_path)

        if not os.path.exists(self.file_path):
            raise FileNotFoundError(
                f"Configuration file {self.file_path} does not exist."
            )
        if not os.path.isfile(self.file_path):
            raise IsADirectoryError(
                f"Configuration file {self.file_path} is a directory, not a file."
            )
        if not os.access(self.file_path, os.R_OK):
            raise PermissionError(
                f"Configuration file {self.file_path} is not readable."
            )
        if not os.access(self.file_path, os.W_OK):
            raise PermissionError(
                f"Configuration file {self.file_path} is not writable."
            )
        configuration_loader = ConfigurationLoader(self.file_path)
        self.configuration_model = configuration_loader.get_configuration_model()

    def get_connection_credentials(self) -> Connection:
        return self.configuration_model.source_connection

    def get_table_collection(self) -> list[TableConfiguration]:
        return self.configuration_model.tables

    def add_partitioned_table_configuration(self, content_to_add: str) -> bool:
        with open(self.file_path, encoding="utf-8") as config_file:
            config_file_content = config_file.read()

        new_file_content = (
            config_file_content.split("tables:")[0]
            + "tables:"
            + NEWLINE
            + content_to_add
        )
        datetime_str = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        new_file_path = self.file_path.with_stem(
            f"{self.file_path.stem}_partitioned_{datetime_str}"
        ).with_suffix(".yaml")

        with open(new_file_path, "w", encoding="utf-8") as config_file:
            config_file.write(new_file_content)

        return os.path.exists(new_file_path)
