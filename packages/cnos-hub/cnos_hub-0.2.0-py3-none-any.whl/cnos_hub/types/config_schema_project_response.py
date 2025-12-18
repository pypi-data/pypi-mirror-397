# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from .._models import BaseModel

__all__ = ["ConfigSchemaProjectResponse"]


class ConfigSchemaProjectResponse(BaseModel):
    description: str

    notes: str

    type: str
