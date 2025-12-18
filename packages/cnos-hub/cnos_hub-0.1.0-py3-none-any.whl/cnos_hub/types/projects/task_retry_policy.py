# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Union, Optional
from typing_extensions import Literal, TypeAlias

from ..._models import BaseModel

__all__ = ["TaskRetryPolicy", "Backoff", "BackoffBackoffStrategyFixed", "BackoffBackoffStrategyExponential"]


class BackoffBackoffStrategyFixed(BaseModel):
    """Fixed delay between attempts."""

    delay_ms: int
    """Milliseconds to wait before retrying."""

    kind: Literal["fixed"]


class BackoffBackoffStrategyExponential(BaseModel):
    """Exponential growth with a maximum cap."""

    base_ms: int
    """Starting delay in milliseconds."""

    kind: Literal["exponential"]

    max_ms: int
    """Maximum delay in milliseconds."""


Backoff: TypeAlias = Union[BackoffBackoffStrategyFixed, BackoffBackoffStrategyExponential]


class TaskRetryPolicy(BaseModel):
    """Retry policy for task executions."""

    backoff: Backoff
    """Backoff strategy between attempts."""

    max_attempts: int
    """Maximum attempts before surfacing failure."""

    scope: Optional[Literal["none", "scheduled_only", "all_triggers"]] = None
    """Which triggers allow retries."""
