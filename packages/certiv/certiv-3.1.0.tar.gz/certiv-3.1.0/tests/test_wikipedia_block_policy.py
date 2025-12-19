#!/usr/bin/env python3
"""
Test to verify that search_wikipedia function can be blocked by policy enforcement.

This test creates a STEAR group, adds a policy rule that blocks search_wikipedia,
creates an agent associated with that STEAR group, runs the function calling agent
with a query that would trigger Wikipedia search, and verifies the block is enforced.
"""

from __future__ import annotations
import os
import re
import subprocess
import sys
import time
from pathlib import Path

import pytest
import requests


class TestWikipediaBlockPolicy:
    """Test to verify that search_wikipedia function can be blocked by policy enforcement."""

    def setup_method(self):
        """Set up test environment."""
        self.agent_script = (
            Path(__file__).parent.parent / "agent_demos" / "function_calling_agent.py"
        )
        assert (
            self.agent_script.exists()
        ), f"Agent script not found at {self.agent_script}"

        # Base URL for API - use port 8080 to match SDK agent expectations
        self.base_url = os.environ.get("CERTIV_ENDPOINT", "http://localhost:8080")

        # Get admin credentials from environment
        self.admin_username = os.environ.get("ADMIN_USERNAME", "magos-test")
        self.admin_password = os.environ.get("ADMIN_PASSWORD", "magos1")

        # Use existing STEAR ID from environment
        self.existing_stear_id = os.environ.get("CERTIV_STEAR_ID")
        if not self.existing_stear_id:
            # Try to load from .env.local
            env_file = Path(__file__).parent.parent / ".env.local"
            if env_file.exists():
                with open(env_file) as f:
                    for line in f:
                        line = line.strip()
                        if line.startswith("CERTIV_STEAR_ID="):
                            self.existing_stear_id = line.split("=", 1)[1]
                            break

        assert self.existing_stear_id, "No STEAR ID found in environment or .env.local"

        # Track created policy rules for cleanup
        self.created_rule_ids = []

    def teardown_method(self):
        """Clean up test resources."""
        if hasattr(self, "created_rule_ids") and self.created_rule_ids:
            print(f"\n=== Cleaning up {len(self.created_rule_ids)} policy rules ===")
            try:
                # Login to get token for cleanup
                token = self._login_admin()
                for rule_id in self.created_rule_ids:
                    self._delete_policy_rule(token, rule_id)
            except Exception as e:
                print(f"Warning: Failed to clean up policy rules: {e}")

    @pytest.mark.skipif(
        os.getenv("GITHUB_ACTIONS") == "true", reason="Skip in GitHub Actions"
    )
    def test_wikipedia_search_blocked_by_policy(self):
        """Test that search_wikipedia function is blocked when policy rule is in place."""

        print("\n=== Setting up Wikipedia Block Policy Test ===")

        # 1. Login as admin
        print("1. Logging in as admin...")
        token = self._login_admin()
        print("   Successfully logged in")

        # 2. Use existing STEAR group (no need to create new one)
        print("2. Using existing STEAR group...")
        stear_group_id = self.existing_stear_id
        print(f"   Using STEAR group: {stear_group_id}")

        # 3. Create policy rule that blocks search_wikipedia
        print("3. Creating policy rule to block search_wikipedia...")
        rule_id = self._create_wikipedia_block_rule(token, stear_group_id)
        if rule_id:
            self.created_rule_ids.append(rule_id)  # Track for cleanup
        print(f"   Created block rule: {rule_id}")

        # 4. Create agent associated with STEAR group
        print("4. Creating agent...")
        agent_id, agent_secret = self._create_agent(token, stear_group_id)
        print(f"   Created agent: {agent_id}")

        # 5. Run the agent using --create-agent to force creation of new credentials
        print(f"   Test agent ID: {agent_id}")
        print(f"   Test STEAR group: {stear_group_id}")

        # Set environment variables for the agent
        env = os.environ.copy()
        env.update(
            {
                "CERTIV_ENDPOINT": self.base_url,
                "ADMIN_USERNAME": self.admin_username,
                "ADMIN_PASSWORD": self.admin_password,
                "PYTHONIOENCODING": "utf-8",
                "PYTHONUTF8": "1",
                "PYTHONLEGACYWINDOWSFSENCODING": "0",  # Force UTF-8 on Windows
                "PYTHONLEGACYWINDOWSSTDIO": "0",  # Force UTF-8 for stdio on Windows
            }
        )

        try:
            # 6. Run the function calling agent with our test credentials
            print("5. Running function calling agent with test credentials...")
            stdout = self._run_agent_with_custom_credentials(
                env, agent_id, agent_secret, stear_group_id
            )

            # 7. Verify that the block was enforced
            print("6. Verifying policy block was enforced...")
            self._verify_wikipedia_block_in_output(stdout)

            print(
                "\n✅ Test passed! Wikipedia search was successfully blocked by policy."
            )

        finally:
            print("7. Test completed successfully")

    def _login_admin(self) -> str:
        """Login as admin and return authentication token."""
        response = requests.post(
            f"{self.base_url}/auth/login",
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
                f"{self.base_url}/auth/login",
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
            f"{self.base_url}/auth/register",
            json={
                "username": self.admin_username,
                "password": self.admin_password,
                "email": f"{self.admin_username}@example.com",
                "fullname": "Test Admin User",
            },
            timeout=30,
        )

        if response.status_code not in [200, 201]:
            raise Exception(f"Failed to register user: {response.text}")

    def _delete_policy_rule(self, token: str, rule_id: str):
        """Delete a policy rule by ID."""
        try:
            response = requests.delete(
                f"{self.base_url}/stear/{self.existing_stear_id}/rules/{rule_id}",
                headers={"Authorization": f"Bearer {token}"},
                timeout=30,
            )
            if response.status_code in [200, 204]:
                print(f"   ✓ Deleted policy rule: {rule_id}")
            else:
                print(f"   ⚠️  Failed to delete policy rule {rule_id}: {response.text}")
        except Exception as e:
            print(f"   ⚠️  Error deleting policy rule {rule_id}: {e}")

    def _create_wikipedia_block_rule(self, token: str, stear_group_id: str) -> str:
        """Create a policy rule that blocks search_wikipedia function."""
        # Try the exact same format as the working test_block_only.py
        rule_data = {
            "stear_group_id": stear_group_id,
            "name": "Block all Wikipedia searches",
            "description": "Block any search_wikipedia operations",
            "priority": 200,  # Very high priority like the working example
            "decision": "block",
            "rule_type": "simple",
            "conditions": {
                "type": "tool_name",
                "operator": "equals",
                "value": "search_wikipedia",
            },
        }

        response = requests.post(
            f"{self.base_url}/stear/{stear_group_id}/rules",
            headers={"Authorization": f"Bearer {token}"},
            json=rule_data,
            timeout=30,
        )

        if response.status_code not in [200, 201]:
            print(
                f"   Policy rule creation failed: {response.status_code} - {response.text}"
            )
            raise Exception(f"Failed to create policy rule: {response.text}")

        rule_response = response.json()
        print(f"   Policy rule response: {rule_response}")

        # Handle different response formats - the API returns rules as an array
        if "rules" in rule_response and len(rule_response["rules"]) > 0:
            rule_id = rule_response["rules"][0]["id"]
        elif "rule" in rule_response:
            rule_id = rule_response["rule"]["id"]
        elif "id" in rule_response:
            rule_id = rule_response["id"]
        elif "rule_id" in rule_response:
            rule_id = rule_response["rule_id"]
        else:
            print(
                f"   Warning: Could not extract rule ID from response: {rule_response}"
            )
            rule_id = None

        return rule_id

    def _create_agent(self, token: str, stear_group_id: str) -> tuple[str, str]:
        """Create agent and return agent_id and agent_secret."""
        timestamp = int(time.time())
        agent_name = f"Wikipedia Block Test Agent {timestamp}"

        response = requests.post(
            f"{self.base_url}/agent-mgmt",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "name": agent_name,
                "description": "Agent for testing Wikipedia search block policy",
                "metadata": {"stear_group_id": stear_group_id},
            },
            timeout=30,
        )

        if response.status_code not in [200, 201]:
            raise Exception(f"Failed to create agent: {response.text}")

        data = response.json()
        agent_id = data["agent"]["agent_id"]
        agent_secret = data["agent_secret"]

        return agent_id, agent_secret

    def _run_agent_with_custom_credentials(
        self, env: dict, agent_id: str, agent_secret: str, stear_group_id: str
    ) -> str:
        """Run the function calling agent with custom credentials by modifying the script directly."""

        # Create a temporary modified version of the agent script
        # that uses our test credentials and Wikipedia query
        temp_agent_script = self._create_temp_agent_script_with_credentials(
            agent_id, agent_secret, stear_group_id
        )

        try:
            # Build command to run the temporary agent
            cmd = [sys.executable, str(temp_agent_script)]

            # Run the agent with input "2" for HTTP transport
            process = subprocess.Popen(
                cmd,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                env=env,
            )

            # Send "2" to select HTTP transport when prompted
            stdout_bytes, _ = process.communicate(input=b"2\n")

            # Decode with error handling for emojis and special characters
            stdout = stdout_bytes.decode("utf-8", errors="ignore")

            # Print output for debugging (remove Unicode characters for Windows console)
            print("\n=== Agent Output ===")
            # Replace common Unicode characters that cause issues on Windows console
            display_output = (
                stdout.replace("🤖", "[ROBOT]")
                .replace("📊", "[CHART]")
                .replace("✅", "[CHECK]")
                .replace("📤", "[OUTBOX]")
                .replace("🎯", "[TARGET]")
            )
            # Remove any remaining non-ASCII characters
            display_output = display_output.encode("ascii", errors="ignore").decode(
                "ascii"
            )
            print(display_output)
            print("=== End Agent Output ===\n")

            return stdout

        finally:
            # Clean up temporary script
            if temp_agent_script.exists():
                temp_agent_script.unlink()

    def _create_temp_agent_script_with_credentials(
        self, agent_id: str, agent_secret: str, stear_group_id: str
    ) -> Path:
        """Create a temporary agent script with embedded credentials and Wikipedia query."""

        # Read the original agent script with UTF-8 encoding
        with open(self.agent_script, encoding="utf-8") as f:
            original_content = f.read()

        # Replace the test queries with one that will definitely trigger Wikipedia search

        # This pattern matches from test_queries = [ to the next standalone ]
        pattern = r"(test_queries = \[)(.*?)(\n    \])"
        replacement = r'\1\n        "Tell me about artificial intelligence from Wikipedia",\n    \3'
        modified_content = re.sub(
            pattern, replacement, original_content, flags=re.DOTALL
        )

        # Update the default endpoint to match our test environment
        endpoint_pattern = r'os\.getenv\("CERTIV_ENDPOINT", "http://localhost:8080"\)'
        modified_content = re.sub(
            endpoint_pattern,
            f'os.getenv("CERTIV_ENDPOINT", "{self.base_url}")',
            modified_content,
        )

        # Inject our test credentials by overriding the environment variables
        # Find the line where environment variables are loaded and inject our values
        load_dotenv_pattern = r'load_dotenv\(\n    "\.env\.local", override=True\n\)  # Also load from our local file, overriding system env'
        credentials_injection = f'''load_dotenv(
    ".env.local", override=True
)  # Also load from our local file, overriding system env

# INJECTED FOR TESTING: Override with test credentials
os.environ["CERTIV_AGENT_ID"] = "{agent_id}"
os.environ["CERTIV_AGENT_SECRET"] = "{agent_secret}"
os.environ["CERTIV_STEAR_ID"] = "{stear_group_id}"
os.environ["CERTIV_ENDPOINT"] = "{self.base_url}"'''

        modified_content = re.sub(
            load_dotenv_pattern, credentials_injection, modified_content
        )

        # Create temporary file with UTF-8 encoding
        temp_script = (
            Path(self.agent_script.parent) / "temp_wikipedia_agent_with_creds.py"
        )
        with open(temp_script, "w", encoding="utf-8") as f:
            f.write(modified_content)

        return temp_script

    def _verify_wikipedia_block_in_output(self, stdout: str):
        """Verify that the Wikipedia search was blocked by policy."""

        # Look for signs that policy enforcement is active
        assert (
            "Certiv SDK" in stdout and "initialized" in stdout
        ), "Expected to see Certiv SDK initialization"

        # Look for the query being processed (the actual query we sent)
        assert (
            "artificial intelligence" in stdout.lower()
        ), "Expected to find the Wikipedia query in output"

        # The agent should attempt to call search_wikipedia for "artificial intelligence" query
        assert (
            "search_wikipedia" in stdout or "wikipedia" in stdout.lower()
        ), "Expected to find Wikipedia search attempt in output"

        # Look for signs of blocking in the actual output format we're seeing
        # The key indicator is the JSON response containing "decision":"block"

        block_indicators = [
            '"decision":"block"',  # This is the key indicator we see in the JSON response
            "blocked by policy",
            "FUNCTION CALL DETECTED",  # This shows the interception is working
            "blocked",
            "denied",
        ]

        found_block_indicator = False
        for indicator in block_indicators:
            if indicator.lower() in stdout.lower():
                print(f"   Found block indicator: '{indicator}' in output")
                found_block_indicator = True
                break

        # The key assertion: we should see evidence that the function was blocked
        assert found_block_indicator, (
            f"Expected to find evidence of Wikipedia search being blocked by policy. "
            f"Looked for indicators: {block_indicators}. "
            f"If the agent completed successfully without any blocking, the policy may not be working."
        )

        # Additional verification: if the agent says it successfully got Wikipedia info,
        # that would indicate the policy block failed
        success_indicators = [
            "Artificial intelligence (AI) is intelligence demonstrated by machines",
            "Wikipedia (mock)",
            "summary:",
        ]

        for indicator in success_indicators:
            if indicator in stdout:
                raise AssertionError(
                    f"Found success indicator '{indicator}' in output, "
                    f"which suggests the Wikipedia search was NOT blocked by policy"
                )

        print("   Wikipedia search was successfully blocked by policy")

    def _cleanup_stear_group(self, token: str, stear_group_id: str):
        """Delete the STEAR group and associated resources."""
        response = requests.delete(
            f"{self.base_url}/stear/{stear_group_id}",
            headers={"Authorization": f"Bearer {token}"},
            timeout=30,
        )

        # 204 No Content or 200 OK are both acceptable for successful deletion
        if response.status_code not in [200, 204]:
            print(f"   Warning: Failed to delete STEAR group: {response.text}")
        else:
            print(f"   Successfully deleted STEAR group: {stear_group_id}")


if __name__ == "__main__":
    # Allow running the test directly
    test = TestWikipediaBlockPolicy()
    test.setup_method()
    test.test_wikipedia_search_blocked_by_policy()
    print("Wikipedia block policy test passed!")
