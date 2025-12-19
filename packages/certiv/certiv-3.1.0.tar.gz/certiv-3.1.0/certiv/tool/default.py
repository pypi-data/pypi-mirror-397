# Copyright (c) 2024 Certiv.ai
# SPDX-License-Identifier: MIT

"""
Default Certiv tool for LLMs

Usage:
    from certiv.tool import CertivTool

    function_map = {
        "send_email": send_email_function,
        "get_weather": get_weather_function,
        **CertivTool,
    }

    for tool_call in message.tool_calls:
        tool_fn = function_map[tool_call.function.name]
        if tool_fn:
            result = tool_fn(tool_call.function.arguments)
            # ... handle result
"""

from __future__ import annotations

from types import MappingProxyType

from .core import handle_certiv_tool

# Frozen dict (Python equivalent of Object.freeze)
CertivTool = MappingProxyType(
    {"__CERTIV_TOOL__": lambda *args, **kwargs: handle_certiv_tool(*args, **kwargs)}
)
