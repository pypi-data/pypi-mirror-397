# Copyright (c) 2024 Certiv.ai
# SPDX-License-Identifier: MIT

from __future__ import annotations

from ..logger import logger
from .base import PolicyDecisionHandler


class PolicyHandlerRegistry:
    def __init__(self, *handlers: PolicyDecisionHandler) -> None:
        self.handlers: dict[str, PolicyDecisionHandler] = {
            handler.name: handler for handler in handlers
        }

    def get(self, decision: str) -> PolicyDecisionHandler:
        handler = self.handlers.get(decision)
        if not handler:
            logger.warn(
                f"No handler found for decision type: {decision}, using allow handler"
            )
            return self.handlers["allow"]
        return handler
