# Copyright (c) 2024 Certiv.ai
# SPDX-License-Identifier: MIT

from __future__ import annotations

from typing import Any

from ..logger import logger
from .types import CertivToolArgs


def handle_certiv_tool(*args: Any, **kwargs: Any) -> str:
    """
    Handle Certiv tool execution and return user-friendly policy block message.

    Supports:
    - handle_certiv_tool('{"action":...}')  # JSON string
    - handle_certiv_tool({"action":...})    # Dict/object
    - handle_certiv_tool(action, timestamp, tool, policy)  # 4 positional args
    - handle_certiv_tool(action="...", timestamp="...", tool={}, policy={})  # kwargs

    Returns:
        String message explaining the policy block
    """
    try:
        parsed_args: CertivToolArgs

        # Pattern 1: Single JSON string argument
        if len(args) == 1 and isinstance(args[0], str):
            parsed_args = CertivToolArgs.model_validate_json(args[0])

        # Pattern 2: Single dict/object argument
        elif len(args) == 1 and isinstance(args[0], dict):
            parsed_args = CertivToolArgs.model_validate(args[0])

        # Pattern 3: Four separate positional arguments (action, timestamp, tool, policy)
        elif len(args) == 4:
            parsed_args = CertivToolArgs.model_validate(
                {
                    "action": args[0],
                    "timestamp": args[1],
                    "tool": args[2],
                    "policy": args[3],
                }
            )

        # Pattern 4: Keyword arguments (unpacked dict)
        elif len(args) == 0 and len(kwargs) > 0:
            parsed_args = CertivToolArgs.model_validate(kwargs)

        else:
            return "Tool execution blocked by Certiv.ai policy: Invalid arguments"

        # Handle policy_block_graceful action
        if parsed_args.action == "policy_block_graceful":
            if not parsed_args.tool or not parsed_args.policy:
                return (
                    "Tool execution blocked by Certiv.ai policy: Invalid tool call data"
                )

            tool_name = parsed_args.tool.name
            reason = parsed_args.policy.reason

            return f"Tool execution blocked by Certiv.ai policy: {tool_name} - {reason}"

        return "Tool execution blocked by Certiv.ai policy: Unknown action"

    except Exception as e:
        logger.error(
            "Failed to process Certiv tool arguments", {"error": str(e), "args": args}
        )
        return (
            "Tool execution blocked by Certiv.ai policy: Unable to parse block details"
        )
