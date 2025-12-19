# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Dict
from typing_extensions import TypedDict

__all__ = ["EventFilterJsonParam"]


class EventFilterJsonParam(TypedDict, total=False):
    """Event-level filter placeholder."""

    payload_equals: Dict[str, object]
    """
    For now: simple "payload contains this field == value". Extendable without
    breaking wire format.
    """
