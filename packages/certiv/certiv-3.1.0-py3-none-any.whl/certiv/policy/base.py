# Copyright (c) 2024 Certiv.ai
# SPDX-License-Identifier: MIT

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Annotated, Any, Literal, Union

from pydantic import BaseModel, Field

from ..api.client import CertivAPIClient
from ..api.types import PolicyDecision
from ..provider.types import LLMInteraction


class RemoveToolCallsModification(BaseModel):
    """Remove specific tool calls from the response"""

    type: Literal["remove_tool_calls"] = "remove_tool_calls"
    tool_call_ids: list[str] | None = None
    tool_call_names: list[str] | None = None


class ReplaceToolCallsModification(BaseModel):
    """Replace all tool calls with a single tool call"""

    type: Literal["replace_tool_calls"] = "replace_tool_calls"
    tool_call: dict[str, Any]


class ReplaceContentModification(BaseModel):
    """Replace the text content of the response"""

    type: Literal["replace_content"] = "replace_content"
    content: str


# Discriminated union type
ResponseModification = Annotated[
    Union[
        RemoveToolCallsModification,
        ReplaceToolCallsModification,
        ReplaceContentModification,
    ],
    Field(discriminator="type"),
]


class PolicyDecisionHandler(ABC):
    name: str

    def __init__(self, api_client: CertivAPIClient) -> None:
        self.api_client = api_client

    @abstractmethod
    def handle(
        self, decision: PolicyDecision, interaction: LLMInteraction
    ) -> list[ResponseModification]:
        pass
