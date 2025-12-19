# Copyright (c) 2024 Certiv.ai
# SPDX-License-Identifier: MIT

from __future__ import annotations

import os
import platform
from datetime import datetime, timezone

from .api import CertivAPIClient
from .api.types import InstanceRegistration, RuntimeInfo
from .batch import BatchManager
from .heartbeat import Heartbeat
from .interceptor.http_interceptor import (
    init_http_interceptor,
    restore_http_interceptor,
)
from .logger import logger
from .policy import (
    AllowHandler,
    BlockHandler,
    GracefulBlockHandler,
    PauseHandler,
    PolicyHandlerRegistry,
)
from .provider import (
    AnthropicProvider,
    GoogleProvider,
    OpenAIProvider,
    ProviderRegistry,
)
from .remote_exec.function_patcher import FunctionPatcher
from .shutdown import run_before_shutdown
from .traffic_handler import CertivTrafficHandler

SDK_NAME = "certiv-python"
SDK_VERSION = "3.0.2"
SDK_NAME_VERSION = f"{SDK_NAME}/{SDK_VERSION}"


class CertivClient:
    def __init__(
        self,
        agent_id: str,
        agent_secret: str,
        endpoint: str = "https://api.certiv.ai",
        debug: bool = False,
    ) -> None:
        self.initialized = False
        self.agent_id = agent_id
        self.agent_secret = agent_secret
        self.endpoint = endpoint

        if debug:
            logger.set_log_level("debug")

        self.api_client = CertivAPIClient(
            self.endpoint,
            self.agent_id,
            self.agent_secret,
            SDK_NAME_VERSION,
        )
        self.traffic_handler: CertivTrafficHandler | None = None
        self.heartbeat: Heartbeat | None = None
        self.instance_id: str | None = None

    def init(self) -> None:
        if self.initialized:
            logger.warn("Certiv already initialized, reinitializing")
            self.shutdown()

        try:
            logger.debug(
                f"Initializing {SDK_NAME_VERSION}",
                {"agent_id": self.agent_id, "endpoint": self.endpoint},
            )

            registration = InstanceRegistration(
                hostname=platform.node(),
                process_id=os.getpid(),
                runtime_info=RuntimeInfo(
                    python_version=platform.python_version(),
                    platform=platform.system(),
                    sdk_version=SDK_NAME_VERSION,
                    started_at=datetime.now(timezone.utc).isoformat(),
                ),
            )

            registered_instance = self.api_client.register_instance(registration)

            self.instance_id = registered_instance.instance.instance_id

            logger.debug(f"Instance registered: {self.instance_id}")

            providers = ProviderRegistry(
                OpenAIProvider(),
                AnthropicProvider(),
                GoogleProvider(),
            )

            allow = AllowHandler(self.api_client)
            block = BlockHandler(self.api_client)
            pause = PauseHandler(self.api_client, block)
            graceful_block = GracefulBlockHandler(self.api_client)
            policy = PolicyHandlerRegistry(allow, block, pause, graceful_block)

            batch = BatchManager(self.api_client, self.agent_id)
            function_patcher = FunctionPatcher(self.api_client)

            self.traffic_handler = CertivTrafficHandler(
                self.instance_id,
                providers,
                policy,
                batch,
                function_patcher,
                SDK_NAME_VERSION,
            )

            init_http_interceptor(
                self.traffic_handler.handle_outbound_request,
                self.traffic_handler.handle_inbound_response,
                self.endpoint,
            )

            self.heartbeat = Heartbeat(self.api_client, self.instance_id)
            self.heartbeat.start()

            self.initialized = True
            logger.info("Certiv initialized successfully")
        except Exception as error:
            logger.error(f"Failed to initialize Certiv: {error}")
            raise error

    def shutdown(self) -> None:
        if not self.initialized:
            logger.debug("Certiv not initialized, nothing to shutdown")
            return

        logger.debug("Shutting down Certiv")
        try:
            if self.heartbeat:
                self.heartbeat.stop()
        except Exception as error:
            logger.error(f"Error stopping heartbeat: {error}")

        try:
            if self.traffic_handler:
                self.traffic_handler.shutdown()
        except Exception as error:
            logger.error(f"Error shutting down traffic handler: {error}")
        finally:
            restore_http_interceptor()

            self.initialized = False
            self.traffic_handler = None
            self.heartbeat = None
            self.instance_id = None

        logger.info("Certiv shutdown complete")


_client: CertivClient | None = None


def init(
    agent_id: str,
    agent_secret: str,
    endpoint: str = "https://api.certiv.ai",
    debug: bool = False,
) -> None:
    global _client
    if _client is None:
        _client = CertivClient(agent_id, agent_secret, endpoint, debug)
    _client.init()


def shutdown() -> None:
    global _client
    if not _client:
        logger.debug("Certiv not initialized")
        return
    _client.shutdown()
    _client = None


run_before_shutdown(shutdown)
