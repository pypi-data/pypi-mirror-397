# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, TypedDict

__all__ = ["MemberHistoryParams"]


class MemberHistoryParams(TypedDict, total=False):
    org_id: Required[str]

    cursor: str
    """Pagination cursor"""

    limit: int
    """Page size (1-100, default 50)"""
