# Copyright (c) 2024 Certiv.ai
# SPDX-License-Identifier: MIT

from __future__ import annotations

import time
from datetime import datetime, timezone
from typing import Any

from ..api.client import CertivAPIClient
from ..api.types import (
    BatchClosure,
    BatchCreation,
    BatchItem,
    PolicyDecision,
)
from ..logger import logger


class BatchManager:
    def __init__(self, api_client: CertivAPIClient, agent_id: str) -> None:
        self.api_client = api_client
        self.agent_id = agent_id
        self.current_batch_id: str | None = None
        self.queued_items: list[BatchItem] = []
        self.max_retries = 3
        self.retry_delay_ms = 1000

    def add_item(self, item: BatchItem) -> None:
        self.queued_items.append(item)
        logger.debug(f"Added item to queue (size: {len(self.queued_items)})")

    def flush(self) -> PolicyDecision | None:
        if not self.queued_items:
            logger.debug("No items to flush")
            return None

        if self.current_batch_id is None:
            self._ensure_batch_created()

        if self.current_batch_id is None:
            logger.error("Failed to create batch, cannot flush items")
            return None

        logger.debug(
            f"Flushing {len(self.queued_items)} items in batch {self.current_batch_id}"
        )

        # Copy items before clearing queue to prevent concurrent modification issues
        items = list(self.queued_items)
        self.queued_items.clear()

        policy_decision: PolicyDecision | None = None

        for item in items:
            result = self._add_item_with_retry(self.current_batch_id, item)

            if not result:
                continue

            # Only consider policy decisions from tool_execution items
            if item.item_type != "tool_execution":
                continue

            if result.policy_decision:
                policy_decision = result.policy_decision

        self.close_batch()

        logger.debug(f"Flushed batch {self.current_batch_id}")

        return policy_decision

    def close_batch(self) -> None:
        if self.current_batch_id is None:
            logger.debug("No batch to close")
            return

        logger.debug(f"Closing batch: {self.current_batch_id}")

        try:
            closure = BatchClosure(batch_id=self.current_batch_id)
            self.api_client.close_batch(closure)
            logger.debug(f"Closed batch {self.current_batch_id}")
            self.current_batch_id = None
        except Exception as e:
            logger.error(f"Failed to close batch: {e}")

    def _ensure_batch_created(self) -> None:
        if self.current_batch_id is not None:
            return

        try:
            batch_creation = BatchCreation(agent_id=self.agent_id)
            result = self.api_client.create_batch(batch_creation)
            self.current_batch_id = result.batch.id
            logger.debug(f"Created batch {self.current_batch_id}")
        except Exception as e:
            logger.error(f"Failed to create batch: {e}")
            self.current_batch_id = None

    def _add_item_with_retry(self, batch_id: str, item: BatchItem) -> Any | None:
        for attempt in range(1, self.max_retries + 1):
            try:
                result = self.api_client.add_item_to_batch(batch_id, item)
                logger.debug(f"Added item to batch {batch_id}")
                return result
            except Exception as e:
                logger.warn(
                    f"Failed to add item to batch (attempt {attempt}/{self.max_retries}): {e}"
                )

                if attempt < self.max_retries:
                    delay_seconds = (self.retry_delay_ms * (2 ** (attempt - 1))) / 1000
                    time.sleep(delay_seconds)
                else:
                    logger.error(
                        f"Failed to add item to batch after {self.max_retries} attempts"
                    )
                    return None

        return None
