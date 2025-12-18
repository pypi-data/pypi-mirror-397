# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional

from ..._models import BaseModel
from ..budgets_json import BudgetsJson

__all__ = ["BudgetResolveResponse"]


class BudgetResolveResponse(BaseModel):
    """Response for budget resolution."""

    effective: BudgetsJson
    """Effective budget after applying defaults and limits."""

    limit: Optional[BudgetsJson] = None
    """Hard limit that was applied."""

    requested: Optional[BudgetsJson] = None
    """Originally requested budget."""
