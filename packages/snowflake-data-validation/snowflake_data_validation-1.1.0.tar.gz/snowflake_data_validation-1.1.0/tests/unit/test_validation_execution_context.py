# Copyright 2025 Snowflake Inc.
# SPDX-License-Identifier: Apache-2.0

"""Unit tests for ValidationExecutionContext."""

import pytest
from snowflake.snowflake_data_validation.validation.validation_execution_context import (
    ValidationExecutionContext,
)


class TestValidationExecutionContext:
    """Test cases for ValidationExecutionContext."""

    def test_starts_empty(self):
        """Test that context starts with no errors."""
        context = ValidationExecutionContext()
        assert not context.has_fatal_errors()

    def test_records_and_retrieves_error(self):
        """Test recording and retrieving a fatal error."""
        context = ValidationExecutionContext()
        context.record_fatal_error("DB.SCHEMA.TABLE", "Connection failed")
        
        assert context.has_fatal_errors()
        errors = context.get_fatal_errors()
        assert errors["DB.SCHEMA.TABLE"] == "Connection failed"

    def test_handles_multiple_errors(self):
        """Test recording multiple errors."""
        context = ValidationExecutionContext()
        context.record_fatal_error("TABLE1", "Error 1")
        context.record_fatal_error("TABLE2", "Error 2")
        
        errors = context.get_fatal_errors()
        assert len(errors) == 2
        assert errors["TABLE1"] == "Error 1"
        assert errors["TABLE2"] == "Error 2"

