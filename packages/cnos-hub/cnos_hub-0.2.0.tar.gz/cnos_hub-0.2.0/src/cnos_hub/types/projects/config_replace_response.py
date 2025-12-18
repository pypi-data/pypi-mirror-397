# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Dict, Optional
from typing_extensions import Literal

from ..._models import BaseModel

__all__ = ["ConfigReplaceResponse", "Meta", "Scope"]


class Meta(BaseModel):
    """Store-managed metadata."""

    version: str
    """Logical version token."""

    created_at: Optional[str] = None
    """Creation timestamp formatted as RFC3339."""

    type_version: Optional[int] = None
    """Optional type alias version for validation."""

    updated_at: Optional[str] = None
    """Update timestamp formatted as RFC3339."""

    updated_by: Optional[str] = None
    """Optional actor identifier."""


class Scope(BaseModel):
    """Owning scope for the configuration."""

    kind: Literal["Project", "Org", "System"]
    """Scope discriminator."""

    org_id: Optional[str] = None
    """Owning organization identifier (when applicable)."""

    project_id: Optional[str] = None
    """Owning project identifier (when applicable)."""


class ConfigReplaceResponse(BaseModel):
    """Unified response payload for configuration endpoints."""

    config: Dict[str, object]
    """Configuration payload."""

    meta: Meta
    """Store-managed metadata."""

    scope: Scope
    """Owning scope for the configuration."""
