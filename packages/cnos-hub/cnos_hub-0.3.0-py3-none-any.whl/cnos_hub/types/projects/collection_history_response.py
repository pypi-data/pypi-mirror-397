# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from ..._models import BaseModel
from .collection_dto import CollectionDto
from ..shared.audit_meta import AuditMeta

__all__ = ["CollectionHistoryResponse"]


class CollectionHistoryResponse(BaseModel):
    """Revision entry for a collection definition."""

    collection: CollectionDto
    """Collection payload at the revision."""

    meta: AuditMeta
    """Audit metadata for the revision."""
