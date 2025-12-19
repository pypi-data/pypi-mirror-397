# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Dict, Union, Iterable, Optional
from typing_extensions import Literal, Required, TypeAlias, TypedDict

from .tx_request_param import TxRequestParam

__all__ = ["TaskPlanParam", "Action", "ActionTaskOpTx", "ActionTaskOpEmitEvent", "ActionTaskOpWebhook"]


class ActionTaskOpTx(TypedDict, total=False):
    """Execute a transactional batch on collections."""

    kind: Required[Literal["tx"]]

    request: Required[TxRequestParam]
    """Request payload."""


class ActionTaskOpEmitEvent(TypedDict, total=False):
    """Emit a new event."""

    event_type: Required[str]
    """Logical event type."""

    kind: Required[Literal["emit_event"]]

    meta: object
    """Optional metadata."""

    payload: object
    """Optional payload."""


class ActionTaskOpWebhook(TypedDict, total=False):
    """Call a webhook (close to `EventAction::Webhook`)."""

    kind: Required[Literal["webhook"]]

    url: Required[str]
    """Target URL."""

    body: object
    """Body payload."""

    headers: Dict[str, str]
    """Headers to include."""

    method: str
    """HTTP method (defaults to POST)."""

    timeout_ms: Optional[int]
    """Optional timeout in milliseconds."""


Action: TypeAlias = Union[ActionTaskOpTx, ActionTaskOpEmitEvent, ActionTaskOpWebhook]


class TaskPlanParam(TypedDict, total=False):
    """Declarative plan comprising one or more `TaskOps`.

    Plans must contain at most `MAX_ACTIONS_PER_TASK` actions; validation rejects
    larger payloads before execution.
    """

    actions: Required[Iterable[Action]]
    """Actions to apply sequentially."""
