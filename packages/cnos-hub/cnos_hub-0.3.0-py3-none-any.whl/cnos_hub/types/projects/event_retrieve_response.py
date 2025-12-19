# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Dict, Optional
from typing_extensions import Literal

from ..._models import BaseModel

__all__ = ["EventRetrieveResponse"]


class EventRetrieveResponse(BaseModel):
    """Event DTO for API responses."""

    id: str
    """Event identifier."""

    created_at: str
    """Creation timestamp (RFC3339)."""

    payload: Dict[str, object]
    """Event payload."""

    project_id: str
    """Project identifier."""

    status: Literal["pending", "processing", "succeeded", "failed", "dead_letter"]
    """Event status."""

    type: str
    """Event type."""

    updated_at: str
    """Last update timestamp (RFC3339)."""

    meta: Optional[Dict[str, object]] = None
    """Event metadata."""
