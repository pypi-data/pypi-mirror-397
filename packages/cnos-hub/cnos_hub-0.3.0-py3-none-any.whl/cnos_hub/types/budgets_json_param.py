# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Optional
from typing_extensions import TypedDict

__all__ = ["BudgetsJsonParam"]


class BudgetsJsonParam(TypedDict, total=False):
    """Execution budgets supplied by callers."""

    items: Optional[int]
    """Maximum collection items processed."""

    steps: Optional[int]
    """Maximum evaluation steps."""

    time_ms: Optional[int]
    """Time budget in milliseconds."""
