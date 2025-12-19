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

"""Context object for tracking validation execution state."""

from dataclasses import dataclass, field


@dataclass
class ValidationExecutionContext:
    """Context object that tracks state during validation execution.

    This is passed to the engine and populated with fatal errors as they occur.

    Fatal errors are exceptions that prevent a table from being validated,
    distinct from validation failures (schema/metrics mismatches).
    """

    fatal_errors: dict[str, str] = field(default_factory=dict)

    def record_fatal_error(self, table_name: str, error_message: str) -> None:
        """Record a fatal error for a table that couldn't be validated.

        Args:
            table_name: Fully qualified table name
            error_message: Description of the fatal error

        """
        self.fatal_errors[table_name] = error_message

    def has_fatal_errors(self) -> bool:
        """Check if any fatal errors were recorded.

        Returns:
            bool: True if there are fatal errors

        """
        return len(self.fatal_errors) > 0

    def get_fatal_errors(self) -> dict[str, str]:
        """Get all fatal errors.

        Returns:
            dict[str, str]: Table names mapped to error messages

        """
        return self.fatal_errors.copy()
