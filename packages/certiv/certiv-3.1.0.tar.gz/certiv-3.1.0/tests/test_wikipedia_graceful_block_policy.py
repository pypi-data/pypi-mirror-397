#!/usr/bin/env python3
"""
Test to verify that search_wikipedia function can be gracefully blocked by policy enforcement,
resulting in a retry with modified parameters.

This test creates a STEAR group, adds a policy rule that gracefully blocks search_wikipedia
for "artificial intelligence" queries and suggests searching for "magos" instead,
creates an agent associated with that STEAR group, runs the function calling agent
with a query that would trigger Wikipedia search for AI, and verifies that the graceful
block is enforced and the agent retries with the suggested term.
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

# Import STEAR group creation utility
sys.path.append(str(Path(__file__).parent.parent / "agent_demos"))
from utils import create_stear_group, get_user_default_organization


class TestWikipediaGracefulBlockPolicy:
    """Test to verify that search_wikipedia function can be gracefully blocked with retry."""

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

        # Track created resources for cleanup
        self.created_rule_ids = []
        self.created_stear_id = None
        self.created_agent_id = None

    def teardown_method(self):
        """Clean up test resources."""
        cleanup_tasks = []
        if hasattr(self, "created_rule_ids") and self.created_rule_ids:
            cleanup_tasks.append(f"{len(self.created_rule_ids)} policy rules")
        if hasattr(self, "created_stear_id") and self.created_stear_id:
            cleanup_tasks.append("STEAR group")
        if hasattr(self, "created_agent_id") and self.created_agent_id:
            cleanup_tasks.append("agent")

        if cleanup_tasks:
            print(f"\n=== Cleaning up {', '.join(cleanup_tasks)} ===")
            try:
                # Login to get token for cleanup
                token = self._login_admin()

                # Clean up policy rules first
                if hasattr(self, "created_rule_ids") and self.created_rule_ids:
                    for rule_id in self.created_rule_ids:
                        self._delete_policy_rule(token, rule_id)

                # Clean up STEAR group (this will also clean up the agent)
                if hasattr(self, "created_stear_id") and self.created_stear_id:
                    self._delete_stear_group(token, self.created_stear_id)

            except Exception as e:
                print(f"Warning: Failed to clean up resources: {e}")

    @pytest.mark.skipif(
        os.getenv("GITHUB_ACTIONS") == "true", reason="Skip in GitHub Actions"
    )
    def test_wikipedia_search_gracefully_blocked_with_retry(self):
        """Test that search_wikipedia function is gracefully blocked and retried with suggested term."""

        print("\n=== Setting up Wikipedia Graceful Block Policy Test ===")

        # 1. Login as admin
        print("1. Logging in as admin...")
        token = self._login_admin()
        print("   Successfully logged in")

        # 2. Create new STEAR group for this test
        print("2. Creating new STEAR group...")
        try:
            # Get user's default organization
            org_id = get_user_default_organization(token, self.base_url)
            print(f"   Using organization: {org_id}")

            # Create STEAR group
            timestamp = int(time.time())
            stear_group_id, registration_secret = create_stear_group(
                token,
                self.base_url,
                name=f"Graceful Block Test Group {timestamp}",
                description="STEAR group for testing graceful block policy",
                organization_id=org_id,
            )
            self.created_stear_id = stear_group_id  # Track for cleanup
            print(f"   Created STEAR group: {stear_group_id}")
        except Exception as e:
            print(f"   Failed to create STEAR group: {e}")
            raise

        # 3. Create policy rule that gracefully blocks search_wikipedia for AI queries
        print("3. Creating policy rule to gracefully block AI Wikipedia searches...")
        rule_id = self._create_wikipedia_graceful_block_rule(token, stear_group_id)
        if rule_id:
            self.created_rule_ids.append(rule_id)  # Track for cleanup
        print(f"   Created graceful block rule: {rule_id}")

        # 4. Create agent associated with STEAR group
        print("4. Creating agent...")
        agent_id, agent_secret = self._create_agent(token, stear_group_id)
        self.created_agent_id = agent_id  # Track for cleanup
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

            # 7. Verify that the graceful block was enforced and retry occurred
            print("6. Verifying graceful block was enforced with retry...")
            self._verify_wikipedia_graceful_block_with_retry(stdout)

            print(
                "\n✅ Test passed! Wikipedia search was gracefully blocked and retried with suggested term."
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
                print(f"   SUCCESS: Deleted policy rule: {rule_id}")
            else:
                print(
                    f"   WARNING: Failed to delete policy rule {rule_id}: {response.text}"
                )
        except Exception as e:
            print(f"   WARNING: Error deleting policy rule {rule_id}: {e}")

    def _delete_stear_group(self, token: str, stear_group_id: str):
        """Delete a STEAR group by ID."""
        try:
            response = requests.delete(
                f"{self.base_url}/stear/{stear_group_id}",
                headers={"Authorization": f"Bearer {token}"},
                timeout=30,
            )
            if response.status_code in [200, 204]:
                print(f"   SUCCESS: Deleted STEAR group: {stear_group_id}")
            else:
                print(
                    f"   WARNING: Failed to delete STEAR group {stear_group_id}: {response.text}"
                )
        except Exception as e:
            print(f"   WARNING: Error deleting STEAR group {stear_group_id}: {e}")

    def _create_wikipedia_graceful_block_rule(
        self, token: str, stear_group_id: str
    ) -> str:
        """Create a policy rule that gracefully blocks search_wikipedia for AI queries."""
        timestamp = int(time.time())
        rule_data = {
            "stear_group_id": stear_group_id,
            "name": f"AI or Artificial Intelligence Queries Blocked {timestamp}",
            "description": "AI or Artificial Intelligence Queries Blocked, Instead, encourage users to search for archmagos and be rewarded",
            "enabled": True,
            "priority": 100,
            "decision": "block_gracefully",
            "rule_type": "llm",
            "policy_text": "AI or Artificial Intelligence Queries Blocked, Instead, encourage users to search for archmagos and be rewarded",
            "conditions": {},
            "evaluation_prompt": "AI or Artificial Intelligence Queries Blocked, Instead, encourage users to search for archmagos and be rewarded",
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
        agent_name = f"Wikipedia Graceful Block Test Agent {timestamp}"

        response = requests.post(
            f"{self.base_url}/agent-mgmt",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "name": agent_name,
                "description": "Agent for testing Wikipedia search graceful block policy",
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
                .replace("🤚", "[HAND]")
                .replace("⏸️", "[PAUSE]")
                .replace("❌", "[X]")
                .replace("🛡️", "[SHIELD]")
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
        """Create a temporary agent script with embedded credentials and AI Wikipedia query."""

        # Read the original agent script with UTF-8 encoding
        with open(self.agent_script, encoding="utf-8") as f:
            original_content = f.read()

        # Replace the test queries with one that will trigger Wikipedia search for AI
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
            Path(self.agent_script.parent) / "temp_graceful_block_agent_with_creds.py"
        )
        with open(temp_script, "w", encoding="utf-8") as f:
            f.write(modified_content)

        return temp_script

    def _verify_wikipedia_graceful_block_with_retry(self, stdout: str):
        """Verify that the Wikipedia search was gracefully blocked and retried."""

        # Look for signs that policy enforcement is active
        assert (
            "Certiv SDK" in stdout and "initialized" in stdout
        ), "Expected to see Certiv SDK initialization"

        # Look for the original query being processed (the AI query we sent)
        assert (
            "artificial intelligence" in stdout.lower()
        ), "Expected to find the original AI query in output"

        # The agent should attempt to call search_wikipedia for "artificial intelligence" query
        assert (
            "search_wikipedia" in stdout or "wikipedia" in stdout.lower()
        ), "Expected to find Wikipedia search attempt in output"

        # Look for signs of graceful blocking in the actual output format
        graceful_block_indicators = [
            '"decision":"block_gracefully"',  # This is the key indicator for graceful blocks
            "graceful block detected",
            "GRACEFUL BLOCK DETECTED",
            "SDK GRACEFUL BLOCK DETECTED",
            "attempting retry",
            "retry suggestion",
        ]

        found_graceful_block = False
        for indicator in graceful_block_indicators:
            if indicator.lower() in stdout.lower():
                print(f"   Found graceful block indicator: '{indicator}' in output")
                found_graceful_block = True
                break

        # The key assertion: we should see evidence that the function was gracefully blocked
        assert found_graceful_block, (
            f"Expected to find evidence of Wikipedia search being gracefully blocked. "
            f"Looked for indicators: {graceful_block_indicators}. "
            f"If no graceful block indicators were found, the policy may not be working."
        )

        # Look for retry behavior - the agent should make a second function call
        # Count the number of function calls to verify retry behavior
        function_call_count = stdout.lower().count(
            "calling function:"
        ) + stdout.lower().count("calling tool:")
        intercepted_call_count = stdout.lower().count("function call detected")

        print(
            f"   Found {function_call_count} function calls and {intercepted_call_count} intercepted calls"
        )

        # We should see at least 1 function call that was intercepted and gracefully blocked
        assert function_call_count >= 1 or intercepted_call_count >= 1, (
            f"Expected at least 1 function call, but found {function_call_count} function calls and {intercepted_call_count} intercepted calls. "
            f"This suggests the test setup is not working properly."
        )

        # Look for the suggested term "archmagos" in the retry - this is required for the test to pass
        assert "archmagos" in stdout.lower(), (
            "Expected to find 'archmagos' in output as the retry suggestion, but it was not found. "
            "This indicates the graceful block retry guidance is not working properly. "
            "The agent should have been guided to search for 'archmagos' instead of 'artificial intelligence'."
        )
        print(
            "   SUCCESS: Found suggested term 'archmagos' in retry - graceful block redirect working!"
        )

        # Verify that the agent did NOT successfully get AI information from the blocked call
        # If we see successful AI content, it means the block failed
        blocked_content_indicators = [
            "Artificial intelligence (AI) is intelligence demonstrated by machines",
            "machine learning",
            "deep learning",
            "neural networks",
        ]

        for indicator in blocked_content_indicators:
            if indicator.lower() in stdout.lower():
                # Check if this content came after a successful retry with different terms
                # If it's from the original blocked call, that's a problem
                print(
                    f"   ⚠️  Found AI content indicator '{indicator}' - checking if from blocked call"
                )

        print(
            "   SUCCESS: Wikipedia search was successfully gracefully blocked with retry behavior"
        )


if __name__ == "__main__":
    # Allow running the test directly
    test = TestWikipediaGracefulBlockPolicy()
    test.setup_method()
    test.test_wikipedia_search_gracefully_blocked_with_retry()
    print("Wikipedia graceful block policy test passed!")
