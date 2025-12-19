# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Dict
from typing_extensions import Required, TypedDict

__all__ = ["DocReplaceParams"]


class DocReplaceParams(TypedDict, total=False):
    project_id: Required[str]

    name: Required[str]

    expected_version: Required[str]
    """Required version token for optimistic concurrency."""

    value: Required[Dict[str, object]]
    """New payload."""
