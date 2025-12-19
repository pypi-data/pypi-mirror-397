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


class OpenAIProvider(LLMProvider):
    name = "openai"
    hostnames = ["api.openai.com"]

    def matches(self, req: InterceptedRequest) -> bool:
        parsed_url = urlparse(req.url)
        host = parsed_url.hostname or parsed_url.netloc
        return any(hostname in host for hostname in self.hostnames)

    def extract_interaction(
        self, req: InterceptedRequest, res: InterceptedResponse
    ) -> LLMInteraction | None:
        if not req.body or not res.body:
            logger.debug("OpenAI: Missing request or response body")
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
            logger.debug(f"OpenAI: Failed to extract interaction: {e}")
            return None

    def apply_modifications(self, body: Any, modifications: list[Any]) -> Any:
        if not body.get("choices") or not body["choices"][0].get("message"):
            return body

        message = body["choices"][0]["message"]

        for mod in modifications:
            if mod.type == "remove_tool_calls":
                if mod.tool_call_ids and message.get("tool_calls"):
                    message["tool_calls"] = [
                        tc
                        for tc in message["tool_calls"]
                        if tc.get("id") not in mod.tool_call_ids
                    ]

                    if not message["tool_calls"]:
                        del message["tool_calls"]

            elif mod.type == "replace_content":
                message["content"] = mod.content

            elif mod.type == "replace_tool_calls":
                message["tool_calls"] = [
                    {
                        "id": mod.tool_call["id"],
                        "type": "function",
                        "function": {
                            "name": mod.tool_call["name"],
                            "arguments": mod.tool_call["arguments"],
                        },
                    }
                ]

        return body

    def revert_certiv_tool(self, request_body: Any) -> Any:
        if not request_body.get("messages") or not isinstance(
            request_body["messages"], list
        ):
            return request_body

        for message in request_body["messages"]:
            if message.get("role") != "assistant" or not message.get("tool_calls"):
                continue

            for tool_call in message["tool_calls"]:
                if (
                    tool_call.get("type") == "function"
                    and tool_call.get("function", {}).get("name") == "__CERTIV_TOOL__"
                ):
                    try:
                        certiv_args = json.loads(
                            tool_call["function"].get("arguments", "{}")
                        )
                        if certiv_args.get("tool", {}).get("name") and certiv_args.get(
                            "tool", {}
                        ).get("arguments"):
                            tool_call["function"]["name"] = certiv_args["tool"]["name"]
                            tool_call["function"]["arguments"] = certiv_args["tool"][
                                "arguments"
                            ]
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

        # OpenAI-specific fields
        if body.get("top_p") is not None:
            data.top_p = body["top_p"]
        if body.get("n") is not None:
            data.n = body["n"]
        if body.get("stop") is not None:
            data.stop = body["stop"]
        if body.get("presence_penalty") is not None:
            data.presence_penalty = body["presence_penalty"]
        if body.get("frequency_penalty") is not None:
            data.frequency_penalty = body["frequency_penalty"]
        if body.get("logit_bias"):
            data.logit_bias = body["logit_bias"]
        if body.get("user"):
            data.user = body["user"]
        if body.get("seed") is not None:
            data.seed = body["seed"]
        if body.get("tool_choice"):
            data.tool_choice = body["tool_choice"]
        if body.get("response_format"):
            data.response_format = body["response_format"]

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

        # OpenAI-specific response fields
        if body.get("id"):
            data.id = body["id"]
        if body.get("object"):
            data.object = body["object"]
        if body.get("created"):
            data.created = body["created"]
        if body.get("system_fingerprint"):
            data.system_fingerprint = body["system_fingerprint"]

        if (
            body.get("choices")
            and isinstance(body["choices"], list)
            and body["choices"]
        ):
            choice = body["choices"][0]

            if choice.get("message"):
                data.message = self._extract_message(choice["message"])

                if choice["message"].get("tool_calls") and isinstance(
                    choice["message"]["tool_calls"], list
                ):
                    data.tool_calls = self._extract_tool_calls(
                        choice["message"]["tool_calls"]
                    )

            if choice.get("finish_reason"):
                data.finish_reason = choice["finish_reason"]

            # Include all choices if there are multiple
            if len(body["choices"]) > 1:
                data.choices = body["choices"]

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

        if msg.get("content"):
            message.content = msg["content"]
        if msg.get("name"):
            message.name = msg["name"]

        if msg.get("tool_calls") and isinstance(msg["tool_calls"], list):
            message.tool_calls = self._extract_tool_calls(msg["tool_calls"])

        if msg.get("tool_call_id"):
            message.tool_call_id = msg["tool_call_id"]

        return message

    def _extract_tools(
        self, tools: list[dict[str, Any]]
    ) -> list[ToolDefinition] | None:
        if not isinstance(tools, list):
            return None

        result = []
        for tool in tools:
            if not tool or tool.get("type") != "function" or not tool.get("function"):
                continue

            definition = ToolDefinition(
                type="function",
                function=ToolDefinitionFunction(
                    name=tool["function"].get("name", ""),
                    description=tool["function"].get("description"),
                    parameters=tool["function"].get("parameters"),
                ),
            )
            result.append(definition)

        return result if result else None

    def _extract_tool_calls(self, tool_calls: list[dict[str, Any]]) -> list[ToolCall]:
        if not isinstance(tool_calls, list):
            return []

        result = []
        for call in tool_calls:
            if not call or call.get("type") != "function" or not call.get("function"):
                continue

            tool_call = ToolCall(
                id=call.get("id", ""),
                type="function",
                function=ToolCallFunction(
                    name=call["function"].get("name", ""),
                    arguments=call["function"].get("arguments", "{}"),
                ),
            )
            result.append(tool_call)

        return result

    def _extract_usage(self, usage: dict[str, Any]) -> Usage | None:
        if not usage or not isinstance(usage, dict):
            return None

        return Usage(
            prompt_tokens=usage.get("prompt_tokens", 0),
            completion_tokens=usage.get("completion_tokens", 0),
            total_tokens=usage.get("total_tokens", 0),
        )
