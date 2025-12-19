# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Dict, Union, Iterable, Optional
from typing_extensions import Literal, Required, TypeAlias, TypedDict

from .._types import SequenceNotStr
from .budgets_json_param import BudgetsJsonParam

__all__ = [
    "CnoExecuteFunctionParams",
    "Module",
    "Args",
    "ArgsExecuteArgsJson",
    "ArgsExecuteArgsCnon",
    "ArgsExecuteArgsBin",
]


class CnoExecuteFunctionParams(TypedDict, total=False):
    function: Required[str]
    """Dotted function path relative to the root module."""

    modules: Required[Iterable[Module]]
    """Modules to prepare and run."""

    root: Required[str]
    """Path of the root module to analyze."""

    args: Optional[Args]
    """Arguments encoded as JSON, CNON, or base64 binary.

    Provide exactly one encoding.
    """

    budget: Optional[BudgetsJsonParam]
    """Optional runtime budget configuration."""

    result_encoding: Optional[Literal["binary", "cnon", "json"]]
    """Desired result encoding.

    Defaults to binary (base64-wrapped) when omitted. Clients should set this
    instead of relying on Accept overrides.
    """

    trace: bool
    """Whether to capture an execution trace."""

    validate_as: Optional[SequenceNotStr[str]]
    """Optional type aliases to validate each argument against (aligned to args)."""


class Module(TypedDict, total=False):
    """Public request/response models for the CNOS stateless APIs."""

    path: Required[str]
    """Importable module path (e.g., `"main"` or `"foo.bar"`)."""

    source: Required[str]
    """Source text for this module."""


class ArgsExecuteArgsJson(TypedDict, total=False):
    """JSON-encoded arguments."""

    json: Required[Union[Iterable[object], Dict[str, object]]]
    """JSON arguments (positional or named)."""


class ArgsExecuteArgsCnon(TypedDict, total=False):
    """CNON-encoded arguments (lossless JSON superset)."""

    cnon: Required[Iterable[Dict[str, object]]]
    """CNON-encoded argument array."""


class ArgsExecuteArgsBin(TypedDict, total=False):
    """Binary (base64) encoded arguments."""

    bin: Required[str]
    """Base64-encoded binary arguments."""


Args: TypeAlias = Union[ArgsExecuteArgsJson, ArgsExecuteArgsCnon, ArgsExecuteArgsBin]
