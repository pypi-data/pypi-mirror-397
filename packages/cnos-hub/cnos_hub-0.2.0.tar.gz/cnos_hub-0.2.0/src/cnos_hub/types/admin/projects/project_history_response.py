# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing_extensions import Literal

from ...._models import BaseModel
from ...shared.audit_meta import AuditMeta

__all__ = ["ProjectHistoryResponse", "Project"]


class Project(BaseModel):
    """Project payload for the revision."""

    id: str
    """Project identifier."""

    created_at: str
    """Creation timestamp in RFC3339 format."""

    name: str
    """Human-readable name."""

    org_id: str
    """Owning organization identifier."""

    status: Literal["active", "readonly", "deleted"]
    """Current lifecycle status."""

    updated_at: str
    """Last update timestamp in RFC3339 format."""


class ProjectHistoryResponse(BaseModel):
    """Revision entry for a project."""

    meta: AuditMeta
    """Audit metadata for the revision."""

    project: Project
    """Project payload for the revision."""
