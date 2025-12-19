# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Dict, Optional
from typing_extensions import Required, TypedDict

__all__ = ["ConfigReplaceParams"]


class ConfigReplaceParams(TypedDict, total=False):
    config: Required[Dict[str, object]]
    """Configuration payload to store."""

    expected_version: Optional[str]
    """Expected version for optimistic concurrency (omit for create)."""
