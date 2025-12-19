# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import TypedDict

__all__ = ["CollectionListParams"]


class CollectionListParams(TypedDict, total=False):
    cursor: str
    """Pagination cursor"""

    limit: int
    """Page size (1-100, default 50)"""
