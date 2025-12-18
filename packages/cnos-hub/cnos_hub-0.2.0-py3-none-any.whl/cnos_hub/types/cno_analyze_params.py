# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Iterable, Optional
from typing_extensions import Required, TypedDict

__all__ = ["CnoAnalyzeParams", "Module", "Options"]


class CnoAnalyzeParams(TypedDict, total=False):
    modules: Required[Iterable[Module]]
    """Modules to analyze."""

    root: Required[str]
    """Path of the root module to analyze."""

    options: Options
    """Optional flags controlling output."""


class Module(TypedDict, total=False):
    """Public request/response models for the CNOS stateless APIs."""

    path: Required[str]
    """Importable module path (e.g., `"main"` or `"foo.bar"`)."""

    source: Required[str]
    """Source text for this module."""


class Options(TypedDict, total=False):
    """Optional flags controlling output."""

    include_entrypoints: Optional[bool]
    """Include entrypoint metadata; defaults to `true`."""

    include_functions: Optional[bool]
    """Include function metadata; defaults to `true`."""

    include_types: Optional[bool]
    """Include type alias metadata; defaults to `true`."""

    runtime_lower: Optional[bool]
    """
    Whether to lower for runtime metadata; currently only affects entrypoint
    discovery and defaults to `include_entrypoints`.
    """
