# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List

from .._models import BaseModel

__all__ = ["MeProjectsResponse", "Item"]


class Item(BaseModel):
    """Project summary for self APIs."""

    id: str
    """Project identifier."""

    name: str
    """Project name."""

    org_id: str
    """Owning organization identifier."""

    status: str
    """Project status."""


class MeProjectsResponse(BaseModel):
    """Response containing the caller's projects."""

    items: List[Item]
    """Projects the caller has access to."""
