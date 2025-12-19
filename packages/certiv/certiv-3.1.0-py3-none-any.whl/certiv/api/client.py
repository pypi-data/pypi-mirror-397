# Copyright (c) 2024 Certiv.ai
# SPDX-License-Identifier: MIT

from __future__ import annotations

import json
from datetime import datetime, timezone

import httpx

from .auth import HMACAuthenticator, SignatureGenerator
from .types import (
    AddedBatchItem,
    ApiError,
    BatchClosure,
    BatchCreation,
    BatchItem,
    ClosedBatch,
    CreatedBatch,
    ExecutionOperation,
    Heartbeat,
    HeartbeatAck,
    InstanceRegistration,
    JobOperation,
    JobOperationApiResponse,
    PolicyStatus,
    RegisteredInstance,
    RemoteExecution,
)


class CertivAPIClient:
    def __init__(
        self,
        endpoint: str,
        agent_id: str,
        agent_secret: str,
        sdk_version: str,
        authenticator: SignatureGenerator | None = None,
    ) -> None:
        self.endpoint = endpoint.rstrip("/")
        self.agent_id = agent_id
        self.agent_secret = agent_secret
        self.sdk_version = sdk_version
        self._client = httpx.Client(timeout=30.0)
        self.instance_id: str | None = None
        self.authenticator = authenticator or HMACAuthenticator()

    def register_instance(
        self, registration: InstanceRegistration
    ) -> RegisteredInstance:
        """Register this SDK instance with the backend.

        Side effect: Sets self.instance_id from the response. All subsequent
        API requests will include X-Instance-ID header and modified HMAC signature.
        """
        path = f"/agents/{self.agent_id}/instances"
        response = self._make_request("POST", path, registration.model_dump())
        result = RegisteredInstance.model_validate(response)
        self.instance_id = result.instance.instance_id
        return result

    def send_heartbeat(self, heartbeat: Heartbeat) -> HeartbeatAck:
        path = f"/agents/{self.agent_id}/heartbeat"
        response = self._make_request("POST", path, heartbeat.model_dump())
        return HeartbeatAck.model_validate(response)

    def create_batch(self, batch: BatchCreation) -> CreatedBatch:
        path = f"/agents/{self.agent_id}/transactions/batches"
        batch_dict = batch.model_dump()
        if batch_dict.get("batch_metadata") is None:
            batch_dict["batch_metadata"] = {}
        response = self._make_request("POST", path, batch_dict)
        return CreatedBatch.model_validate(response)

    def add_item_to_batch(self, batch_id: str, item: BatchItem) -> AddedBatchItem:
        path = f"/agents/{self.agent_id}/transactions/batches/{batch_id}/items"
        response = self._make_request("POST", path, item.model_dump())
        return AddedBatchItem.model_validate(response)

    def close_batch(self, closure: BatchClosure) -> ClosedBatch:
        path = f"/agents/{self.agent_id}/transactions/batches/close"
        response = self._make_request("POST", path, closure.model_dump())
        return ClosedBatch.model_validate(response)

    def poll_policy_decision(self, pause_id: str) -> PolicyStatus:
        path = f"/agents/{self.agent_id}/pauses/{pause_id}"
        response = self._make_request("GET", path)
        return PolicyStatus.model_validate(response)

    def execute_remote(self, execution: RemoteExecution) -> ExecutionOperation:
        path = f"/agents/{self.agent_id}/execute-remote"
        response = self._make_request("POST", path, execution.model_dump())
        return ExecutionOperation.model_validate(response)

    def poll_execution_operation(self, operation_id: str) -> JobOperation:
        path = f"/jobs/{operation_id}"
        response = self._make_request("GET", path)

        # Parse the wrapped API response
        wrapped_response = JobOperationApiResponse.model_validate(response)

        # Unwrap and return as JobOperation with the expected structure
        return JobOperation(
            operation_id=wrapped_response.job.id,
            status=wrapped_response.job.status,
            job_result=wrapped_response.job.job_result,
            error_message=wrapped_response.job.error_message,
        )

    def _make_request(
        self,
        method: str,
        path: str,
        body: dict | None = None,
    ) -> dict:
        url = f"{self.endpoint}{path}"
        timestamp = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        timestamp = timestamp.split(".")[0] + "Z"

        # Serialize body to bytes for signature computation
        body_bytes: bytes | None = None
        if body is not None:
            body_bytes = json.dumps(body).encode("utf-8")

        # Build headers dict for signature (lowercase keys as expected by authenticator)
        # Signed headers: x-agent-id, x-agent-timestamp, and x-instance-id (when set)
        sig_headers = {
            "x-agent-id": self.agent_id,
            "x-agent-timestamp": timestamp,
        }
        if self.instance_id is not None:
            sig_headers["x-instance-id"] = self.instance_id

        signature = self.authenticator.generate_signature(
            method=method,
            url=url,
            headers=sig_headers,
            body=body_bytes,
            secret=self.agent_secret,
        )

        headers = {
            "Authorization": f"Bearer {self.agent_secret}",
            "X-Agent-ID": self.agent_id,
            "X-Agent-Signature": signature,
            "X-Agent-Timestamp": timestamp,
            "User-Agent": self.sdk_version,
        }

        if self.instance_id is not None:
            headers["X-Instance-ID"] = self.instance_id

        if method == "POST" and body is not None:
            headers["Content-Type"] = "application/json"

        try:
            if method == "GET":
                response = self._client.get(url, headers=headers)
            elif method == "POST":
                response = self._client.post(url, headers=headers, content=body_bytes)
            else:
                raise ApiError(f"Unsupported HTTP method: {method}")

        except httpx.TimeoutException as e:
            raise ApiError(
                "Backend request timed out",
                status_code=504,
                context={"url": url, "timeout": 30.0},
            ) from e
        except httpx.RequestError as e:
            raise ApiError(
                f"Backend request failed: {str(e)}",
                status_code=0,
                context={"url": url, "original_error": str(e)},
            ) from e

        if not response.is_success:
            error_body = ""
            try:
                error_body = response.text
            except Exception:
                pass

            raise ApiError(
                f"Backend request failed with status {response.status_code}",
                status_code=response.status_code,
                context={"url": url, "response_body": error_body},
            )

        try:
            return response.json()
        except Exception as e:
            raise ApiError(
                f"Failed to parse response JSON: {str(e)}",
                status_code=response.status_code,
                context={"url": url, "response_text": response.text},
            ) from e

    def close(self) -> None:
        self._client.close()
