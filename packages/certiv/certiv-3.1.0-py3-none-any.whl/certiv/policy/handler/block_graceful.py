# Copyright (c) 2024 Certiv.ai
# SPDX-License-Identifier: MIT

from __future__ import annotations

from datetime import datetime, timezone

from ...api.types import PolicyDecision
from ...provider.types import LLMInteraction
from ...tool.types import CertivToolArgs, PolicyInfo, ToolInfo
from ..base import (
    PolicyDecisionHandler,
    ReplaceToolCallsModification,
    ResponseModification,
)


class GracefulBlockHandler(PolicyDecisionHandler):
    name = "block_gracefully"

    def handle(
        self, decision: PolicyDecision, interaction: LLMInteraction
    ) -> list[ResponseModification]:
        if not interaction.response.tool_calls or not interaction.response.tool_calls:
            return []

        tool = interaction.response.tool_calls[0]

        args = CertivToolArgs(
            action="policy_block_graceful",
            timestamp=datetime.now(timezone.utc).isoformat(),
            tool=ToolInfo(
                name=tool.function.name,
                arguments=tool.function.arguments,
            ),
            policy=PolicyInfo(
                decision_id=decision.decision_id,
                decision=decision.decision,
                reason=decision.reason,
            ),
        )

        return [
            ReplaceToolCallsModification(
                tool_call={
                    "id": tool.id,
                    "name": "__CERTIV_TOOL__",
                    "arguments": args.model_dump_json(),
                },
            )
        ]
