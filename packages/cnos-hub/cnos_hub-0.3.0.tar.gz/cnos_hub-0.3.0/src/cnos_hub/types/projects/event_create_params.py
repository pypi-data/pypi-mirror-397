# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Dict, Optional
from typing_extensions import Required, TypedDict

__all__ = ["EventCreateParams"]


class EventCreateParams(TypedDict, total=False):
    type: Required[str]
    """Event type (e.g., `cnos.custom.example`)."""

    key: Optional[str]
    """Optional partitioning key for deduplication."""

    meta: Dict[str, object]
    """Additional metadata merged with org/project identifiers."""

    payload: Dict[str, object]
    """Event payload."""
