# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Optional
from typing_extensions import Literal, Required, TypedDict

__all__ = ["WebhookUpdateParams"]


class WebhookUpdateParams(TypedDict, total=False):
    project_id: Required[str]

    description: Optional[str]
    """Updated description."""

    event_pattern: Optional[str]
    """Updated event pattern."""

    name: Optional[str]
    """Updated name."""

    status: Optional[Literal["active", "disabled"]]
    """Updated status."""

    url: Optional[str]
    """Updated URL."""
