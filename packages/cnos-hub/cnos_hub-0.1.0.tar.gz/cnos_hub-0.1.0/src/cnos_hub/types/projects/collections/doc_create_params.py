# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Dict, Optional
from typing_extensions import Required, TypedDict

__all__ = ["DocCreateParams"]


class DocCreateParams(TypedDict, total=False):
    project_id: Required[str]

    value: Required[Dict[str, object]]
    """Document payload."""

    id: Optional[str]
    """Optional explicit ID (server generates ULID if omitted)."""
