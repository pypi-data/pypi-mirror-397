# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Dict, List, Union, Optional
from datetime import datetime
from typing_extensions import Literal, TypeAlias

from ..._models import BaseModel
from .task_plan import TaskPlan
from .task_run_as import TaskRunAs
from .event_filter_json import EventFilterJson
from .task_retry_policy import TaskRetryPolicy

__all__ = [
    "TaskCreateResponse",
    "Runner",
    "RunnerTaskRunnerCnos",
    "RunnerTaskRunnerCnosArgsFrom",
    "RunnerTaskRunnerCnosArgsFromCustom",
    "RunnerTaskRunnerStatic",
    "Trigger",
    "TriggerTaskTriggerManual",
    "TriggerTaskTriggerEvent",
    "TriggerTaskTriggerSchedule",
    "TriggerTaskTriggerScheduleSpec",
    "TriggerTaskTriggerScheduleSpecScheduleSpecOneShot",
    "TriggerTaskTriggerScheduleSpecScheduleSpecInterval",
    "TriggerTaskTriggerScheduleSpecScheduleSpecCron",
]


class RunnerTaskRunnerCnosArgsFromCustom(BaseModel):
    """Pass a custom static value as arguments."""

    custom: List[object]
    """Pass a custom static value as arguments."""


RunnerTaskRunnerCnosArgsFrom: TypeAlias = Union[
    Literal["empty", "event_envelope", "schedule_payload", "manual_payload"], RunnerTaskRunnerCnosArgsFromCustom
]


class RunnerTaskRunnerCnos(BaseModel):
    """Call a CNOS function in the current project program to compute the plan."""

    args_from: RunnerTaskRunnerCnosArgsFrom
    """How to build CNOS args from the trigger context."""

    function: str
    """Fully-qualified function name."""

    kind: Literal["cnos"]

    result_mode: Literal["ignore", "event_actions", "tx", "task_plan"]
    """How to interpret the CNOS return value."""


class RunnerTaskRunnerStatic(BaseModel):
    """No CNOS; a fixed plan baked into the task."""

    kind: Literal["static"]

    plan: TaskPlan
    """Pre-computed plan to execute."""


Runner: TypeAlias = Union[RunnerTaskRunnerCnos, RunnerTaskRunnerStatic]


class TriggerTaskTriggerManual(BaseModel):
    """Only runs when explicitly invoked via `/run`."""

    kind: Literal["manual"]


class TriggerTaskTriggerEvent(BaseModel):
    """Runs when a matching event is observed."""

    event_type: str
    """Logical event type, e.g. "collection.document.created"."""

    kind: Literal["event"]

    filter: Optional[EventFilterJson] = None
    """Optional JSON-based filter on envelope/payload/meta."""


class TriggerTaskTriggerScheduleSpecScheduleSpecOneShot(BaseModel):
    """Run once at a fixed time."""

    kind: Literal["one_shot"]

    run_at: datetime
    """Timestamp when the schedule should fire."""


class TriggerTaskTriggerScheduleSpecScheduleSpecInterval(BaseModel):
    """Run every `every_ms` milliseconds, starting at `start_at` (or now)."""

    every_ms: int
    """Interval between runs in milliseconds."""

    kind: Literal["interval"]

    start_at: Optional[datetime] = None
    """Optional start time; defaults to `now` when omitted."""


class TriggerTaskTriggerScheduleSpecScheduleSpecCron(BaseModel):
    """Standard cron expression in a given timezone."""

    expression: str
    """Cron expression using standard syntax."""

    kind: Literal["cron"]

    timezone: str
    """Timezone identifier (e.g., `UTC`, `Asia/Kuala_Lumpur`)."""


TriggerTaskTriggerScheduleSpec: TypeAlias = Union[
    TriggerTaskTriggerScheduleSpecScheduleSpecOneShot,
    TriggerTaskTriggerScheduleSpecScheduleSpecInterval,
    TriggerTaskTriggerScheduleSpecScheduleSpecCron,
]


class TriggerTaskTriggerSchedule(BaseModel):
    """Runs according to a time schedule."""

    kind: Literal["schedule"]

    spec: TriggerTaskTriggerScheduleSpec
    """Execution schedule (cron/interval/one-shot)."""

    payload: Optional[Dict[str, object]] = None
    """Optional schedule payload passed to the runner."""


Trigger: TypeAlias = Union[TriggerTaskTriggerManual, TriggerTaskTriggerEvent, TriggerTaskTriggerSchedule]


class TaskCreateResponse(BaseModel):
    """API representation of a task."""

    id: str
    """Task identifier."""

    created_at: str
    """Creation timestamp (RFC3339)."""

    name: str
    """Human-friendly name."""

    project_id: str
    """Owning project identifier."""

    retry: TaskRetryPolicy
    """Retry policy."""

    run_as: TaskRunAs
    """Synthetic principal for execution."""

    runner: Runner
    """Runner definition."""

    status: Literal["active", "disabled"]
    """Lifecycle status."""

    trigger: Trigger
    """Trigger definition."""

    updated_at: str
    """Last update timestamp (RFC3339)."""

    description: Optional[str] = None
    """Optional description."""

    last_run_at: Optional[str] = None
    """Last execution timestamp (RFC3339)."""

    next_run_at: Optional[str] = None
    """Next scheduled execution time (RFC3339)."""
