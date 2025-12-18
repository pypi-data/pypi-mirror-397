# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from .._models import BaseModel

__all__ = ["ConfigSchemaOrgResponse"]


class ConfigSchemaOrgResponse(BaseModel):
    description: str

    notes: str

    type: str
