# Copyright (c) 2024 Certiv.ai
# SPDX-License-Identifier: MIT

from __future__ import annotations

from ...api.types import PolicyDecision
from ...provider.types import LLMInteraction
from ..base import (
    PolicyDecisionHandler,
    RemoveToolCallsModification,
    ReplaceContentModification,
    ResponseModification,
)


class BlockHandler(PolicyDecisionHandler):
    name = "block"

    def handle(
        self, decision: PolicyDecision, interaction: LLMInteraction
    ) -> list[ResponseModification]:
        if not interaction.response.tool_calls:
            return []

        tool_call_ids = [tc.id for tc in interaction.response.tool_calls]
        tool_names = [tc.function.name for tc in interaction.response.tool_calls]
        all_tools = ", ".join(tool_names) if tool_names else "unknown"
        replacement_text = (
            f"Response was blocked by Certiv.ai policy: {all_tools} - {decision.reason}"
        )

        return [
            RemoveToolCallsModification(
                tool_call_ids=tool_call_ids,
                tool_call_names=tool_names,
            ),
            ReplaceContentModification(
                content=replacement_text,
            ),
        ]
