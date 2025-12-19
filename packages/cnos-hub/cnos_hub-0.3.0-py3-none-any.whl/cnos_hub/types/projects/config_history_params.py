# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import TypedDict

__all__ = ["ConfigHistoryParams"]


class ConfigHistoryParams(TypedDict, total=False):
    cursor: str
    """Pagination cursor."""

    limit: int
    """Maximum page size (1-100, default 50)."""
