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


class HelperDatabase:
    """A helper class for database-related utility functions."""

    @staticmethod
    def normalize_identifier(identifier: str) -> str:
        """
        Remove leading and trailing square brackets or double quotes from an identifier.

        Args:
            identifier (str): The identifier to normalize.

        Returns:
            str: The normalized identifier without leading/trailing brackets or quotes.

        """
        if not identifier:
            return identifier

        if (
            identifier[0] in ("[", '"')
            and identifier[-1] in ("]", '"')
            and len(identifier) > 1
        ):
            return identifier[1:-1]

        return identifier

    @staticmethod
    def normalize_to_snowflake_identifier(value: str) -> str:
        """
        Normalize a string to a Snowflake identifier format.

        Args:
            value (str): The string to normalize.

        Returns:
            str: The normalized Snowflake identifier, or None if value is None.

        """
        if value is None:
            return None
        if value and value.startswith('\\"') and value.endswith('\\"'):
            return f'"{value[2:-2]}"'
        return value.upper()

    @staticmethod
    def remove_escape_quotes(value: str) -> str:
        """
        Remove escape quotes from a string if they exist.

        Args:
            value (str): The string from which to remove escape quotes.

        Returns:
            str: The string with escape quotes removed if they were present.

        """
        if value and value.startswith('\\"') and value.endswith('\\"'):
            return f"{value[2:-2]}"
        return value
