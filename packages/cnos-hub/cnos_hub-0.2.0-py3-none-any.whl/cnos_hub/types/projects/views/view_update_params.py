# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Optional
from typing_extensions import Literal, Required, TypedDict

from ...._types import SequenceNotStr

__all__ = ["ViewUpdateParams"]


class ViewUpdateParams(TypedDict, total=False):
    project_id: Required[str]

    allowed_labels: Optional[SequenceNotStr[str]]
    """Updated allowed labels."""

    allowed_roles: Optional[SequenceNotStr[str]]
    """Updated allowed roles."""

    description: Optional[str]
    """Updated description."""

    status: Optional[Literal["active", "disabled", "deleted"]]
    """Updated status."""
