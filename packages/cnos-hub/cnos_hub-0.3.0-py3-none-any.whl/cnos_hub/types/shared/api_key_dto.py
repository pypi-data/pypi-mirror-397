# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional
from typing_extensions import Literal

from ..._models import BaseModel

__all__ = ["APIKeyDto"]


class APIKeyDto(BaseModel):
    """API key metadata returned by admin endpoints."""

    id: str

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

    created_at: str
    """Creation timestamp in RFC3339 format."""

    name: str

    org_id: str

    project_id: str

    status: str

    description: Optional[str] = None

    expires_at: Optional[str] = None
    """Expiration timestamp in RFC3339 format."""

    last_used_at: Optional[str] = None
    """Last usage timestamp in RFC3339 format."""

    roles: Optional[List[str]] = None
