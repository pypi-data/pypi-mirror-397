# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Dict, List, Union, Optional
from typing_extensions import Literal, TypeAlias

from ..._models import BaseModel
from .tx_request import TxRequest

__all__ = ["TaskPlan", "Action", "ActionTaskOpTx", "ActionTaskOpEmitEvent", "ActionTaskOpWebhook"]


class ActionTaskOpTx(BaseModel):
    """Execute a transactional batch on collections."""

    kind: Literal["tx"]

    request: TxRequest
    """Request payload."""


class ActionTaskOpEmitEvent(BaseModel):
    """Emit a new event."""

    event_type: str
    """Logical event type."""

    kind: Literal["emit_event"]

    meta: Optional[object] = None
    """Optional metadata."""

    payload: Optional[object] = None
    """Optional payload."""


class ActionTaskOpWebhook(BaseModel):
    """Call a webhook (close to `EventAction::Webhook`)."""

    kind: Literal["webhook"]

    url: str
    """Target URL."""

    body: Optional[object] = None
    """Body payload."""

    headers: Optional[Dict[str, str]] = None
    """Headers to include."""

    method: Optional[str] = None
    """HTTP method (defaults to POST)."""

    timeout_ms: Optional[int] = None
    """Optional timeout in milliseconds."""


Action: TypeAlias = Union[ActionTaskOpTx, ActionTaskOpEmitEvent, ActionTaskOpWebhook]


class TaskPlan(BaseModel):
    """Declarative plan comprising one or more `TaskOps`.

    Plans must contain at most `MAX_ACTIONS_PER_TASK` actions; validation rejects
    larger payloads before execution.
    """

    actions: List[Action]
    """Actions to apply sequentially."""
