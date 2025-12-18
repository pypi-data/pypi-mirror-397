# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from ...._models import BaseModel
from ..organization import Organization
from ...shared.audit_meta import AuditMeta

__all__ = ["HistoryListResponse"]


class HistoryListResponse(BaseModel):
    """Revision entry for an organization."""

    meta: AuditMeta
    """Audit metadata for the revision."""

    org: Organization
    """Organization payload for the revision."""
