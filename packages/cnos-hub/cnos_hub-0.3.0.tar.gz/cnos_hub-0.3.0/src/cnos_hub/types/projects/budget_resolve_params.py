# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Optional
from typing_extensions import TypedDict

from ..budgets_json_param import BudgetsJsonParam

__all__ = ["BudgetResolveParams"]


class BudgetResolveParams(TypedDict, total=False):
    requested: Optional[BudgetsJsonParam]
    """Requested budget to resolve."""
