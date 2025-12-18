# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List
from typing_extensions import TypeAlias

from .._models import BaseModel

__all__ = ["MetaCapabilitiesResponse", "MetaCapabilitiesResponseItem"]


class MetaCapabilitiesResponseItem(BaseModel):
    """Capability metadata entry."""

    name: str
    """Canonical capability identifier."""


MetaCapabilitiesResponse: TypeAlias = List[MetaCapabilitiesResponseItem]
