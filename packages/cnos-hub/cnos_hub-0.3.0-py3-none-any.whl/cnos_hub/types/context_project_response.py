# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional
from datetime import datetime
from typing_extensions import Literal

from .._models import BaseModel

__all__ = ["ContextProjectResponse"]


class ContextProjectResponse(BaseModel):
    """Project entity representing a unit of isolation for workloads."""

    id: str
    """Unique project identifier."""

    created_at: datetime
    """Creation timestamp."""

    name: str
    """Human-readable name for the project."""

    org_id: str
    """Owning organization."""

    revision_id: str
    """Revision for this project metadata row."""

    status: Literal["active", "readonly", "deleted"]
    """Current lifecycle status."""

    updated_at: datetime
    """Last update timestamp."""

    updated_by: Optional[str] = None
    """Actor that last updated the project."""
