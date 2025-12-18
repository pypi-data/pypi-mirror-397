# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from .._models import BaseModel
from .shared.api_key_dto import APIKeyDto

__all__ = ["APIKeyCreateResponse"]


class APIKeyCreateResponse(BaseModel):
    """Response returned after issuing an API key."""

    key: APIKeyDto
    """API key metadata returned by admin endpoints."""

    secret: str
