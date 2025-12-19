# Copyright (c) 2024 Certiv.ai
# SPDX-License-Identifier: MIT

from __future__ import annotations

import json
import random
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


class GoogleProvider(LLMProvider):
    name = "google"
    hostnames = ["generativelanguage.googleapis.com"]

    def matches(self, req: InterceptedRequest) -> bool:
        parsed_url = urlparse(req.url)
        host = parsed_url.hostname or parsed_url.netloc
        return any(hostname in host for hostname in self.hostnames)

    def extract_interaction(
        self, req: InterceptedRequest, res: InterceptedResponse
    ) -> LLMInteraction | None:
        if not req.body or not res.body:
            logger.debug("Google: Missing request or response body")
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
            logger.debug(f"Google: Failed to extract interaction: {e}")
            return None

    def apply_modifications(self, body: Any, modifications: list[Any]) -> Any:
        if not body.get("candidates") or not isinstance(body["candidates"], list):
            return body

        for mod in modifications:
            if mod.type == "remove_tool_calls":
                for candidate in body["candidates"]:
                    if not candidate.get("content", {}).get("parts"):
                        continue

                    candidate["content"]["parts"] = [
                        part
                        for part in candidate["content"]["parts"]
                        if not (
                            part.get("functionCall")
                            and part["functionCall"].get("name") in mod.tool_call_ids
                        )
                    ]

            elif mod.type == "replace_content":
                # Preserve existing parts structure by finding and replacing text parts only
                for candidate in body["candidates"]:
                    if not candidate.get("content", {}).get("parts"):
                        continue

                    parts = candidate["content"]["parts"]
                    text_part_index = next(
                        (i for i, part in enumerate(parts) if "text" in part), None
                    )
                    if text_part_index is not None:
                        parts[text_part_index]["text"] = mod.content
                    else:
                        # No text part found, prepend one
                        parts.insert(0, {"text": mod.content})

            elif mod.type == "replace_tool_calls":
                for candidate in body["candidates"]:
                    candidate["content"] = {
                        "parts": [
                            {
                                "functionCall": {
                                    "name": mod.tool_call.name,
                                    "args": json.loads(mod.tool_call.arguments),
                                }
                            }
                        ],
                        "role": "model",
                    }

        return body

    def revert_certiv_tool(self, request_body: Any) -> Any:
        if not request_body.get("contents") or not isinstance(
            request_body["contents"], list
        ):
            return request_body

        for content in request_body["contents"]:
            if content.get("role") != "model" or not content.get("parts"):
                continue

            for part in content["parts"]:
                if (
                    part.get("functionCall")
                    and part["functionCall"].get("name") == "__CERTIV_TOOL__"
                ):
                    try:
                        certiv_args = part["functionCall"].get("args", {})
                        if certiv_args.get("tool", {}).get("name") and certiv_args.get(
                            "tool", {}
                        ).get("arguments"):
                            part["functionCall"]["name"] = certiv_args["tool"]["name"]
                            part["functionCall"]["args"] = json.loads(
                                certiv_args["tool"]["arguments"]
                            )
                    except (json.JSONDecodeError, KeyError) as e:
                        logger.debug(f"Failed to parse __CERTIV_TOOL__ arguments: {e}")

        return request_body

    def _extract_request_data(self, body: dict[str, Any]) -> LLMRequest:
        data = LLMRequest()

        model_match = urlparse(body.get("url", "")).path
        if "/models/" in model_match:
            data.model = model_match.split("/models/")[1].split(":")[0]

        if body.get("contents"):
            data.messages = self._extract_messages(body["contents"])
        if body.get("tools"):
            data.tools = self._extract_tools(body["tools"])

        generation_config = body.get("generationConfig", {})
        if generation_config.get("temperature") is not None:
            data.temperature = generation_config["temperature"]
        if generation_config.get("maxOutputTokens") is not None:
            data.max_tokens = generation_config["maxOutputTokens"]
        if generation_config.get("topP") is not None:
            data.top_p = generation_config["topP"]
        if generation_config.get("topK") is not None:
            data.top_k = generation_config["topK"]
        if generation_config.get("stopSequences"):
            data.stop_sequences = generation_config["stopSequences"]

        # Google-specific fields
        if body.get("safetySettings"):
            data.safetySettings = body["safetySettings"]
        if body.get("systemInstruction"):
            data.systemInstruction = body["systemInstruction"]

        return data

    def _extract_response_data(self, body: dict[str, Any]) -> LLMResponse:
        data = LLMResponse()

        if body.get("error"):
            data.error = body["error"]
            return data

        if body.get("usageMetadata"):
            data.usage = self._extract_usage(body["usageMetadata"])

        if body.get("candidates") and isinstance(body["candidates"], list):
            candidate = body["candidates"][0]

            if candidate.get("content"):
                content = candidate["content"]
                parts = content.get("parts", [])

                text_parts = []
                tool_calls = []

                for part in parts:
                    if part.get("text"):
                        text_parts.append(part["text"])
                    elif part.get("functionCall"):
                        func_call = part["functionCall"]
                        # Generate unique ID because Google doesn't provide tool call IDs
                        unique_id = f"call_{int(time.time() * 1000)}_{random.randint(1000, 9999)}"
                        tool_call = ToolCall(
                            id=unique_id,
                            type="function",
                            function=ToolCallFunction(
                                name=func_call.get("name", ""),
                                arguments=json.dumps(func_call.get("args", {})),
                            ),
                        )
                        tool_calls.append(tool_call)

                content_str = "\n".join(text_parts) if text_parts else None
                data.message = Message(role="assistant", content=content_str)

                if tool_calls:
                    data.tool_calls = tool_calls

            if candidate.get("finishReason"):
                data.finish_reason = candidate["finishReason"]

            # Google-specific response fields
            if candidate.get("safetyRatings"):
                data.safetyRatings = candidate["safetyRatings"]

            # Include all candidates if there are multiple
            if len(body["candidates"]) > 1:
                data.candidates = body["candidates"]

        # Additional Google-specific fields
        if body.get("promptFeedback"):
            data.promptFeedback = body["promptFeedback"]

        return data

    def _extract_messages(self, contents: list[dict[str, Any]]) -> list[Message]:
        if not isinstance(contents, list):
            return []

        result = []
        for content in contents:
            extracted = self._extract_message(content)
            if extracted:
                result.append(extracted)
        return result

    def _extract_message(self, content: dict[str, Any]) -> Message | None:
        if not content or not isinstance(content, dict):
            return None

        role = content.get("role", "user")
        if role == "model":
            role = "assistant"

        message = Message(role=role)

        parts = content.get("parts", [])
        text_parts = []
        tool_calls = []

        for part in parts:
            if part.get("text"):
                text_parts.append(part["text"])
            elif part.get("functionCall"):
                func_call = part["functionCall"]
                # Generate unique ID because Google doesn't provide tool call IDs
                unique_id = (
                    f"call_{int(time.time() * 1000)}_{random.randint(1000, 9999)}"
                )
                tool_call = ToolCall(
                    id=unique_id,
                    type="function",
                    function=ToolCallFunction(
                        name=func_call.get("name", ""),
                        arguments=json.dumps(func_call.get("args", {})),
                    ),
                )
                tool_calls.append(tool_call)

        if text_parts:
            message.content = "\n".join(text_parts)
        if tool_calls:
            message.tool_calls = tool_calls

        return message

    def _extract_tools(
        self, tools: list[dict[str, Any]]
    ) -> list[ToolDefinition] | None:
        if not isinstance(tools, list):
            return None

        result = []
        for tool in tools:
            if not tool or not tool.get("functionDeclarations"):
                continue

            for func_decl in tool["functionDeclarations"]:
                if not func_decl.get("name"):
                    continue

                definition = ToolDefinition(
                    type="function",
                    function=ToolDefinitionFunction(
                        name=func_decl.get("name", ""),
                        description=func_decl.get("description"),
                        parameters=func_decl.get("parameters"),
                    ),
                )
                result.append(definition)

        return result if result else None

    def _extract_usage(self, usage: dict[str, Any]) -> Usage | None:
        if not usage or not isinstance(usage, dict):
            return None

        return Usage(
            prompt_tokens=usage.get("promptTokenCount", 0),
            completion_tokens=usage.get("candidatesTokenCount", 0),
            total_tokens=usage.get("totalTokenCount", 0),
        )
