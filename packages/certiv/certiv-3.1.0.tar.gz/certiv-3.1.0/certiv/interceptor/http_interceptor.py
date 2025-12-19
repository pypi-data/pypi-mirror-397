# Copyright (c) 2024 Certiv.ai
# SPDX-License-Identifier: MIT

from __future__ import annotations

from typing import Callable

from ..logger import logger
from .patcher.httpx_patcher import patch_httpx, restore_httpx
from .patcher.requests_patcher import patch_requests, restore_requests
from .types import HandlerResult, InterceptedRequest, InterceptedResponse

_is_intercepting = False


def init_http_interceptor(
    request_handler: Callable[[InterceptedRequest], HandlerResult | None],
    response_handler: Callable[
        [InterceptedRequest, InterceptedResponse], HandlerResult | None
    ],
    endpoint: str,
) -> None:
    global _is_intercepting

    if _is_intercepting:
        logger.warn("HTTP interceptor already initialized")
        return

    logger.debug("Initializing HTTP interceptor")

    patch_httpx(request_handler, response_handler, endpoint)
    patch_requests(request_handler, response_handler, endpoint)

    _is_intercepting = True
    logger.debug("HTTP interceptor initialized (patched httpx, requests)")


def restore_http_interceptor() -> None:
    global _is_intercepting

    if not _is_intercepting:
        logger.debug("HTTP interceptor not initialized, nothing to restore")
        return

    logger.debug("Restoring original HTTP implementations")

    restore_httpx()
    restore_requests()

    _is_intercepting = False
    logger.debug("HTTP interceptor restored")
