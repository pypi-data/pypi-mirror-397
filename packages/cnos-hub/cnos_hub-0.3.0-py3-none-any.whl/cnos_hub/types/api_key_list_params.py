# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import TypedDict

from .shared.api_key_status import APIKeyStatus

__all__ = ["APIKeyListParams"]


class APIKeyListParams(TypedDict, total=False):
    cursor: str
    """Pagination cursor"""

    limit: int
    """Page size (1-100, default 50)"""

    status: APIKeyStatus
    """Filter by status"""
