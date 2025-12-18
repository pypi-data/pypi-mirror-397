# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional

from .._models import BaseModel

__all__ = ["AuthzTestResponse", "Result"]


class Result(BaseModel):
    """Result of a single authorization test."""

    allowed: bool
    """Whether the request is authorized."""

    reason: Optional[str] = None
    """Optional denial reason."""


class AuthzTestResponse(BaseModel):
    """Aggregated authorization test response."""

    results: List[Result]
    """Per-resource authorization results."""
