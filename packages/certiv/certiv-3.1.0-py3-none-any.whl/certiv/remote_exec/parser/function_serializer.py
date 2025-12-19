# Copyright (c) 2024 Certiv.ai
# SPDX-License-Identifier: MIT

"""
Function serialization for remote execution.

This module handles serializing Python functions into executable code strings
that can be transmitted and executed remotely.
"""

import inspect
import json
import textwrap
from typing import Any, Callable

from ...api.types import CertivFunctionResult, JobResultData
from ...logger import logger
from .function_import_analyzer import extract_function_imports


def serialize_function_for_remote_execution(
    original_func: Callable, function_name: str, args: tuple, kwargs: dict
) -> str:
    """
    Serialize a function for remote execution with all necessary imports and dependencies.

    This creates a complete, self-contained Python script that can be executed
    remotely to run the function with the specified arguments.

    Args:
        original_func: The original function object
        function_name: Name of the function
        args: Positional arguments to pass to the function
        kwargs: Keyword arguments to pass to the function

    Returns:
        Complete Python code string that can be executed remotely
    """
    logger.debug(f"🔧 Serializing function '{function_name}' for remote execution")

    try:
        # Get the source code of the function
        function_source = inspect.getsource(original_func)

        # Remove common leading whitespace to get clean code
        function_definition = textwrap.dedent(function_source).strip()

        # Extract imports needed by the function (if function_import_analyzer is available)
        imports = extract_function_imports(original_func, function_source)

        # Convert args and kwargs to JSON strings for embedding in the code
        # Use repr() to properly escape the JSON strings for Python code
        args_json = repr(json.dumps(list(args)))
        kwargs_json = repr(json.dumps(kwargs))

        # Create the complete executable code
        serialized_code = f"""
# === IMPORTS ===
{imports}

# === FUNCTION DEFINITION ===
{function_definition}

# === EXECUTION WRAPPER ===
def execute_function():
    import json

    # Parse arguments from JSON
    args = json.loads({args_json})
    kwargs = json.loads({kwargs_json})

    try:
        # Execute the function with the provided arguments
        function_result = {function_name}(*args, **kwargs)

        # Return structured result
        result = {{
            "function_name": "{function_name}",
            "args": args,
            "kwargs": kwargs,
            "result": function_result,
            "success": True,
            "error": None
        }}

        print("CERTIV_FUNCTION_RESULT:", json.dumps(result))
        return result

    except Exception as e:
        # Return error information
        error_result = {{
            "function_name": "{function_name}",
            "args": args,
            "kwargs": kwargs,
            "result": None,
            "success": False,
            "error": str(e)
        }}

        print("CERTIV_FUNCTION_RESULT:", json.dumps(error_result))
        return error_result

# Execute the function
if __name__ == "__main__":
    execute_function()
""".strip()

        logger.debug(
            f"🔧 Serialized function code length: {len(serialized_code)} characters"
        )
        return serialized_code

    except Exception as e:
        logger.error(f"❌ Failed to serialize function '{function_name}': {e}")
        raise RuntimeError(f"Function serialization failed: {e}") from e


def get_function_code_for_hashing(original_func: Callable) -> str:
    """
    Get only the function source code for consistent hashing.
    This excludes execution wrapper and arguments to ensure the hash
    represents the actual function logic, not the call parameters.

    Args:
        original_func: The original function object

    Returns:
        Just the function source code
    """
    try:
        function_source = inspect.getsource(original_func)
        return textwrap.dedent(function_source).strip()
    except Exception as e:
        logger.error(f"❌ Failed to extract function code for hashing: {e}")
        return ""


def extract_remote_execution_result(
    job_result: JobResultData | None, function_name: str
) -> Any:
    """
    Extract the function result from remote execution job output.

    This parses the structured output from remote execution to get the actual
    function return value or error information.

    Args:
        job_result: The JobResultData from remote execution
        function_name: Name of the function that was executed

    Returns:
        The function's return value, or an error message if execution failed
    """
    if not job_result:
        return f"[No job result available for {function_name}]"

    try:
        # Check if result field has CertivFunctionResult
        if job_result.result:
            if isinstance(job_result.result, CertivFunctionResult):
                if job_result.result.success:
                    logger.debug(f"✅ Function '{function_name}' executed successfully")
                    return job_result.result.result
                else:
                    error_msg = job_result.result.error or "Unknown error"
                    logger.warn(
                        f"⚠️ Function '{function_name}' execution failed: {error_msg}"
                    )
                    return f"[Function execution failed: {error_msg}]"
            elif isinstance(job_result.result, dict):
                # Fallback: backend returned dict instead of CertivFunctionResult
                if job_result.result.get("success", False):
                    logger.debug(
                        f"✅ Function '{function_name}' executed successfully (dict format)"
                    )
                    return job_result.result.get("result")
                else:
                    error_msg = job_result.result.get("error", "Unknown error")
                    logger.warn(
                        f"⚠️ Function '{function_name}' execution failed (dict format): {error_msg}"
                    )
                    return f"[Function execution failed: {error_msg}]"

        # Check output field for CERTIV_FUNCTION_RESULT (if output is dict)
        if job_result.output and isinstance(job_result.output, dict):
            if "CERTIV_FUNCTION_RESULT" in job_result.output:
                result_data = job_result.output["CERTIV_FUNCTION_RESULT"]
                if isinstance(result_data, dict):
                    if result_data.get("success", False):
                        logger.debug(
                            f"✅ Function '{function_name}' executed successfully (from output)"
                        )
                        return result_data.get("result")
                    else:
                        error_msg = result_data.get("error", "Unknown error")
                        logger.warn(
                            f"⚠️ Function '{function_name}' execution failed (from output): {error_msg}"
                        )
                        return f"[Function execution failed: {error_msg}]"

        # Check stdout for function result markers
        stdout = job_result.stdout or (
            job_result.output if isinstance(job_result.output, str) else ""
        )

        if stdout and "CERTIV_FUNCTION_RESULT:" in stdout:
            # Extract the JSON result from stdout
            try:
                import re

                match = re.search(r"CERTIV_FUNCTION_RESULT:\s*(.+)", stdout)
                if match:
                    result_json = match.group(1).strip()
                    result_data = json.loads(result_json)

                    if result_data.get("success", False):
                        logger.debug(
                            f"✅ Function '{function_name}' executed successfully (from stdout)"
                        )
                        return result_data.get("result")
                    else:
                        error_msg = result_data.get("error", "Unknown error")
                        logger.warn(
                            f"⚠️ Function '{function_name}' execution failed (from stdout): {error_msg}"
                        )
                        return f"[Function execution failed: {error_msg}]"

            except json.JSONDecodeError as e:
                logger.error(f"❌ Failed to parse JSON from stdout: {e}")

        # Fallback to returning full stdout
        if stdout:
            logger.debug("🔍 Returning full stdout as result")
            return stdout

        return f"[No output available for {function_name}]"

    except Exception as e:
        logger.error(f"❌ Failed to extract result for '{function_name}': {e}")
        return f"[Error extracting result: {str(e)}]"
