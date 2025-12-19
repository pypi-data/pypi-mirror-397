# Copyright (c) 2024 Certiv.ai
# SPDX-License-Identifier: MIT

from __future__ import annotations

import threading
from datetime import datetime, timezone

import psutil

from .api.client import CertivAPIClient
from .api.types import Heartbeat as HeartbeatPayload
from .api.types import ResourceUsage
from .logger import logger


class Heartbeat:
    def __init__(self, api_client: CertivAPIClient, instance_id: str) -> None:
        self.api_client = api_client
        self.instance_id = instance_id
        self._thread: threading.Thread | None = None
        self._stop_event = threading.Event()
        self._interval = 30

    def start(self) -> None:
        self._stop_event.clear()
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def _run(self) -> None:
        process = psutil.Process()

        while not self._stop_event.is_set():
            try:
                resource_usage = ResourceUsage(
                    timestamp=datetime.now(timezone.utc).isoformat(),
                    cpu_percent=process.cpu_percent(),
                    memory_mb=process.memory_info().rss / 1024 / 1024,
                    memory_percent=process.memory_percent(),
                    num_threads=process.num_threads(),
                )

                heartbeat = HeartbeatPayload(
                    instance_id=self.instance_id,
                    status="healthy",
                    resource_usage=resource_usage,
                )

                self.api_client.send_heartbeat(heartbeat)
            except Exception as e:
                logger.error(f"Heartbeat failed: {e}")

            self._stop_event.wait(self._interval)

    def stop(self) -> None:
        if self._thread:
            self._stop_event.set()
            self._thread.join(timeout=5)
