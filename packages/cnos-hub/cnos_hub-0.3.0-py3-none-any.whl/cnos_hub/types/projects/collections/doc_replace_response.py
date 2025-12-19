# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Dict

from ...._models import BaseModel
from .document_meta import DocumentMeta

__all__ = ["DocReplaceResponse"]


class DocReplaceResponse(BaseModel):
    """Document returned by data-plane operations."""

    id: str
    """Document identifier."""

    meta: DocumentMeta
    """Store-managed metadata."""

    value: Dict[str, object]
    """User payload."""
