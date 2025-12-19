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

import threading

from snowflake.snowflake_data_validation.configuration.singleton import Singleton
from snowflake.snowflake_data_validation.utils.constants import MAX_CONSECUTIVE_FAILURES


class MaxConnectionFailuresExceededError(Exception):
    """Raised when the maximum number of consecutive connection failures is exceeded."""

    pass


class ConnectionFailureTracker(metaclass=Singleton):
    """
    Thread-safe Singleton class for tracking consecutive connection failures.

    This class implements a global circuit breaker pattern that monitors
    connection failures across all connector instances. When the maximum
    number of consecutive failures is reached, it raises an exception
    to prevent further connection attempts.
    """

    def __init__(self) -> None:
        """Initialize the tracker (no-op for singleton)."""
        self.max_consecutive_failures = MAX_CONSECUTIVE_FAILURES
        self._consecutive_failures = 0
        self._counter_lock = threading.Lock()

    def increment(self) -> None:
        """Increment the consecutive failure counter (thread-safe)."""
        with self._counter_lock:
            self._consecutive_failures += 1

    def reset(self) -> None:
        """Reset the consecutive failure counter to zero (thread-safe)."""
        with self._counter_lock:
            self._consecutive_failures = 0

    def get_count(self) -> int:
        """Get the current consecutive failure count (thread-safe)."""
        with self._counter_lock:
            return self._consecutive_failures

    def check_threshold(self) -> None:
        """
        Check if the consecutive failure threshold has been exceeded.

        Raises:
            MaxConnectionFailuresExceededError: If threshold is exceeded.

        """
        with self._counter_lock:
            if self._consecutive_failures >= self.max_consecutive_failures:
                raise MaxConnectionFailuresExceededError(
                    f"Failed to establish connection. Maximum consecutive connection failures "
                    f"({self.max_consecutive_failures}) exceeded. "
                    f"Please verify your connection settings and network connectivity."
                )
