# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List

from ...._models import BaseModel

__all__ = ["MemberHistoryResponse"]


class MemberHistoryResponse(BaseModel):
    """Project membership DTO."""

    created_at: str
    """Membership creation timestamp (RFC3339)."""

    project_id: str
    """Project identifier."""

    roles: List[str]
    """Assigned roles."""

    user_id: str
    """User identifier."""
