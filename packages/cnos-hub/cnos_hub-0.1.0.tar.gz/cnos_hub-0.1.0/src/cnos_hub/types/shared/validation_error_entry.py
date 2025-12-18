# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Dict, List, Optional

from ..._models import BaseModel

__all__ = ["ValidationErrorEntry"]


class ValidationErrorEntry(BaseModel):
    """Structured validation error entry derived from Typus diagnostic validators."""

    code: str
    """Error code emitted by the validator."""

    path: List[str]
    """Path to the failing element."""

    detail: Optional[Dict[str, object]] = None
    """Optional payload describing the violation."""
