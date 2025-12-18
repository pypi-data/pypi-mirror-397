# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Literal, TypedDict

__all__ = ["EventListParams"]


class EventListParams(TypedDict, total=False):
    cursor: str
    """Pagination cursor."""

    limit: int
    """Maximum items to return."""

    status: Literal["pending", "processing", "succeeded", "failed", "dead_letter"]
    """Optional status filter."""

    type: str
    """Optional type filter."""
