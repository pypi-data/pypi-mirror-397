# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional
from typing_extensions import Literal

from ..._models import BaseModel

__all__ = ["TaskRunAs"]


class TaskRunAs(BaseModel):
    """Synthetic principal used when running a task."""

    capabilities: List[
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
    """Capabilities granted to the task execution."""

    principal_id: str
    """Principal identifier (often `task:{task_id}`)."""

    labels: Optional[List[str]] = None
    """Attached labels."""

    roles: Optional[List[str]] = None
    """Effective roles."""
