# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Optional
from typing_extensions import Required, TypedDict

__all__ = ["WebhookCreateParams"]


class WebhookCreateParams(TypedDict, total=False):
    event_pattern: Required[str]
    """Event type pattern (supports globs like "user.\\**")."""

    name: Required[str]
    """Human-friendly name."""

    url: Required[str]
    """Target URL for webhook delivery."""

    description: Optional[str]
    """Optional description."""
