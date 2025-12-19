# Copyright (c) 2024 Certiv.ai
# SPDX-License-Identifier: MIT

from __future__ import annotations

import time

from ...api.types import PolicyDecision, PolicyStatus
from ...logger import logger
from ...provider.types import LLMInteraction
from ..base import PolicyDecisionHandler, ResponseModification


class PauseHandler(PolicyDecisionHandler):
    name = "pause"

    POLL_INTERVAL_MS = 1000
    MAX_POLL_ATTEMPTS = 300

    def __init__(self, api_client, block_handler: PolicyDecisionHandler) -> None:
        super().__init__(api_client)
        self.block_handler = block_handler

    def handle(
        self, decision: PolicyDecision, interaction: LLMInteraction
    ) -> list[ResponseModification]:
        pause_id = decision.pause_id

        if not pause_id:
            logger.error(f"Pause decision missing pause_id: {decision.decision_id}")

            return self.block_handler.handle(
                PolicyDecision(
                    decision="block",
                    reason="Pause decision missing pause_id",
                    decision_id=decision.decision_id,
                ),
                interaction,
            )

        logger.debug(
            f"Tool execution paused: {pause_id} (decision: {decision.decision_id})"
        )

        pause_result = self._poll_for_decision(pause_id)

        if pause_result == "timeout":
            logger.warn(f"Pause polling timed out: {pause_id}")

            return self.block_handler.handle(
                PolicyDecision(
                    decision="block",
                    reason="Pause request timed out",
                    decision_id=decision.decision_id,
                ),
                interaction,
            )

        if pause_result.status == "denied":
            logger.warn(
                f"Pause request denied: {pause_id} (reason: {pause_result.reason})"
            )

            return self.block_handler.handle(
                PolicyDecision(
                    decision="block",
                    reason="Pause request was denied",
                    decision_id=decision.decision_id,
                ),
                interaction,
            )

        logger.debug(f"Pause request approved: {pause_id}")
        return []

    def _poll_for_decision(self, pause_id: str) -> PolicyStatus | str:
        start_time = time.time()

        for attempt in range(1, self.MAX_POLL_ATTEMPTS + 1):
            elapsed = time.time() - start_time

            if elapsed > (self.MAX_POLL_ATTEMPTS * self.POLL_INTERVAL_MS / 1000):
                return "timeout"

            if attempt % 10 == 0 or attempt <= 5:
                logger.debug(
                    f"Polling for pause decision (attempt: {attempt}/{self.MAX_POLL_ATTEMPTS}, elapsed: {int(elapsed)}s)"
                )

            try:
                status = self.api_client.poll_policy_decision(pause_id)

                if status.status == "approved" or status.status == "denied":
                    return status

                time.sleep(self.POLL_INTERVAL_MS / 1000)
            except Exception as e:
                logger.warn(f"Polling error (attempt {attempt}): {e}")

                time.sleep(self.POLL_INTERVAL_MS / 1000)

        return "timeout"
