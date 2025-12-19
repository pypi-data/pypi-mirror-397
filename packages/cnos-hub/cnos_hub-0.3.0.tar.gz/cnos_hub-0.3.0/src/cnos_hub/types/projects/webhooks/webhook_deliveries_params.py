# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Literal, Required, TypedDict

__all__ = ["WebhookDeliveriesParams"]


class WebhookDeliveriesParams(TypedDict, total=False):
    project_id: Required[str]

    cursor: str
    """Pagination cursor."""

    limit: int
    """Maximum items to return."""

    status: Literal["pending", "processing", "succeeded", "failed", "dead_letter"]
    """Optional status filter."""
