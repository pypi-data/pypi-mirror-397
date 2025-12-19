# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List

from ..._models import BaseModel
from ..shared.api_status import APIStatus

__all__ = ["WorkspaceListResponse", "Item"]


class Item(BaseModel):
    """Workspace file metadata."""

    created_at: str
    """Creation timestamp."""

    path: str
    """File path."""

    revision_id: str
    """Revision identifier."""

    size_bytes: int
    """Content size in bytes."""

    updated_at: str
    """Last update timestamp."""


class WorkspaceListResponse(BaseModel):
    """Workspace file metadata list response."""

    items: List[Item]
    """Workspace files (metadata only)."""

    status: APIStatus
    """API status indicator."""
