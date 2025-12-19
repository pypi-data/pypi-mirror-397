# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, TypedDict

from ...._types import SequenceNotStr

__all__ = ["MemberCreateParams"]


class MemberCreateParams(TypedDict, total=False):
    project_id: Required[str]

    roles: SequenceNotStr[str]
    """Roles to assign."""
