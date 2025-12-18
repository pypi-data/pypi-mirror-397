# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Dict, Optional

from ..._models import BaseModel

__all__ = ["ExecuteErrorJson"]


class ExecuteErrorJson(BaseModel):
    """Execution error payload."""

    kind: str
    """Error class: `"check" | "execution" | "internal"`."""

    message: str
    """Human-friendly message."""

    code: Optional[str] = None
    """Optional machine-readable code."""

    details: Optional[Dict[str, object]] = None
    """Optional machine-friendly details."""
