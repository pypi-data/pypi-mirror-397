# Copyright (c) 2024 Certiv.ai
# SPDX-License-Identifier: MIT

from __future__ import annotations

from .core import handle_certiv_tool
from .default import CertivTool
from .types import (
    CertivToolArgs,
    CertivToolArgsBase,
    PolicyBlockGracefulArgs,
    PolicyInfo,
    ToolInfo,
)

# Conditionally import LangChain tool if langchain is installed
try:
    from .langchain import certiv_langchain_tool

    _has_langchain = True
except ImportError:
    certiv_langchain_tool = None  # type: ignore
    _has_langchain = False

__all__ = [
    "CertivToolArgs",
    "CertivToolArgsBase",
    "PolicyBlockGracefulArgs",
    "ToolInfo",
    "PolicyInfo",
    "handle_certiv_tool",
    "CertivTool",
    "certiv_langchain_tool",
]
