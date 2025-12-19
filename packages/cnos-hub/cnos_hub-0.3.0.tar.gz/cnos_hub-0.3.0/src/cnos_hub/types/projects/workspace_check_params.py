# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Iterable, Optional
from typing_extensions import Required, TypedDict

__all__ = ["WorkspaceCheckParams", "Change"]


class WorkspaceCheckParams(TypedDict, total=False):
    changes: Required[Iterable[Change]]
    """Set of file changes to validate."""


class Change(TypedDict, total=False):
    """A single file change to be applied to a workspace."""

    path: Required[str]
    """Logical path within the project workspace."""

    content: Optional[str]
    """New contents for the path. `None` indicates deletion."""
