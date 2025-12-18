# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Union, Optional
from typing_extensions import Literal, TypeAlias

from ..._models import BaseModel

__all__ = [
    "TxRequest",
    "Operation",
    "OperationTxOpCreateDocument",
    "OperationTxOpReplaceDocument",
    "OperationTxOpDeleteDocument",
    "OperationTxOpCreateCollection",
    "OperationTxOpDeleteCollection",
    "Event",
]


class OperationTxOpCreateDocument(BaseModel):
    """Create a document."""

    collection: str
    """Target collection name."""

    op: Literal["create_document"]

    value: object
    """Document payload."""

    id: Optional[str] = None
    """Optional explicit ID (server generates ULID if omitted)."""


class OperationTxOpReplaceDocument(BaseModel):
    """Replace a document using optimistic concurrency."""

    id: str
    """Document identifier."""

    collection: str
    """Target collection name."""

    expected_version: str
    """Required version token."""

    op: Literal["replace_document"]

    value: object
    """New payload."""


class OperationTxOpDeleteDocument(BaseModel):
    """Delete a document using optimistic concurrency."""

    id: str
    """Document identifier."""

    collection: str
    """Target collection name."""

    expected_version: str
    """Required version token."""

    op: Literal["delete_document"]


class OperationTxOpCreateCollection(BaseModel):
    """Create a collection."""

    backend: Literal["in_place", "log"]
    """Storage backend."""

    name: str
    """Collection name (must match pattern `[a-zA-Z][a-zA-Z0-9_]*`)."""

    op: Literal["create_collection"]


class OperationTxOpDeleteCollection(BaseModel):
    """Delete a collection."""

    name: str
    """Collection name."""

    op: Literal["delete_collection"]


Operation: TypeAlias = Union[
    OperationTxOpCreateDocument,
    OperationTxOpReplaceDocument,
    OperationTxOpDeleteDocument,
    OperationTxOpCreateCollection,
    OperationTxOpDeleteCollection,
]


class Event(BaseModel):
    """Event to emit within a transaction.

    Events are emitted atomically with document operations,
    ensuring transactional consistency.
    """

    payload: object
    """Event payload data."""

    type: str
    """Event type identifier (e.g., "collection.document.created")."""

    meta: Optional[object] = None
    """Event metadata (actor, context, etc.)."""


class TxRequest(BaseModel):
    """Transaction request containing ordered operations."""

    operations: List[Operation]
    """Operations to execute atomically."""

    events: Optional[List[Event]] = None
    """Optional events to emit within the same transaction."""
