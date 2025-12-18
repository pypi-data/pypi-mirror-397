# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional

from ..._models import BaseModel

__all__ = ["BudgetLimitsResponse", "Limits"]


class Limits(BaseModel):
    """Effective per-project limits."""

    max_collections_per_project: Optional[int] = None
    """Maximum collections per project."""

    max_documents_per_collection: Optional[int] = None
    """Maximum documents per collection."""

    max_file_size_bytes: Optional[int] = None
    """Maximum individual file size in bytes."""

    max_files_per_project: Optional[int] = None
    """Maximum files per project."""

    max_projects: Optional[int] = None
    """Maximum projects allowed (when applicable)."""

    max_schedules_per_project: Optional[int] = None
    """Maximum schedules per project."""

    max_total_file_bytes_per_project: Optional[int] = None
    """Maximum total file bytes per project."""


class BudgetLimitsResponse(BaseModel):
    """Response for project limit inspection."""

    limits: Limits
    """Effective per-project limits."""
