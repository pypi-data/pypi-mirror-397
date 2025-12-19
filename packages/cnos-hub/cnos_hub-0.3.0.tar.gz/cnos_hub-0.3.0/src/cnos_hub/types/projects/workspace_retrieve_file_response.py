# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from ..._models import BaseModel
from ..shared.api_status import APIStatus

__all__ = ["WorkspaceRetrieveFileResponse", "File"]


class File(BaseModel):
    """Workspace file payload."""

    content: str
    """Source content."""

    created_at: str
    """Creation timestamp."""

    path: str
    """File path."""

    revision_id: str
    """Revision identifier."""

    updated_at: str
    """Last update timestamp."""


class WorkspaceRetrieveFileResponse(BaseModel):
    """Response payload for fetching a workspace file."""

    file: File
    """Workspace file payload."""

    status: APIStatus
    """API status indicator."""
