# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import List
from typing_extensions import Literal, Required, TypedDict

from ..._types import SequenceNotStr

__all__ = ["TaskRunAsParam"]


class TaskRunAsParam(TypedDict, total=False):
    """Synthetic principal used when running a task."""

    capabilities: Required[
        List[
            Literal[
                "OrgRead",
                "OrgWrite",
                "OrgDelete",
                "OrgConfigRead",
                "OrgConfigWrite",
                "ProjectRead",
                "ProjectWrite",
                "ProjectDelete",
                "ProjectConfigRead",
                "ProjectConfigWrite",
                "CnosCheck",
                "CnosExecute",
                "PrincipalRead",
                "CollectionsRead",
                "CollectionsWrite",
                "CollectionsAdmin",
                "DataRead",
                "DataWrite",
                "FilesRead",
                "FilesWrite",
                "TasksRead",
                "TasksWrite",
                "EventsRead",
                "EventsWrite",
                "WebhooksRead",
                "WebhooksWrite",
                "ViewsRead",
                "ViewsWrite",
                "ViewsExecute",
                "ViewsGrant",
                "ApiKeysRead",
                "ApiKeysWrite",
                "OrgMembersRead",
                "OrgMembersWrite",
                "OrgMembersManage",
                "ProjectMembersRead",
                "ProjectMembersWrite",
                "ProjectMembersManage",
                "PlatformOrgAdmin",
                "PlatformSystemConfigAdmin",
                "ImpersonatePrincipal",
            ]
        ]
    ]
    """Capabilities granted to the task execution."""

    principal_id: Required[str]
    """Principal identifier (often `task:{task_id}`)."""

    labels: SequenceNotStr[str]
    """Attached labels."""

    roles: SequenceNotStr[str]
    """Effective roles."""
