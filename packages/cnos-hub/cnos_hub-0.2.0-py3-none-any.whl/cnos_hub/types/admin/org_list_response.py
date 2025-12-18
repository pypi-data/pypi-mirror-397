# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional
from typing_extensions import Literal

from ..._models import BaseModel

__all__ = ["OrgListResponse"]


class OrgListResponse(BaseModel):
    """Organization DTO returned by admin endpoints."""

    id: str
    """Organization identifier."""

    created_at: str
    """Creation timestamp in RFC3339 format."""

    name: str
    """Human-readable name."""

    status: Literal["active", "suspended", "deleted"]
    """Current lifecycle status."""

    updated_at: str
    """Last update timestamp in RFC3339 format."""

    billing_tier: Optional[str] = None
    """Optional billing tier."""
