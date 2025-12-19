# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional
from typing_extensions import Literal

from ..._models import BaseModel

__all__ = ["TaskRunResponse"]


class TaskRunResponse(BaseModel):
    """API representation of a task run."""

    id: str
    """Run identifier."""

    started_at: str
    """Start timestamp (RFC3339)."""

    status: Literal["running", "succeeded", "failed", "retried", "cancelled"]
    """Run status."""

    task_id: str
    """Associated task identifier."""

    error: Optional[str] = None
    """Optional error message."""

    finished_at: Optional[str] = None
    """Optional finish timestamp (RFC3339)."""
