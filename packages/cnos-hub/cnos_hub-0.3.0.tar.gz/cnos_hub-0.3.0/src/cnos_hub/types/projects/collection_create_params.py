# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Literal, Required, TypedDict

__all__ = ["CollectionCreateParams"]


class CollectionCreateParams(TypedDict, total=False):
    backend: Required[Literal["in_place", "log"]]
    """Storage backend."""

    name: Required[str]
    """Collection name (must match pattern `[a-zA-Z][a-zA-Z0-9_]*`)."""
