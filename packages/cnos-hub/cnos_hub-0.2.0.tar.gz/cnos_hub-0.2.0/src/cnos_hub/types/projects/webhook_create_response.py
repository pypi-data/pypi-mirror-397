# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional
from typing_extensions import Literal

from ..._models import BaseModel

__all__ = ["WebhookCreateResponse"]


class WebhookCreateResponse(BaseModel):
    """Webhook subscription DTO for API responses."""

    id: str
    """Subscription identifier."""

    created_at: str
    """Creation timestamp (RFC3339)."""

    event_pattern: str
    """Event type pattern."""

    name: str
    """Human-friendly name."""

    project_id: str
    """Project identifier."""

    status: Literal["active", "disabled"]
    """Lifecycle status."""

    updated_at: str
    """Last update timestamp (RFC3339)."""

    url: str
    """Target URL."""

    description: Optional[str] = None
    """Optional description."""
