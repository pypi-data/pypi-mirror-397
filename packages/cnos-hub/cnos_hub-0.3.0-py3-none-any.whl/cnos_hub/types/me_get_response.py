# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional

from .._models import BaseModel

__all__ = ["MeGetResponse", "Org", "Principal", "Project"]


class Org(BaseModel):
    """Active organization summary."""

    id: str
    """Organization identifier."""

    name: str
    """Organization name."""

    status: str
    """Organization status."""


class Principal(BaseModel):
    """Current authenticated principal."""

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


class Project(BaseModel):
    """Active project summary."""

    id: str
    """Project identifier."""

    name: str
    """Project name."""

    org_id: str
    """Owning organization identifier."""

    status: str
    """Project status."""


class MeGetResponse(BaseModel):
    """Combined view of the current principal, org, and project."""

    org: Org
    """Active organization summary."""

    principal: Principal
    """Current authenticated principal."""

    project: Project
    """Active project summary."""
