# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing_extensions import Literal

from ..._models import BaseModel

__all__ = ["ProjectListResponse"]


class ProjectListResponse(BaseModel):
    """Project DTO returned by admin endpoints."""

    id: str
    """Project identifier."""

    created_at: str
    """Creation timestamp in RFC3339 format."""

    name: str
    """Human-readable name."""

    org_id: str
    """Owning organization identifier."""

    status: Literal["active", "readonly", "deleted"]
    """Current lifecycle status."""

    updated_at: str
    """Last update timestamp in RFC3339 format."""
