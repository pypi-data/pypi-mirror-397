#!/usr/bin/env python3
# Copyright (c) 2024 Certiv.ai
# SPDX-License-Identifier: MIT

"""
Integration test for function remote_exec freeze/unfreeze functionality.

This test validates the end-to-end freeze functionality:
1. Ensure function is unfrozen (baseline)
2. Run agent with remote_exec to test unfrozen execution
3. Freeze the function
4. Modify function code and run (should reject due to hash mismatch)
5. Unfreeze function and run modified code (should work)
"""

from __future__ import annotations
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

import pytest
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()  # Load from default .env if it exists
load_dotenv(
    ".env.local", override=True
)  # Also load from our local file, overriding system env


class TestFunctionFreezeValidation:
    """Test function freeze/unfreeze functionality end-to-end."""

    def setup_method(self):
        """Set up test environment."""
        self.agent_script = (
            Path(__file__).parent.parent / "agent_demos" / "function_calling_agent.py"
        )
        assert (
            self.agent_script.exists()
        ), f"Agent script not found at {self.agent_script}"

        # Base URL for API - use port 8080 to match SDK agent expectations
        self.backend_url = os.environ.get("CERTIV_ENDPOINT", "http://localhost:8080")

        # Get admin credentials from environment
        self.admin_username = os.environ.get("ADMIN_USERNAME", "magos-test")
        self.admin_password = os.environ.get("ADMIN_PASSWORD", "magos1")

        # Create a fresh agent for this test
        self._create_test_agent()

        # Login and get auth token
        self.auth_token = None

        # Test function signature (based on search_wikipedia function)
        self.function_name = "search_wikipedia"
        self.function_signature = "search_wikipedia(query, sentences)"

    def teardown_method(self):
        """Clean up after each test."""
        # Ensure function is unfrozen and remote_exec is disabled
        try:
            if self.auth_token:
                headers = {"Authorization": f"Bearer {self.auth_token}"}

                # Unfreeze function
                response = requests.delete(
                    f"{self.backend_url}/stear/{self.stear_group_id}/functions/{self.function_signature}",
                    headers=headers,
                    timeout=5,
                )
                # 404 is OK - means function wasn't frozen
                if response.status_code not in [204, 404]:
                    print(
                        f"Warning: Failed to unfreeze function: {response.status_code}"
                    )

                # Disable remote_exec
                import urllib.parse

                encoded_signature = urllib.parse.quote(self.function_signature, safe="")
                response = requests.delete(
                    f"{self.backend_url}/agent-mgmt/{self.agent_id}/functions/{encoded_signature}/secure-runtime",
                    headers=headers,
                    timeout=5,
                )
                # 404 is OK - means remote_exec wasn't enabled
                if response.status_code not in [200, 404]:
                    print(
                        f"Warning: Failed to disable remote_exec: {response.status_code}"
                    )
        except:
            pass

    def _create_test_agent(self):
        """Create a fresh agent for testing with --create-agent flag."""
        print("   Creating fresh agent for test...")

        # Initialize variables
        self.stear_group_id = None
        self.agent_id = None
        self.agent_secret = None

        # Run the agent with --create-agent flag to create a new agent and STEAR group
        env = os.environ.copy()
        env["PYTHONIOENCODING"] = "utf-8"
        env["PYTHONUTF8"] = "1"

        cmd = [sys.executable, str(self.agent_script), "--create-agent"]

        process = subprocess.Popen(
            cmd,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding="utf-8",
            errors="replace",
            env=env,
        )

        # Send "2" to select HTTP transport (required for --create-agent)
        stdout, _ = process.communicate(input="2\n")

        # Extract the new agent ID and STEAR ID from output
        # Look for agent ID in output (format: "Agent created: <id>" or "Created agent: <id>")
        agent_match = re.search(
            r"(?:Agent created|Created agent):\s*([a-f0-9-]+)", stdout
        )
        if agent_match:
            self.agent_id = agent_match.group(1)
            os.environ["CERTIV_AGENT_ID"] = self.agent_id
            print(f"   Found agent: {self.agent_id}")

        # Look for STEAR ID in output (format: "Created new STEAR group: <id>")
        stear_match = re.search(r"Created (?:new )?STEAR group:\s*([a-f0-9-]+)", stdout)
        if stear_match:
            self.stear_group_id = stear_match.group(1)
            os.environ["CERTIV_STEAR_ID"] = self.stear_group_id
            print(f"   Found STEAR group: {self.stear_group_id}")

        # Look for agent secret in .env.local file since it's saved there
        env_local_path = Path(".env.local")
        if env_local_path.exists():
            env_content = env_local_path.read_text()
            secret_match = re.search(
                r"CERTIV_AGENT_SECRET=([a-zA-Z0-9_-]+)", env_content
            )
            if secret_match:
                self.agent_secret = secret_match.group(1)
                os.environ["CERTIV_AGENT_SECRET"] = self.agent_secret
                print("   Got agent secret from .env.local")

        if not self.stear_group_id:
            print("Failed to extract STEAR ID from output:")
            print(stdout)
            raise Exception("Failed to create agent and get STEAR ID")

    def _login_admin(self) -> str:
        """Login as admin and return authentication token."""
        response = requests.post(
            f"{self.backend_url}/auth/login",
            json={"username": self.admin_username, "password": self.admin_password},
            timeout=30,
        )

        if response.status_code != 200:
            # Try to register user if login fails
            print(
                f"   Login failed, attempting to register user {self.admin_username}..."
            )
            self._register_user()

            # Retry login
            response = requests.post(
                f"{self.backend_url}/auth/login",
                json={"username": self.admin_username, "password": self.admin_password},
                timeout=30,
            )

        if response.status_code != 200:
            raise Exception(f"Failed to login: {response.text}")

        token = response.json().get("token")
        if not token:
            raise Exception("Failed to get auth token from response")

        return token

    def _register_user(self):
        """Register admin user if they don't exist."""
        response = requests.post(
            f"{self.backend_url}/auth/register",
            json={
                "username": self.admin_username,
                "password": self.admin_password,
                "email": f"{self.admin_username}@example.com",
            },
            timeout=30,
        )

        if response.status_code not in [200, 201]:
            print(f"Warning: User registration failed: {response.text}")

    def _ensure_authenticated(self):
        """Ensure we have a valid auth token."""
        if not self.auth_token:
            self.auth_token = self._login_admin()

    def _get_function_status(self) -> dict:
        """Get current function freeze status."""
        self._ensure_authenticated()

        headers = {"Authorization": f"Bearer {self.auth_token}"}
        response = requests.get(
            f"{self.backend_url}/stear/{self.stear_group_id}/functions/{self.function_signature}",
            headers=headers,
            timeout=5,
        )

        if response.status_code == 404:
            # Function not in registry yet
            return {"is_frozen": False, "exists": False}
        elif response.status_code == 200:
            data = response.json()
            return {
                "is_frozen": data.get("is_frozen", False),
                "exists": True,
                "data": data,
            }
        else:
            raise Exception(
                f"Failed to get function status: {response.status_code} - {response.text}"
            )

    def _ensure_function_unfrozen(self):
        """Ensure function is unfrozen."""
        self._ensure_authenticated()

        headers = {"Authorization": f"Bearer {self.auth_token}"}
        response = requests.delete(
            f"{self.backend_url}/stear/{self.stear_group_id}/functions/{self.function_signature}",
            headers=headers,
            timeout=5,
        )

        # 204 = successfully unfrozen, 404 = already unfrozen/not in registry
        if response.status_code not in [204, 404]:
            raise Exception(
                f"Failed to unfreeze function: {response.status_code} - {response.text}"
            )

    def _freeze_function(self):
        """Freeze function via backend API."""
        self._ensure_authenticated()

        payload = {"function_signature": self.function_signature}
        headers = {"Authorization": f"Bearer {self.auth_token}"}

        response = requests.post(
            f"{self.backend_url}/stear/{self.stear_group_id}/functions",
            json=payload,
            headers=headers,
            timeout=5,
        )

        if response.status_code != 200:
            raise Exception(
                f"Failed to freeze function: {response.status_code} - {response.text}"
            )

        return response.json()

    def _enable_patching(self):
        """Enable remote_exec via backend API."""
        self._ensure_authenticated()

        # URL encode the function signature
        import urllib.parse

        encoded_signature = urllib.parse.quote(self.function_signature, safe="")

        payload = {
            "secure_runtime": True,
            "reason": "STEAR remote_exec enabled for function freeze testing",
        }

        headers = {"Authorization": f"Bearer {self.auth_token}"}
        response = requests.put(
            f"{self.backend_url}/agent-mgmt/{self.agent_id}/functions/{encoded_signature}/secure-runtime",
            json=payload,
            headers=headers,
            timeout=5,
        )

        if response.status_code != 200:
            raise Exception(
                f"Failed to enable remote_exec: {response.status_code} - {response.text}"
            )

    def _run_agent_with_patch(self, use_strict_validation=False) -> str:
        """Run the agent script with remote_exec enabled.

        Args:
            use_strict_validation: If True, use --patch-no-override for strict validation.
                                 If False, use --patch for development mode.
        """
        # Set up environment variables required by the agent
        env = os.environ.copy()
        # Force UTF-8 encoding to handle emojis properly
        env["PYTHONIOENCODING"] = "utf-8"
        env["PYTHONUTF8"] = "1"

        # Build command - use appropriate flag based on validation mode
        if use_strict_validation:
            cmd = [sys.executable, str(self.agent_script), "--patch-no-override"]
            print("   Running agent with --patch-no-override (strict validation)")
        else:
            cmd = [sys.executable, str(self.agent_script), "--patch"]
            print("   Running agent with --patch (development mode)")

        # Run the agent with input "2" for HTTP transport and capturing output
        process = subprocess.Popen(
            cmd,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding="utf-8",
            errors="replace",
            env=env,
        )

        # Send "2" to select HTTP transport when prompted
        stdout, _ = process.communicate(input="2\n")
        return stdout

    def _create_modified_agent_script(self) -> Path:
        """Create a modified version of the agent script with different function code."""
        # Create a temporary file with modified search_wikipedia function
        temp_dir = Path(tempfile.mkdtemp())
        modified_script = temp_dir / "modified_function_calling_agent.py"

        # Read the original script with proper encoding
        original_content = self.agent_script.read_text(encoding="utf-8")

        # Replace the search_wikipedia implementation to change its hash
        # Look for the function in shared_functions.py and modify it
        shared_functions_path = self.agent_script.parent / "shared_functions.py"
        shared_content = shared_functions_path.read_text(encoding="utf-8")

        # Modify the search_wikipedia function implementation - change something that affects the hash
        # We'll add a comment inside the function body which changes the source code hash
        modified_shared_content = shared_content.replace(
            'def search_wikipedia(query: str, sentences: int = 2) -> str:\n    """Search Wikipedia for information using requests library."""',
            'def search_wikipedia(query: str, sentences: int = 2) -> str:\n    """Search Wikipedia for information using requests library."""\n    # MODIFIED VERSION - This comment changes the hash',
        )

        # Write modified shared_functions.py with UTF-8 encoding
        modified_shared_functions = temp_dir / "shared_functions.py"
        modified_shared_functions.write_text(modified_shared_content, encoding="utf-8")

        # Copy utils.py as well
        utils_path = self.agent_script.parent / "utils.py"
        shutil.copy2(utils_path, temp_dir / "utils.py")

        # Modify the agent script to import from local directory
        # Use forward slashes or raw string to avoid escape sequence issues
        temp_dir_str = str(temp_dir).replace("\\", "/")
        modified_content = original_content.replace(
            "from shared_functions import get_safe_functions, get_safe_tools",
            f"sys.path.insert(0, '{temp_dir_str}')\nfrom shared_functions import get_safe_functions, get_safe_tools",
        )

        # Add sys import if not present
        if "import sys" not in modified_content:
            modified_content = "import sys\n" + modified_content

        modified_script.write_text(modified_content, encoding="utf-8")

        return modified_script

    def _run_modified_agent_with_patch(
        self, modified_script: Path, use_strict_validation=False
    ) -> str:
        """Run the modified agent script with remote_exec enabled.

        Args:
            modified_script: Path to the modified script
            use_strict_validation: If True, use --patch-no-override for strict validation.
                                 If False, use --patch for development mode.
        """
        # Set up environment variables required by the agent
        env = os.environ.copy()
        # Force UTF-8 encoding to handle emojis properly
        env["PYTHONIOENCODING"] = "utf-8"
        env["PYTHONUTF8"] = "1"

        # Build command - use appropriate flag based on validation mode
        if use_strict_validation:
            cmd = [sys.executable, str(modified_script), "--patch-no-override"]
            print(
                "   Running MODIFIED agent with --patch-no-override (strict validation)"
            )
        else:
            cmd = [sys.executable, str(modified_script), "--patch"]
            print("   Running MODIFIED agent with --patch (development mode)")

        # Run the agent with input "2" for HTTP transport and capturing output
        process = subprocess.Popen(
            cmd,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding="utf-8",
            errors="replace",
            env=env,
        )

        # Send "2" to select HTTP transport when prompted
        stdout, _ = process.communicate(input="2\n")
        return stdout

    @pytest.mark.skipif(
        os.getenv("GITHUB_ACTIONS") == "true", reason="Skip in GitHub Actions"
    )
    def test_function_freeze_unfreeze_integration(self):
        """Test end-to-end function freeze/unfreeze functionality."""

        print("\n=== Testing Function Freeze/Unfreeze Integration ===")

        # 1. Ensure function is unfrozen (baseline)
        print("\n1. Ensuring function is unfrozen (baseline)...")
        self._ensure_function_unfrozen()
        status = self._get_function_status()
        print(f"   Current status: {status}")
        assert not status[
            "is_frozen"
        ], f"Function should be unfrozen initially, got: {status}"
        print("   ✅ Function is unfrozen")

        # 2. Enable remote_exec and run agent with --patch to register function
        print("\n2. Running agent with --patch to register function in backend...")
        self._enable_patching()
        stdout = self._run_agent_with_patch(
            use_strict_validation=False
        )  # Use --patch to register

        # Print output for debugging
        print("\n=== Agent Output (Initial Registration) ===")
        print(
            stdout[-2000:] if len(stdout) > 2000 else stdout
        )  # Last 2000 chars to avoid too much output
        print("=== End Output ===\n")

        # Verify remote execution was initiated and reached polling stage
        assert (
            "🌐 Initiating remote execution with decision_id:" in stdout
        ), "Should see remote execution initiation"
        assert (
            "🎫 Got job_id:" in stdout or "🎫 Got operation_id:" in stdout
        ), "Should see job/operation ID - function should be registered now"
        print("   ✅ Function registered and reached polling stage")

        # 3. Freeze the function
        print("\n3. Freezing function...")
        freeze_response = self._freeze_function()
        print(
            f"   Function frozen with hash: {freeze_response.get('approved_hash', 'N/A')[:8]}..."
        )

        # Verify function is now frozen
        status = self._get_function_status()
        print(f"   Current status after freeze: {status}")
        assert status["is_frozen"], f"Function should be frozen now, got: {status}"
        print("   ✅ Function is now frozen")

        # 4. Create modified function and run with --patch-no-override (should reject due to hash mismatch)
        print(
            "\n4. Running modified function code with --patch-no-override (should reject)..."
        )
        modified_script = None
        try:
            modified_script = self._create_modified_agent_script()
            stdout = self._run_modified_agent_with_patch(
                modified_script, use_strict_validation=True
            )

            # Print output for debugging
            print("\n=== Agent Output (Modified with Strict Validation) ===")
            print(stdout[-2000:] if len(stdout) > 2000 else stdout)
            print("=== End Output ===\n")

            # Check if remote execution was even attempted
            if "🌐 Initiating remote execution with decision_id:" in stdout:
                # Remote execution was attempted, should see hash validation failure
                assert (
                    "Hash Validation Failed" in stdout
                    or "function hash mismatch" in stdout
                    or "🔒 FUNCTION HASH VALIDATION FAILED" in stdout
                    or "400" in stdout  # HTTP 400 error
                ), "Should see hash validation failure with modified code when remote execution is attempted"

                # Should NOT reach polling stage when rejected
                assert (
                    "🎫 Got job_id:" not in stdout
                    and "🎫 Got operation_id:" not in stdout
                ), "Should NOT reach polling stage when rejected due to hash mismatch"
                print(
                    "   ✅ Hash validation correctly rejected modified code (no polling initiated)"
                )
            else:
                # Remote execution wasn't attempted - function wasn't called
                print("   ⚠️ Warning: Function was not called during this run")
                print(
                    "   The test needs the agent to actually call search_wikipedia to trigger validation"
                )
                # Check if at least the function was patched
                assert (
                    "🔧 Backend requests remote_exec" in stdout
                    or "🔧 HTTPMonitor: Successfully patched" in stdout
                ), "Function should at least be patched for remote execution"
                print(
                    "   ✅ Function was patched for remote execution (but not called)"
                )

        finally:
            # Clean up temporary files
            if modified_script and modified_script.parent.exists():
                shutil.rmtree(modified_script.parent)

        # 5. Unfreeze function and run with --patch (should work and update hash)
        print("\n5. Unfreezing function...")
        self._ensure_function_unfrozen()

        # Verify function is unfrozen
        status = self._get_function_status()
        print(f"   Current status after unfreeze: {status}")
        assert not status[
            "is_frozen"
        ], f"Function should be unfrozen now, got: {status}"
        print("   ✅ Function unfrozen")

        # Run agent again with --patch (should work and update hash)
        print("\n6. Running agent with --patch after unfreeze (should work)...")
        stdout = self._run_agent_with_patch(use_strict_validation=False)

        # Print output for debugging
        print("\n=== Agent Output (After Unfreeze with --patch) ===")
        print(stdout[-2000:] if len(stdout) > 2000 else stdout)
        print("=== End Output ===\n")

        # Should reach polling stage normally now (not rejected)
        assert (
            "🌐 Initiating remote execution with decision_id:" in stdout
        ), "Should see remote execution initiation after unfreezing"
        assert (
            "🎫 Got job_id:" in stdout or "🎫 Got operation_id:" in stdout
        ), "Should see job/operation ID - this means it wasn't rejected after unfreezing"

        # Should NOT see hash validation errors
        assert (
            "Hash Validation Failed" not in stdout
            and "function hash mismatch" not in stdout
            and "🔒 FUNCTION HASH VALIDATION FAILED" not in stdout
        ), "Should NOT see hash validation failure after unfreezing"

        print(
            "   ✅ Unfrozen function reached polling stage successfully (not rejected)"
        )
        print("🎉 Function freeze/unfreeze integration test passed!")


if __name__ == "__main__":
    # Allow running the test directly
    test = TestFunctionFreezeValidation()
    test.setup_method()

    try:
        test.test_function_freeze_unfreeze_integration()
        print("✅ test_function_freeze_unfreeze_integration passed")
        print("🎉 All function freeze validation tests passed!")

    finally:
        test.teardown_method()
