# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional

from ..._models import BaseModel
from ..shared.api_status import APIStatus

__all__ = ["WorkspaceCheckResponse", "Diagnostic", "DiagnosticSpan", "Entrypoint", "EntrypointInput"]


class DiagnosticSpan(BaseModel):
    """Optional span."""

    end_col: int
    """Ending column (1-based)."""

    end_line: int
    """Ending line (1-based)."""

    path: str
    """File path."""

    start_col: int
    """Starting column (1-based)."""

    start_line: int
    """Starting line (1-based)."""


class Diagnostic(BaseModel):
    """Workspace diagnostic payload."""

    message: str
    """Message describing the issue."""

    severity: str
    """Severity string (error/warning/info)."""

    span: Optional[DiagnosticSpan] = None
    """Optional span."""


class EntrypointInput(BaseModel):
    """Parameter metadata."""

    name: str
    """Parameter name."""

    required: bool
    """Whether the parameter is required."""

    typ: str
    """Rendered type."""


class Entrypoint(BaseModel):
    """Entrypoint metadata rendered for clients."""

    inputs: List[EntrypointInput]
    """Parameters accepted by the entrypoint."""

    output: str
    """Return type representation."""

    qualified_name: str
    """Fully-qualified function name."""

    description: Optional[str] = None
    """Optional description."""


class WorkspaceCheckResponse(BaseModel):
    """Response payload for workspace validation and patch endpoints."""

    diagnostics: List[Diagnostic]
    """Validation diagnostics (empty on success)."""

    entrypoints: List[Entrypoint]
    """Entrypoints discovered by the runtime."""

    status: APIStatus
    """API status indicator."""
