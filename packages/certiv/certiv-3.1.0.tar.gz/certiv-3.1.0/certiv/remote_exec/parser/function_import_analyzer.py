# Copyright (c) 2024 Certiv.ai
# SPDX-License-Identifier: MIT

"""
Import detection for function serialization.

This module analyzes Python functions to detect their import dependencies,
including module-level imports, function-level imports, and third-party dependencies.
"""

import ast
import inspect
from typing import Callable

from ...logger import logger

STANDARD_MODULES = {
    "json",
    "time",
    "datetime",
    "random",
    "math",
    "os",
    "sys",
    "re",
    "collections",
    "itertools",
    "functools",
    "typing",
}


def extract_function_imports(original_func: Callable, function_source: str) -> str:
    """
    Extract import statements required by a function.

    This analyzes both module-level imports and function-level imports
    to determine what imports are needed for the function to work.

    Args:
        original_func: The original function object
        function_source: The source code of the function

    Returns:
        String containing necessary import statements
    """
    imports = []

    # First, get module-level imports that the function uses
    module_imports = _extract_module_level_imports(original_func, function_source)
    if module_imports:
        imports.extend(module_imports.split("\n"))
        logger.debug(f"🔍 Added module-level imports: {module_imports}")

    # Then get function-level imports and other detected imports
    function_level_imports = _extract_function_level_imports(
        original_func, function_source
    )
    if function_level_imports:
        imports.extend(function_level_imports.split("\n"))
        logger.debug(f"🔍 Added function-level imports: {function_level_imports}")

    # Remove duplicates and sort for consistency
    imports = sorted(set(filter(None, imports)))

    logger.debug(f"🔍 Final imports for {original_func.__name__}: {imports}")
    return "\n".join(imports) if imports else ""


def _extract_module_level_imports(original_func: Callable, function_source: str) -> str:
    """
    Extract module-level imports that the function actually uses.
    This parses the entire module file to find file-level imports,
    then analyzes the function to see which ones it actually needs.

    Args:
        original_func: The original function object
        function_source: The source code of the function

    Returns:
        String containing necessary module-level import statements
    """
    try:
        # Get the module where the function is defined
        module = inspect.getmodule(original_func)
        if not module or not hasattr(module, "__file__") or not module.__file__:
            logger.debug(f"No module file found for {original_func.__name__}")
            return ""

        # Read the entire module source code
        try:
            with open(module.__file__, encoding="utf-8") as f:
                module_source = f.read()
        except Exception as e:
            logger.debug(f"Failed to read module file {module.__file__}: {e}")
            return ""

        # Parse the module to extract all top-level imports
        module_tree = ast.parse(module_source)

        # Collect all module-level imports and create name mappings
        import_statements = {}  # name -> import statement
        import_aliases = {}  # alias -> real_name

        for node in module_tree.body:
            if isinstance(node, ast.Import):
                for alias in node.names:
                    name = alias.asname if alias.asname else alias.name
                    import_statements[name] = f"import {alias.name}" + (
                        f" as {alias.asname}" if alias.asname else ""
                    )
                    if alias.asname:
                        import_aliases[alias.asname] = alias.name
            elif isinstance(node, ast.ImportFrom):
                module_name = node.module if node.module else ""
                for alias in node.names:
                    name = alias.asname if alias.asname else alias.name
                    import_statements[name] = (
                        f"from {module_name} import {alias.name}"
                        + (f" as {alias.asname}" if alias.asname else "")
                    )
                    if alias.asname:
                        import_aliases[alias.asname] = alias.name

        # Parse the function to find what names it uses
        function_tree = ast.parse(function_source)
        used_names = set()

        for node in ast.walk(function_tree):
            if isinstance(node, ast.Name):
                used_names.add(node.id)
            elif isinstance(node, ast.Attribute):
                # For x.y.z, we want 'x' (the root module/object)
                if isinstance(node.value, ast.Name):
                    used_names.add(node.value.id)
            elif isinstance(node, ast.Call):
                # For function calls like json.dumps()
                if isinstance(node.func, ast.Attribute) and isinstance(
                    node.func.value, ast.Name
                ):
                    used_names.add(node.func.value.id)

        # Find which module-level imports are actually needed
        needed_imports = []
        for name in used_names:
            if name in import_statements:
                needed_imports.append(import_statements[name])
            # Also check if this name is an alias for something we imported
            elif name in import_aliases:
                real_name = import_aliases[name]
                if real_name in import_statements:
                    needed_imports.append(import_statements[real_name])

        # Remove duplicates and sort
        needed_imports = sorted(set(needed_imports))

        logger.debug(
            f"🔍 Found module-level imports for {original_func.__name__}: {needed_imports}"
        )
        return "\n".join(needed_imports) if needed_imports else ""

    except Exception as e:
        logger.warn(
            f"⚠️ Failed to extract module-level imports for {original_func.__name__}: {e}"
        )
        return ""


def _extract_function_level_imports(
    original_func: Callable, function_source: str
) -> str:
    """
    Extract function-level imports and other imports detected from the module globals.
    This is the original logic that detects imports within the function body
    and checks module globals for standard library imports.

    Args:
        original_func: The original function object
        function_source: The source code of the function

    Returns:
        String containing function-level import statements
    """
    imports = []

    try:
        tree = ast.parse(function_source)

        # Collect all names used in the function
        used_names = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Name):
                used_names.add(node.id)
            elif isinstance(node, ast.Attribute):
                # For x.y.z, we want 'x'
                if isinstance(node.value, ast.Name):
                    used_names.add(node.value.id)
            elif isinstance(node, ast.Call):
                # For function calls
                if isinstance(node.func, ast.Name):
                    used_names.add(node.func.id)
                elif isinstance(node.func, ast.Attribute) and isinstance(
                    node.func.value, ast.Name
                ):
                    used_names.add(node.func.value.id)

        # Get the module where the function is defined
        module = inspect.getmodule(original_func)
        if module:
            # Check which names are available in the module's globals
            module_globals = getattr(module, "__dict__", {})

            # Check for direct module imports (e.g., json.dumps)
            for name in used_names:
                if name in module_globals:
                    obj = module_globals[name]
                    # Check if it's an imported module
                    if inspect.ismodule(obj):
                        module_name = obj.__name__
                        if module_name in STANDARD_MODULES:
                            imports.append(f"import {module_name}")
                    # Check if it's imported from a module (e.g., from datetime import datetime)
                    elif hasattr(obj, "__module__"):
                        if obj.__module__ in ["datetime", "typing", "collections"]:
                            # Handle common from imports
                            if obj.__module__ == "datetime" and name == "datetime":
                                imports.append("from datetime import datetime")
                            elif obj.__module__ == "typing" and name in [
                                "Dict",
                                "List",
                                "Optional",
                                "Any",
                                "Union",
                                "Tuple",
                            ]:
                                imports.append(f"from typing import {name}")
                            elif obj.__module__ == "collections" and name in [
                                "defaultdict",
                                "OrderedDict",
                                "Counter",
                            ]:
                                imports.append(f"from collections import {name}")

            # Special handling for Optional[T] syntax which requires typing import
            if (
                "Optional[" in function_source
                or "List[" in function_source
                or "Dict[" in function_source
            ):
                if not any("from typing import" in imp for imp in imports):
                    # Extract all typing hints used
                    typing_imports = []
                    if "Optional[" in function_source:
                        typing_imports.append("Optional")
                    if "List[" in function_source:
                        typing_imports.append("List")
                    if "Dict[" in function_source:
                        typing_imports.append("Dict")
                    if "Union[" in function_source:
                        typing_imports.append("Union")
                    if "Any" in function_source:
                        typing_imports.append("Any")
                    if typing_imports:
                        imports.append(
                            f"from typing import {', '.join(sorted(set(typing_imports)))}"
                        )

        # Remove duplicates and sort for consistency
        imports = sorted(set(imports))
        logger.debug(
            f"🔍 Extracted function-level imports for {original_func.__name__}: {imports}"
        )
        return "\n".join(imports) if imports else ""

    except Exception as e:
        logger.warn(
            f"⚠️ Failed to extract function-level imports for {original_func.__name__}: {e}"
        )
        # Return basic imports that most functions might need
        return "import json\nfrom typing import Any, Dict, List, Optional"
