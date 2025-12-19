# Copyright (c) 2024 Certiv.ai
# SPDX-License-Identifier: MIT

from __future__ import annotations

from typing import Any, Callable
from urllib.parse import urlparse

import httpx

from ...logger import logger
from ..types import HandlerResult, InterceptedRequest, InterceptedResponse
from .parse import parse_json_body

_original_send: Callable | None = None
_certiv_endpoint_host: bytearray


def patch_httpx(
    request_handler: Callable[[InterceptedRequest], HandlerResult | None],
    response_handler: Callable[
        [InterceptedRequest, InterceptedResponse], HandlerResult | None
    ],
    endpoint: str,
) -> None:
    global _original_send, _certiv_endpoint_host

    if _original_send is not None:
        logger.warn("httpx already patched, skipping")
        return

    _original_send = httpx.Client.send

    # Extract hostname from endpoint to exclude SDK's own backend calls
    if endpoint:
        parsed = urlparse(endpoint)
        _certiv_endpoint_host = bytearray(parsed.netloc, "utf-8")
        logger.debug(f"httpx patcher will exclude requests to: {_certiv_endpoint_host}")

    def patched_send(
        self: httpx.Client, request: httpx.Request, **kwargs: Any
    ) -> httpx.Response:
        # Skip interception for SDK's own backend calls
        if request.url.netloc == _certiv_endpoint_host:
            return _original_send(self, request, **kwargs)

        req_headers = dict(request.headers)
        body_bytes = request.content if hasattr(request, "content") else b""

        intercepted_req = InterceptedRequest(
            url=str(request.url),
            method=request.method,
            headers=req_headers,
            body=parse_json_body(body_bytes, req_headers),
        )

        request_result = request_handler(intercepted_req)
        if request_result and request_result.body:
            modified_headers = dict(request.headers)
            modified_headers.pop("content-length", None)

            if request_result.additional_headers:
                modified_headers.update(request_result.additional_headers)

            request = httpx.Request(
                method=request.method,
                url=request.url,
                headers=modified_headers,
                content=request_result.body.encode("utf-8"),
            )
        elif request_result and request_result.additional_headers:
            # Only headers modified, not body
            for key, value in request_result.additional_headers.items():
                request.headers[key] = value

        response = _original_send(self, request, **kwargs)

        res_headers = dict(response.headers)
        res_body = response.content if hasattr(response, "content") else b""

        intercepted_res = InterceptedResponse(
            status=response.status_code,
            headers=res_headers,
            body=parse_json_body(res_body, res_headers),
        )

        handler_result = response_handler(intercepted_req, intercepted_res)

        if handler_result and handler_result.body:
            modified_headers = dict(response.headers)
            modified_headers.pop("content-length", None)
            modified_headers.pop("transfer-encoding", None)
            modified_headers.pop("content-encoding", None)

            if handler_result.additional_headers:
                modified_headers.update(handler_result.additional_headers)

            response = httpx.Response(
                status_code=response.status_code,
                headers=modified_headers,
                content=handler_result.body.encode("utf-8"),
                request=response.request,
            )

        return response

    httpx.Client.send = patched_send


def restore_httpx() -> None:
    global _original_send, _certiv_endpoint_host
    if _original_send is not None:
        httpx.Client.send = _original_send
        _original_send = None
        _certiv_endpoint_host = None
