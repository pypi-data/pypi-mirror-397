#!/usr/bin/env python3
# Copyright (c) 2024 Certiv.ai
# SPDX-License-Identifier: MIT

"""Unit tests for HMACAuthenticator (AWS SigV4-style signatures)."""

from __future__ import annotations

import hashlib

import pytest

from certiv.api.auth import HMACAuthenticator

# SHA-256 hash of empty string
EMPTY_BODY_HASH = "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"


class TestBuildCanonicalQueryString:
    """Tests for _build_canonical_query_string."""

    def test_empty_query_string(self):
        auth = HMACAuthenticator()
        assert auth._build_canonical_query_string("") == ""

    def test_single_param(self):
        auth = HMACAuthenticator()
        result = auth._build_canonical_query_string("foo=bar")
        assert result == "foo=bar"

    def test_params_sorted_by_key(self):
        auth = HMACAuthenticator()
        result = auth._build_canonical_query_string("z_param=last&a_param=first")
        assert result == "a_param=first&z_param=last"

    def test_multiple_values_for_same_key(self):
        auth = HMACAuthenticator()
        result = auth._build_canonical_query_string("key=b&key=a")
        # Values should be sorted within the same key
        assert result == "key=a&key=b"

    def test_special_characters_uri_encoded(self):
        auth = HMACAuthenticator()
        result = auth._build_canonical_query_string("key=hello world")
        assert result == "key=hello%20world"

    def test_empty_value(self):
        auth = HMACAuthenticator()
        result = auth._build_canonical_query_string("key=")
        assert result == "key="


class TestHashBody:
    """Tests for _hash_body."""

    def test_empty_body(self):
        auth = HMACAuthenticator()
        result = auth._hash_body(None)
        assert result == EMPTY_BODY_HASH

    def test_empty_bytes(self):
        auth = HMACAuthenticator()
        result = auth._hash_body(b"")
        assert result == EMPTY_BODY_HASH

    def test_body_with_content(self):
        auth = HMACAuthenticator()
        body = b'{"action": "test"}'
        result = auth._hash_body(body)
        expected = hashlib.sha256(body).hexdigest()
        assert result == expected

    def test_body_hash_is_deterministic(self):
        auth = HMACAuthenticator()
        body = b'{"key": "value"}'
        assert auth._hash_body(body) == auth._hash_body(body)


class TestBuildCanonicalRequest:
    """Tests for _build_canonical_request."""

    def test_get_request_no_query_no_instance(self):
        auth = HMACAuthenticator()
        result = auth._build_canonical_request(
            method="GET",
            uri="/agents/agent-123/heartbeat",
            query_string="",
            headers={
                "x-agent-id": "agent-123",
                "x-agent-timestamp": "2024-01-01T00:00:00Z",
            },
            signed_header_names=["x-agent-id", "x-agent-timestamp"],
            body_hash=EMPTY_BODY_HASH,
        )

        expected = "\n".join(
            [
                "GET",
                "/agents/agent-123/heartbeat",
                "",  # empty query string
                "x-agent-id:agent-123",
                "x-agent-timestamp:2024-01-01T00:00:00Z",
                "",  # blank line after headers
                "x-agent-id;x-agent-timestamp",
                EMPTY_BODY_HASH,
            ]
        )
        assert result == expected

    def test_post_request_with_body(self):
        auth = HMACAuthenticator()
        body_hash = hashlib.sha256(b'{"status": "healthy"}').hexdigest()
        result = auth._build_canonical_request(
            method="POST",
            uri="/agents/agent-123/heartbeat",
            query_string="",
            headers={
                "x-agent-id": "agent-123",
                "x-agent-timestamp": "2024-01-01T00:00:00Z",
                "x-instance-id": "instance-456",
            },
            signed_header_names=["x-agent-id", "x-agent-timestamp", "x-instance-id"],
            body_hash=body_hash,
        )

        expected = "\n".join(
            [
                "POST",
                "/agents/agent-123/heartbeat",
                "",
                "x-agent-id:agent-123",
                "x-agent-instance-id:instance-456",  # alphabetically sorted
                "x-agent-timestamp:2024-01-01T00:00:00Z",
                "",
                "x-agent-id;x-agent-instance-id;x-agent-timestamp",
                body_hash,
            ]
        )
        # Note: headers are sorted, so x-instance-id comes before x-agent-timestamp
        # Wait, let me reconsider - the signed_header_names list determines what gets included
        # and they are sorted alphabetically when building the canonical request
        # x-agent-id < x-agent-timestamp < x-instance-id (alphabetically)
        # Actually: x-agent-id, x-agent-timestamp, x-instance-id
        # Sorting: x-agent-id < x-agent-timestamp < x-instance-id

        expected = "\n".join(
            [
                "POST",
                "/agents/agent-123/heartbeat",
                "",
                "x-agent-id:agent-123",
                "x-agent-timestamp:2024-01-01T00:00:00Z",
                "x-instance-id:instance-456",
                "",
                "x-agent-id;x-agent-timestamp;x-instance-id",
                body_hash,
            ]
        )
        assert result == expected

    def test_request_with_query_string(self):
        auth = HMACAuthenticator()
        result = auth._build_canonical_request(
            method="GET",
            uri="/test",
            query_string="a_param=first&z_param=last",
            headers={
                "x-agent-id": "agent-123",
                "x-agent-timestamp": "2024-01-01T00:00:00Z",
            },
            signed_header_names=["x-agent-id", "x-agent-timestamp"],
            body_hash=EMPTY_BODY_HASH,
        )

        expected = "\n".join(
            [
                "GET",
                "/test",
                "a_param=first&z_param=last",
                "x-agent-id:agent-123",
                "x-agent-timestamp:2024-01-01T00:00:00Z",
                "",
                "x-agent-id;x-agent-timestamp",
                EMPTY_BODY_HASH,
            ]
        )
        assert result == expected

    def test_headers_are_sorted_alphabetically(self):
        auth = HMACAuthenticator()
        result = auth._build_canonical_request(
            method="GET",
            uri="/test",
            query_string="",
            headers={
                "z-header": "last",
                "a-header": "first",
            },
            signed_header_names=["z-header", "a-header"],
            body_hash=EMPTY_BODY_HASH,
        )

        # Headers should be sorted alphabetically
        assert "a-header:first\nz-header:last" in result
        assert "a-header;z-header" in result


class TestGenerateSignature:
    """Tests for full signature generation using pre-computed test vectors."""

    def test_signature_without_instance_id(self):
        """POST request without instance_id - pre-computed signature."""
        auth = HMACAuthenticator()
        # Pre-computed: body_hash of b'{"hostname": "test-host"}' is
        # 36e7cbecd5e88c7e07e112c60bd544ac9f445ea72f76a4d9db8418c079b2736c
        signature = auth.generate_signature(
            method="POST",
            url="https://api.test.com/agents/agent-123/instances",
            headers={
                "x-agent-id": "agent-123",
                "x-agent-timestamp": "2024-01-01T00:00:00Z",
            },
            body=b'{"hostname": "test-host"}',
            secret="test-secret",
        )
        assert (
            signature
            == "c8e6d425bae699c17d960bd9e5974350eccf225e1e0cefa320c55ecf7321c129"
        )

    def test_signature_with_instance_id(self):
        """POST request with instance_id - pre-computed signature."""
        auth = HMACAuthenticator()
        # Pre-computed: body_hash of b'{"status": "healthy"}' is
        # 407cb67ade5df48a7fb4f8042f9f57de52af72d16e5122d436e487d8a122769c
        signature = auth.generate_signature(
            method="POST",
            url="https://api.test.com/agents/agent-123/heartbeat",
            headers={
                "x-agent-id": "agent-123",
                "x-agent-timestamp": "2024-01-01T00:00:00Z",
                "x-instance-id": "instance-456",
            },
            body=b'{"status": "healthy"}',
            secret="test-secret",
        )
        assert (
            signature
            == "a1f6a86e2bf27dfd6ee291d122f4faceabc8b3f11c9c4b1f73987d6e253a6a10"
        )

    def test_signature_with_query_string(self):
        """GET request with query string - pre-computed signature."""
        auth = HMACAuthenticator()
        signature = auth.generate_signature(
            method="GET",
            url="https://api.test.com/test?z_param=last&a_param=first",
            headers={
                "x-agent-id": "agent-123",
                "x-agent-timestamp": "2024-01-01T00:00:00Z",
            },
            body=None,
            secret="test-secret",
        )
        assert (
            signature
            == "6352784771766de9d5c412a51d1b578ad89309bc5f265fa7ee2de5d4b0f3d68f"
        )

    def test_different_secrets_produce_different_signatures(self):
        """Different secrets must produce different signatures."""
        auth = HMACAuthenticator()
        base_args = {
            "method": "GET",
            "url": "https://api.test.com/test",
            "headers": {
                "x-agent-id": "agent-123",
                "x-agent-timestamp": "2024-01-01T00:00:00Z",
            },
            "body": None,
        }

        sig1 = auth.generate_signature(**base_args, secret="secret-1")
        sig2 = auth.generate_signature(**base_args, secret="secret-2")

        assert sig1 != sig2

    def test_different_bodies_produce_different_signatures(self):
        """Different request bodies must produce different signatures."""
        auth = HMACAuthenticator()
        base_args = {
            "method": "POST",
            "url": "https://api.test.com/test",
            "headers": {
                "x-agent-id": "agent-123",
                "x-agent-timestamp": "2024-01-01T00:00:00Z",
            },
            "secret": "test-secret",
        }

        sig1 = auth.generate_signature(**base_args, body=b'{"data": "value1"}')
        sig2 = auth.generate_signature(**base_args, body=b'{"data": "value2"}')

        assert sig1 != sig2

    def test_signature_is_deterministic(self):
        """Same inputs must always produce the same signature."""
        auth = HMACAuthenticator()
        kwargs = {
            "method": "POST",
            "url": "https://api.test.com/test",
            "headers": {
                "x-agent-id": "agent-123",
                "x-agent-timestamp": "2024-01-01T00:00:00Z",
            },
            "body": b'{"key": "value"}',
            "secret": "test-secret",
        }

        sig1 = auth.generate_signature(**kwargs)
        sig2 = auth.generate_signature(**kwargs)

        assert sig1 == sig2
