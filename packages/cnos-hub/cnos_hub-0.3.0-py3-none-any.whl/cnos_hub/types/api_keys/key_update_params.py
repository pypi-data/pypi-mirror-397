# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import List, Optional
from typing_extensions import Literal, TypedDict

from ..._types import SequenceNotStr

__all__ = ["KeyUpdateParams"]


class KeyUpdateParams(TypedDict, total=False):
    capabilities: Optional[
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

    description: str

    name: Optional[str]

    roles: Optional[SequenceNotStr[str]]
