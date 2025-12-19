# Copyright (c) 2024 Certiv.ai
# SPDX-License-Identifier: MIT

from __future__ import annotations

from typing import Any, Callable
from urllib.parse import urlparse

import requests
from requests.adapters import HTTPAdapter

from ...logger import logger
from ..types import HandlerResult, InterceptedRequest, InterceptedResponse
from .parse import parse_json_body


class CertivHTTPAdapter(HTTPAdapter):
    def __init__(
        self,
        request_handler: Callable[[InterceptedRequest], HandlerResult | None],
        response_handler: Callable[
            [InterceptedRequest, InterceptedResponse], HandlerResult | None
        ],
        endpoint_host: str,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self.request_handler = request_handler
        self.response_handler = response_handler
        self.endpoint_host = endpoint_host

    def send(
        self,
        request: requests.PreparedRequest,
        **kwargs: Any,
    ) -> requests.Response:
        # Skip interception for SDK's own backend calls
        parsed_url = urlparse(request.url)
        if parsed_url.netloc == self.endpoint_host:
            return super().send(request, **kwargs)

        req_headers = dict(request.headers) if request.headers else {}
        body_bytes = request.body if request.body else b""

        if isinstance(body_bytes, str):
            body_bytes = body_bytes.encode("utf-8")

        intercepted_req = InterceptedRequest(
            url=str(request.url),
            method=str(request.method),
            headers=req_headers,
            body=parse_json_body(body_bytes, req_headers),
        )

        request_result = self.request_handler(intercepted_req)
        if request_result and request_result.body:
            request.body = request_result.body.encode("utf-8")
            request.headers.pop("Content-Length", None)
            if request_result.additional_headers:
                for key, value in request_result.additional_headers.items():
                    request.headers[key] = value

        response = super().send(request, **kwargs)

        res_headers = dict(response.headers)
        res_body = response.content if hasattr(response, "content") else b""

        intercepted_res = InterceptedResponse(
            status=response.status_code,
            headers=res_headers,
            body=parse_json_body(res_body, res_headers),
        )

        handler_result = self.response_handler(intercepted_req, intercepted_res)

        if handler_result and handler_result.body:
            response._content = handler_result.body.encode("utf-8")
            response.headers.pop("Transfer-Encoding", None)
            response.headers.pop("Content-Encoding", None)
            if handler_result.additional_headers:
                for key, value in handler_result.additional_headers.items():
                    response.headers[key] = value

        return response


_original_get_adapter: Callable | None = None
_certiv_adapter: CertivHTTPAdapter | None = None


def patch_requests(
    request_handler: Callable[[InterceptedRequest], HandlerResult | None],
    response_handler: Callable[
        [InterceptedRequest, InterceptedResponse], HandlerResult | None
    ],
    endpoint: str,
) -> None:
    global _certiv_adapter, _original_get_adapter

    if _certiv_adapter is not None:
        logger.warn("requests already patched, skipping")
        return

    # Extract hostname from endpoint to exclude SDK's own backend calls
    parsed = urlparse(endpoint)
    endpoint_host = parsed.netloc
    logger.debug(f"requests patcher will exclude requests to: {endpoint_host}")

    _certiv_adapter = CertivHTTPAdapter(
        request_handler, response_handler, endpoint_host
    )

    # Patch Session.get_adapter to return our adapter for http/https
    _original_get_adapter = requests.Session.get_adapter

    def patched_get_adapter(self: requests.Session, url: str) -> HTTPAdapter:
        # Return our custom adapter for http/https URLs
        if url.startswith(("http://", "https://")):
            return _certiv_adapter
        return _original_get_adapter(self, url)

    requests.Session.get_adapter = patched_get_adapter


def restore_requests() -> None:
    global _certiv_adapter, _original_get_adapter
    if _original_get_adapter is not None:
        requests.Session.get_adapter = _original_get_adapter
        _original_get_adapter = None
        _certiv_adapter = None
