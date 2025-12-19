# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Optional
from typing_extensions import Literal, Required, TypedDict

from ..._types import SequenceNotStr

__all__ = ["ViewCreateParams"]


class ViewCreateParams(TypedDict, total=False):
    function_name: Required[str]
    """Target function name."""

    module_path: Required[str]
    """Target CNOS module path."""

    name: Required[str]
    """Human-readable name (unique within project)."""

    allowed_labels: SequenceNotStr[str]
    """Labels allowed to execute."""

    allowed_roles: SequenceNotStr[str]
    """Roles allowed to execute."""

    description: Optional[str]
    """Optional description."""

    security_mode: Literal["definer", "invoker"]
    """Security mode: "definer" or "invoker"."""
