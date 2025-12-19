# Copyright (c) 2024 Certiv.ai
# SPDX-License-Identifier: MIT

from __future__ import annotations

from urllib.parse import urlparse

from ..interceptor.types import InterceptedRequest
from ..logger import logger
from .types import LLMProvider


class ProviderRegistry:
    def __init__(self, *providers: LLMProvider) -> None:
        self.provider_by_name: dict[str, LLMProvider] = {}
        self.provider_by_hostname: dict[str, LLMProvider] = {}

        for provider in providers:
            self.provider_by_name[provider.name] = provider

            for hostname in provider.hostnames:
                self.provider_by_hostname[hostname] = provider

    def find(self, req: InterceptedRequest) -> LLMProvider | None:
        parsed_url = urlparse(req.url)
        host = parsed_url.hostname or parsed_url.netloc

        candidate = self.provider_by_hostname.get(host)
        if candidate:
            logger.debug(f"Found provider {candidate.name} for {host} (direct match)")
            return candidate

        for provider in self.provider_by_name.values():
            if not provider.matches(req):
                continue

            logger.debug(f"Found provider {provider.name} for {host} (fallback match)")
            return provider

        return None
