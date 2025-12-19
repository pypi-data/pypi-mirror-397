# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, TypedDict

__all__ = ["WorkspaceRetrieveFileParams"]


class WorkspaceRetrieveFileParams(TypedDict, total=False):
    path: Required[str]
    """Workspace file path"""
