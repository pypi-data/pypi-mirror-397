# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional

from ...._models import BaseModel

__all__ = ["DocumentMeta"]


class DocumentMeta(BaseModel):
    """Document metadata exposed to clients."""

    deleted: bool
    """Whether the document is soft-deleted."""

    version: str
    """Opaque version token for optimistic concurrency."""

    created_at: Optional[str] = None
    """Creation timestamp (RFC3339)."""

    deleted_at: Optional[str] = None
    """Deletion timestamp (RFC3339)."""

    type_version: Optional[int] = None
    """Schema version when last written."""

    updated_at: Optional[str] = None
    """Last update timestamp (RFC3339)."""

    updated_by: Optional[str] = None
    """Actor that last wrote this document."""
