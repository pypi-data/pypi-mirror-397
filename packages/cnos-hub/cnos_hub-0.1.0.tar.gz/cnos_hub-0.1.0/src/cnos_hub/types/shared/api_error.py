# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Union, Optional
from typing_extensions import Literal, TypeAlias

from ..._models import BaseModel
from .validation_error_entry import ValidationErrorEntry

__all__ = [
    "APIError",
    "APIErrorValidationFailed",
    "APIErrorValidationFailedDetails",
    "APIErrorNotFound",
    "APIErrorNotFoundDetails",
    "APIErrorUnauthorized",
    "APIErrorForbidden",
    "APIErrorForbiddenDetails",
    "APIErrorQuotaExceeded",
    "APIErrorQuotaExceededDetails",
    "APIErrorConflict",
    "APIErrorConflictDetails",
    "APIErrorTimeout",
    "APIErrorTimeoutDetails",
    "APIErrorInternal",
    "APIErrorInternalDetails",
]


class APIErrorValidationFailedDetails(BaseModel):
    """Validation failed with structured errors."""

    errors: List[ValidationErrorEntry]
    """Structured validation errors."""


class APIErrorValidationFailed(BaseModel):
    """Validation failed with structured errors."""

    details: APIErrorValidationFailedDetails
    """Validation failed with structured errors."""

    kind: Literal["ValidationFailed"]


class APIErrorNotFoundDetails(BaseModel):
    """Resource was not found."""

    resource: str
    """Name or identifier of the missing resource."""


class APIErrorNotFound(BaseModel):
    """Resource was not found."""

    details: APIErrorNotFoundDetails
    """Resource was not found."""

    kind: Literal["NotFound"]


class APIErrorUnauthorized(BaseModel):
    """Caller is not authenticated."""

    kind: Literal["Unauthorized"]


class APIErrorForbiddenDetails(BaseModel):
    """Caller lacks required scope/permission."""

    scope: Optional[str] = None
    """Optional scope identifier."""


class APIErrorForbidden(BaseModel):
    """Caller lacks required scope/permission."""

    details: APIErrorForbiddenDetails
    """Caller lacks required scope/permission."""

    kind: Literal["Forbidden"]


class APIErrorQuotaExceededDetails(BaseModel):
    """Request exceeds configured quota/limits."""

    limit: int
    """Maximum allowed value."""

    resource: str
    """Name of the limited resource."""

    current: Optional[int] = None
    """Optional current usage."""


class APIErrorQuotaExceeded(BaseModel):
    """Request exceeds configured quota/limits."""

    details: APIErrorQuotaExceededDetails
    """Request exceeds configured quota/limits."""

    kind: Literal["QuotaExceeded"]


class APIErrorConflictDetails(BaseModel):
    """Request conflicts with existing state."""

    resource: str
    """Name of the conflicting resource."""

    reason: Optional[str] = None
    """Optional reason for the conflict."""


class APIErrorConflict(BaseModel):
    """Request conflicts with existing state."""

    details: APIErrorConflictDetails
    """Request conflicts with existing state."""

    kind: Literal["Conflict"]


class APIErrorTimeoutDetails(BaseModel):
    """Request timed out."""

    message: str
    """Description of what timed out."""


class APIErrorTimeout(BaseModel):
    """Request timed out."""

    details: APIErrorTimeoutDetails
    """Request timed out."""

    kind: Literal["Timeout"]


class APIErrorInternalDetails(BaseModel):
    """Internal server error."""

    message: str
    """Opaque message for debugging/log correlation."""


class APIErrorInternal(BaseModel):
    """Internal server error."""

    details: APIErrorInternalDetails
    """Internal server error."""

    kind: Literal["Internal"]


APIError: TypeAlias = Union[
    APIErrorValidationFailed,
    APIErrorNotFound,
    APIErrorUnauthorized,
    APIErrorForbidden,
    APIErrorQuotaExceeded,
    APIErrorConflict,
    APIErrorTimeout,
    APIErrorInternal,
]
