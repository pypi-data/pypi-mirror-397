# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional
from typing_extensions import Literal

from ...._models import BaseModel

__all__ = ["WebhookDeliveriesResponse"]


class WebhookDeliveriesResponse(BaseModel):
    """Webhook delivery DTO for API responses."""

    id: str
    """Delivery identifier."""

    attempt_count: int
    """Number of attempts."""

    created_at: str
    """Creation timestamp (RFC3339)."""

    event_id: str
    """Event identifier."""

    status: Literal["pending", "processing", "succeeded", "failed", "dead_letter"]
    """Delivery status."""

    subscription_id: str
    """Subscription identifier."""

    last_error: Optional[str] = None
    """Last error message."""

    last_response_status: Optional[int] = None
    """HTTP status from last attempt."""
