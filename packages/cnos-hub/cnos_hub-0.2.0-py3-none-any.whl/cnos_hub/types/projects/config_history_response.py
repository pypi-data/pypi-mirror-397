# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Dict

from ..._models import BaseModel
from ..shared.audit_meta import AuditMeta

__all__ = ["ConfigHistoryResponse"]


class ConfigHistoryResponse(BaseModel):
    """Revision entry for configuration history."""

    config: Dict[str, object]
    """Config payload at the revision."""

    meta: AuditMeta
    """Audit metadata for the revision."""
