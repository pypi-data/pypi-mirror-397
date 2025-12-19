# Copyright (c) 2024 Certiv.ai
# SPDX-License-Identifier: MIT

from __future__ import annotations

import json

from .api.types import PolicyDecision
from .batch.adapter import to_batch_item
from .batch.manager import BatchManager
from .interceptor.types import HandlerResult, InterceptedRequest, InterceptedResponse
from .logger import logger
from .policy import ResponseModification
from .policy.registry import PolicyHandlerRegistry
from .provider import LLMInteraction
from .provider.registry import ProviderRegistry
from .remote_exec.function_patcher import FunctionPatcher


class CertivTrafficHandler:
    def __init__(
        self,
        instance_id: str,
        providers: ProviderRegistry,
        policy: PolicyHandlerRegistry,
        batch_manager: BatchManager,
        function_patcher: FunctionPatcher,
        sdk_version: str,
    ) -> None:
        self.instance_id = instance_id
        self.providers = providers
        self.policy = policy
        self.batch_manager = batch_manager
        self.function_patcher = function_patcher
        self.sdk_version = sdk_version
        self.additional_headers = {
            "X-Certiv-ID": instance_id,
        }

    def handle_inbound_response(
        self, req: InterceptedRequest, res: InterceptedResponse
    ) -> HandlerResult | None:
        provider = self.providers.find(req)
        if not provider:
            return None

        logger.debug(f"Provider '{provider.name}' matched request: {req.url}")

        if is_streaming(res.headers):
            logger.debug("Streaming response detected, ignoring for now")
            return None

        content_type = res.headers.get("content-type", "")
        if "application/json" not in content_type:
            logger.debug("Non-JSON response, passing through")
            return None

        llm_interaction = provider.extract_interaction(req, res)
        if not llm_interaction:
            logger.debug(
                f"Provider '{provider.name}' could not extract interaction data"
            )
            return None

        log_interaction(llm_interaction)

        batch_item = to_batch_item(self.instance_id, llm_interaction, self.sdk_version)
        self.batch_manager.add_item(batch_item)

        if (
            not llm_interaction.response.tool_calls
            or len(llm_interaction.response.tool_calls) == 0
        ):
            logger.debug("No tool calls found in response")
            return None

        logger.debug(
            f"Found {len(llm_interaction.response.tool_calls)} tool call(s) from {provider.name}: "
            + ", ".join(
                [
                    f"{tc.function.name}({tc.function.arguments})"
                    for tc in llm_interaction.response.tool_calls
                ]
            )
        )

        try:
            policy_decision = self.batch_manager.flush()
        except Exception as e:
            logger.error(f"Flush failed: {e}")
            return None

        if not policy_decision:
            logger.debug("No policy decision (allowed by default)")
            return None

        logger.debug(f"Policy decision received: {policy_decision}")

        original_body = res.body
        modified_body = original_body

        policy_handler = self.policy.get(policy_decision.decision)

        try:
            modifications = policy_handler.handle(policy_decision, llm_interaction)
        except Exception as e:
            logger.error(f"Failed to handle policy decision: {e}")
            return None

        if policy_decision.should_patch and is_approved(
            policy_decision=policy_decision, modifications=modifications
        ):
            patched = self.function_patcher.patch_function_once(
                function_name=batch_item.content.tool_name,
                decision_id=policy_decision.decision_id,
                override=False,
            )

            if patched:
                logger.debug(
                    f"Patched function '{batch_item.content.tool_name}' based on policy decision '{policy_decision.decision_id}'"
                )
            else:
                logger.warn(
                    f"Failed to patch function '{batch_item.content.tool_name}' based on policy decision '{policy_decision.decision_id}'"
                )

        if modifications and len(modifications) > 0:
            modified_body = provider.apply_modifications(original_body, modifications)

        return HandlerResult(
            body=json.dumps(modified_body),
            additional_headers=self.additional_headers,
        )

    def handle_outbound_request(self, req: InterceptedRequest) -> HandlerResult | None:
        provider = self.providers.find(req)
        if not provider:
            return None

        if not req.body:
            return None

        body = provider.revert_certiv_tool(req.body)
        return HandlerResult(
            body=json.dumps(body),
            additional_headers=self.additional_headers,
        )

    def shutdown(self) -> None:
        self.batch_manager.flush()
        self.batch_manager.close_batch()


def is_streaming(headers: dict[str, str]) -> bool:
    content_type = headers.get("content-type", "")
    return "text/event-stream" in content_type


def log_interaction(interaction: LLMInteraction) -> None:
    data = {
        "model": interaction.request.model or interaction.response.model,
        "tool_definitions": (
            len(interaction.request.tools) if interaction.request.tools else 0
        ),
        "tool_calls": (
            len(interaction.response.tool_calls)
            if interaction.response.tool_calls
            else 0
        ),
        "messages": (
            len(interaction.request.messages) if interaction.request.messages else 0
        ),
    }

    if interaction.response.error:
        data["error"] = interaction.response.error

    logger.debug(f"Extracted {interaction.provider} interaction", data)


def is_approved(
    policy_decision: PolicyDecision, modifications: list[ResponseModification]
) -> bool:
    if policy_decision.decision == "allow":
        return True

    if not policy_decision.decision == "pause":
        return False

    # No modifications means approval in a pause case
    return len(modifications) == 0
