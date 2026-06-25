from dataclasses import dataclass
from typing import Optional


@dataclass
class Operation:
    operation_uid: str
    api_name: str
    method: str
    path: str
    operation_id: str
    summary: str
    description: str
    parameters_count: int
    has_request_body: bool
    response_codes: str


@dataclass
class TestCase:
    operation_uid: str
    prompt: str
    request_method: str
    request_path: str
    request_body: Optional[str]
    expected_status: Optional[int]


@dataclass
class ExecutionResult:
    operation_uid: str
    status_code: int
    response_time_ms: float
    response_body: str
    error_message: str


@dataclass
class RuntimeFeedback:
    operation_uid: str
    feedback: str
    success: bool


@dataclass
class MetricResult:
    operation_uid: str
    endpoint_covered: bool
    valid_request: bool
    status_code: int