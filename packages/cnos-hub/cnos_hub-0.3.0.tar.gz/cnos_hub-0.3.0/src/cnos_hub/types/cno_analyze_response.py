# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional

from .._models import BaseModel
from .shared.api_status import APIStatus

__all__ = [
    "CnoAnalyzeResponse",
    "Entrypoint",
    "EntrypointParam",
    "Module",
    "ModuleDiagnostic",
    "ModuleDiagnosticPrimary",
    "ModuleFunction",
    "ModuleFunctionParam",
    "ModuleType",
    "Summary",
]


class EntrypointParam(BaseModel):
    """Function parameter metadata."""

    name: str
    """Parameter name."""

    declared_type: Optional[str] = None
    """Declared type annotation, if present."""

    inferred_type: Optional[str] = None
    """Inferred type when available."""


class Entrypoint(BaseModel):
    """Entrypoint metadata (currently derived from runtime lowering)."""

    module_path: str
    """Module path that contains the entrypoint."""

    params: List[EntrypointParam]
    """Parameter metadata for the entrypoint."""

    qualified_name: str
    """Fully-qualified function path."""

    doc: Optional[str] = None
    """Optional documentation string."""

    return_type: Optional[str] = None
    """Return type representation."""


class ModuleDiagnosticPrimary(BaseModel):
    """Primary highlighted span."""

    end: int
    """End byte offset (exclusive)."""

    path: str
    """Module path (as provided in the request)."""

    start: int
    """Start byte offset (inclusive)."""


class ModuleDiagnostic(BaseModel):
    """Diagnostic payload surfaced by the check API."""

    message: str
    """Human-friendly message."""

    severity: str
    """Severity level."""

    code: Optional[str] = None
    """Optional machine-readable code."""

    primary: Optional[ModuleDiagnosticPrimary] = None
    """Primary highlighted span."""


class ModuleFunctionParam(BaseModel):
    """Function parameter metadata."""

    name: str
    """Parameter name."""

    declared_type: Optional[str] = None
    """Declared type annotation, if present."""

    inferred_type: Optional[str] = None
    """Inferred type when available."""


class ModuleFunction(BaseModel):
    """Function metadata exported by the server."""

    name: str
    """Unqualified function name."""

    namespace: List[str]
    """Namespace components enclosing the function."""

    params: List[ModuleFunctionParam]
    """Parameter list."""

    public: bool
    """Visibility flag."""

    qualified_name: str
    """Fully-qualified function path."""

    doc: Optional[str] = None
    """Attached documentation text."""

    inferred_return_type: Optional[str] = None
    """Inferred return type, when available."""

    return_type: Optional[str] = None
    """Declared return type, when provided."""


class ModuleType(BaseModel):
    """Type alias metadata exported by the server."""

    name: str
    """Unqualified alias name."""

    namespace: List[str]
    """Namespace components enclosing the alias."""

    qualified_name: str
    """Fully-qualified alias path."""

    doc: Optional[str] = None
    """Attached documentation text."""

    repr: Optional[str] = None
    """Rendered representation of the alias body."""


class Module(BaseModel):
    """Per-module analysis result."""

    diagnostics: List[ModuleDiagnostic]
    """Collected diagnostics for the module."""

    functions: List[ModuleFunction]
    """Function metadata (optional based on request)."""

    path: str
    """Module path (as provided in the request)."""

    types: List[ModuleType]
    """Type alias metadata (optional based on request)."""


class Summary(BaseModel):
    """Aggregate summary counts."""

    error_count: int
    """Total error diagnostic count across modules."""

    module_count: int
    """Number of modules included in the response."""


class CnoAnalyzeResponse(BaseModel):
    """Response body returned by `/v1/cnos/check` on success."""

    entrypoints: List[Entrypoint]
    """Collected entrypoint metadata."""

    modules: List[Module]
    """Per-module results."""

    status: APIStatus
    """Status string: `"ok"` or `"error"`."""

    summary: Summary
    """Aggregate summary counts."""
