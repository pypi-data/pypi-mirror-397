# Copyright (c) 2024 Certiv.ai
# SPDX-License-Identifier: MIT

from __future__ import annotations

from enum import Enum
from typing import Any, Literal

from pydantic import BaseModel


class RuntimeInfo(BaseModel):
    python_version: str | None = None
    platform: str
    sdk_version: str
    started_at: str
    environment: str | None = None


class ResourceUsage(BaseModel):
    cpu_percent: float | None = None
    memory_mb: float | None = None
    memory_percent: float | None = None
    num_threads: int | None = None
    timestamp: str
    note: str | None = None
    error: str | None = None


class InstanceRegistration(BaseModel):
    hostname: str
    process_id: int
    runtime_info: RuntimeInfo


class RegisteredInstanceData(BaseModel):
    instance_id: str


class RegisteredInstance(BaseModel):
    instance: RegisteredInstanceData


class Heartbeat(BaseModel):
    instance_id: str
    status: Literal["healthy", "unhealthy", "stopped"]
    resource_usage: ResourceUsage


class HeartbeatAck(BaseModel):
    acknowledged: bool


class BatchStatus(str, Enum):
    OPEN = "open"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class BatchCreation(BaseModel):
    agent_id: str
    stear_group_id: str | None = None
    tags: list[str] | None = None
    timestamp: str | None = None
    batch_metadata: dict[str, Any] | None = None


class CreatedBatchData(BaseModel):
    id: str
    status: BatchStatus
    created_at: str


class CreatedBatch(BaseModel):
    batch: CreatedBatchData


class FunctionCall(BaseModel):
    name: str
    arguments: str


class ToolCallFunction(BaseModel):
    name: str
    arguments: str


class ToolDefinitionFunction(BaseModel):
    name: str
    description: str | None = None
    parameters: Any | None = None


class BatchItemMessage(BaseModel):
    role: Literal["system", "user", "assistant", "tool", "function"]
    content: str | None = None
    tool_calls: list[BatchItemToolCall] | None = None
    function_call: FunctionCall | None = None
    tool_call_id: str | None = None
    name: str | None = None


class BatchItemToolCall(BaseModel):
    type: Literal["function"]
    id: str | None = None
    function: ToolCallFunction


class BatchItemToolDefinition(BaseModel):
    type: Literal["function"]
    function: ToolDefinitionFunction


class ToolExecutionContent(BaseModel):
    tool_calls: list[BatchItemToolCall]
    tool_name: str
    tool_parameters: dict[str, Any]
    messages: list[BatchItemMessage]
    timestamp: str
    interaction_type: Literal["request", "response"]
    instance_id: str
    execution_id: str | None = None
    sdk_version: str | None = None


class ChatHistoryContent(BaseModel):
    messages: list[BatchItemMessage]
    timestamp: str
    interaction_type: Literal["request", "response"]
    instance_id: str


class UsageData(BaseModel):
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int


class AnalysisData(BaseModel):
    is_llm: bool
    has_tool_requests: bool
    provider: str | None = None
    model: str | None = None
    confidence: float | None = None


class ItemMetadata(BaseModel):
    auto_captured: bool | None = None
    capture_method: Literal["http", "manual"] | None = None
    response_id: str | None = None
    usage: UsageData | None = None
    has_tool_calls: bool | None = None
    tool_calls: list[BatchItemToolCall] | None = None
    available_tools: list[BatchItemToolDefinition] | None = None
    available_tools_count: int | None = None
    has_graceful_block: bool | None = None
    llm_detected: bool | None = None
    analysis: AnalysisData | None = None
    policy_decision: PolicyDecision | None = None
    pause_id: str | None = None

    class Config:
        extra = "allow"


class ToolExecutionItem(BaseModel):
    item_type: Literal["tool_execution"]
    content: ToolExecutionContent
    item_metadata: ItemMetadata | None = None


class ChatHistoryItem(BaseModel):
    item_type: Literal["chat_history"]
    content: ChatHistoryContent
    item_metadata: ItemMetadata | None = None


BatchItem = ToolExecutionItem | ChatHistoryItem


class PolicyDecision(BaseModel):
    decision: Literal["allow", "block", "block_gracefully", "pause"]
    reason: str
    decision_id: str
    pause_id: str | None = None
    should_patch: bool | None = None
    patch_reason: str | None = None


class AddedBatchItemMetadata(BaseModel):
    policy_decision: PolicyDecision | None = None
    pause_id: str | None = None

    class Config:
        extra = "allow"


class AddedBatchItemData(BaseModel):
    id: str
    item_metadata: AddedBatchItemMetadata | None = None


class RecommendationData(BaseModel):
    function_name: str
    recommendation: str
    reason: str


class AddedBatchItem(BaseModel):
    success: bool
    item: AddedBatchItemData
    policy_decision: PolicyDecision | None = None
    recommendation: RecommendationData | None = None


class BatchClosure(BaseModel):
    batch_id: str


class ClosedBatch(BaseModel):
    id: str


class PolicyStatus(BaseModel):
    status: Literal["pending", "approved", "denied"]
    execution_response_id: str | None = None
    policy_decision: PolicyDecision | None = None
    reason: str | None = None


class RemoteExecution(BaseModel):
    decision_id: str
    function_name: str
    function_signature: str | None = None
    args: list[Any] | None = None
    kwargs: dict[str, Any] | None = None
    function_code: str | None = None
    function_hash: str
    dependencies: list[str] | None = None
    override: bool


class CertivFunctionResult(BaseModel):
    function_name: str
    args: list[Any]
    kwargs: dict[str, Any]
    result: Any | None
    success: bool
    error: str | None


class JobResultData(BaseModel):
    result: CertivFunctionResult | dict[str, Any] | None = None
    stdout: str | None = None
    output: str | dict[str, Any] | None = None


class JobStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    TIMEOUT = "timeout"


class JobData(BaseModel):
    """Inner job object from the API response"""

    id: str
    status: JobStatus
    job_result: JobResultData | None = None
    error_message: str | None = None
    # Include other fields that might be in the response but we don't need
    stear_group_id: str | None = None
    created_by: str | None = None
    created_at: str | None = None
    updated_at: str | None = None
    job_type: str | None = None
    priority: int | None = None
    timeout_at: str | None = None
    timeout_seconds: int | None = None
    job_payload: dict[str, Any] | None = None
    progress_percent: int | None = None
    agent_id: str | None = None

    class Config:
        extra = "allow"  # Allow extra fields we don't care about


class JobOperationApiResponse(BaseModel):
    """API response wrapper for job polling - matches backend response format"""

    job: JobData


class JobOperation(BaseModel):
    """Internal representation after unwrapping the API response"""

    operation_id: str
    status: JobStatus
    job_result: JobResultData | None = None
    error_message: str | None = None


class ExecutionOperation(BaseModel):
    operation_id: str
    status: str


class ApiError(Exception):
    def __init__(
        self,
        message: str,
        status_code: int | None = None,
        context: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.context = context or {}
        self.name = "CertivApiError"
        self.code = "API_ERROR"
