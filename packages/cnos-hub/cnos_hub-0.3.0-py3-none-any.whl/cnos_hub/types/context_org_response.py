# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional
from datetime import datetime
from typing_extensions import Literal

from .._models import BaseModel

__all__ = ["ContextOrgResponse"]


class ContextOrgResponse(BaseModel):
    """Organization entity representing a tenant in the system."""

    id: str
    """Unique organization identifier."""

    created_at: datetime
    """Creation timestamp."""

    name: str
    """Human-readable name for the organization."""

    revision_id: str
    """Revision for this org metadata row."""

    status: Literal["active", "suspended", "deleted"]
    """Current lifecycle status."""

    updated_at: datetime
    """Last update timestamp."""

    billing_tier: Optional[str] = None
    """Optional billing tier identifier."""

    updated_by: Optional[str] = None
    """Actor that last updated the org."""
