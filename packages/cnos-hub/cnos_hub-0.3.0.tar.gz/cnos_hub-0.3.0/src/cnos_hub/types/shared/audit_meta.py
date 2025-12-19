# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional
from datetime import datetime

from ..._models import BaseModel

__all__ = ["AuditMeta"]


class AuditMeta(BaseModel):
    """Canonical audit metadata describing who wrote a value and when."""

    created_at: datetime
    """Creation timestamp in RFC3339."""

    revision_id: str
    """Stable revision identifier supplied by the backing store."""

    updated_at: datetime
    """Last update timestamp in RFC3339."""

    updated_by: Optional[str] = None
    """Optional actor responsible for the last write."""
