# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List
from typing_extensions import Literal

from .._models import BaseModel

__all__ = ["CnoTemplatesResponse", "Template", "TemplateModule"]


class TemplateModule(BaseModel):
    """CNOS module content for this template."""

    path: str
    """Importable module path (e.g., `"main"` or `"foo.bar"`)."""

    source: str
    """Source text for this module."""


class Template(BaseModel):
    """Description of a template module."""

    description: str
    """Human-friendly description of what the template provides."""

    kind: Literal["auth", "collections", "events", "tasks", "config", "builtins"]
    """Template kind identifier."""

    module: TemplateModule
    """CNOS module content for this template."""


class CnoTemplatesResponse(BaseModel):
    """Response payload returned by the templates endpoint."""

    templates: List[Template]
    """Available templates."""
