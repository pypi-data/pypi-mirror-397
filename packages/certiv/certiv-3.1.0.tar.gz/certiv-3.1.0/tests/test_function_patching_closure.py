#!/usr/bin/env python3
# Copyright (c) 2024 Certiv.ai
# SPDX-License-Identifier: MIT

"""
Test to verify that closure-based patching works correctly.

This test demonstrates that variables captured in closures survive
after the wrapper function is created, allowing proper restoration
even when the function is called later from a different context
(like an agent calling the patched function).
"""

from __future__ import annotations
import sys
from unittest.mock import Mock, patch

import pytest

from certiv.api import CertivAPIClient
from certiv.api.types import ExecutionOperation, JobOperation, JobResultData, JobStatus
from certiv.remote_exec.function_patcher import FunctionPatcher, create_one_time_wrapper


class TestClosureBasedPatching:
    """Test suite for closure-based function patching and restoration."""

    def test_closure_variables_survive_and_restoration_works(self):
        """
        Test that closure variables survive after create_one_time_wrapper returns,
        and that restoration works correctly when called from different context.
        """

        # Create a test function that will be patched
        def test_add(a: int, b: int) -> int:
            return a + b

        # Store original result
        original_result = test_add(5, 3)
        assert original_result == 8

        # Create mock objects for closure
        mock_module = Mock()
        mock_module.test_add = test_add
        all_references = [(mock_module, "test_add")]

        # Create a patched version that returns different result
        def patched_add(*args, **kwargs):
            return 999  # Return obviously different result

        # Create wrapper using the closure pattern
        wrapper = create_one_time_wrapper(
            original_func=test_add,
            patched_func=patched_add,
            module=mock_module,
            function_name="test_add",
            all_references=all_references,
        )

        # CRITICAL: Verify closure exists and contains our variables
        assert wrapper.__closure__ is not None, "Closure should exist"
        assert len(wrapper.__closure__) > 0, "Closure should contain captured variables"

        # Apply the wrapper to the module (simulate patching)
        mock_module.test_add = wrapper

        # FIRST CALL: Should execute patched version and restore original
        first_result = mock_module.test_add(5, 3)
        assert (
            first_result == 999
        ), "First call should execute patched version (via closure)"

        # SECOND CALL: Should execute original version
        second_result = mock_module.test_add(5, 3)
        assert (
            second_result == 8
        ), "Second call should execute original version (after restoration via closure)"

        # Verify restoration happened correctly via closure
        assert (
            mock_module.test_add == test_add
        ), "Original function should be restored in module"

    def test_full_patching_flow_with_mocked_remote_execution(self):
        """
        Test the complete patching flow from FunctionPatcher through execution and restoration.
        This simulates the real-world scenario where an agent calls a patched function.
        """
        # Create a test function in a mock module
        test_module = Mock()
        test_module.__name__ = "test_module"

        def multiply(x: int, y: int) -> int:
            return x * y

        test_module.multiply = multiply

        # Add module to sys.modules so find_function_in_modules can find it
        sys.modules["test_module"] = test_module

        try:
            # Mock API client to simulate remote execution
            mock_api_client = Mock(spec=CertivAPIClient)

            # Mock execute_remote to return operation_id
            mock_execute_response = ExecutionOperation(
                operation_id="test-op-123", status="pending"
            )
            mock_api_client.execute_remote.return_value = mock_execute_response

            # Mock poll_execution_operation to return completed job with result
            mock_job_result = JobResultData(
                result={
                    "function_name": "multiply",
                    "args": [10, 20],
                    "kwargs": {},
                    "result": 500,  # Remote execution returns 500 (not 200)
                    "success": True,
                    "error": None,
                }
            )
            mock_poll_response = JobOperation(
                operation_id="test-op-123",
                status=JobStatus.COMPLETED,
                job_result=mock_job_result,
                error_message=None,
            )
            mock_api_client.poll_execution_operation.return_value = mock_poll_response

            # Create FunctionPatcher with mocked client
            patcher = FunctionPatcher(api_client=mock_api_client)

            # Patch the function
            success = patcher.patch_function_once(
                function_name="multiply", decision_id="decision-123", override=True
            )

            assert success, "Patching should succeed"

            # Verify function was patched (wrapper should be different from original)
            assert test_module.multiply != multiply, "Function should be wrapped"

            # FIRST CALL: Should execute remote version (returns 500 from mock)
            first_result = test_module.multiply(10, 20)
            assert (
                first_result == 500
            ), "First call should execute remote version via closure"

            # Verify API client was called
            assert (
                mock_api_client.execute_remote.called
            ), "Remote execution should be triggered"
            assert (
                mock_api_client.poll_execution_operation.called
            ), "Polling should happen"

            # SECOND CALL: Should execute original version (returns 200)
            second_result = test_module.multiply(10, 20)
            assert (
                second_result == 200
            ), "Second call should execute original version after restoration"

            # Verify restoration happened
            assert (
                test_module.multiply == multiply
            ), "Original function should be restored"

        finally:
            # Cleanup: Remove test module from sys.modules
            if "test_module" in sys.modules:
                del sys.modules["test_module"]

    def test_closure_survives_across_contexts(self):
        """
        Test that demonstrates closure variables survive even when the
        wrapper is passed to a different function/context (like an agent).
        """

        def original_function():
            return "original"

        def patched_function(*args, **kwargs):
            return "patched"

        mock_module = Mock()
        mock_module.func = original_function
        all_references = [(mock_module, "func")]

        # Create wrapper in one context
        wrapper = create_one_time_wrapper(
            original_func=original_function,
            patched_func=patched_function,
            module=mock_module,
            function_name="func",
            all_references=all_references,
        )

        # Simulate passing wrapper to different context (like agent)
        def agent_calls_function(func):
            """Simulates agent in different context calling the function."""
            return func()  # Call with no knowledge of closure internals

        # First call from "agent" context
        result1 = agent_calls_function(wrapper)
        assert result1 == "patched", "First call should use patched version"

        # After first call, restoration should have happened via closure
        assert mock_module.func == original_function, "Original should be restored"

        # Second call should use original
        result2 = agent_calls_function(mock_module.func)
        assert result2 == "original", "Second call should use original version"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
