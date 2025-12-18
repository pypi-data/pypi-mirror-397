# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Dict, Optional

from ..._models import BaseModel

__all__ = ["EventFilterJson"]


class EventFilterJson(BaseModel):
    """Event-level filter placeholder."""

    payload_equals: Optional[Dict[str, object]] = None
    """
    For now: simple "payload contains this field == value". Extendable without
    breaking wire format.
    """
