# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Union, Iterable, Optional
from typing_extensions import Literal, Required, TypeAlias, TypedDict

__all__ = [
    "TxRequestParam",
    "Operation",
    "OperationTxOpCreateDocument",
    "OperationTxOpReplaceDocument",
    "OperationTxOpDeleteDocument",
    "OperationTxOpCreateCollection",
    "OperationTxOpDeleteCollection",
    "Event",
]


class OperationTxOpCreateDocument(TypedDict, total=False):
    """Create a document."""

    collection: Required[str]
    """Target collection name."""

    op: Required[Literal["create_document"]]

    value: Required[object]
    """Document payload."""

    id: Optional[str]
    """Optional explicit ID (server generates ULID if omitted)."""


class OperationTxOpReplaceDocument(TypedDict, total=False):
    """Replace a document using optimistic concurrency."""

    id: Required[str]
    """Document identifier."""

    collection: Required[str]
    """Target collection name."""

    expected_version: Required[str]
    """Required version token."""

    op: Required[Literal["replace_document"]]

    value: Required[object]
    """New payload."""


class OperationTxOpDeleteDocument(TypedDict, total=False):
    """Delete a document using optimistic concurrency."""

    id: Required[str]
    """Document identifier."""

    collection: Required[str]
    """Target collection name."""

    expected_version: Required[str]
    """Required version token."""

    op: Required[Literal["delete_document"]]


class OperationTxOpCreateCollection(TypedDict, total=False):
    """Create a collection."""

    backend: Required[Literal["in_place", "log"]]
    """Storage backend."""

    name: Required[str]
    """Collection name (must match pattern `[a-zA-Z][a-zA-Z0-9_]*`)."""

    op: Required[Literal["create_collection"]]


class OperationTxOpDeleteCollection(TypedDict, total=False):
    """Delete a collection."""

    name: Required[str]
    """Collection name."""

    op: Required[Literal["delete_collection"]]


Operation: TypeAlias = Union[
    OperationTxOpCreateDocument,
    OperationTxOpReplaceDocument,
    OperationTxOpDeleteDocument,
    OperationTxOpCreateCollection,
    OperationTxOpDeleteCollection,
]


class Event(TypedDict, total=False):
    """Event to emit within a transaction.

    Events are emitted atomically with document operations,
    ensuring transactional consistency.
    """

    payload: Required[object]
    """Event payload data."""

    type: Required[str]
    """Event type identifier (e.g., "collection.document.created")."""

    meta: object
    """Event metadata (actor, context, etc.)."""


class TxRequestParam(TypedDict, total=False):
    """Transaction request containing ordered operations."""

    operations: Required[Iterable[Operation]]
    """Operations to execute atomically."""

    events: Iterable[Event]
    """Optional events to emit within the same transaction."""
