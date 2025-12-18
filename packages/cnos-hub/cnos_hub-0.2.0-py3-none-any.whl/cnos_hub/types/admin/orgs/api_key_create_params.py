# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import List, Union, Optional
from datetime import datetime
from typing_extensions import Literal, Required, Annotated, TypedDict

from ...._types import SequenceNotStr
from ...._utils import PropertyInfo

__all__ = ["APIKeyCreateParams"]


class APIKeyCreateParams(TypedDict, total=False):
    name: Required[str]

    project_id: Required[str]

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

    description: Optional[str]

    expires_at: Annotated[Union[str, datetime, None], PropertyInfo(format="iso8601")]

    roles: SequenceNotStr[str]
