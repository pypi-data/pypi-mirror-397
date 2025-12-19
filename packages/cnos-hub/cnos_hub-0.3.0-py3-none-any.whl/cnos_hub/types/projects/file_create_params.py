# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Optional
from typing_extensions import Required, TypedDict

__all__ = ["FileCreateParams"]


class FileCreateParams(TypedDict, total=False):
    name: Required[str]

    content_type: Optional[str]

    data: Optional[str]

    data_base64: Optional[str]
