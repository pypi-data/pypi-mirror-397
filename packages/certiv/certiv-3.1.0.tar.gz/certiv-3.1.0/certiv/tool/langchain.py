# Copyright (c) 2024 Certiv.ai
# SPDX-License-Identifier: MIT

"""LangChain tool wrapper for Certiv"""

from __future__ import annotations

from langchain_core.tools import StructuredTool

from .core import handle_certiv_tool
from .types import PolicyBlockGracefulArgs


def _certiv_tool_wrapper(**kwargs: dict) -> str:
    """Wrapper function for handle_certiv_tool to work with LangChain."""
    return handle_certiv_tool(**kwargs)


certiv_langchain_tool = StructuredTool.from_function(
    func=_certiv_tool_wrapper,
    name="__CERTIV_TOOL__",
    description=(
        "Certiv SDK tool for policy enforcement and tool execution management. "
        "Handles various actions including graceful blocking of policy-restricted operations."
    ),
    args_schema=PolicyBlockGracefulArgs,
)
