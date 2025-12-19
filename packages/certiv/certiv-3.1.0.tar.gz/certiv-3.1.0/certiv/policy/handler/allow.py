# Copyright (c) 2024 Certiv.ai
# SPDX-License-Identifier: MIT

from __future__ import annotations

from ...api.types import PolicyDecision
from ...provider.types import LLMInteraction
from ..base import PolicyDecisionHandler, ResponseModification


class AllowHandler(PolicyDecisionHandler):
    name = "allow"

    def handle(
        self, decision: PolicyDecision, interaction: LLMInteraction
    ) -> list[ResponseModification]:
        return []
