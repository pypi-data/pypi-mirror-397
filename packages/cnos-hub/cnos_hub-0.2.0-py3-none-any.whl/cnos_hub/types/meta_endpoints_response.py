# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List
from typing_extensions import TypeAlias

from .._models import BaseModel

__all__ = ["MetaEndpointsResponse", "MetaEndpointsResponseItem"]


class MetaEndpointsResponseItem(BaseModel):
    """Endpoint metadata entry for `/v1/meta/endpoints`."""

    action: str
    """Action verb."""

    capabilities: List[str]
    """Capabilities required to call the endpoint."""

    method: str
    """HTTP method."""

    path: str
    """Path template."""

    resource: str
    """Resource name."""


MetaEndpointsResponse: TypeAlias = List[MetaEndpointsResponseItem]
