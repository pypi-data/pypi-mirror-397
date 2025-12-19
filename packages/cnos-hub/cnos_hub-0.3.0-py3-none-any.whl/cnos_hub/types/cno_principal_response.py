# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional

from .._models import BaseModel

__all__ = ["CnoPrincipalResponse"]


class CnoPrincipalResponse(BaseModel):
    """Return the authenticated principal for the current request."""

    capabilities: List[str]
    """Granted capabilities."""

    labels: List[str]
    """External labels/tags."""

    org_id: str
    """Owning organization."""

    project_id: str
    """Owning project."""

    roles: List[str]
    """Resolved roles."""

    user_id: Optional[str] = None
    """User identifier when available."""
