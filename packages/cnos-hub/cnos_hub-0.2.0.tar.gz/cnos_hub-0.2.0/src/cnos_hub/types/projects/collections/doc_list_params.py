# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, TypedDict

__all__ = ["DocListParams"]


class DocListParams(TypedDict, total=False):
    project_id: Required[str]

    include_deleted: Required[bool]
    """Include soft-deleted documents"""

    cursor: str
    """Pagination cursor"""

    limit: int
    """Page size (1-100, default 50)"""
