# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional

from ..._models import BaseModel

__all__ = ["CollectionListResponse"]


class CollectionListResponse(BaseModel):
    """Collection DTO for API responses."""

    backend: str
    """Storage backend."""

    created_at: str
    """Creation timestamp (ISO 8601)."""

    name: str
    """Collection name."""

    revision_id: str
    """Revision identifier for this collection metadata row."""

    status: str
    """Lifecycle status."""

    updated_at: str
    """Last update timestamp (ISO 8601)."""

    deleted_at: Optional[str] = None
    """Deletion timestamp (ISO 8601) if soft-deleted."""

    max_documents: Optional[int] = None
    """Maximum documents allowed in this collection (None = unlimited)."""

    type_alias: Optional[str] = None
    """Type alias in the collection module (optional)."""

    updated_by: Optional[str] = None
    """Actor who last updated the collection, if known."""
