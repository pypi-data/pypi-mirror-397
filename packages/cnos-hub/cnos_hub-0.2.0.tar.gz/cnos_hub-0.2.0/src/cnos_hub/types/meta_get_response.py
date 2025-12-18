# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from .._models import BaseModel

__all__ = ["MetaGetResponse", "Features"]


class Features(BaseModel):
    """Enabled feature flags."""

    collections_enabled: bool
    """Whether collections are enabled."""

    events_enabled: bool
    """Whether events are enabled."""

    tasks_enabled: bool
    """Whether tasks are enabled."""


class MetaGetResponse(BaseModel):
    """Service metadata payload."""

    features: Features
    """Enabled feature flags."""

    service: str
    """Service identifier."""

    time: str
    """Current timestamp in RFC3339."""

    version: str
    """Service version."""
