# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional
from typing_extensions import Literal

from .._models import BaseModel
from .budgets_json import BudgetsJson
from .shared.api_status import APIStatus
from .shared.execute_error_json import ExecuteErrorJson

__all__ = [
    "CnoExecuteFunctionResponse",
    "Result",
    "ResultBudget",
    "ResultRuntimeStats",
    "ResultTrace",
    "ResultTraceEvent",
]


class ResultBudget(BaseModel):
    """Budget details when clamping was applied."""

    effective: BudgetsJson
    """Budget applied for execution."""

    limit: Optional[BudgetsJson] = None
    """Limit configured for the project/org/system."""

    requested: Optional[BudgetsJson] = None
    """Budget requested by the caller (after normalization)."""

    source: Optional[str] = None
    """Source of the budget computation."""


class ResultRuntimeStats(BaseModel):
    """Runtime statistics for the invocation."""

    duration_ms: int
    """Duration in milliseconds."""

    events_emitted: int
    """Trace events emitted (proxy for fuel/step usage)."""


class ResultTraceEvent(BaseModel):
    """Serialized trace event."""

    id: int
    """Unique identifier."""

    depth: int
    """Depth within the evaluation tree."""

    operation: str
    """Operation label."""

    duration_ms: Optional[int] = None
    """Duration in milliseconds, if known."""

    error: Optional[str] = None
    """Error string if the span failed."""

    input: Optional[object] = None
    """Input value at span start."""

    output: Optional[object] = None
    """Output value if the span completed successfully."""

    parent_id: Optional[int] = None
    """Parent span id when nested."""


class ResultTrace(BaseModel):
    """Optional captured trace."""

    events: List[ResultTraceEvent]
    """All span events."""

    roots: List[int]
    """Root span identifiers."""


class Result(BaseModel):
    """Successful execution payload."""

    value: object
    """JSON-encoded result value."""

    budget: Optional[ResultBudget] = None
    """Budget details when clamping was applied."""

    runtime_stats: Optional[ResultRuntimeStats] = None
    """Runtime statistics for the invocation."""

    trace: Optional[ResultTrace] = None
    """Optional captured trace."""

    value_cnon: Optional[object] = None
    """Optional CNON encoding of the value for lossless clients."""

    value_encoding: Optional[Literal["binary", "cnon", "json"]] = None
    """Encoding of `value` (e.g., `"json"` or `"base64"`)."""


class CnoExecuteFunctionResponse(BaseModel):
    """Response body for `/v1/cnos/execute` on success."""

    status: APIStatus
    """
    NOTE: Over HTTP, CNOS endpoints usually signal errors with HTTP 4xx/5xx
    responses and an `ErrorResponse` body, not with
    `ExecuteResponse.status = "error"`. The `error` field is primarily for non-HTTP
    transports or future expansion. Status string: `"ok"` or `"error"`.
    """

    error: Optional[ExecuteErrorJson] = None
    """Error payload (HTTP errors are typically surfaced via response envelopes)."""

    result: Optional[Result] = None
    """Successful execution payload."""
