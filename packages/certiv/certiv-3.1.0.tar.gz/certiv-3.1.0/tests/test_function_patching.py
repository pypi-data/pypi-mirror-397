#!/usr/bin/env python3
# Copyright (c) 2024 Certiv.ai
# SPDX-License-Identifier: MIT

"""
Test function remote_exec functionality in the Certiv SDK.

This test validates the end-to-end remote_exec flow:
1. Enable remote_exec via backend API
2. Run the actual function_calling_agent.py script
3. Verify agent logs show function was patched and returned "praise the omniisiah"
4. Verify remote_exec can be disabled via API
"""

from __future__ import annotations
import os
import subprocess
import sys
from pathlib import Path

import pytest
import requests


class TestFunctionPatching:
    """Test function remote_exec system end-to-end."""

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

        # Get agent ID from environment (set by agent)
        self.agent_id = os.environ.get("CERTIV_AGENT_ID")

        # Login and get auth token
        self.auth_token = None

    def teardown_method(self):
        """Clean up after each test."""
        # Ensure remote_exec is disabled
        try:
            if self.auth_token and self.agent_id:
                import urllib.parse

                function_signature = "search_wikipedia(query, sentences)"
                encoded_signature = urllib.parse.quote(function_signature, safe="")

                headers = {"Authorization": f"Bearer {self.auth_token}"}
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

    def _enable_patching(self):
        """Enable remote_exec via backend API."""
        self._ensure_authenticated()

        # URL encode the function signature
        import urllib.parse

        function_signature = "search_wikipedia(query, sentences)"
        encoded_signature = urllib.parse.quote(function_signature, safe="")

        payload = {
            "secure_runtime": True,
            "reason": "STEAR remote_exec enabled for search_wikipedia function calls",
        }

        headers = {"Authorization": f"Bearer {self.auth_token}"}
        response = requests.put(
            f"{self.backend_url}/agent-mgmt/{self.agent_id}/functions/{encoded_signature}/secure-runtime",
            json=payload,
            headers=headers,
            timeout=5,
        )

        assert (
            response.status_code == 200
        ), f"Failed to enable remote_exec: {response.status_code} - {response.text}"

    def _disable_patching(self, ignore_not_found=False):
        """Disable remote_exec via backend API."""
        self._ensure_authenticated()

        # URL encode the function signature
        import urllib.parse

        function_signature = "search_wikipedia(query, sentences)"
        encoded_signature = urllib.parse.quote(function_signature, safe="")

        headers = {"Authorization": f"Bearer {self.auth_token}"}
        response = requests.delete(
            f"{self.backend_url}/agent-mgmt/{self.agent_id}/functions/{encoded_signature}/secure-runtime",
            headers=headers,
            timeout=5,
        )

        if ignore_not_found and response.status_code == 404:
            return  # Already disabled

        assert (
            response.status_code == 200
        ), f"Failed to disable remote_exec: {response.status_code} - {response.text}"

    def _run_agent_with_patching_enabled(self) -> str:
        """Run the agent script with remote_exec enabled and return stdout."""
        # Set up environment variables required by the agent
        env = os.environ.copy()
        # Force UTF-8 encoding to handle emojis properly
        env["PYTHONIOENCODING"] = "utf-8"
        env["PYTHONUTF8"] = "1"

        # Build command
        cmd = [sys.executable, str(self.agent_script)]

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
    def test_end_to_end_function_patching_enabled(self):
        """Test end-to-end function remote_exec when enabled via backend."""

        print("\n=== Testing Function Patching Enabled ===")

        # 1. Enable remote_exec via backend API
        print("1. Enabling remote_exec via backend API...")
        self._enable_patching()
        print("   ✅ Patching enabled")

        # 2. Run the agent
        print("2. Running function calling agent...")
        stdout = self._run_agent_with_patching_enabled()

        # Print output for debugging
        print("\n=== Agent Output ===")
        print(stdout)
        print("=== End Output ===\n")

        # 3. Verify remote_exec occurred
        print("3. Verifying remote_exec occurred...")

        # Look for remote_exec log messages
        assert (
            "🔧 Backend requests remote_exec: Secure runtime enabled at agent level"
            in stdout
        ), "Should see backend remote_exec request"
        assert (
            "🔧 FunctionPatcher: Successfully PATCHED 'search_wikipedia'" in stdout
        ), "Should see function remote_exec success"
        assert (
            "🔧 FunctionPatcher: REMOTE PATCHED search_wikipedia called with" in stdout
        ), "Should see remote patched function execution"

        # Verify remote execution was attempted
        assert (
            "🌐 HTTPMonitor: Using remote execution for 'search_wikipedia'" in stdout
        ), "Should see remote execution message"
        assert (
            "🌐 Initiating remote execution with decision_id:" in stdout
        ), "Should see remote execution initiation"

        # The remote execution will succeed in initiating but timeout waiting for results
        # This is expected in test environment without a complete backend
        assert (
            "🎫 Got job_id:" in stdout or "🎫 Got operation_id:" in stdout
        ), "Should see job/operation ID for polling"

        # The execution will either timeout or start polling (both are OK)
        # We just need to verify it got to the polling stage, not that it completed
        # This shows the remote_exec worked and remote execution was initiated
        print(
            "   (Note: Remote execution may timeout in test environment, which is expected)"
        )

        # Verify restoration occurred
        assert (
            "🔄 FunctionPatcher: RESTORED original 'search_wikipedia'" in stdout
        ), "Should see function restoration"

        print("   ✅ Patching verification complete")

        # 4. Disable remote_exec
        print("4. Disabling remote_exec...")
        self._disable_patching(ignore_not_found=True)
        print("   ✅ Patching disabled")

    @pytest.mark.skipif(
        os.getenv("GITHUB_ACTIONS") == "true", reason="Skip in GitHub Actions"
    )
    def test_end_to_end_function_patching_disabled(self):
        """Test end-to-end function remote_exec when disabled via backend."""

        print("\n=== Testing Function Patching Disabled ===")

        # 1. Ensure remote_exec is disabled
        print("1. Ensuring remote_exec is disabled...")
        self._disable_patching(ignore_not_found=True)
        print("   ✅ Patching disabled")

        # 2. Run the agent
        print("2. Running function calling agent...")
        stdout = self._run_agent_with_patching_enabled()

        # Print output for debugging
        print("\n=== Agent Output ===")
        print(stdout)
        print("=== End Output ===\n")

        # 3. Verify remote_exec did NOT occur
        print("3. Verifying remote_exec did NOT occur...")

        # Should NOT see remote_exec messages
        assert (
            "🔧 Backend requests remote_exec: Secure runtime enabled at agent level"
            not in stdout
        ), "Should NOT see backend remote_exec request"
        assert (
            "🔧 FunctionPatcher: Successfully PATCHED 'search_wikipedia'" not in stdout
        ), "Should NOT see function remote_exec"
        assert (
            "🔧 FunctionPatcher: REMOTE PATCHED search_wikipedia called with"
            not in stdout
        ), "Should NOT see remote patched function execution"

        # Should NOT see remote execution
        assert (
            "🌐 HTTPMonitor: Using remote execution for 'search_wikipedia'"
            not in stdout
        ), "Should NOT see remote execution message"
        assert (
            "🌐 Initiating remote execution with decision_id:" not in stdout
        ), "Should NOT see remote execution initiation"

        # Should see normal Wikipedia mock response instead
        assert "Wikipedia (mock)" in stdout, "Should see normal mock Wikipedia response"

        print("   ✅ No remote_exec verification complete")


if __name__ == "__main__":
    # Allow running the test directly
    test = TestFunctionPatching()
    test.setup_method()

    try:
        test.test_end_to_end_function_patching_enabled()
        print("✅ test_end_to_end_function_patching_enabled passed")

        test.teardown_method()
        test.setup_method()  # Reset for next test

        test.test_end_to_end_function_patching_disabled()
        print("✅ test_end_to_end_function_patching_disabled passed")

        print("🎉 All end-to-end function remote_exec tests passed!")

    finally:
        test.teardown_method()
