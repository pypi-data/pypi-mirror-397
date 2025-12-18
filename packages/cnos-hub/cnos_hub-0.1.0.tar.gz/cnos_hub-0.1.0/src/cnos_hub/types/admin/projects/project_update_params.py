# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Optional
from typing_extensions import Literal, TypedDict

__all__ = ["ProjectUpdateParams"]


class ProjectUpdateParams(TypedDict, total=False):
    name: Optional[str]
    """Updated name."""

    status: Optional[Literal["active", "readonly", "deleted"]]
    """Updated status."""
