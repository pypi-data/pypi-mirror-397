# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Iterable, Optional
from typing_extensions import Required, TypedDict

__all__ = ["AuthzTestParams", "Resource"]


class AuthzTestParams(TypedDict, total=False):
    resources: Required[Iterable[Resource]]
    """Resources to test."""


class Resource(TypedDict, total=False):
    """Resource descriptor for authorization testing."""

    kind: Required[str]
    """Resource kind (collection, document, etc.)."""

    action: Optional[str]
    """Action to test (read/write/list/delete/execute/admin)."""

    name: Optional[str]
    """Optional resource name (collection)."""

    org_id: Optional[str]
    """Target organization identifier."""

    project_id: Optional[str]
    """Target project identifier."""
