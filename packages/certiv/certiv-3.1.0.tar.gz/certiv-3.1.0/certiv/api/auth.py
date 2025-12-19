# Copyright (c) 2024 Certiv.ai
# SPDX-License-Identifier: MIT

"""AWS SigV4-style HMAC authentication for Certiv API requests."""

from __future__ import annotations

import hashlib
import hmac
from typing import Protocol
from urllib.parse import parse_qs, quote, urlparse


class SignatureGenerator(Protocol):
    """Protocol for signature generation, enabling dependency injection in tests."""

    def generate_signature(
        self,
        method: str,
        url: str,
        headers: dict[str, str],
        body: bytes | None,
        secret: str,
    ) -> str:
        """Generate HMAC signature for a request."""
        ...


class HMACAuthenticator:
    """AWS SigV4-style HMAC authenticator for Certiv API requests.

    Builds a canonical request and generates an HMAC-SHA256 signature.
    The canonical request format matches the api-server's expectations:

        HTTPMethod\\n
        CanonicalURI\\n
        CanonicalQueryString\\n
        CanonicalHeaders\\n
        \\n
        SignedHeaders\\n
        HashedPayload
    """

    def generate_signature(
        self,
        method: str,
        url: str,
        headers: dict[str, str],
        body: bytes | None,
        secret: str,
    ) -> str:
        """Generate HMAC-SHA256 signature for a request.

        Args:
            method: HTTP method (GET, POST, etc.)
            url: Full URL including scheme, host, path, and query string
            headers: Headers to include in signature (lowercase keys expected)
            body: Request body bytes (or None for bodyless requests)
            secret: Agent secret for HMAC signing

        Returns:
            Hex-encoded HMAC-SHA256 signature
        """
        parsed = urlparse(url)
        uri = parsed.path or "/"
        query_string = self._build_canonical_query_string(parsed.query)
        body_hash = self._hash_body(body)

        # Get sorted header names for signing
        signed_header_names = sorted(headers.keys())

        canonical_request = self._build_canonical_request(
            method=method,
            uri=uri,
            query_string=query_string,
            headers=headers,
            signed_header_names=signed_header_names,
            body_hash=body_hash,
        )

        return self._hmac_sha256(canonical_request, secret)

    def _build_canonical_query_string(self, query: str) -> str:
        """Build canonical query string per AWS SigV4.

        Query params are sorted by key name, then by value, URI-encoded.
        """
        if not query:
            return ""

        # Parse query string into dict of lists
        params = parse_qs(query, keep_blank_values=True)

        pairs = []
        for key in sorted(params.keys()):
            values = sorted(params[key])
            for value in values:
                # URI encode both key and value
                encoded_key = quote(key, safe="")
                encoded_value = quote(value, safe="")
                pairs.append(f"{encoded_key}={encoded_value}")

        return "&".join(pairs)

    def _hash_body(self, body: bytes | None) -> str:
        """Compute SHA-256 hash of request body.

        Returns hex-encoded hash. Empty/None body returns hash of empty bytes.
        """
        data = body if body is not None else b""
        return hashlib.sha256(data).hexdigest()

    def _build_canonical_request(
        self,
        method: str,
        uri: str,
        query_string: str,
        headers: dict[str, str],
        signed_header_names: list[str],
        body_hash: str,
    ) -> str:
        """Build AWS SigV4-style canonical request.

        Format:
            HTTPMethod\\n
            CanonicalURI\\n
            CanonicalQueryString\\n
            CanonicalHeaders\\n
            \\n
            SignedHeaders\\n
            HashedPayload
        """
        # Sort header names alphabetically (per AWS SigV4 spec)
        sorted_header_names = sorted(signed_header_names)

        lines = []

        # 1. HTTP Method
        lines.append(method.upper())

        # 2. Canonical URI
        lines.append(uri)

        # 3. Canonical Query String
        lines.append(query_string)

        # 4. Canonical Headers (sorted, lowercase name:trimmed value)
        for name in sorted_header_names:
            value = headers.get(name, "").strip()
            lines.append(f"{name.lower()}:{value}")

        # 5. Blank line after headers (per AWS spec)
        lines.append("")

        # 6. Signed headers list (semicolon-separated, lowercase, sorted)
        lines.append(";".join(name.lower() for name in sorted_header_names))

        # 7. Hashed payload
        lines.append(body_hash)

        return "\n".join(lines)

    def _hmac_sha256(self, message: str, secret: str) -> str:
        """Generate HMAC-SHA256 signature."""
        mac = hmac.new(
            secret.encode("utf-8"),
            message.encode("utf-8"),
            hashlib.sha256,
        )
        return mac.hexdigest()
