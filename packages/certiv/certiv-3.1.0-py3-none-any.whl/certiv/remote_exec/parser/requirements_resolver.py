# Copyright (c) 2024 Certiv.ai
# SPDX-License-Identifier: MIT

"""
Dependency resolution for function serialization.

This module handles detection and resolution of third-party dependencies
from requirements.txt files and package mappings.
"""

import ast
import inspect
import re
from pathlib import Path
from typing import Callable

from ...logger import logger

STANDARD_LIBRARY = {
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
    "pathlib",
    "urllib",
    "http",
    "email",
    "html",
    "xml",
    "csv",
    "sqlite3",
    "logging",
    "threading",
    "multiprocessing",
    "subprocess",
    "io",
    "tempfile",
    "shutil",
    "glob",
    "fnmatch",
    "argparse",
    "copy",
    "pickle",
    "base64",
    "hashlib",
    "hmac",
    "secrets",
    "uuid",
    "decimal",
    "fractions",
    "statistics",
    "zlib",
    "gzip",
    "bz2",
    "lzma",
    "zipfile",
    "tarfile",
    "configparser",
    "socketserver",
    "ssl",
    "select",
    "selectors",
    "asyncio",
    "queue",
    "sched",
    "mutex",
    "_thread",
    "dummy_threading",
    "contextvars",
    "unittest",
}

PACKAGE_MAPPINGS = {
    "pillow": "pil",
    "beautifulsoup4": "bs4",
    "pyyaml": "yaml",
    "scikit-learn": "sklearn",
    "opencv-python": "cv2",
    "python-dateutil": "dateutil",
}


def detect_third_party_dependencies(
    original_func: Callable, function_code: str
) -> list[str]:
    """
    Detect third-party package dependencies needed by a function.

    This analyzes the function code and cross-references with requirements.txt
    to find the specific package versions that need to be installed.

    Args:
        original_func: The original function object
        function_code: The serialized function code string

    Returns:
        List of package specifications (e.g., ["requests==2.32.4", "numpy>=1.21.0"])
    """
    try:
        # Parse the function code to extract import statements
        tree = ast.parse(function_code)
        third_party_modules = set()

        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    module_name = alias.name.split(".")[0]  # Get root module
                    third_party_modules.add(module_name)
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    module_name = node.module.split(".")[0]  # Get root module
                    third_party_modules.add(module_name)

        # Filter out standard library modules
        third_party_modules = {
            m for m in third_party_modules if m not in STANDARD_LIBRARY
        }

        if not third_party_modules:
            logger.debug("🔍 No third-party modules found in function code")
            return []

        logger.debug(f"🔍 Third-party modules found: {third_party_modules}")

        # Find requirements.txt files in the project hierarchy
        requirements_files = _find_requirements_files(original_func)

        if not requirements_files:
            logger.warn(
                "⚠️ No requirements.txt files found, returning module names as dependencies"
            )
            # Fallback: return the module names directly (pip will try to install them)
            return list(third_party_modules)

        # Parse requirements.txt files to find matching packages
        dependencies = _resolve_dependencies_from_requirements(
            third_party_modules, requirements_files
        )

        logger.debug(f"🔍 Resolved dependencies: {dependencies}")
        return dependencies

    except Exception as e:
        logger.warn(f"⚠️ Failed to detect third-party dependencies: {e}")
        return []


def _find_requirements_files(original_func: Callable) -> list[Path]:
    """Find requirements.txt files in the project hierarchy."""
    requirements_files = []

    try:
        # Get the module where the function is defined
        module = inspect.getmodule(original_func)
        if not module or not hasattr(module, "__file__") or not module.__file__:
            logger.warn("⚠️ Cannot determine module file path for requirements search")
            return requirements_files

        # Start from the module's directory and walk up the hierarchy
        current_path = Path(module.__file__).parent

        # Look for requirements.txt files going up the directory tree
        for _ in range(10):  # Limit search depth to avoid infinite loops
            req_file = current_path / "requirements.txt"
            if req_file.exists():
                requirements_files.append(req_file)
                logger.debug(f"📄 Found requirements.txt: {req_file}")

            # Check if we've reached the root or can't go up further
            if current_path.parent == current_path:
                break
            current_path = current_path.parent

        return requirements_files

    except Exception as e:
        logger.warn(f"⚠️ Error finding requirements files: {e}")
        return requirements_files


def _resolve_dependencies_from_requirements(
    third_party_modules: set[str], requirements_files: list[Path]
) -> list[str]:
    """Resolve dependencies from requirements.txt files."""
    # Parse requirements.txt files to find matching packages
    # Process in two passes: first for exact matches, then for fuzzy matches
    package_specs = {}
    all_packages = []

    # First, collect all packages from requirements files
    for req_file in requirements_files:
        try:
            logger.debug(f"📖 Parsing requirements file: {req_file}")
            with open(req_file, encoding="utf-8") as f:
                for line_num, line in enumerate(f, 1):
                    line = line.strip()

                    # Skip empty lines and comments
                    if not line or line.startswith("#"):
                        continue

                    # Skip -e git+ entries (editable installs)
                    if line.startswith("-e git+"):
                        continue

                    # Parse package specification (package==version, package>=version, etc.)
                    # Handle formats like: requests==2.32.4, numpy>=1.21.0, flask
                    match = re.match(r"^([a-zA-Z0-9_-]+)([>=<!=~]+.*)?", line)
                    if match:
                        package_name = match.group(1).lower()
                        version_spec = match.group(2) or ""
                        full_spec = f"{package_name}{version_spec}"
                        all_packages.append((package_name, full_spec))

        except Exception as e:
            logger.warn(f"⚠️ Error parsing requirements file {req_file}: {e}")
            continue

    # Pass 1: Look for exact matches first
    for module_name in third_party_modules:
        for package_name, full_spec in all_packages:
            if _is_package_match(package_name, module_name):
                package_specs[module_name] = full_spec
                break

    # Pass 2: Look for fuzzy matches for modules not found in pass 1
    remaining_modules = third_party_modules - set(package_specs.keys())
    for module_name in remaining_modules:
        for package_name, full_spec in all_packages:
            if _is_fuzzy_package_match(package_name, module_name):
                package_specs[module_name] = full_spec
                break

    # Return the package specifications
    found_dependencies = list(package_specs.values())

    # For modules we couldn't find in requirements, return the module name
    unfound_modules = third_party_modules - set(package_specs.keys())
    if unfound_modules:
        logger.warn(f"⚠️ Could not find requirements for modules: {unfound_modules}")
        found_dependencies.extend(list(unfound_modules))

    return found_dependencies


def _is_package_match(package_name: str, module_name: str) -> bool:
    """Check if a package matches a module name exactly or via known mappings."""
    package_name = package_name.lower()
    module_name = module_name.lower()

    # Direct match
    if package_name == module_name:
        return True

    # Check known mappings
    if package_name in PACKAGE_MAPPINGS:
        return PACKAGE_MAPPINGS[package_name] == module_name

    return False


def _is_fuzzy_package_match(package_name: str, module_name: str) -> bool:
    """Check if a package matches a module name using fuzzy matching."""
    package_name = package_name.lower()
    module_name = module_name.lower()

    # Check if module name is a substring of package name (e.g., requests-toolbelt contains requests)
    if module_name in package_name:
        return True

    # Check if package name is a substring of module name
    if package_name in module_name:
        return True

    return False
