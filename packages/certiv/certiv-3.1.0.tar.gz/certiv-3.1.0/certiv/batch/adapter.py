# Copyright (c) 2024 Certiv.ai
# SPDX-License-Identifier: MIT

from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any

from ..api.types import (
    AnalysisData,
    BatchItem,
    BatchItemMessage,
    BatchItemToolCall,
    BatchItemToolDefinition,
    ChatHistoryContent,
    ChatHistoryItem,
    ItemMetadata,
    ToolCallFunction,
    ToolDefinitionFunction,
    ToolExecutionContent,
    ToolExecutionItem,
    UsageData,
)
from ..logger import logger
from ..provider.types import LLMInteraction, ToolCall, ToolDefinition

SENSITIVE_KEYS = [
    "api_key",
    "apikey",
    "api-key",
    "authorization",
    "password",
    "secret",
    "token",
    "access_token",
    "refresh_token",
    "private_key",
    "credential",
    "credentials",
    "bearer",
]


def to_batch_item(
    instance_id: str, llm_interaction: LLMInteraction, sdk_version: str
) -> BatchItem:
    timestamp = datetime.fromtimestamp(
        llm_interaction.timestamp, tz=timezone.utc
    ).isoformat()
    metadata = _extract_metadata(llm_interaction)

    sanitized_data = _sanitize_data(
        {
            "provider": llm_interaction.provider,
            "endpoint": llm_interaction.endpoint,
            "request": llm_interaction.request.model_dump(),
            "response": llm_interaction.response.model_dump(),
        }
    )

    has_tool_calls = _detect_tool_calls(llm_interaction, metadata)

    if has_tool_calls:
        return _build_tool_execution_item(
            sanitized_data,
            metadata,
            timestamp,
            instance_id,
            sdk_version,
        )

    return _build_chat_history_item(
        sanitized_data,
        metadata,
        timestamp,
        instance_id,
    )


def _extract_metadata(llm_interaction: LLMInteraction) -> ItemMetadata:
    metadata = ItemMetadata(
        auto_captured=True,
        capture_method="http",
    )

    if hasattr(llm_interaction.response, "id"):
        metadata.response_id = getattr(llm_interaction.response, "id", None)

    if llm_interaction.response.usage:
        usage_dict = llm_interaction.response.usage.model_dump()
        metadata.usage = UsageData(
            prompt_tokens=usage_dict["prompt_tokens"],
            completion_tokens=usage_dict["completion_tokens"],
            total_tokens=usage_dict["total_tokens"],
        )

    has_tool_calls = bool(
        llm_interaction.response.tool_calls
        and len(llm_interaction.response.tool_calls) > 0
    )
    metadata.has_tool_calls = has_tool_calls

    if has_tool_calls and llm_interaction.response.tool_calls:
        metadata.tool_calls = _convert_tool_calls_to_wire_format(
            llm_interaction.response.tool_calls
        )

    if llm_interaction.request.tools and len(llm_interaction.request.tools) > 0:
        metadata.available_tools = _convert_tool_definitions(
            llm_interaction.request.tools
        )
        metadata.available_tools_count = len(llm_interaction.request.tools)

    metadata.has_graceful_block = False

    metadata.llm_detected = True
    metadata.analysis = AnalysisData(
        is_llm=True,
        has_tool_requests=has_tool_calls,
        provider=llm_interaction.provider,
        model=llm_interaction.request.model or llm_interaction.response.model,
        confidence=1.0,
    )

    return metadata


def _convert_tool_calls_to_wire_format(
    tool_calls: list[ToolCall],
) -> list[BatchItemToolCall]:
    return [
        BatchItemToolCall(
            type="function",
            id=tc.id,
            function=ToolCallFunction(
                name=tc.function.name,
                arguments=tc.function.arguments,
            ),
        )
        for tc in tool_calls
    ]


def _convert_tool_definitions(
    tools: list[ToolDefinition],
) -> list[BatchItemToolDefinition]:
    return [
        BatchItemToolDefinition(
            type="function",
            function=ToolDefinitionFunction(
                name=tool.function.name,
                description=tool.function.description,
                parameters=tool.function.parameters,
            ),
        )
        for tool in tools
    ]


def _sanitize_data(data: Any) -> Any:
    if isinstance(data, list):
        return [_sanitize_data(item) for item in data]

    if not (data and isinstance(data, dict)):
        return data

    sanitized = {}

    for key, value in data.items():
        key_lower = key.lower()
        is_sensitive = any(sk in key_lower for sk in SENSITIVE_KEYS)

        if is_sensitive:
            sanitized[key] = "[REDACTED]"
        else:
            sanitized[key] = _sanitize_data(value)

    return sanitized


def _detect_tool_calls(llm_interaction: LLMInteraction, metadata: ItemMetadata) -> bool:
    if (
        llm_interaction.response.tool_calls
        and len(llm_interaction.response.tool_calls) > 0
    ):
        return True

    return bool(metadata.has_tool_calls)


def _build_tool_execution_item(
    sanitized_data: dict[str, Any],
    metadata: ItemMetadata,
    timestamp: str,
    instance_id: str,
    sdk_version: str,
) -> ToolExecutionItem:
    tool_calls = _extract_tool_calls(sanitized_data, metadata)

    last_tool_call = tool_calls[-1] if tool_calls else None

    tool_name = "unknown"
    tool_parameters: dict[str, Any] = {}

    if last_tool_call and last_tool_call.function:
        tool_name = last_tool_call.function.name

        args = last_tool_call.function.arguments
        try:
            tool_parameters = json.loads(args)
        except (json.JSONDecodeError, TypeError) as e:
            logger.warn(f"Failed to parse tool arguments: {e}")
            tool_parameters = {}

    messages = _build_messages(sanitized_data)

    content = ToolExecutionContent(
        tool_calls=tool_calls,
        tool_name=tool_name,
        tool_parameters=tool_parameters,
        messages=messages,
        timestamp=timestamp,
        interaction_type="response",
        instance_id=instance_id,
        sdk_version=sdk_version,
    )

    return ToolExecutionItem(
        item_type="tool_execution",
        content=content,
        item_metadata=metadata,
    )


def _build_chat_history_item(
    sanitized_data: dict[str, Any],
    metadata: ItemMetadata,
    timestamp: str,
    instance_id: str,
) -> ChatHistoryItem:
    messages = _build_messages(sanitized_data)

    content = ChatHistoryContent(
        messages=messages,
        timestamp=timestamp,
        interaction_type="response",
        instance_id=instance_id,
    )

    return ChatHistoryItem(
        item_type="chat_history",
        content=content,
        item_metadata=metadata,
    )


def _build_messages(sanitized_data: dict[str, Any]) -> list[BatchItemMessage]:
    messages: list[BatchItemMessage] = []

    if sanitized_data.get("request", {}).get("messages"):
        for msg in sanitized_data["request"]["messages"]:
            messages.append(_convert_message(msg))

    if sanitized_data.get("response", {}).get("message"):
        response_msg = _convert_message(sanitized_data["response"]["message"])

        if (
            sanitized_data.get("response", {}).get("tool_calls")
            and sanitized_data["response"]["tool_calls"]
        ):
            response_msg.tool_calls = [
                BatchItemToolCall(
                    type="function",
                    id=tc.get("id", ""),
                    function=ToolCallFunction(
                        name=tc.get("function", {}).get("name", ""),
                        arguments=tc.get("function", {}).get("arguments", "{}"),
                    ),
                )
                for tc in sanitized_data["response"]["tool_calls"]
            ]

        messages.append(response_msg)

    return messages


def _convert_message(msg: dict[str, Any]) -> BatchItemMessage:
    wire_msg = BatchItemMessage(
        role=msg.get("role", "user"),
        content=msg.get("content"),
    )

    if msg.get("tool_calls") and len(msg["tool_calls"]) > 0:
        wire_msg.tool_calls = [
            BatchItemToolCall(
                type="function",
                id=tc.get("id", ""),
                function=ToolCallFunction(
                    name=tc.get("function", {}).get("name", ""),
                    arguments=tc.get("function", {}).get("arguments", "{}"),
                ),
            )
            for tc in msg["tool_calls"]
        ]

    if msg.get("tool_call_id"):
        wire_msg.tool_call_id = msg["tool_call_id"]

    if msg.get("name"):
        wire_msg.name = msg["name"]

    return wire_msg


def _extract_tool_calls(
    sanitized_data: dict[str, Any], metadata: ItemMetadata
) -> list[BatchItemToolCall]:
    if (
        sanitized_data.get("response", {}).get("tool_calls")
        and sanitized_data["response"]["tool_calls"]
    ):
        return [
            BatchItemToolCall(
                type="function",
                id=tc.get("id", ""),
                function=ToolCallFunction(
                    name=tc.get("function", {}).get("name", ""),
                    arguments=tc.get("function", {}).get("arguments", "{}"),
                ),
            )
            for tc in sanitized_data["response"]["tool_calls"]
        ]

    if metadata.tool_calls:
        return metadata.tool_calls

    return []
