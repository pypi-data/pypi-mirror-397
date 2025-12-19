# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional

from ..._models import BaseModel

__all__ = ["FileListResponse"]


class FileListResponse(BaseModel):
    """File response envelope returned from HTTP APIs."""

    id: str
    """File identifier."""

    created_at: str
    """Creation timestamp (RFC3339)."""

    name: str
    """Logical name/path."""

    org_id: str
    """Owning organization."""

    project_id: str
    """Owning project."""

    size_bytes: int
    """Raw size in bytes."""

    updated_at: str
    """Last update timestamp (RFC3339)."""

    content_type: Optional[str] = None
    """MIME type if provided."""

    deleted_at: Optional[str] = None
    """Soft-delete timestamp when applicable (RFC3339)."""
