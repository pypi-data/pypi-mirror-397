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
import pytest
from concurrent.futures import ThreadPoolExecutor, as_completed

from snowflake.snowflake_data_validation.connector.connector_failure_tracker import (
    ConnectionFailureTracker,
    MaxConnectionFailuresExceededError,
)
from snowflake.snowflake_data_validation.configuration.singleton import Singleton
from snowflake.snowflake_data_validation.utils.constants import MAX_CONSECUTIVE_FAILURES


@pytest.fixture(autouse=True)
def singleton():
    """Clear singleton instances before each test."""
    Singleton._instances = {}


# Singleton tests


def test_singleton_returns_same_instance():
    """Test that multiple instantiations return the same instance."""
    tracker1 = ConnectionFailureTracker()
    tracker2 = ConnectionFailureTracker()

    assert tracker1 is tracker2


def test_singleton_state_is_shared():
    """Test that state is shared across all references to the singleton."""
    tracker1 = ConnectionFailureTracker()
    tracker2 = ConnectionFailureTracker()

    tracker1.increment()
    assert tracker2.get_count() == 1

    tracker2.increment()
    assert tracker1.get_count() == 2


def test_singleton_reset_affects_all_references():
    """Test that resetting from one reference affects all references."""
    tracker1 = ConnectionFailureTracker()
    tracker2 = ConnectionFailureTracker()

    tracker1.increment()
    tracker1.increment()
    assert tracker2.get_count() == 2

    tracker2.reset()
    assert tracker1.get_count() == 0


# Increment tests


def test_increment_increases_count_by_one():
    """Test that increment increases the counter by one."""
    tracker = ConnectionFailureTracker()

    assert tracker.get_count() == 0
    tracker.increment()
    assert tracker.get_count() == 1
    tracker.increment()
    assert tracker.get_count() == 2


def test_increment_multiple_times():
    """Test incrementing multiple times."""
    tracker = ConnectionFailureTracker()

    for i in range(10):
        tracker.increment()

    assert tracker.get_count() == 10


# Reset tests


def test_reset_sets_count_to_zero():
    """Test that reset sets the counter to zero."""
    tracker = ConnectionFailureTracker()

    tracker.increment()
    tracker.increment()
    tracker.increment()
    assert tracker.get_count() == 3

    tracker.reset()
    assert tracker.get_count() == 0


def test_reset_on_zero_count():
    """Test that reset works correctly when count is already zero."""
    tracker = ConnectionFailureTracker()

    assert tracker.get_count() == 0
    tracker.reset()
    assert tracker.get_count() == 0


def test_reset_allows_increment_again():
    """Test that after reset, increment works correctly."""
    tracker = ConnectionFailureTracker()

    tracker.increment()
    tracker.increment()
    tracker.reset()
    tracker.increment()

    assert tracker.get_count() == 1


# Get count tests


def test_get_count_returns_zero_initially():
    """Test that get_count returns zero for a new tracker."""
    tracker = ConnectionFailureTracker()

    assert tracker.get_count() == 0


def test_get_count_returns_correct_value():
    """Test that get_count returns the correct value after increments."""
    tracker = ConnectionFailureTracker()

    tracker.increment()
    assert tracker.get_count() == 1

    tracker.increment()
    tracker.increment()
    assert tracker.get_count() == 3


# Check threshold tests


def test_check_threshold_does_not_raise_when_below_max():
    """Test that check_threshold does not raise when count is below max."""
    tracker = ConnectionFailureTracker()

    # Should not raise for counts 0 to max_consecutive_failures - 1
    for i in range(tracker.max_consecutive_failures - 1):
        tracker.increment()
        tracker.check_threshold()  # Should not raise


def test_check_threshold_raises_when_at_max():
    """Test that check_threshold raises when count equals max."""
    tracker = ConnectionFailureTracker()

    for _ in range(tracker.max_consecutive_failures):
        tracker.increment()

    with pytest.raises(MaxConnectionFailuresExceededError) as exc_info:
        tracker.check_threshold()

    assert "Maximum consecutive connection failures" in str(exc_info.value)
    assert str(tracker.max_consecutive_failures) in str(exc_info.value)


def test_check_threshold_raises_when_above_max():
    """Test that check_threshold raises when count exceeds max."""
    tracker = ConnectionFailureTracker()

    for _ in range(tracker.max_consecutive_failures + 2):
        tracker.increment()

    with pytest.raises(MaxConnectionFailuresExceededError):
        tracker.check_threshold()


def test_check_threshold_after_reset_does_not_raise():
    """Test that check_threshold does not raise after reset."""
    tracker = ConnectionFailureTracker()

    # Exceed threshold
    for _ in range(tracker.max_consecutive_failures):
        tracker.increment()

    # Reset
    tracker.reset()

    # Should not raise now
    tracker.check_threshold()


# Max consecutive failures tests


def test_max_consecutive_failures():
    """Test that max_consecutive_failures is set to MAX_CONSECUTIVE_FAILURES."""
    tracker = ConnectionFailureTracker()

    assert tracker.max_consecutive_failures == MAX_CONSECUTIVE_FAILURES


def test_threshold_triggers_at_exactly_max():
    """Test that the threshold triggers exactly at max_consecutive_failures."""
    tracker = ConnectionFailureTracker()

    # Increment to one below max - should not raise
    for _ in range(tracker.max_consecutive_failures - 1):
        tracker.increment()
    tracker.check_threshold()  # Should not raise

    # One more increment to reach max - should raise
    tracker.increment()
    with pytest.raises(MaxConnectionFailuresExceededError):
        tracker.check_threshold()


# Exception tests


def test_exception_is_raised_with_correct_type():
    """Test that the correct exception type is raised."""
    tracker = ConnectionFailureTracker()

    for _ in range(tracker.max_consecutive_failures):
        tracker.increment()

    with pytest.raises(MaxConnectionFailuresExceededError):
        tracker.check_threshold()


def test_exception_message_contains_helpful_info():
    """Test that the exception message contains helpful information."""
    tracker = ConnectionFailureTracker()

    for _ in range(tracker.max_consecutive_failures):
        tracker.increment()

    with pytest.raises(MaxConnectionFailuresExceededError) as exc_info:
        tracker.check_threshold()

    error_message = str(exc_info.value)
    assert "connection" in error_message.lower()
    assert str(tracker.max_consecutive_failures) in error_message


def test_exception_inherits_from_exception():
    """Test that MaxConnectionFailuresExceededError inherits from Exception."""
    assert issubclass(MaxConnectionFailuresExceededError, Exception)


# Thread safety tests


def test_concurrent_increments():
    """Test that concurrent increments are thread-safe."""
    tracker = ConnectionFailureTracker()
    num_threads = 10
    increments_per_thread = 100

    def increment_many_times():
        for _ in range(increments_per_thread):
            tracker.increment()

    threads = []
    for _ in range(num_threads):
        thread = threading.Thread(target=increment_many_times)
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

    expected_count = num_threads * increments_per_thread
    assert tracker.get_count() == expected_count


def test_concurrent_increments_and_resets():
    """Test thread safety with mixed increment and reset operations."""
    tracker = ConnectionFailureTracker()
    num_operations = 100

    def increment_operation():
        tracker.increment()
        return "increment"

    def reset_operation():
        tracker.reset()
        return "reset"

    # Mix increments and resets
    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = []
        for i in range(num_operations):
            if i % 5 == 0:  # Every 5th operation is a reset
                futures.append(executor.submit(reset_operation))
            else:
                futures.append(executor.submit(increment_operation))

        # Wait for all operations to complete
        for future in as_completed(futures):
            future.result()

    # Count should be non-negative (we can't predict exact value due to race)
    assert tracker.get_count() >= 0


def test_concurrent_get_count():
    """Test that concurrent get_count calls are thread-safe."""
    tracker = ConnectionFailureTracker()
    tracker.increment()
    tracker.increment()
    tracker.increment()

    results = []
    num_threads = 50

    def read_count():
        count = tracker.get_count()
        results.append(count)

    threads = []
    for _ in range(num_threads):
        thread = threading.Thread(target=read_count)
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

    # All reads should return the same value
    assert all(count == 3 for count in results)


def test_singleton_across_threads():
    """Test that the singleton instance is the same across threads."""
    instances = []

    def get_instance():
        tracker = ConnectionFailureTracker()
        instances.append(id(tracker))

    threads = []
    for _ in range(10):
        thread = threading.Thread(target=get_instance)
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

    # All instances should have the same id
    assert len(set(instances)) == 1


# Integration tests


def test_circuit_breaker_pattern():
    """Test the complete circuit breaker pattern workflow."""
    tracker = ConnectionFailureTracker()

    # Simulate connection attempts
    for attempt in range(tracker.max_consecutive_failures - 1):
        # Connection fails
        tracker.increment()
        # Check if we should stop trying
        tracker.check_threshold()  # Should not raise yet

    # One more failure
    tracker.increment()

    # Circuit should be open now
    with pytest.raises(MaxConnectionFailuresExceededError):
        tracker.check_threshold()


def test_circuit_breaker_reset_on_success():
    """Test that successful connection resets the circuit breaker."""
    tracker = ConnectionFailureTracker()

    # Accumulate some failures
    for _ in range(tracker.max_consecutive_failures - 1):
        tracker.increment()

    # Simulate successful connection
    tracker.reset()

    # Should be able to handle failures again
    for _ in range(tracker.max_consecutive_failures - 1):
        tracker.increment()
        tracker.check_threshold()  # Should not raise


def test_multiple_failure_cycles():
    """Test multiple failure and recovery cycles."""
    tracker = ConnectionFailureTracker()

    for cycle in range(3):
        # Accumulate failures
        for _ in range(tracker.max_consecutive_failures - 1):
            tracker.increment()

        # "Recover" with a successful connection
        tracker.reset()
        assert tracker.get_count() == 0
