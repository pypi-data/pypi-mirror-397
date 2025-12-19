# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List

from .._models import BaseModel

__all__ = ["MeOrgsResponse", "Item"]


class Item(BaseModel):
    """Organization summary for self APIs."""

    id: str
    """Organization identifier."""

    name: str
    """Organization name."""

    status: str
    """Organization status."""


class MeOrgsResponse(BaseModel):
    """Response containing the caller's organizations."""

    items: List[Item]
    """Organizations the caller has access to."""
