# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Literal, TypedDict

__all__ = ["WebhookListParams"]


class WebhookListParams(TypedDict, total=False):
    cursor: str
    """Pagination cursor."""

    limit: int
    """Maximum items to return."""

    status: Literal["active", "disabled"]
    """Optional status filter."""
