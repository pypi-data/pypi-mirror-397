# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from ..._models import BaseModel

__all__ = ["CollectionStatsResponse"]


class CollectionStatsResponse(BaseModel):
    """Aggregated metadata for a collection."""

    backend: str
    """Storage backend for the collection."""

    documents: int
    """Number of documents (excluding soft-deleted)."""

    name: str
    """Collection name."""

    status: str
    """Current collection status."""

    type_alias: str
    """Type alias backing the schema."""
