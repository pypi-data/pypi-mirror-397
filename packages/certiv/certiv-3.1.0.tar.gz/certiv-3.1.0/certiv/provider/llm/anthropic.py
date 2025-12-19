# Copyright (c) 2024 Certiv.ai
# SPDX-License-Identifier: MIT

from __future__ import annotations

import json
import time
from typing import Any
from urllib.parse import urlparse

from ...interceptor.types import InterceptedRequest, InterceptedResponse
from ...logger import logger
from ..types import (
    LLMInteraction,
    LLMProvider,
    LLMRequest,
    LLMResponse,
    Message,
    ToolCall,
    ToolCallFunction,
    ToolDefinition,
    ToolDefinitionFunction,
    Usage,
)


class AnthropicProvider(LLMProvider):
    name = "anthropic"
    hostnames = ["api.anthropic.com"]

    def matches(self, req: InterceptedRequest) -> bool:
        parsed_url = urlparse(req.url)
        host = parsed_url.hostname or parsed_url.netloc
        return any(hostname in host for hostname in self.hostnames)

    def extract_interaction(
        self, req: InterceptedRequest, res: InterceptedResponse
    ) -> LLMInteraction | None:
        if not req.body or not res.body:
            logger.debug("Anthropic: Missing request or response body")
            return None

        try:
            return LLMInteraction(
                provider=self.name,
                endpoint=urlparse(req.url).path,
                timestamp=time.time(),
                request=self._extract_request_data(req.body),
                response=self._extract_response_data(res.body),
            )
        except Exception as e:
            logger.debug(f"Anthropic: Failed to extract interaction: {e}")
            return None

    def apply_modifications(self, body: Any, modifications: list[Any]) -> Any:
        if not body.get("content") or not isinstance(body["content"], list):
            return body

        for mod in modifications:
            if mod.type == "remove_tool_calls":
                if mod.tool_call_ids:
                    body["content"] = [
                        block
                        for block in body["content"]
                        if block.get("type") != "tool_use"
                        or block.get("id") not in mod.tool_call_ids
                    ]

            elif mod.type == "replace_content":
                # Preserve existing content structure by finding and replacing text blocks only
                text_block_index = next(
                    (
                        i
                        for i, block in enumerate(body["content"])
                        if block.get("type") == "text"
                    ),
                    None,
                )
                if text_block_index is not None:
                    body["content"][text_block_index]["text"] = mod.content
                else:
                    # No text block found, prepend one
                    body["content"].insert(0, {"type": "text", "text": mod.content})

            elif mod.type == "replace_tool_calls":
                body["content"] = [
                    {
                        "type": "tool_use",
                        "id": mod.tool_call.id,
                        "name": mod.tool_call.name,
                        "input": json.loads(mod.tool_call.arguments),
                    }
                ]

        return body

    def revert_certiv_tool(self, request_body: Any) -> Any:
        if not request_body.get("messages") or not isinstance(
            request_body["messages"], list
        ):
            return request_body

        for message in request_body["messages"]:
            if message.get("role") != "assistant" or not message.get("content"):
                continue

            if not isinstance(message["content"], list):
                continue

            for block in message["content"]:
                if (
                    block.get("type") == "tool_use"
                    and block.get("name") == "__CERTIV_TOOL__"
                ):
                    try:
                        certiv_args = block.get("input", {})
                        if certiv_args.get("tool", {}).get("name") and certiv_args.get(
                            "tool", {}
                        ).get("arguments"):
                            block["name"] = certiv_args["tool"]["name"]
                            block["input"] = json.loads(
                                certiv_args["tool"]["arguments"]
                            )
                    except (json.JSONDecodeError, KeyError) as e:
                        logger.debug(f"Failed to parse __CERTIV_TOOL__ arguments: {e}")

        return request_body

    def _extract_request_data(self, body: dict[str, Any]) -> LLMRequest:
        data = LLMRequest()

        if body.get("model"):
            data.model = body["model"]
        if body.get("messages"):
            data.messages = self._extract_messages(body["messages"])
        if body.get("tools"):
            data.tools = self._extract_tools(body["tools"])
        if body.get("temperature") is not None:
            data.temperature = body["temperature"]
        if body.get("max_tokens") is not None:
            data.max_tokens = body["max_tokens"]
        if body.get("stream") is not None:
            data.stream = body["stream"]

        # Anthropic-specific fields
        if body.get("system"):
            data.system = body["system"]
        if body.get("metadata"):
            data.metadata = body["metadata"]
        if body.get("stop_sequences"):
            data.stop_sequences = body["stop_sequences"]
        if body.get("top_p") is not None:
            data.top_p = body["top_p"]
        if body.get("top_k") is not None:
            data.top_k = body["top_k"]

        return data

    def _extract_response_data(self, body: dict[str, Any]) -> LLMResponse:
        data = LLMResponse()

        if body.get("error"):
            data.error = body["error"]
            return data

        if body.get("model"):
            data.model = body["model"]
        if body.get("usage"):
            data.usage = self._extract_usage(body["usage"])

        # Anthropic-specific response fields
        if body.get("id"):
            data.id = body["id"]
        if body.get("type"):
            data.type = body["type"]
        if body.get("role"):
            data.role = body["role"]
        if body.get("stop_sequence"):
            data.stop_sequence = body["stop_sequence"]

        if body.get("content") and isinstance(body["content"], list):
            text_content = []
            tool_calls = []

            for block in body["content"]:
                if block.get("type") == "text":
                    text_content.append(block.get("text", ""))
                elif block.get("type") == "tool_use":
                    tool_call = ToolCall(
                        id=block.get("id", ""),
                        type="function",
                        function=ToolCallFunction(
                            name=block.get("name", ""),
                            arguments=json.dumps(block.get("input", {})),
                        ),
                    )
                    tool_calls.append(tool_call)

            content_str = "\n".join(text_content) if text_content else None
            data.message = Message(role="assistant", content=content_str)

            if tool_calls:
                data.tool_calls = tool_calls

        if body.get("stop_reason"):
            data.finish_reason = body["stop_reason"]

        return data

    def _extract_messages(self, messages: list[dict[str, Any]]) -> list[Message]:
        if not isinstance(messages, list):
            return []

        result = []
        for msg in messages:
            extracted = self._extract_message(msg)
            if extracted:
                result.append(extracted)
        return result

    def _extract_message(self, msg: dict[str, Any]) -> Message | None:
        if not msg or not isinstance(msg, dict):
            return None

        message = Message(role=msg.get("role", "user"))

        if isinstance(msg.get("content"), str):
            message.content = msg["content"]
        elif isinstance(msg.get("content"), list):
            text_parts = []
            tool_calls = []
            tool_result_id = None

            for block in msg["content"]:
                if block.get("type") == "text":
                    text_parts.append(block.get("text", ""))
                elif block.get("type") == "tool_use":
                    tool_call = ToolCall(
                        id=block.get("id", ""),
                        type="function",
                        function=ToolCallFunction(
                            name=block.get("name", ""),
                            arguments=json.dumps(block.get("input", {})),
                        ),
                    )
                    tool_calls.append(tool_call)
                elif block.get("type") == "tool_result" and block.get("tool_use_id"):
                    # Extract tool_call_id from tool_result blocks
                    tool_result_id = block["tool_use_id"]

            if text_parts:
                message.content = "\n".join(text_parts)
            if tool_calls:
                message.tool_calls = tool_calls
            if tool_result_id:
                message.tool_call_id = tool_result_id

        return message

    def _extract_tools(
        self, tools: list[dict[str, Any]]
    ) -> list[ToolDefinition] | None:
        if not isinstance(tools, list):
            return None

        result = []
        for tool in tools:
            if not tool or not tool.get("name"):
                continue

            definition = ToolDefinition(
                type="function",
                function=ToolDefinitionFunction(
                    name=tool.get("name", ""),
                    description=tool.get("description"),
                    parameters=tool.get("input_schema"),
                ),
            )
            result.append(definition)

        return result if result else None

    def _extract_usage(self, usage: dict[str, Any]) -> Usage | None:
        if not usage or not isinstance(usage, dict):
            return None

        return Usage(
            prompt_tokens=usage.get("input_tokens", 0),
            completion_tokens=usage.get("output_tokens", 0),
            total_tokens=usage.get("input_tokens", 0) + usage.get("output_tokens", 0),
        )
