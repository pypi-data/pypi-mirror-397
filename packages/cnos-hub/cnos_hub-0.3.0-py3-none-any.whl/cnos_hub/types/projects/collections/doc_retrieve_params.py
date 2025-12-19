# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, TypedDict

__all__ = ["DocRetrieveParams"]


class DocRetrieveParams(TypedDict, total=False):
    project_id: Required[str]

    name: Required[str]

    include_deleted: Required[bool]
    """Include soft-deleted documents"""
