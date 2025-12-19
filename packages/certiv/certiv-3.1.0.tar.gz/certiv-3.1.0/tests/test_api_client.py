#!/usr/bin/env python3
# Copyright (c) 2024 Certiv.ai
# SPDX-License-Identifier: MIT

"""
Unit tests for CertivAPIClient.

Tests the X-Instance-ID header and HMAC signature behavior:
- X-Instance-ID header should NOT be included on registerInstance
- X-Instance-ID header should be included on all subsequent calls
- HMAC signature format changes based on whether instance_id is set (AWS SigV4-style)
"""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from certiv.api.auth import HMACAuthenticator
from certiv.api.client import CertivAPIClient
from certiv.api.types import Heartbeat, InstanceRegistration, ResourceUsage, RuntimeInfo


class MockAuthenticator:
    """Mock authenticator that returns a fixed signature for testing."""

    def generate_signature(
        self,
        method: str,
        url: str,
        headers: dict[str, str],
        body: bytes | None,
        secret: str,
    ) -> str:
        return "mock-signature"


class CapturingAuthenticator:
    """Authenticator that captures calls for verification and delegates to real implementation."""

    def __init__(self):
        self.calls: list[dict] = []
        self._real = HMACAuthenticator()

    def generate_signature(
        self,
        method: str,
        url: str,
        headers: dict[str, str],
        body: bytes | None,
        secret: str,
    ) -> str:
        self.calls.append(
            {
                "method": method,
                "url": url,
                "headers": dict(headers),  # copy
                "body": body,
                "secret": secret,
            }
        )
        return self._real.generate_signature(method, url, headers, body, secret)


TEST_AGENT_ID = "test-agent-id"
TEST_AGENT_SECRET = "test-agent-secret"
TEST_INSTANCE_ID = "test-instance-123"
TEST_ENDPOINT = "https://api.test.com"


def create_registration() -> InstanceRegistration:
    return InstanceRegistration(
        hostname="test-host",
        process_id=1234,
        runtime_info=RuntimeInfo(
            python_version="3.12.0",
            platform="darwin",
            sdk_version="test-sdk-1.0.0",
            started_at="2024-01-01T00:00:00Z",
        ),
    )


def create_heartbeat() -> Heartbeat:
    return Heartbeat(
        instance_id=TEST_INSTANCE_ID,
        status="healthy",
        resource_usage=ResourceUsage(
            timestamp="2024-01-01T00:00:00Z",
        ),
    )


class TestXInstanceIDHeader:
    """Test X-Instance-ID header behavior."""

    def test_should_not_include_x_instance_id_on_register_instance(self):
        """X-Instance-ID should NOT be included on registerInstance."""
        captured_requests: list[dict] = []

        def mock_post(url, *, headers=None, content=None):
            captured_requests.append({"url": url, "headers": headers or {}})
            mock_response = MagicMock()
            mock_response.is_success = True
            mock_response.json.return_value = {
                "instance": {"instance_id": TEST_INSTANCE_ID}
            }
            return mock_response

        client = CertivAPIClient(
            TEST_ENDPOINT,
            TEST_AGENT_ID,
            TEST_AGENT_SECRET,
            "test-sdk",
            authenticator=MockAuthenticator(),
        )

        with patch.object(client._client, "post", side_effect=mock_post):
            client.register_instance(create_registration())

        assert len(captured_requests) == 1
        assert "X-Instance-ID" not in captured_requests[0]["headers"]

    def test_should_include_x_instance_id_on_calls_after_register_instance(self):
        """X-Instance-ID should be included on calls after registerInstance."""
        captured_requests: list[dict] = []

        def mock_post(url, *, headers=None, content=None):
            captured_requests.append({"url": url, "headers": headers or {}})
            mock_response = MagicMock()
            mock_response.is_success = True
            if "instances" in url:
                mock_response.json.return_value = {
                    "instance": {"instance_id": TEST_INSTANCE_ID}
                }
            else:
                mock_response.json.return_value = {"acknowledged": True}
            return mock_response

        client = CertivAPIClient(
            TEST_ENDPOINT,
            TEST_AGENT_ID,
            TEST_AGENT_SECRET,
            "test-sdk",
            authenticator=MockAuthenticator(),
        )

        with patch.object(client._client, "post", side_effect=mock_post):
            client.register_instance(create_registration())
            client.send_heartbeat(create_heartbeat())

        assert len(captured_requests) == 2
        assert "X-Instance-ID" not in captured_requests[0]["headers"]
        assert captured_requests[1]["headers"]["X-Instance-ID"] == TEST_INSTANCE_ID

    def test_should_include_x_instance_id_on_all_subsequent_calls(self):
        """X-Instance-ID should be included on all subsequent calls."""
        captured_requests: list[dict] = []

        def mock_post(url, *, headers=None, content=None):
            captured_requests.append({"url": url, "headers": headers or {}})
            mock_response = MagicMock()
            mock_response.is_success = True
            if "instances" in url:
                mock_response.json.return_value = {
                    "instance": {"instance_id": TEST_INSTANCE_ID}
                }
            else:
                mock_response.json.return_value = {"acknowledged": True}
            return mock_response

        client = CertivAPIClient(
            TEST_ENDPOINT,
            TEST_AGENT_ID,
            TEST_AGENT_SECRET,
            "test-sdk",
            authenticator=MockAuthenticator(),
        )

        with patch.object(client._client, "post", side_effect=mock_post):
            client.register_instance(create_registration())
            client.send_heartbeat(create_heartbeat())
            client.send_heartbeat(create_heartbeat())

        assert captured_requests[1]["headers"]["X-Instance-ID"] == TEST_INSTANCE_ID
        assert captured_requests[2]["headers"]["X-Instance-ID"] == TEST_INSTANCE_ID


class TestHMACSignature:
    """Test HMAC signature behavior with AWS SigV4-style canonical requests.

    Uses pre-computed test vectors to verify signature generation independently
    of the implementation being tested.
    """

    def test_should_not_include_instance_id_in_signature_for_register_instance(self):
        """Signature should be computed without x-instance-id header for registerInstance."""
        capturing_auth = CapturingAuthenticator()

        def mock_post(url, *, headers=None, content=None):
            mock_response = MagicMock()
            mock_response.is_success = True
            mock_response.json.return_value = {
                "instance": {"instance_id": TEST_INSTANCE_ID}
            }
            return mock_response

        client = CertivAPIClient(
            TEST_ENDPOINT,
            TEST_AGENT_ID,
            TEST_AGENT_SECRET,
            "test-sdk",
            authenticator=capturing_auth,
        )

        with patch.object(client._client, "post", side_effect=mock_post):
            client.register_instance(create_registration())

        # Verify authenticator was called with correct headers (no instance_id)
        assert len(capturing_auth.calls) == 1
        call = capturing_auth.calls[0]
        assert "x-agent-id" in call["headers"]
        assert "x-agent-timestamp" in call["headers"]
        assert "x-instance-id" not in call["headers"]

    def test_should_include_instance_id_in_signature_after_register_instance(self):
        """Signature should be computed with x-instance-id header after registerInstance."""
        capturing_auth = CapturingAuthenticator()

        def mock_post(url, *, headers=None, content=None):
            mock_response = MagicMock()
            mock_response.is_success = True
            if "instances" in url:
                mock_response.json.return_value = {
                    "instance": {"instance_id": TEST_INSTANCE_ID}
                }
            else:
                mock_response.json.return_value = {"acknowledged": True}
            return mock_response

        client = CertivAPIClient(
            TEST_ENDPOINT,
            TEST_AGENT_ID,
            TEST_AGENT_SECRET,
            "test-sdk",
            authenticator=capturing_auth,
        )

        with patch.object(client._client, "post", side_effect=mock_post):
            client.register_instance(create_registration())
            client.send_heartbeat(create_heartbeat())

        # Verify second call (heartbeat) includes instance_id
        assert len(capturing_auth.calls) == 2
        heartbeat_call = capturing_auth.calls[1]
        assert "x-agent-id" in heartbeat_call["headers"]
        assert "x-agent-timestamp" in heartbeat_call["headers"]
        assert heartbeat_call["headers"]["x-instance-id"] == TEST_INSTANCE_ID

    def test_different_signature_formats_before_and_after_registration(self):
        """Signature format should include instance_id only after registration."""
        capturing_auth = CapturingAuthenticator()

        def mock_post(url, *, headers=None, content=None):
            mock_response = MagicMock()
            mock_response.is_success = True
            if "instances" in url:
                mock_response.json.return_value = {
                    "instance": {"instance_id": TEST_INSTANCE_ID}
                }
            else:
                mock_response.json.return_value = {"acknowledged": True}
            return mock_response

        client = CertivAPIClient(
            TEST_ENDPOINT,
            TEST_AGENT_ID,
            TEST_AGENT_SECRET,
            "test-sdk",
            authenticator=capturing_auth,
        )

        with patch.object(client._client, "post", side_effect=mock_post):
            client.register_instance(create_registration())
            client.send_heartbeat(create_heartbeat())

        # Register call should NOT have instance_id
        register_headers = capturing_auth.calls[0]["headers"]
        assert "x-instance-id" not in register_headers

        # Heartbeat call SHOULD have instance_id
        heartbeat_headers = capturing_auth.calls[1]["headers"]
        assert heartbeat_headers["x-instance-id"] == TEST_INSTANCE_ID


class TestHMACSignatureVectors:
    """Test signature generation against pre-computed test vectors.

    These vectors were computed independently and hardcoded to ensure the
    implementation produces correct signatures without self-referential testing.
    """

    # Pre-computed test vector: GET request without instance_id
    # Canonical request:
    #   GET\n/test\n\nx-agent-id:agent-123\nx-agent-timestamp:2024-01-01T00:00:00Z\n\n
    #   x-agent-id;x-agent-timestamp\n<empty_body_hash>
    VECTOR_GET_NO_INSTANCE = {
        "method": "GET",
        "url": "https://api.test.com/test",
        "headers": {
            "x-agent-id": "agent-123",
            "x-agent-timestamp": "2024-01-01T00:00:00Z",
        },
        "body": None,
        "secret": "test-secret-key",
        "expected_signature": "468d58dcf4958159015ee48082639849ee6623ea362bda909abc37d1b0b28a44",
    }

    # Pre-computed test vector: POST request with instance_id and body
    # Body: {"status": "healthy"}
    # Body hash: 407cb67ade5df48a7fb4f8042f9f57de52af72d16e5122d436e487d8a122769c
    VECTOR_POST_WITH_INSTANCE = {
        "method": "POST",
        "url": "https://api.test.com/agents/agent-123/heartbeat",
        "headers": {
            "x-agent-id": "agent-123",
            "x-agent-timestamp": "2024-01-01T00:00:00Z",
            "x-instance-id": "instance-456",
        },
        "body": b'{"status": "healthy"}',
        "secret": "test-secret-key",
        "expected_signature": "ef626f3851ce71340cb2f9da476192a480b2b1ce3d252f6a0d0335223ea11ca7",
    }

    # Pre-computed test vector: GET with query string (params should be sorted)
    # URL: /test?z_param=last&a_param=first -> canonical query: a_param=first&z_param=last
    VECTOR_GET_WITH_QUERY = {
        "method": "GET",
        "url": "https://api.test.com/test?z_param=last&a_param=first",
        "headers": {
            "x-agent-id": "agent-123",
            "x-agent-timestamp": "2024-01-01T00:00:00Z",
        },
        "body": None,
        "secret": "test-secret-key",
        "expected_signature": "6f28c70e7045d591777e3701afa34b979afdd0e78d4e689cc22e991e8ccd7df1",
    }

    @pytest.fixture
    def auth(self):
        return HMACAuthenticator()

    def test_get_request_without_instance_id(self, auth):
        """Verify GET request signature against pre-computed vector."""
        v = self.VECTOR_GET_NO_INSTANCE
        signature = auth.generate_signature(
            method=v["method"],
            url=v["url"],
            headers=v["headers"],
            body=v["body"],
            secret=v["secret"],
        )
        assert signature == v["expected_signature"]

    def test_post_request_with_instance_id(self, auth):
        """Verify POST request with instance_id signature against pre-computed vector."""
        v = self.VECTOR_POST_WITH_INSTANCE
        signature = auth.generate_signature(
            method=v["method"],
            url=v["url"],
            headers=v["headers"],
            body=v["body"],
            secret=v["secret"],
        )
        assert signature == v["expected_signature"]

    def test_get_request_with_query_string(self, auth):
        """Verify GET request with query string signature against pre-computed vector."""
        v = self.VECTOR_GET_WITH_QUERY
        signature = auth.generate_signature(
            method=v["method"],
            url=v["url"],
            headers=v["headers"],
            body=v["body"],
            secret=v["secret"],
        )
        assert signature == v["expected_signature"]
