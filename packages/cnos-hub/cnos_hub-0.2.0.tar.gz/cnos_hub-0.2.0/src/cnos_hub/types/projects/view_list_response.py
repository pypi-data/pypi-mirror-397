# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional
from typing_extensions import Literal

from ..._models import BaseModel

__all__ = ["ViewListResponse"]


class ViewListResponse(BaseModel):
    """View DTO for API responses."""

    id: str
    """View identifier."""

    allowed_labels: List[str]
    """Labels allowed to execute."""

    allowed_roles: List[str]
    """Roles allowed to execute."""

    created_at: str
    """Creation timestamp (RFC3339)."""

    function_name: str
    """Target function name."""

    module_path: str
    """Target CNOS module path."""

    name: str
    """Human-readable name."""

    project_id: str
    """Project identifier."""

    security_mode: Literal["definer", "invoker"]
    """Security mode."""

    status: Literal["active", "disabled", "deleted"]
    """Lifecycle status."""

    updated_at: str
    """Last update timestamp (RFC3339)."""

    description: Optional[str] = None
    """Optional description."""
