# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional

from .._models import BaseModel

__all__ = ["BudgetsJson"]


class BudgetsJson(BaseModel):
    """Execution budgets supplied by callers."""

    items: Optional[int] = None
    """Maximum collection items processed."""

    steps: Optional[int] = None
    """Maximum evaluation steps."""

    time_ms: Optional[int] = None
    """Time budget in milliseconds."""
