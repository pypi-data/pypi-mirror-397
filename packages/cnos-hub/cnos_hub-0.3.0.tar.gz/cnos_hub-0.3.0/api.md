# Shared Types

```python
from cnos_hub.types import (
    APIError,
    APIKeyDto,
    APIKeyStatus,
    APIStatus,
    AuditMeta,
    ExecuteErrorJson,
    ValidationErrorEntry,
)
```

# Admin

## Orgs

Types:

```python
from cnos_hub.types.admin import Organization, OrgListResponse
```

Methods:

- <code title="post /v1/admin/orgs">client.admin.orgs.<a href="./src/cnos_hub/resources/admin/orgs/orgs.py">create</a>(\*\*<a href="src/cnos_hub/types/admin/org_create_params.py">params</a>) -> <a href="./src/cnos_hub/types/admin/organization.py">Organization</a></code>
- <code title="get /v1/admin/orgs/{org_id}">client.admin.orgs.<a href="./src/cnos_hub/resources/admin/orgs/orgs.py">retrieve</a>(org_id) -> <a href="./src/cnos_hub/types/admin/organization.py">Organization</a></code>
- <code title="patch /v1/admin/orgs/{org_id}">client.admin.orgs.<a href="./src/cnos_hub/resources/admin/orgs/orgs.py">update</a>(org_id, \*\*<a href="src/cnos_hub/types/admin/org_update_params.py">params</a>) -> <a href="./src/cnos_hub/types/admin/organization.py">Organization</a></code>
- <code title="get /v1/admin/orgs">client.admin.orgs.<a href="./src/cnos_hub/resources/admin/orgs/orgs.py">list</a>(\*\*<a href="src/cnos_hub/types/admin/org_list_params.py">params</a>) -> <a href="./src/cnos_hub/types/admin/org_list_response.py">SyncPage[OrgListResponse]</a></code>
- <code title="delete /v1/admin/orgs/{org_id}">client.admin.orgs.<a href="./src/cnos_hub/resources/admin/orgs/orgs.py">delete</a>(org_id) -> None</code>

### History

Types:

```python
from cnos_hub.types.admin.orgs import HistoryListResponse
```

Methods:

- <code title="get /v1/admin/orgs/{org_id}/history">client.admin.orgs.history.<a href="./src/cnos_hub/resources/admin/orgs/history.py">list</a>(org_id, \*\*<a href="src/cnos_hub/types/admin/orgs/history_list_params.py">params</a>) -> <a href="./src/cnos_hub/types/admin/orgs/history_list_response.py">SyncPage[HistoryListResponse]</a></code>

### Members

Types:

```python
from cnos_hub.types.admin.orgs import (
    MemberCreateResponse,
    MemberListResponse,
    MemberHistoryResponse,
)
```

Methods:

- <code title="post /v1/admin/orgs/{org_id}/members/{user_id}">client.admin.orgs.members.<a href="./src/cnos_hub/resources/admin/orgs/members.py">create</a>(user_id, \*, org_id, \*\*<a href="src/cnos_hub/types/admin/orgs/member_create_params.py">params</a>) -> <a href="./src/cnos_hub/types/admin/orgs/member_create_response.py">MemberCreateResponse</a></code>
- <code title="get /v1/admin/orgs/{org_id}/members">client.admin.orgs.members.<a href="./src/cnos_hub/resources/admin/orgs/members.py">list</a>(org_id, \*\*<a href="src/cnos_hub/types/admin/orgs/member_list_params.py">params</a>) -> <a href="./src/cnos_hub/types/admin/orgs/member_list_response.py">SyncPage[MemberListResponse]</a></code>
- <code title="delete /v1/admin/orgs/{org_id}/members/{user_id}">client.admin.orgs.members.<a href="./src/cnos_hub/resources/admin/orgs/members.py">delete</a>(user_id, \*, org_id) -> None</code>
- <code title="get /v1/admin/orgs/{org_id}/members/{user_id}/history">client.admin.orgs.members.<a href="./src/cnos_hub/resources/admin/orgs/members.py">history</a>(user_id, \*, org_id, \*\*<a href="src/cnos_hub/types/admin/orgs/member_history_params.py">params</a>) -> <a href="./src/cnos_hub/types/admin/orgs/member_history_response.py">SyncPage[MemberHistoryResponse]</a></code>

### APIKeys

Types:

```python
from cnos_hub.types.admin.orgs import APIKeyCreateResponse, APIKeyListResponse
```

Methods:

- <code title="post /v1/admin/orgs/{org_id}/api-keys">client.admin.orgs.api_keys.<a href="./src/cnos_hub/resources/admin/orgs/api_keys.py">create</a>(org_id, \*\*<a href="src/cnos_hub/types/admin/orgs/api_key_create_params.py">params</a>) -> <a href="./src/cnos_hub/types/admin/orgs/api_key_create_response.py">APIKeyCreateResponse</a></code>
- <code title="get /v1/admin/orgs/{org_id}/api-keys">client.admin.orgs.api_keys.<a href="./src/cnos_hub/resources/admin/orgs/api_keys.py">list</a>(org_id, \*\*<a href="src/cnos_hub/types/admin/orgs/api_key_list_params.py">params</a>) -> <a href="./src/cnos_hub/types/admin/orgs/api_key_list_response.py">SyncPage[APIKeyListResponse]</a></code>

## APIKeys

### Key

Types:

```python
from cnos_hub.types.admin.api_keys import KeyRotateResponse
```

Methods:

- <code title="get /v1/admin/api-keys/{key_id}">client.admin.api_keys.key.<a href="./src/cnos_hub/resources/admin/api_keys/key.py">retrieve</a>(key_id) -> <a href="./src/cnos_hub/types/shared/api_key_dto.py">APIKeyDto</a></code>
- <code title="patch /v1/admin/api-keys/{key_id}">client.admin.api_keys.key.<a href="./src/cnos_hub/resources/admin/api_keys/key.py">update</a>(key_id, \*\*<a href="src/cnos_hub/types/admin/api_keys/key_update_params.py">params</a>) -> <a href="./src/cnos_hub/types/shared/api_key_dto.py">APIKeyDto</a></code>
- <code title="delete /v1/admin/api-keys/{key_id}">client.admin.api_keys.key.<a href="./src/cnos_hub/resources/admin/api_keys/key.py">delete</a>(key_id) -> None</code>
- <code title="post /v1/admin/api-keys/{key_id}/rotate">client.admin.api_keys.key.<a href="./src/cnos_hub/resources/admin/api_keys/key.py">rotate</a>(key_id) -> <a href="./src/cnos_hub/types/admin/api_keys/key_rotate_response.py">KeyRotateResponse</a></code>

## Projects

Types:

```python
from cnos_hub.types.admin import ProjectCreateResponse, ProjectListResponse
```

Methods:

- <code title="post /v1/admin/orgs/{org_id}/projects">client.admin.projects.<a href="./src/cnos_hub/resources/admin/projects/projects.py">create</a>(org_id, \*\*<a href="src/cnos_hub/types/admin/project_create_params.py">params</a>) -> <a href="./src/cnos_hub/types/admin/project_create_response.py">ProjectCreateResponse</a></code>
- <code title="get /v1/admin/orgs/{org_id}/projects">client.admin.projects.<a href="./src/cnos_hub/resources/admin/projects/projects.py">list</a>(org_id, \*\*<a href="src/cnos_hub/types/admin/project_list_params.py">params</a>) -> <a href="./src/cnos_hub/types/admin/project_list_response.py">SyncPage[ProjectListResponse]</a></code>

### Project

Types:

```python
from cnos_hub.types.admin.projects import (
    ProjectRetrieveResponse,
    ProjectUpdateResponse,
    ProjectHistoryResponse,
)
```

Methods:

- <code title="get /v1/admin/projects/{project_id}">client.admin.projects.project.<a href="./src/cnos_hub/resources/admin/projects/project.py">retrieve</a>(project_id) -> <a href="./src/cnos_hub/types/admin/projects/project_retrieve_response.py">ProjectRetrieveResponse</a></code>
- <code title="patch /v1/admin/projects/{project_id}">client.admin.projects.project.<a href="./src/cnos_hub/resources/admin/projects/project.py">update</a>(project_id, \*\*<a href="src/cnos_hub/types/admin/projects/project_update_params.py">params</a>) -> <a href="./src/cnos_hub/types/admin/projects/project_update_response.py">ProjectUpdateResponse</a></code>
- <code title="delete /v1/admin/projects/{project_id}">client.admin.projects.project.<a href="./src/cnos_hub/resources/admin/projects/project.py">delete</a>(project_id) -> None</code>
- <code title="get /v1/admin/projects/{project_id}/history">client.admin.projects.project.<a href="./src/cnos_hub/resources/admin/projects/project.py">history</a>(project_id, \*\*<a href="src/cnos_hub/types/admin/projects/project_history_params.py">params</a>) -> <a href="./src/cnos_hub/types/admin/projects/project_history_response.py">SyncPage[ProjectHistoryResponse]</a></code>

### Members

Types:

```python
from cnos_hub.types.admin.projects import (
    MemberCreateResponse,
    MemberListResponse,
    MemberHistoryResponse,
)
```

Methods:

- <code title="post /v1/admin/projects/{project_id}/members/{user_id}">client.admin.projects.members.<a href="./src/cnos_hub/resources/admin/projects/members.py">create</a>(user_id, \*, project_id, \*\*<a href="src/cnos_hub/types/admin/projects/member_create_params.py">params</a>) -> <a href="./src/cnos_hub/types/admin/projects/member_create_response.py">MemberCreateResponse</a></code>
- <code title="get /v1/admin/projects/{project_id}/members">client.admin.projects.members.<a href="./src/cnos_hub/resources/admin/projects/members.py">list</a>(project_id, \*\*<a href="src/cnos_hub/types/admin/projects/member_list_params.py">params</a>) -> <a href="./src/cnos_hub/types/admin/projects/member_list_response.py">SyncPage[MemberListResponse]</a></code>
- <code title="delete /v1/admin/projects/{project_id}/members/{user_id}">client.admin.projects.members.<a href="./src/cnos_hub/resources/admin/projects/members.py">delete</a>(user_id, \*, project_id) -> None</code>
- <code title="get /v1/admin/projects/{project_id}/members/{user_id}/history">client.admin.projects.members.<a href="./src/cnos_hub/resources/admin/projects/members.py">history</a>(user_id, \*, project_id, \*\*<a href="src/cnos_hub/types/admin/projects/member_history_params.py">params</a>) -> <a href="./src/cnos_hub/types/admin/projects/member_history_response.py">SyncPage[MemberHistoryResponse]</a></code>

### APIKeys

Types:

```python
from cnos_hub.types.admin.projects import APIKeyListResponse
```

Methods:

- <code title="get /v1/admin/projects/{project_id}/api-keys">client.admin.projects.api_keys.<a href="./src/cnos_hub/resources/admin/projects/api_keys.py">list</a>(project_id, \*\*<a href="src/cnos_hub/types/admin/projects/api_key_list_params.py">params</a>) -> <a href="./src/cnos_hub/types/admin/projects/api_key_list_response.py">SyncPage[APIKeyListResponse]</a></code>

# Cnos

Types:

```python
from cnos_hub.types import (
    BudgetsJson,
    CnoAnalyzeResponse,
    CnoExecuteFunctionResponse,
    CnoPrincipalResponse,
    CnoTemplatesResponse,
)
```

Methods:

- <code title="post /v1/cnos/check">client.cnos.<a href="./src/cnos_hub/resources/cnos.py">analyze</a>(\*\*<a href="src/cnos_hub/types/cno_analyze_params.py">params</a>) -> <a href="./src/cnos_hub/types/cno_analyze_response.py">CnoAnalyzeResponse</a></code>
- <code title="post /v1/cnos/execute">client.cnos.<a href="./src/cnos_hub/resources/cnos.py">execute_function</a>(\*\*<a href="src/cnos_hub/types/cno_execute_function_params.py">params</a>) -> <a href="./src/cnos_hub/types/cno_execute_function_response.py">CnoExecuteFunctionResponse</a></code>
- <code title="get /v1/principal">client.cnos.<a href="./src/cnos_hub/resources/cnos.py">principal</a>() -> <a href="./src/cnos_hub/types/cno_principal_response.py">CnoPrincipalResponse</a></code>
- <code title="get /v1/cnos/templates">client.cnos.<a href="./src/cnos_hub/resources/cnos.py">templates</a>() -> <a href="./src/cnos_hub/types/cno_templates_response.py">CnoTemplatesResponse</a></code>

# Meta

Types:

```python
from cnos_hub.types import MetaCapabilitiesResponse, MetaEndpointsResponse, MetaGetResponse
```

Methods:

- <code title="get /v1/meta/capabilities">client.meta.<a href="./src/cnos_hub/resources/meta.py">capabilities</a>() -> <a href="./src/cnos_hub/types/meta_capabilities_response.py">MetaCapabilitiesResponse</a></code>
- <code title="get /v1/meta/endpoints">client.meta.<a href="./src/cnos_hub/resources/meta.py">endpoints</a>() -> <a href="./src/cnos_hub/types/meta_endpoints_response.py">MetaEndpointsResponse</a></code>
- <code title="get /v1/meta">client.meta.<a href="./src/cnos_hub/resources/meta.py">get</a>() -> <a href="./src/cnos_hub/types/meta_get_response.py">MetaGetResponse</a></code>

# Authz

Types:

```python
from cnos_hub.types import AuthzTestResponse
```

Methods:

- <code title="post /v1/authorize-test">client.authz.<a href="./src/cnos_hub/resources/authz.py">test</a>(\*\*<a href="src/cnos_hub/types/authz_test_params.py">params</a>) -> <a href="./src/cnos_hub/types/authz_test_response.py">AuthzTestResponse</a></code>

# ConfigSchema

Types:

```python
from cnos_hub.types import (
    ConfigSchemaOrgResponse,
    ConfigSchemaProjectResponse,
    ConfigSchemaSystemResponse,
)
```

Methods:

- <code title="get /v1/config/schema/org">client.config_schema.<a href="./src/cnos_hub/resources/config_schema.py">org</a>() -> <a href="./src/cnos_hub/types/config_schema_org_response.py">ConfigSchemaOrgResponse</a></code>
- <code title="get /v1/config/schema/project">client.config_schema.<a href="./src/cnos_hub/resources/config_schema.py">project</a>() -> <a href="./src/cnos_hub/types/config_schema_project_response.py">ConfigSchemaProjectResponse</a></code>
- <code title="get /v1/config/schema/system">client.config_schema.<a href="./src/cnos_hub/resources/config_schema.py">system</a>() -> <a href="./src/cnos_hub/types/config_schema_system_response.py">ConfigSchemaSystemResponse</a></code>

# Me

Types:

```python
from cnos_hub.types import MeGetResponse, MeOrgsResponse, MeProjectsResponse
```

Methods:

- <code title="get /v1/me">client.me.<a href="./src/cnos_hub/resources/me.py">get</a>() -> <a href="./src/cnos_hub/types/me_get_response.py">MeGetResponse</a></code>
- <code title="get /v1/me/orgs">client.me.<a href="./src/cnos_hub/resources/me.py">orgs</a>() -> <a href="./src/cnos_hub/types/me_orgs_response.py">MeOrgsResponse</a></code>
- <code title="get /v1/me/projects">client.me.<a href="./src/cnos_hub/resources/me.py">projects</a>() -> <a href="./src/cnos_hub/types/me_projects_response.py">MeProjectsResponse</a></code>

# Context

Types:

```python
from cnos_hub.types import ContextOrgResponse, ContextProjectResponse
```

Methods:

- <code title="get /v1/org">client.context.<a href="./src/cnos_hub/resources/context.py">org</a>() -> <a href="./src/cnos_hub/types/context_org_response.py">ContextOrgResponse</a></code>
- <code title="get /v1/project">client.context.<a href="./src/cnos_hub/resources/context.py">project</a>() -> <a href="./src/cnos_hub/types/context_project_response.py">ContextProjectResponse</a></code>

# APIKeys

Types:

```python
from cnos_hub.types import APIKeyCreateResponse, APIKeyListResponse
```

Methods:

- <code title="post /v1/api-keys">client.api_keys.<a href="./src/cnos_hub/resources/api_keys/api_keys.py">create</a>(\*\*<a href="src/cnos_hub/types/api_key_create_params.py">params</a>) -> <a href="./src/cnos_hub/types/api_key_create_response.py">APIKeyCreateResponse</a></code>
- <code title="get /v1/api-keys">client.api_keys.<a href="./src/cnos_hub/resources/api_keys/api_keys.py">list</a>(\*\*<a href="src/cnos_hub/types/api_key_list_params.py">params</a>) -> <a href="./src/cnos_hub/types/api_key_list_response.py">SyncPage[APIKeyListResponse]</a></code>

## Key

Types:

```python
from cnos_hub.types.api_keys import KeyRotateResponse
```

Methods:

- <code title="get /v1/api-keys/{key_id}">client.api_keys.key.<a href="./src/cnos_hub/resources/api_keys/key.py">retrieve</a>(key_id) -> <a href="./src/cnos_hub/types/shared/api_key_dto.py">APIKeyDto</a></code>
- <code title="patch /v1/api-keys/{key_id}">client.api_keys.key.<a href="./src/cnos_hub/resources/api_keys/key.py">update</a>(key_id, \*\*<a href="src/cnos_hub/types/api_keys/key_update_params.py">params</a>) -> <a href="./src/cnos_hub/types/shared/api_key_dto.py">APIKeyDto</a></code>
- <code title="delete /v1/api-keys/{key_id}">client.api_keys.key.<a href="./src/cnos_hub/resources/api_keys/key.py">delete</a>(key_id) -> None</code>
- <code title="post /v1/api-keys/{key_id}/rotate">client.api_keys.key.<a href="./src/cnos_hub/resources/api_keys/key.py">rotate</a>(key_id) -> <a href="./src/cnos_hub/types/api_keys/key_rotate_response.py">KeyRotateResponse</a></code>

# Projects

Types:

```python
from cnos_hub.types import ProjectTransactionResponse
```

Methods:

- <code title="post /v1/projects/{project_id}/tx">client.projects.<a href="./src/cnos_hub/resources/projects/projects.py">transaction</a>(project_id, \*\*<a href="src/cnos_hub/types/project_transaction_params.py">params</a>) -> <a href="./src/cnos_hub/types/project_transaction_response.py">ProjectTransactionResponse</a></code>

## Collections

Types:

```python
from cnos_hub.types.projects import (
    CollectionDto,
    CollectionListResponse,
    CollectionHistoryResponse,
    CollectionStatsResponse,
)
```

Methods:

- <code title="post /v1/projects/{project_id}/collections">client.projects.collections.<a href="./src/cnos_hub/resources/projects/collections/collections.py">create</a>(project_id, \*\*<a href="src/cnos_hub/types/projects/collection_create_params.py">params</a>) -> <a href="./src/cnos_hub/types/projects/collection_dto.py">CollectionDto</a></code>
- <code title="get /v1/projects/{project_id}/collections/{name}">client.projects.collections.<a href="./src/cnos_hub/resources/projects/collections/collections.py">retrieve</a>(name, \*, project_id) -> <a href="./src/cnos_hub/types/projects/collection_dto.py">CollectionDto</a></code>
- <code title="get /v1/projects/{project_id}/collections">client.projects.collections.<a href="./src/cnos_hub/resources/projects/collections/collections.py">list</a>(project_id, \*\*<a href="src/cnos_hub/types/projects/collection_list_params.py">params</a>) -> <a href="./src/cnos_hub/types/projects/collection_list_response.py">SyncPage[CollectionListResponse]</a></code>
- <code title="delete /v1/projects/{project_id}/collections/{name}">client.projects.collections.<a href="./src/cnos_hub/resources/projects/collections/collections.py">delete</a>(name, \*, project_id) -> None</code>
- <code title="get /v1/projects/{project_id}/collections/{name}/history">client.projects.collections.<a href="./src/cnos_hub/resources/projects/collections/collections.py">history</a>(name, \*, project_id, \*\*<a href="src/cnos_hub/types/projects/collection_history_params.py">params</a>) -> <a href="./src/cnos_hub/types/projects/collection_history_response.py">SyncPage[CollectionHistoryResponse]</a></code>
- <code title="get /v1/projects/{project_id}/collections/{name}/stats">client.projects.collections.<a href="./src/cnos_hub/resources/projects/collections/collections.py">stats</a>(name, \*, project_id) -> <a href="./src/cnos_hub/types/projects/collection_stats_response.py">CollectionStatsResponse</a></code>

### Docs

Types:

```python
from cnos_hub.types.projects.collections import (
    DocumentMeta,
    DocCreateResponse,
    DocRetrieveResponse,
    DocListResponse,
    DocReplaceResponse,
)
```

Methods:

- <code title="post /v1/projects/{project_id}/collections/{name}/docs">client.projects.collections.docs.<a href="./src/cnos_hub/resources/projects/collections/docs.py">create</a>(name, \*, project_id, \*\*<a href="src/cnos_hub/types/projects/collections/doc_create_params.py">params</a>) -> <a href="./src/cnos_hub/types/projects/collections/doc_create_response.py">DocCreateResponse</a></code>
- <code title="get /v1/projects/{project_id}/collections/{name}/docs/{doc_id}">client.projects.collections.docs.<a href="./src/cnos_hub/resources/projects/collections/docs.py">retrieve</a>(doc_id, \*, project_id, name, \*\*<a href="src/cnos_hub/types/projects/collections/doc_retrieve_params.py">params</a>) -> <a href="./src/cnos_hub/types/projects/collections/doc_retrieve_response.py">DocRetrieveResponse</a></code>
- <code title="get /v1/projects/{project_id}/collections/{name}/docs">client.projects.collections.docs.<a href="./src/cnos_hub/resources/projects/collections/docs.py">list</a>(name, \*, project_id, \*\*<a href="src/cnos_hub/types/projects/collections/doc_list_params.py">params</a>) -> <a href="./src/cnos_hub/types/projects/collections/doc_list_response.py">SyncPage[DocListResponse]</a></code>
- <code title="delete /v1/projects/{project_id}/collections/{name}/docs/{doc_id}">client.projects.collections.docs.<a href="./src/cnos_hub/resources/projects/collections/docs.py">delete</a>(doc_id, \*, project_id, name, \*\*<a href="src/cnos_hub/types/projects/collections/doc_delete_params.py">params</a>) -> None</code>
- <code title="put /v1/projects/{project_id}/collections/{name}/docs/{doc_id}">client.projects.collections.docs.<a href="./src/cnos_hub/resources/projects/collections/docs.py">replace</a>(doc_id, \*, project_id, name, \*\*<a href="src/cnos_hub/types/projects/collections/doc_replace_params.py">params</a>) -> <a href="./src/cnos_hub/types/projects/collections/doc_replace_response.py">DocReplaceResponse</a></code>

## Workspace

Types:

```python
from cnos_hub.types.projects import (
    WorkspaceListResponse,
    WorkspaceCheckResponse,
    WorkspacePatchResponse,
    WorkspaceRetrieveFileResponse,
)
```

Methods:

- <code title="get /v1/projects/{project_id}/workspace">client.projects.workspace.<a href="./src/cnos_hub/resources/projects/workspace.py">list</a>(project_id) -> <a href="./src/cnos_hub/types/projects/workspace_list_response.py">WorkspaceListResponse</a></code>
- <code title="post /v1/projects/{project_id}/workspace/check">client.projects.workspace.<a href="./src/cnos_hub/resources/projects/workspace.py">check</a>(project_id, \*\*<a href="src/cnos_hub/types/projects/workspace_check_params.py">params</a>) -> <a href="./src/cnos_hub/types/projects/workspace_check_response.py">WorkspaceCheckResponse</a></code>
- <code title="post /v1/projects/{project_id}/workspace/patch">client.projects.workspace.<a href="./src/cnos_hub/resources/projects/workspace.py">patch</a>(project_id, \*\*<a href="src/cnos_hub/types/projects/workspace_patch_params.py">params</a>) -> <a href="./src/cnos_hub/types/projects/workspace_patch_response.py">WorkspacePatchResponse</a></code>
- <code title="get /v1/projects/{project_id}/workspace/file">client.projects.workspace.<a href="./src/cnos_hub/resources/projects/workspace.py">retrieve_file</a>(project_id, \*\*<a href="src/cnos_hub/types/projects/workspace_retrieve_file_params.py">params</a>) -> <a href="./src/cnos_hub/types/projects/workspace_retrieve_file_response.py">WorkspaceRetrieveFileResponse</a></code>

## Budgets

Types:

```python
from cnos_hub.types.projects import (
    BudgetLimitsResponse,
    BudgetResolveResponse,
    BudgetSettingsResponse,
)
```

Methods:

- <code title="get /v1/projects/{project_id}/limits">client.projects.budgets.<a href="./src/cnos_hub/resources/projects/budgets.py">limits</a>(project_id) -> <a href="./src/cnos_hub/types/projects/budget_limits_response.py">BudgetLimitsResponse</a></code>
- <code title="post /v1/projects/{project_id}/budgets/resolve">client.projects.budgets.<a href="./src/cnos_hub/resources/projects/budgets.py">resolve</a>(project_id, \*\*<a href="src/cnos_hub/types/projects/budget_resolve_params.py">params</a>) -> <a href="./src/cnos_hub/types/projects/budget_resolve_response.py">BudgetResolveResponse</a></code>
- <code title="get /v1/projects/{project_id}/budgets/settings">client.projects.budgets.<a href="./src/cnos_hub/resources/projects/budgets.py">settings</a>(project_id) -> <a href="./src/cnos_hub/types/projects/budget_settings_response.py">BudgetSettingsResponse</a></code>

## Config

Types:

```python
from cnos_hub.types.projects import (
    ConfigRetrieveResponse,
    ConfigHistoryResponse,
    ConfigReplaceResponse,
)
```

Methods:

- <code title="get /v1/projects/{project_id}/config">client.projects.config.<a href="./src/cnos_hub/resources/projects/config.py">retrieve</a>(project_id) -> <a href="./src/cnos_hub/types/projects/config_retrieve_response.py">ConfigRetrieveResponse</a></code>
- <code title="get /v1/projects/{project_id}/config/history">client.projects.config.<a href="./src/cnos_hub/resources/projects/config.py">history</a>(project_id, \*\*<a href="src/cnos_hub/types/projects/config_history_params.py">params</a>) -> <a href="./src/cnos_hub/types/projects/config_history_response.py">SyncPage[ConfigHistoryResponse]</a></code>
- <code title="put /v1/projects/{project_id}/config">client.projects.config.<a href="./src/cnos_hub/resources/projects/config.py">replace</a>(project_id, \*\*<a href="src/cnos_hub/types/projects/config_replace_params.py">params</a>) -> <a href="./src/cnos_hub/types/projects/config_replace_response.py">ConfigReplaceResponse</a></code>

## Events

Types:

```python
from cnos_hub.types.projects import (
    EventCreateResponse,
    EventRetrieveResponse,
    EventListResponse,
    EventRetryResponse,
)
```

Methods:

- <code title="post /v1/projects/{project_id}/events">client.projects.events.<a href="./src/cnos_hub/resources/projects/events.py">create</a>(project_id, \*\*<a href="src/cnos_hub/types/projects/event_create_params.py">params</a>) -> <a href="./src/cnos_hub/types/projects/event_create_response.py">EventCreateResponse</a></code>
- <code title="get /v1/projects/{project_id}/events/{event_id}">client.projects.events.<a href="./src/cnos_hub/resources/projects/events.py">retrieve</a>(event_id, \*, project_id) -> <a href="./src/cnos_hub/types/projects/event_retrieve_response.py">EventRetrieveResponse</a></code>
- <code title="get /v1/projects/{project_id}/events">client.projects.events.<a href="./src/cnos_hub/resources/projects/events.py">list</a>(project_id, \*\*<a href="src/cnos_hub/types/projects/event_list_params.py">params</a>) -> <a href="./src/cnos_hub/types/projects/event_list_response.py">SyncPage[EventListResponse]</a></code>
- <code title="post /v1/projects/{project_id}/events/{event_id}/drop">client.projects.events.<a href="./src/cnos_hub/resources/projects/events.py">drop</a>(event_id, \*, project_id) -> None</code>
- <code title="post /v1/projects/{project_id}/events/{event_id}/retry">client.projects.events.<a href="./src/cnos_hub/resources/projects/events.py">retry</a>(event_id, \*, project_id) -> <a href="./src/cnos_hub/types/projects/event_retry_response.py">EventRetryResponse</a></code>

## Execute

Types:

```python
from cnos_hub.types.projects import ExecuteCreateResponse
```

Methods:

- <code title="post /v1/projects/{project_id}/execute">client.projects.execute.<a href="./src/cnos_hub/resources/projects/execute.py">create</a>(project_id, \*\*<a href="src/cnos_hub/types/projects/execute_create_params.py">params</a>) -> <a href="./src/cnos_hub/types/projects/execute_create_response.py">ExecuteCreateResponse</a></code>

## Files

Types:

```python
from cnos_hub.types.projects import FileCreateResponse, FileRetrieveResponse, FileListResponse
```

Methods:

- <code title="post /v1/projects/{project_id}/files">client.projects.files.<a href="./src/cnos_hub/resources/projects/files.py">create</a>(project_id, \*\*<a href="src/cnos_hub/types/projects/file_create_params.py">params</a>) -> <a href="./src/cnos_hub/types/projects/file_create_response.py">FileCreateResponse</a></code>
- <code title="get /v1/projects/{project_id}/files/{file_id}">client.projects.files.<a href="./src/cnos_hub/resources/projects/files.py">retrieve</a>(file_id, \*, project_id) -> <a href="./src/cnos_hub/types/projects/file_retrieve_response.py">FileRetrieveResponse</a></code>
- <code title="get /v1/projects/{project_id}/files">client.projects.files.<a href="./src/cnos_hub/resources/projects/files.py">list</a>(project_id, \*\*<a href="src/cnos_hub/types/projects/file_list_params.py">params</a>) -> <a href="./src/cnos_hub/types/projects/file_list_response.py">SyncPage[FileListResponse]</a></code>
- <code title="delete /v1/projects/{project_id}/files/{file_id}">client.projects.files.<a href="./src/cnos_hub/resources/projects/files.py">delete</a>(file_id, \*, project_id) -> None</code>
- <code title="get /v1/projects/{project_id}/files/{file_id}/content">client.projects.files.<a href="./src/cnos_hub/resources/projects/files.py">content</a>(file_id, \*, project_id) -> None</code>

## Tasks

Types:

```python
from cnos_hub.types.projects import (
    EventFilterJson,
    TaskPlan,
    TaskRetryPolicy,
    TaskRunAs,
    TxRequest,
    TaskCreateResponse,
    TaskRetrieveResponse,
    TaskUpdateResponse,
    TaskListResponse,
    TaskHistoryResponse,
    TaskRunResponse,
    TaskRunsResponse,
)
```

Methods:

- <code title="post /v1/projects/{project_id}/tasks">client.projects.tasks.<a href="./src/cnos_hub/resources/projects/tasks.py">create</a>(project_id, \*\*<a href="src/cnos_hub/types/projects/task_create_params.py">params</a>) -> <a href="./src/cnos_hub/types/projects/task_create_response.py">TaskCreateResponse</a></code>
- <code title="get /v1/projects/{project_id}/tasks/{task_id}">client.projects.tasks.<a href="./src/cnos_hub/resources/projects/tasks.py">retrieve</a>(task_id, \*, project_id) -> <a href="./src/cnos_hub/types/projects/task_retrieve_response.py">TaskRetrieveResponse</a></code>
- <code title="patch /v1/projects/{project_id}/tasks/{task_id}">client.projects.tasks.<a href="./src/cnos_hub/resources/projects/tasks.py">update</a>(task_id, \*, project_id, \*\*<a href="src/cnos_hub/types/projects/task_update_params.py">params</a>) -> <a href="./src/cnos_hub/types/projects/task_update_response.py">TaskUpdateResponse</a></code>
- <code title="get /v1/projects/{project_id}/tasks">client.projects.tasks.<a href="./src/cnos_hub/resources/projects/tasks.py">list</a>(project_id, \*\*<a href="src/cnos_hub/types/projects/task_list_params.py">params</a>) -> <a href="./src/cnos_hub/types/projects/task_list_response.py">SyncPage[TaskListResponse]</a></code>
- <code title="delete /v1/projects/{project_id}/tasks/{task_id}">client.projects.tasks.<a href="./src/cnos_hub/resources/projects/tasks.py">delete</a>(task_id, \*, project_id) -> None</code>
- <code title="get /v1/projects/{project_id}/tasks/{task_id}/history">client.projects.tasks.<a href="./src/cnos_hub/resources/projects/tasks.py">history</a>(task_id, \*, project_id, \*\*<a href="src/cnos_hub/types/projects/task_history_params.py">params</a>) -> <a href="./src/cnos_hub/types/projects/task_history_response.py">SyncPage[TaskHistoryResponse]</a></code>
- <code title="post /v1/projects/{project_id}/tasks/{task_id}/run">client.projects.tasks.<a href="./src/cnos_hub/resources/projects/tasks.py">run</a>(task_id, \*, project_id, \*\*<a href="src/cnos_hub/types/projects/task_run_params.py">params</a>) -> <a href="./src/cnos_hub/types/projects/task_run_response.py">TaskRunResponse</a></code>
- <code title="get /v1/projects/{project_id}/tasks/{task_id}/runs">client.projects.tasks.<a href="./src/cnos_hub/resources/projects/tasks.py">runs</a>(task_id, \*, project_id, \*\*<a href="src/cnos_hub/types/projects/task_runs_params.py">params</a>) -> <a href="./src/cnos_hub/types/projects/task_runs_response.py">SyncPage[TaskRunsResponse]</a></code>

## Views

Types:

```python
from cnos_hub.types.projects import ViewCreateResponse, ViewListResponse
```

Methods:

- <code title="post /v1/projects/{project_id}/views">client.projects.views.<a href="./src/cnos_hub/resources/projects/views/views.py">create</a>(project_id, \*\*<a href="src/cnos_hub/types/projects/view_create_params.py">params</a>) -> <a href="./src/cnos_hub/types/projects/view_create_response.py">ViewCreateResponse</a></code>
- <code title="get /v1/projects/{project_id}/views">client.projects.views.<a href="./src/cnos_hub/resources/projects/views/views.py">list</a>(project_id, \*\*<a href="src/cnos_hub/types/projects/view_list_params.py">params</a>) -> <a href="./src/cnos_hub/types/projects/view_list_response.py">SyncPage[ViewListResponse]</a></code>

### View

Types:

```python
from cnos_hub.types.projects.views import ViewRetrieveResponse, ViewUpdateResponse
```

Methods:

- <code title="get /v1/projects/{project_id}/views/{view_name}">client.projects.views.view.<a href="./src/cnos_hub/resources/projects/views/view.py">retrieve</a>(view_name, \*, project_id) -> <a href="./src/cnos_hub/types/projects/views/view_retrieve_response.py">ViewRetrieveResponse</a></code>
- <code title="patch /v1/projects/{project_id}/views/{view_name}">client.projects.views.view.<a href="./src/cnos_hub/resources/projects/views/view.py">update</a>(view_name, \*, project_id, \*\*<a href="src/cnos_hub/types/projects/views/view_update_params.py">params</a>) -> <a href="./src/cnos_hub/types/projects/views/view_update_response.py">ViewUpdateResponse</a></code>
- <code title="delete /v1/projects/{project_id}/views/{view_name}">client.projects.views.view.<a href="./src/cnos_hub/resources/projects/views/view.py">delete</a>(view_name, \*, project_id) -> None</code>

## Webhooks

Types:

```python
from cnos_hub.types.projects import WebhookCreateResponse, WebhookListResponse
```

Methods:

- <code title="post /v1/projects/{project_id}/webhooks">client.projects.webhooks.<a href="./src/cnos_hub/resources/projects/webhooks/webhooks.py">create</a>(project_id, \*\*<a href="src/cnos_hub/types/projects/webhook_create_params.py">params</a>) -> <a href="./src/cnos_hub/types/projects/webhook_create_response.py">WebhookCreateResponse</a></code>
- <code title="get /v1/projects/{project_id}/webhooks">client.projects.webhooks.<a href="./src/cnos_hub/resources/projects/webhooks/webhooks.py">list</a>(project_id, \*\*<a href="src/cnos_hub/types/projects/webhook_list_params.py">params</a>) -> <a href="./src/cnos_hub/types/projects/webhook_list_response.py">SyncPage[WebhookListResponse]</a></code>

### Webhook

Types:

```python
from cnos_hub.types.projects.webhooks import (
    WebhookRetrieveResponse,
    WebhookUpdateResponse,
    WebhookDeliveriesResponse,
)
```

Methods:

- <code title="get /v1/projects/{project_id}/webhooks/{webhook_id}">client.projects.webhooks.webhook.<a href="./src/cnos_hub/resources/projects/webhooks/webhook.py">retrieve</a>(webhook_id, \*, project_id) -> <a href="./src/cnos_hub/types/projects/webhooks/webhook_retrieve_response.py">WebhookRetrieveResponse</a></code>
- <code title="patch /v1/projects/{project_id}/webhooks/{webhook_id}">client.projects.webhooks.webhook.<a href="./src/cnos_hub/resources/projects/webhooks/webhook.py">update</a>(webhook_id, \*, project_id, \*\*<a href="src/cnos_hub/types/projects/webhooks/webhook_update_params.py">params</a>) -> <a href="./src/cnos_hub/types/projects/webhooks/webhook_update_response.py">WebhookUpdateResponse</a></code>
- <code title="delete /v1/projects/{project_id}/webhooks/{webhook_id}">client.projects.webhooks.webhook.<a href="./src/cnos_hub/resources/projects/webhooks/webhook.py">delete</a>(webhook_id, \*, project_id) -> None</code>
- <code title="get /v1/projects/{project_id}/webhooks/{webhook_id}/deliveries">client.projects.webhooks.webhook.<a href="./src/cnos_hub/resources/projects/webhooks/webhook.py">deliveries</a>(webhook_id, \*, project_id, \*\*<a href="src/cnos_hub/types/projects/webhooks/webhook_deliveries_params.py">params</a>) -> <a href="./src/cnos_hub/types/projects/webhooks/webhook_deliveries_response.py">SyncPage[WebhookDeliveriesResponse]</a></code>
