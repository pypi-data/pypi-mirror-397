# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional
from typing_extensions import Literal

from .._models import BaseModel
from .shared.api_status import APIStatus
from .shared.execute_error_json import ExecuteErrorJson

__all__ = ["ProjectTransactionResponse", "Result"]


class Result(BaseModel):
    """Per-operation result emitted on success."""

    index: int
    """Zero-based index of the operation in the request."""

    kind: Literal["create_document", "replace_document", "delete_document", "create_collection", "delete_collection"]
    """Operation kind."""

    result: Optional[object] = None
    """Optional result payload (e.g., created document id/meta)."""


class ProjectTransactionResponse(BaseModel):
    """Transaction response envelope."""

    status: APIStatus
    """Status string: `"ok"` or `"error"`."""

    error: Optional[ExecuteErrorJson] = None
    """Error envelope reused from execute endpoints on failure."""

    results: Optional[List[Result]] = None
    """Per-operation results when successful."""
