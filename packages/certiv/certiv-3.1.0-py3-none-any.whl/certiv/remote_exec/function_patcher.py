# Copyright (c) 2024 Certiv.ai
# SPDX-License-Identifier: MIT

"""
Direct function remote_exec for runtime function replacement.

This module provides the capability to temporarily patch functions in user code
at runtime, execute them once with modified behavior, then restore original
implementations. Designed for policy enforcement scenarios where function
outputs need to be controlled without modifying source code.
"""
import hashlib
import re
import sys
from typing import Any, Callable

from ..api import CertivAPIClient
from ..api.types import ApiError, JobStatus, RemoteExecution
from ..logger import logger
from .parser.function_serializer import (
    extract_remote_execution_result,
    get_function_code_for_hashing,
    serialize_function_for_remote_execution,
)
from .parser.requirements_resolver import detect_third_party_dependencies


class FunctionPatcher:
    """Handles runtime remote_exec of functions with automatic restoration."""

    def __init__(self, api_client: CertivAPIClient):
        """Initialize the function patcher."""
        self.api_client = api_client

    def patch_function_once(
        self, function_name: str, decision_id: str, override: bool = True
    ) -> bool:
        """
        Patch a function to execute with modified behavior for one execution only.
        All patched functions now use remote execution via backend polling.

        Args:
            function_name: Name of the function to patch
            decision_id: The decision ID from the policy response for this specific function call
            override: Whether to patch the function only once

        Returns:
            True if remote_exec successful, False otherwise
        """
        # Find the function in loaded modules
        module, original_func, module_name = find_function_in_modules(function_name)

        if module is None or original_func is None:
            logger.warn(
                f"FunctionPatcher: Cannot patch '{function_name}' - function not found"
            )
            return False

        try:
            # Find all references to this function in memory
            all_references = find_all_function_references(original_func)

            # Always use remote execution patch now
            patched_func = self._create_remote_execution_patch(
                function_name, original_func, decision_id, override
            )

            # Create one-time wrapper
            wrapper_func = create_one_time_wrapper(
                original_func, patched_func, module, function_name, all_references
            )

            # Apply patch to ALL references we found
            for container, key_or_attr in all_references:
                try:
                    if isinstance(container, dict):
                        logger.warn(
                            f"🔧 FunctionPatcher: Patching dictionary reference '{key_or_attr}'"
                        )
                        container[key_or_attr] = wrapper_func
                    else:
                        logger.warn(
                            f"🔧 FunctionPatcher: Patching attribute reference '{key_or_attr}'"
                        )
                        setattr(container, key_or_attr, wrapper_func)
                except Exception as e:
                    logger.debug(
                        f"FunctionPatcher: Could not patch reference {key_or_attr}: {e}"
                    )

            # Also apply patch to the original module (in case we missed it)
            setattr(module, function_name, wrapper_func)

            logger.warn(
                f"🔧 FunctionPatcher: Successfully PATCHED '{function_name}' in module '{module_name}'"
            )
            return True

        except Exception as e:
            logger.error(f"FunctionPatcher: Failed to patch '{function_name}': {e}")
            return False

    def _create_remote_execution_patch(
        self,
        function_name: str,
        original_func: Callable,
        decision_id: str,
        override: bool,
    ) -> Callable:
        """
        Create a patched version of a function that executes remotely via backend.

        Args:
            function_name: Name of the function being patched
            original_func: The original function to patch
            decision_id: The decision ID from the policy response for this specific function call

        Returns:
            Patched function that executes remotely and returns the result
        """

        def patched_function(*args, **kwargs):
            """Patched function that executes remotely via backend."""
            logger.warn(
                f"🔧 FunctionPatcher: REMOTE PATCHED {function_name} called with args={args}, kwargs={kwargs}"
            )
            logger.warn(f"🎫 Using decision_id from closure: {decision_id}")

            # Try to get transport instance for remote execution
            try:
                logger.warn(
                    f"🌐 Initiating remote execution with decision_id: {decision_id}"
                )

                # Serialize the original function code for remote execution
                function_code = serialize_function_for_remote_execution(
                    original_func, function_name, args, kwargs
                )

                # Detect third-party dependencies needed by the function
                dependencies = detect_third_party_dependencies(
                    original_func, function_code
                )

                # Generate function signature from the actual function object
                import inspect

                try:
                    sig = inspect.signature(original_func)
                    param_names = [param.name for param in sig.parameters.values()]
                    function_signature = f"{function_name}({', '.join(param_names)})"
                except Exception as e:
                    logger.warn(
                        f"Failed to get signature via inspect: {e}, falling back to regex"
                    )
                    function_signature = _generate_function_signature(
                        function_name, function_code
                    )

                # Generate hash for freeze functionality - hash only the function source, not execution wrapper
                function_code_for_hashing = get_function_code_for_hashing(original_func)
                function_hash = generate_hash(function_code_for_hashing)

                logger.warn(
                    f"🧊 Cached function with hash: {function_hash[:8]}... and signature: {function_signature}"
                )

                # Default override flag to True (development mode)
                logger.warn(f"🔧 Using override flag: {override}")

                # Build typed RemoteExecution request
                execution = RemoteExecution(
                    decision_id=decision_id,
                    function_name=function_name,
                    function_signature=function_signature,
                    args=list(args),
                    kwargs=kwargs,
                    function_code=function_code,
                    function_hash=function_hash,
                    dependencies=dependencies,
                    override=override,
                )
                logger.warn(f"🌐 Sending remote execution request for {function_name}")

                try:
                    # Send request via API client
                    response = self.api_client.execute_remote(execution)
                    operation_id = response.operation_id

                    logger.warn(f"🎫 Got job_id: {operation_id}, starting polling...")

                    # Poll for results
                    import time

                    max_attempts = 30  # 30 seconds timeout
                    poll_interval = 1  # 1 second between polls

                    for attempt in range(max_attempts):
                        try:
                            # Poll via API client - returns JobOperation
                            job_operation = self.api_client.poll_execution_operation(
                                operation_id
                            )

                            logger.debug(
                                f"🔄 Poll attempt {attempt + 1}: status = {job_operation.status.value}"
                            )

                            if job_operation.status == JobStatus.COMPLETED:
                                result = job_operation.job_result
                                logger.warn(
                                    f"✅ Remote execution completed with result: {result}"
                                )

                                # Extract and return the function result
                                return extract_remote_execution_result(
                                    result, function_name
                                )
                            elif job_operation.status == JobStatus.FAILED:
                                error = job_operation.error_message or "Unknown error"
                                logger.error(f"❌ Remote execution failed: {error}")
                                return f"[Remote execution failed: {error}]"
                            elif job_operation.status in [
                                JobStatus.PENDING,
                                JobStatus.RUNNING,
                            ]:
                                # Still processing, wait and retry
                                logger.debug(
                                    f"🔄 Job status: {job_operation.status.value}"
                                )
                                time.sleep(poll_interval)
                            else:
                                logger.warn(
                                    f"⚠️ Unknown status: {job_operation.status.value}"
                                )
                                time.sleep(poll_interval)

                        except ApiError as poll_error:
                            # Handle polling errors
                            logger.warn(
                                f"⚠️ Polling error (attempt {attempt + 1}): {poll_error.message}"
                            )
                            if poll_error.status_code and poll_error.status_code >= 500:
                                # Server error (5xx), retry
                                logger.debug("🔄 Server error, retrying...")
                                time.sleep(poll_interval)
                                continue
                            else:
                                # Client error (4xx) or other, don't retry
                                error_body = (
                                    poll_error.context.get("response_body", "")
                                    if poll_error.context
                                    else ""
                                )
                                logger.error(
                                    f"❌ Polling failed with client error: {error_body or poll_error.message}"
                                )
                                return f"[Polling failed: {error_body or poll_error.message}]"

                    # Timeout
                    logger.error(
                        f"⏱️ Remote execution timed out after {max_attempts} seconds"
                    )
                    return f"[Remote execution timeout for {function_name}]"

                except ApiError as e:
                    # Handle API client errors
                    error_body = e.context.get("response_body", "") if e.context else ""
                    logger.error(
                        f"❌ HTTP {e.status_code} error from remote execution: {error_body}"
                    )

                    # Special handling for 400 Bad Request (hash validation errors)
                    if e.status_code == 400:
                        if (
                            "function hash mismatch" in error_body
                            or "function not frozen" in error_body
                        ):
                            logger.error(
                                f"🔒 FUNCTION HASH VALIDATION FAILED: {error_body}"
                            )
                            logger.error(
                                "💡 This means the function code has been modified since it was frozen."
                            )
                            logger.error(
                                "💡 Use --patch (without --patch-no-override) to update the frozen version."
                            )
                            # Raise an exception to prevent retry behavior
                            raise Exception(
                                f"Hash Validation Failed: {error_body}"
                            ) from e
                        else:
                            logger.error(f"🔒 Bad Request (400): {error_body}")
                            raise Exception(f"Bad Request: {error_body}") from e
                    else:
                        raise Exception(
                            f"HTTP {e.status_code} Error: {error_body}"
                        ) from e
                except Exception as e:
                    logger.error(f"❌ Remote execution error: {e}")
                    raise

            except Exception as e:
                # Re-raise hash validation errors to prevent retry behavior
                if "Hash Validation Failed" in str(e):
                    logger.error(f"❌ Remote execution setup failed: {e}")
                    raise e
                logger.error(f"❌ Remote execution setup failed: {e}")
                return f"[Remote execution setup failed: {str(e)}]"

        # Copy function signature to preserve type hints
        patched_function.__name__ = original_func.__name__
        patched_function.__doc__ = (
            f"Remote execution patched version of {function_name}"
        )

        return patched_function


def create_one_time_wrapper(
    original_func: Callable,
    patched_func: Callable,
    module: Any,
    function_name: str,
    all_references: list,
) -> Callable:
    """
    Create a wrapper that executes patched function once, then restores original.

    Args:
        original_func: Original function implementation
        patched_func: Patched function implementation
        module: Module containing the function
        function_name: Name of the function
        all_references: List of (container, key/attr) tuples where function is referenced

    Returns:
        Wrapper function that handles one-time execution and restoration
    """
    execution_count = {"count": 0}

    def one_time_wrapper(*args, **kwargs):
        execution_count["count"] += 1
        logger.warn(
            f"🔧 FunctionPatcher: one_time_wrapper called for '{function_name}' (execution #{execution_count['count']})"
        )

        if execution_count["count"] == 1:
            logger.warn(
                f"🔧 FunctionPatcher: Executing PATCHED version of '{function_name}'"
            )
            try:
                # Execute patched version
                result = patched_func(*args, **kwargs)

                # Immediately restore original function after first execution
                _restore_function_all_references(
                    original_func, all_references, module, function_name
                )

                return result
            except Exception as e:
                logger.error(
                    f"FunctionPatcher: Error in patched function execution: {e}"
                )
                # Restore original on error
                _restore_function_all_references(
                    original_func, all_references, module, function_name
                )
                raise
        else:
            logger.debug(
                f"FunctionPatcher: Executing ORIGINAL version of '{function_name}' (execution #{execution_count['count']})"
            )
            return original_func(*args, **kwargs)

    return one_time_wrapper


def find_all_function_references(target_function: Callable) -> list:
    """
    Find all references to a function object in memory.

    Args:
        target_function: The function object to find references to

    Returns:
        List of (container, key/attr_name) tuples where the function is referenced
    """
    import gc

    references = []

    # Get all objects that reference our target function
    for obj in gc.get_referrers(target_function):
        try:
            # Check if it's a dictionary (like function_map, COMMON_FUNCTION_MAP, etc.)
            if isinstance(obj, dict):
                for key, value in obj.items():
                    if value is target_function:
                        references.append((obj, key))
                        logger.debug(
                            f"FunctionPatcher: Found function reference in dict key '{key}'"
                        )

            # Check if it's a module
            elif hasattr(obj, "__dict__"):
                for attr_name in dir(obj):
                    try:
                        if getattr(obj, attr_name) is target_function:
                            references.append((obj, attr_name))
                            logger.debug(
                                f"FunctionPatcher: Found function reference as attribute '{attr_name}'"
                            )
                    except (AttributeError, TypeError):
                        continue

        except (TypeError, AttributeError, RuntimeError):
            # Some objects can't be introspected safely
            continue

    logger.debug(f"FunctionPatcher: Found {len(references)} references to function")
    return references


def find_function_in_modules(function_name: str) -> tuple[Any, Callable, str]:
    """
    Find a function by name in loaded modules.

    Args:
        function_name: Name of the function to find

    Returns:
        Tuple of (module, function, module_name) or (None, None, None) if not found
    """
    logger.debug(
        f"FunctionPatcher: Searching for function '{function_name}' in loaded modules"
    )

    # Search through all loaded modules
    for module_name, module in sys.modules.items():
        if module is None:
            continue

        try:
            if hasattr(module, function_name):
                func = getattr(module, function_name)
                if callable(func):
                    logger.debug(
                        f"FunctionPatcher: Found function '{function_name}' in module '{module_name}'"
                    )
                    return module, func, module_name
        except Exception as e:
            logger.debug(f"FunctionPatcher: Error checking module '{module_name}': {e}")
            continue

    logger.warn(
        f"FunctionPatcher: Function '{function_name}' not found in any loaded module"
    )
    return None, None, None


def _generate_function_signature(function_name: str, function_code: str) -> str:
    """Generate function signature from function name and code.

    Args:
        function_name: Name of the function
        function_code: Function code

    Returns:
        Function signature in format "function_name(param1, param2)"
    """
    # Try to extract function definition from code
    # Look for pattern: def function_name(...):
    def_pattern = rf"def\s+{re.escape(function_name)}\s*\(([^)]*)\)\s*:"
    match = re.search(def_pattern, function_code)

    if match:
        # Extract parameter names from the function definition
        params_str = match.group(1).strip()
        if not params_str:
            return f"{function_name}()"

        # Parse parameters - simple parsing, ignores defaults for signature
        param_names = []
        params = params_str.split(",")
        for param in params:
            # Extract just the parameter name (before any = or : annotations)
            param_trimmed = param.strip()
            if not param_trimmed:
                continue

            # Handle parameter with default values or type annotations
            param_name = param_trimmed
            if "=" in param_name:
                param_name = param_name.split("=")[0].strip()
            if ":" in param_name:
                param_name = param_name.split(":")[0].strip()

            if param_name:
                param_names.append(param_name)

        return f"{function_name}({', '.join(param_names)})"

    # Fallback if regex doesn't match
    return f"{function_name}(?)"


def _restore_function_all_references(
    original_func: Callable,
    all_references: list,
    module: Any,
    function_name: str,
):
    """
    Restore original function in all references.

    Args:
        original_func: The original function to restore
        all_references: List of (container, key/attr) tuples where function is referenced
        module: Module containing the function
        function_name: Name of the function
    """
    try:
        # Restore all references
        for container, key_or_attr in all_references:
            try:
                if isinstance(container, dict):
                    logger.warn(
                        f"🔄 FunctionPatcher: Restoring dictionary reference '{key_or_attr}'"
                    )
                    container[key_or_attr] = original_func
                else:
                    logger.warn(
                        f"🔄 FunctionPatcher: Restoring attribute reference '{key_or_attr}'"
                    )
                    setattr(container, key_or_attr, original_func)
            except Exception as e:
                logger.debug(
                    f"FunctionPatcher: Could not restore reference {key_or_attr}: {e}"
                )

        # Also restore the original module attribute
        setattr(module, function_name, original_func)

        logger.warn(
            f"🔄 FunctionPatcher: RESTORED original '{function_name}' in all references"
        )

    except Exception as e:
        logger.error(
            f"FunctionPatcher: Error restoring function '{function_name}': {e}"
        )


def generate_hash(code: str) -> str:
    return hashlib.sha256(code.encode("utf-8")).hexdigest()
