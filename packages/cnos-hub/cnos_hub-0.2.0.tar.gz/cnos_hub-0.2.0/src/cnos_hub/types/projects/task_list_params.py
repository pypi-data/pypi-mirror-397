# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Literal, TypedDict

__all__ = ["TaskListParams"]


class TaskListParams(TypedDict, total=False):
    cursor: str
    """Cursor for pagination."""

    limit: int
    """Maximum items to return."""

    status: Literal["active", "disabled"]
    """Optional status filter."""

    trigger_kind: str
    """Optional trigger kind filter (`event`, `schedule`, `manual`)."""
