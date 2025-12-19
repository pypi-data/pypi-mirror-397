# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional

from ..._models import BaseModel
from ..budgets_json import BudgetsJson

__all__ = ["BudgetSettingsResponse", "Sources"]


class Sources(BaseModel):
    """Sources of each budget component."""

    org_limit: Optional[BudgetsJson] = None
    """Organization-level limit."""

    project_default: Optional[BudgetsJson] = None
    """Project-level default budget."""

    project_max: Optional[BudgetsJson] = None
    """Project-level hard cap."""

    system_default: Optional[BudgetsJson] = None
    """System-level default budget."""

    system_limit: Optional[BudgetsJson] = None
    """System-level limit."""


class BudgetSettingsResponse(BaseModel):
    """Response for budget settings endpoint."""

    sources: Sources
    """Sources of each budget component."""

    default: Optional[BudgetsJson] = None
    """Default budget applied when none requested."""

    limit: Optional[BudgetsJson] = None
    """Hard limit that caps all budgets."""
