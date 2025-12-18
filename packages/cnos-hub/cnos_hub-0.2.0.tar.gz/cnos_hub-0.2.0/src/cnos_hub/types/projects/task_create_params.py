# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Dict, Union, Iterable, Optional
from datetime import datetime
from typing_extensions import Literal, Required, Annotated, TypeAlias, TypedDict

from ..._utils import PropertyInfo
from .task_plan_param import TaskPlanParam
from .task_run_as_param import TaskRunAsParam
from .event_filter_json_param import EventFilterJsonParam
from .task_retry_policy_param import TaskRetryPolicyParam

__all__ = [
    "TaskCreateParams",
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


class TaskCreateParams(TypedDict, total=False):
    name: Required[str]
    """Human-friendly task name."""

    retry: Required[TaskRetryPolicyParam]
    """Retry policy."""

    run_as: Required[TaskRunAsParam]
    """Synthetic principal for execution."""

    runner: Required[Runner]
    """Runner definition."""

    trigger: Required[Trigger]
    """Trigger definition."""

    description: Optional[str]
    """Optional description for the task."""


class RunnerTaskRunnerCnosArgsFromCustom(TypedDict, total=False):
    """Pass a custom static value as arguments."""

    custom: Required[Iterable[object]]
    """Pass a custom static value as arguments."""


RunnerTaskRunnerCnosArgsFrom: TypeAlias = Union[
    Literal["empty", "event_envelope", "schedule_payload", "manual_payload"], RunnerTaskRunnerCnosArgsFromCustom
]


class RunnerTaskRunnerCnos(TypedDict, total=False):
    """Call a CNOS function in the current project program to compute the plan."""

    args_from: Required[RunnerTaskRunnerCnosArgsFrom]
    """How to build CNOS args from the trigger context."""

    function: Required[str]
    """Fully-qualified function name."""

    kind: Required[Literal["cnos"]]

    result_mode: Required[Literal["ignore", "event_actions", "tx", "task_plan"]]
    """How to interpret the CNOS return value."""


class RunnerTaskRunnerStatic(TypedDict, total=False):
    """No CNOS; a fixed plan baked into the task."""

    kind: Required[Literal["static"]]

    plan: Required[TaskPlanParam]
    """Pre-computed plan to execute."""


Runner: TypeAlias = Union[RunnerTaskRunnerCnos, RunnerTaskRunnerStatic]


class TriggerTaskTriggerManual(TypedDict, total=False):
    """Only runs when explicitly invoked via `/run`."""

    kind: Required[Literal["manual"]]


class TriggerTaskTriggerEvent(TypedDict, total=False):
    """Runs when a matching event is observed."""

    event_type: Required[str]
    """Logical event type, e.g. "collection.document.created"."""

    kind: Required[Literal["event"]]

    filter: Optional[EventFilterJsonParam]
    """Optional JSON-based filter on envelope/payload/meta."""


class TriggerTaskTriggerScheduleSpecScheduleSpecOneShot(TypedDict, total=False):
    """Run once at a fixed time."""

    kind: Required[Literal["one_shot"]]

    run_at: Required[Annotated[Union[str, datetime], PropertyInfo(format="iso8601")]]
    """Timestamp when the schedule should fire."""


class TriggerTaskTriggerScheduleSpecScheduleSpecInterval(TypedDict, total=False):
    """Run every `every_ms` milliseconds, starting at `start_at` (or now)."""

    every_ms: Required[int]
    """Interval between runs in milliseconds."""

    kind: Required[Literal["interval"]]

    start_at: Annotated[Union[str, datetime, None], PropertyInfo(format="iso8601")]
    """Optional start time; defaults to `now` when omitted."""


class TriggerTaskTriggerScheduleSpecScheduleSpecCron(TypedDict, total=False):
    """Standard cron expression in a given timezone."""

    expression: Required[str]
    """Cron expression using standard syntax."""

    kind: Required[Literal["cron"]]

    timezone: Required[str]
    """Timezone identifier (e.g., `UTC`, `Asia/Kuala_Lumpur`)."""


TriggerTaskTriggerScheduleSpec: TypeAlias = Union[
    TriggerTaskTriggerScheduleSpecScheduleSpecOneShot,
    TriggerTaskTriggerScheduleSpecScheduleSpecInterval,
    TriggerTaskTriggerScheduleSpecScheduleSpecCron,
]


class TriggerTaskTriggerSchedule(TypedDict, total=False):
    """Runs according to a time schedule."""

    kind: Required[Literal["schedule"]]

    spec: Required[TriggerTaskTriggerScheduleSpec]
    """Execution schedule (cron/interval/one-shot)."""

    payload: Dict[str, object]
    """Optional schedule payload passed to the runner."""


Trigger: TypeAlias = Union[TriggerTaskTriggerManual, TriggerTaskTriggerEvent, TriggerTaskTriggerSchedule]
