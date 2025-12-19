# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Literal, Required, TypedDict

__all__ = ["TaskRunsParams"]


class TaskRunsParams(TypedDict, total=False):
    project_id: Required[str]

    cursor: str
    """Cursor for pagination."""

    limit: int
    """Maximum items to return."""

    status: Literal["running", "succeeded", "failed", "retried", "cancelled"]
    """Optional status filter."""
