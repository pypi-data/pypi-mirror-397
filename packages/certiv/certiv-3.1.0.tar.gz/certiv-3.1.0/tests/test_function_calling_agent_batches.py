from __future__ import annotations
import os
import re
import subprocess
import sys
from pathlib import Path

import pytest


class TestFunctionCallingAgentBatches:
    """Test to verify that function_calling_agent.py sends exactly two batches when using --create-agent flag."""

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
    def test_two_batches_sent_with_create_agent(self):
        """Test that exactly two batches are sent when using --create-agent flag."""
        # Set up environment variables required by the agent
        env = os.environ.copy()
        # Force UTF-8 encoding to handle emojis properly
        env["PYTHONIOENCODING"] = "utf-8"
        env["PYTHONUTF8"] = "1"

        # Build command with --create-agent flag
        cmd = [sys.executable, str(self.agent_script), "--create-agent"]

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
        print("\n=== Agent Output ===")
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

        # Should see function calls being made
        assert (
            "AgentSide: Calling function:" in stdout
        ), "Expected to find function calls in output"

        # Should see flush operation during cleanup
        assert (
            "📤 Shutdown flush: sending data synchronously" in stdout
            or "📤 SHIPPING INTERACTIONS BATCH:" in stdout
            or "Certiv SDK cleanup: flushing pending data" in stdout
        ), "Expected to find flush operation in output"

    @pytest.mark.skipif(
        os.getenv("GITHUB_ACTIONS") == "true", reason="Skip in GitHub Actions"
    )
    def test_batch_content_verification(self):
        """Test that batches contain the expected interactions and tool requests."""
        env = os.environ.copy()
        # Force UTF-8 encoding to handle emojis properly
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

        # Verify policy enforcement is active
        assert (
            "📊 Agent initialized - policy enforcement handled by backend" in stdout
        ), "Expected to see policy enforcement initialization"


if __name__ == "__main__":
    # Allow running the test directly
    test = TestFunctionCallingAgentBatches()
    test.setup_method()
    test.test_two_batches_sent_with_create_agent()
    test.test_batch_content_verification()
    print("All tests passed!")
