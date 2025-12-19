# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Union
from typing_extensions import Literal, Required, TypeAlias, TypedDict

__all__ = ["TaskRetryPolicyParam", "Backoff", "BackoffBackoffStrategyFixed", "BackoffBackoffStrategyExponential"]


class BackoffBackoffStrategyFixed(TypedDict, total=False):
    """Fixed delay between attempts."""

    delay_ms: Required[int]
    """Milliseconds to wait before retrying."""

    kind: Required[Literal["fixed"]]


class BackoffBackoffStrategyExponential(TypedDict, total=False):
    """Exponential growth with a maximum cap."""

    base_ms: Required[int]
    """Starting delay in milliseconds."""

    kind: Required[Literal["exponential"]]

    max_ms: Required[int]
    """Maximum delay in milliseconds."""


Backoff: TypeAlias = Union[BackoffBackoffStrategyFixed, BackoffBackoffStrategyExponential]


class TaskRetryPolicyParam(TypedDict, total=False):
    """Retry policy for task executions."""

    backoff: Required[Backoff]
    """Backoff strategy between attempts."""

    max_attempts: Required[int]
    """Maximum attempts before surfacing failure."""

    scope: Literal["none", "scheduled_only", "all_triggers"]
    """Which triggers allow retries."""
