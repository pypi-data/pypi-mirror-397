from __future__ import annotations
import os
import re
import subprocess
import sys
from pathlib import Path

import pytest


class TestToolsFormatAgentBatches:
    """Test to verify that function_calling_agent.py with --tools flag sends exactly two batches and handles tools format properly."""

    def setup_method(self):
        """Set up test environment."""
        self.agent_script = (
            Path(__file__).parent.parent / "agent_demos" / "function_calling_agent.py"
        )
        assert (
            self.agent_script.exists()
        ), f"Agent script not found at {self.agent_script}"

    @pytest.mark.skipif(
        os.getenv("GITHUB_ACTIONS") == "true", reason="Skip in GitHub Actions"
    )
    def test_two_batches_sent_with_tools_format(self):
        """Test that exactly two batches are sent when using --create-agent --tools flags."""
        # Set up environment variables required by the agent
        env = os.environ.copy()
        # Force UTF-8 encoding to handle emojis properly
        env["PYTHONIOENCODING"] = "utf-8"
        env["PYTHONUTF8"] = "1"

        # Build command with --create-agent and --tools flags
        cmd = [sys.executable, str(self.agent_script), "--create-agent", "--tools"]

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

        # Print output for debugging
        print("\n=== Tools Format Agent Output ===")
        print(stdout)
        print("=== End Output ===\n")

        # Parse output to find batch creation log lines - based on actual log output
        # Look for the specific batch IDs that appear in the logs
        batch_ids_in_logs = re.findall(
            r"batch ([a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12})",
            stdout,
        )
        # Deduplicate while preserving order
        seen = set()
        batch_ids = []
        for batch_id in batch_ids_in_logs:
            if batch_id not in seen:
                seen.add(batch_id)
                batch_ids.append(batch_id)

        # Also look for batch creation patterns
        batch_creation_pattern = r"(?:🆕 )?CREATING new batch for agent"
        batch_creations = re.findall(batch_creation_pattern, stdout)

        # Look for shipping patterns
        shipping_pattern = (
            r"(?:📤 )?SHIPPING INTERACTIONS BATCH: \d+ items to batch ([a-f0-9-]+)"
        )
        shipments = re.findall(shipping_pattern, stdout)

        print(f"Found {len(batch_creations)} batch creation attempts")
        print(f"Found {len(batch_ids)} successful batch creations")
        print(f"Batch IDs: {batch_ids}")
        print(f"Found {len(shipments)} batch shipments")

        # Verify exactly 2 batches were created
        assert (
            len(batch_ids) == 2
        ), f"Expected exactly 2 batches to be created, but found {len(batch_ids)}"

        # Verify the batches are different
        assert batch_ids[0] != batch_ids[1], "The two batches should have different IDs"

        # Verify that at least one batch was shipped (the second batch for post-policy interactions)
        # The first batch is completed synchronously for policy enforcement
        assert (
            len(shipments) >= 1
        ), f"Expected at least 1 batch shipment, but found {len(shipments)}"

        # Verify we can see both batch creation attempts
        assert (
            len(batch_creations) >= 2
        ), f"Expected at least 2 batch creation attempts, but found {len(batch_creations)}"

        # Additional verification: check for specific expected content in batches
        # First batch should contain the initial query
        assert (
            "AgentSide: Query:" in stdout
        ), "Expected to find query processing in output"

        # Should see tool calls being made (not function calls)
        assert (
            "AgentSide: Calling tool:" in stdout
        ), "Expected to find tool calls in output with tools format"

        # Should NOT see legacy function calls
        assert (
            "AgentSide: Calling function:" not in stdout
        ), "Should not see legacy function calls when using tools format"

        # Should see flush operation during cleanup
        assert (
            "📤 Shutdown flush: sending data synchronously" in stdout
            or "📤 SHIPPING INTERACTIONS BATCH:" in stdout
            or "Certiv SDK cleanup: flushing pending data" in stdout
        ), "Expected to find flush operation in output"

    @pytest.mark.skipif(
        os.getenv("GITHUB_ACTIONS") == "true", reason="Skip in GitHub Actions"
    )
    def test_tools_format_policy_enforcement(self):
        """Test that tools format triggers proper policy enforcement."""
        env = os.environ.copy()
        # Force UTF-8 encoding to handle emojis properly
        env["PYTHONIOENCODING"] = "utf-8"
        env["PYTHONUTF8"] = "1"

        cmd = [sys.executable, str(self.agent_script), "--create-agent", "--tools"]

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

        stdout, _ = process.communicate(input="2\n")

        # Verify tools format is being used
        assert (
            "🔧 Using OpenAI tools format" in stdout
        ), "Expected to see tools format being used"

        # Verify policy enforcement is active for tools format
        assert (
            "📊 Agent initialized - policy enforcement handled by backend" in stdout
        ), "Expected to see policy enforcement initialization"

        # Should see tool call interception (not function call)
        assert (
            "HTTPMonitor: INTERCEPTING tool call:" in stdout
            or "🔒 HTTPMonitor: INTERCEPTING tool call:" in stdout
        ), "Expected to see HTTPMonitor intercepting tool call"

        # Should see policy check being created
        assert (
            "🛡️ Created policy check interaction" in stdout
        ), "Expected to see policy check interaction creation"

        # Should see policy decision
        assert (
            "🛡️ Tool" in stdout
            and "ALLOWED by policy" in stdout
            or "🛡️ Function" in stdout
            and "ALLOWED by policy" in stdout
            or "🚫 HTTPMonitor: Tool call blocked by backend policy" in stdout
        ), "Expected to see policy decision for tool call"

    @pytest.mark.skipif(
        os.getenv("GITHUB_ACTIONS") == "true", reason="Skip in GitHub Actions"
    )
    def test_tools_vs_functions_format_consistency(self):
        """Test that both formats produce similar batch patterns."""
        env = os.environ.copy()
        env["PYTHONIOENCODING"] = "utf-8"
        env["PYTHONUTF8"] = "1"

        # Test functions format (default)
        cmd_functions = [sys.executable, str(self.agent_script), "--create-agent"]
        process_functions = subprocess.Popen(
            cmd_functions,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding="utf-8",
            errors="replace",
            env=env,
        )
        stdout_functions, _ = process_functions.communicate(input="2\n")

        # Test tools format
        cmd_tools = [
            sys.executable,
            str(self.agent_script),
            "--create-agent",
            "--tools",
        ]
        process_tools = subprocess.Popen(
            cmd_tools,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding="utf-8",
            errors="replace",
            env=env,
        )
        stdout_tools, _ = process_tools.communicate(input="2\n")

        # Both should create batches
        functions_batches = len(
            re.findall(r"CREATING new batch for agent", stdout_functions)
        )
        tools_batches = len(re.findall(r"CREATING new batch for agent", stdout_tools))

        assert (
            functions_batches >= 2
        ), "Functions format should create at least 2 batches"
        assert tools_batches >= 2, "Tools format should create at least 2 batches"

        # Both should have policy enforcement
        assert (
            "📊 Agent initialized - policy enforcement handled by backend"
            in stdout_functions
        )
        assert (
            "📊 Agent initialized - policy enforcement handled by backend"
            in stdout_tools
        )

        # Both should show the format being used
        assert "📋 Using legacy functions format" in stdout_functions
        assert "🔧 Using OpenAI tools format" in stdout_tools

        # Both should show policy decisions
        policy_pattern = r"🛡️.*ALLOWED by policy"
        assert re.search(
            policy_pattern, stdout_functions
        ), "Functions format should show policy decisions"
        assert re.search(
            policy_pattern, stdout_tools
        ), "Tools format should show policy decisions"

    @pytest.mark.skipif(
        os.getenv("GITHUB_ACTIONS") == "true", reason="Skip in GitHub Actions"
    )
    def test_batch_content_verification_tools_format(self):
        """Test that batches contain the expected interactions and tool requests when using tools format."""
        env = os.environ.copy()
        # Force UTF-8 encoding to handle emojis properly
        env["PYTHONIOENCODING"] = "utf-8"
        env["PYTHONUTF8"] = "1"

        cmd = [sys.executable, str(self.agent_script), "--create-agent", "--tools"]

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

        stdout, _ = process.communicate(input="2\n")

        # Check for interactions being added to batches
        interaction_pattern = (
            r"📝 ADDED INTERACTION to batch ([a-f0-9-]+) \(batch size now: (\d+)\)"
        )
        # Tool execution items are added differently in the logs - look for the actual pattern
        tool_execution_pattern = r"📝 ADDING ITEM TO BATCH ([a-f0-9-]+): tool_execution"

        interactions = re.findall(interaction_pattern, stdout)
        tool_executions = re.findall(tool_execution_pattern, stdout)

        print(f"Found {len(interactions)} interactions added to batches")
        print(f"Found {len(tool_executions)} tool executions added to batches")

        # Verify we have interactions in the batches
        assert len(interactions) > 0, "Expected to find interactions added to batches"

        # Verify we have tool executions (function calls) in the batches
        assert (
            len(tool_executions) > 0
        ), "Expected to find tool executions added to batches"

        # Verify tools format specific behavior
        assert (
            "🔧 Using OpenAI tools format" in stdout
        ), "Expected to see tools format confirmation"

        # The key evidence is that tools format was used and policy enforcement worked
        # If tools format is working, we should see successful execution

        # Print some stdout for debugging
        print("=== STDOUT SAMPLE FOR DEBUGGING ===")
        stdout_lines = stdout.split("\n")
        relevant_lines = [
            line
            for line in stdout_lines
            if any(
                keyword in line.lower()
                for keyword in ["tool", "policy", "intercept", "batch", "allow"]
            )
        ]
        for line in relevant_lines[:10]:  # Show first 10 relevant lines
            print(f"  {line}")
        print("=== END SAMPLE ===")

        # Check that tools format produced successful results
        # The most important thing is that it worked end-to-end
        assert (
            "AgentSide: Tool result:" in stdout or "AgentSide: Calling tool:" in stdout
        ), "Expected to see successful tool execution with tools format"


if __name__ == "__main__":
    # Allow running the test directly
    test = TestToolsFormatAgentBatches()
    test.setup_method()
    test.test_two_batches_sent_with_tools_format()
    test.test_tools_format_policy_enforcement()
    test.test_tools_vs_functions_format_consistency()
    test.test_batch_content_verification_tools_format()
    print("All tests passed!")
