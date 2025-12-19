# Copyright (c) 2024 Certiv.ai
# SPDX-License-Identifier: MIT

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Literal

from pydantic import BaseModel


class Message(BaseModel):
    role: Literal["system", "user", "assistant", "tool"]
    content: str | None = None
    tool_calls: list[ToolCall] | None = None
    tool_call_id: str | None = None
    name: str | None = None


class ToolDefinitionFunction(BaseModel):
    name: str
    description: str | None = None
    parameters: Any | None = None


class ToolCallFunction(BaseModel):
    name: str
    arguments: str


class ToolDefinition(BaseModel):
    type: Literal["function"]
    function: ToolDefinitionFunction


class ToolCall(BaseModel):
    id: str
    type: Literal["function"]
    function: ToolCallFunction


class Usage(BaseModel):
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int


class LLMRequest(BaseModel):
    model: str | None = None
    messages: list[Message] | None = None
    tools: list[ToolDefinition] | None = None
    temperature: float | None = None
    max_tokens: int | None = None
    stream: bool | None = None

    class Config:
        extra = "allow"


class LLMResponse(BaseModel):
    model: str | None = None
    message: Message | None = None
    tool_calls: list[ToolCall] | None = None
    usage: Usage | None = None
    finish_reason: str | None = None
    error: Any | None = None

    class Config:
        extra = "allow"


class LLMInteraction(BaseModel):
    provider: str
    endpoint: str
    timestamp: float
    request: LLMRequest
    response: LLMResponse


class LLMProvider(ABC):
    name: str
    hostnames: list[str]

    @abstractmethod
    def matches(self, req: Any) -> bool:
        pass

    @abstractmethod
    def extract_interaction(self, req: Any, res: Any) -> LLMInteraction | None:
        pass

    @abstractmethod
    def apply_modifications(self, body: Any, modifications: list[Any]) -> Any:
        pass

    @abstractmethod
    def revert_certiv_tool(self, request_body: Any) -> Any:
        pass
