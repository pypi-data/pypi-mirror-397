# Copyright (c) 2024 Certiv.ai
# SPDX-License-Identifier: MIT

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel


class CertivToolArgsBase(BaseModel):
    action: str
    timestamp: str


class ToolInfo(BaseModel):
    name: str
    arguments: str


class PolicyInfo(BaseModel):
    decision_id: str
    decision: str
    reason: str


class PolicyBlockGracefulArgs(CertivToolArgsBase):
    action: Literal["policy_block_graceful"]
    tool: ToolInfo
    policy: PolicyInfo


# Type alias (matching TypeScript)
CertivToolArgs = PolicyBlockGracefulArgs
