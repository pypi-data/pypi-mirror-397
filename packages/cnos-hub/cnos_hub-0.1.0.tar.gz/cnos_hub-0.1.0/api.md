# Shared Types

```python
from cnos_hub.types import APIError, APIStatus, ExecuteErrorJson, ValidationErrorEntry
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

### Members

Types:

```python
from cnos_hub.types.admin.orgs import MemberCreateResponse, MemberListResponse
```

Methods:

- <code title="post /v1/admin/orgs/{org_id}/members/{user_id}">client.admin.orgs.members.<a href="./src/cnos_hub/resources/admin/orgs/members.py">create</a>(user_id, \*, org_id, \*\*<a href="src/cnos_hub/types/admin/orgs/member_create_params.py">params</a>) -> <a href="./src/cnos_hub/types/admin/orgs/member_create_response.py">MemberCreateResponse</a></code>
- <code title="get /v1/admin/orgs/{org_id}/members">client.admin.orgs.members.<a href="./src/cnos_hub/resources/admin/orgs/members.py">list</a>(org_id, \*\*<a href="src/cnos_hub/types/admin/orgs/member_list_params.py">params</a>) -> <a href="./src/cnos_hub/types/admin/orgs/member_list_response.py">SyncPage[MemberListResponse]</a></code>
- <code title="delete /v1/admin/orgs/{org_id}/members/{user_id}">client.admin.orgs.members.<a href="./src/cnos_hub/resources/admin/orgs/members.py">delete</a>(user_id, \*, org_id) -> None</code>

## APIKeys

Types:

```python
from cnos_hub.types.admin import (
    APIKeyCreateResponse,
    APIKeyListResponse,
    APIKeyListForProjectResponse,
)
```

Methods:

- <code title="post /v1/admin/orgs/{org_id}/api-keys">client.admin.api_keys.<a href="./src/cnos_hub/resources/admin/api_keys/api_keys.py">create</a>(org_id, \*\*<a href="src/cnos_hub/types/admin/api_key_create_params.py">params</a>) -> <a href="./src/cnos_hub/types/admin/api_key_create_response.py">APIKeyCreateResponse</a></code>
- <code title="get /v1/admin/orgs/{org_id}/api-keys">client.admin.api_keys.<a href="./src/cnos_hub/resources/admin/api_keys/api_keys.py">list</a>(org_id, \*\*<a href="src/cnos_hub/types/admin/api_key_list_params.py">params</a>) -> <a href="./src/cnos_hub/types/admin/api_key_list_response.py">SyncPage[APIKeyListResponse]</a></code>
- <code title="get /v1/admin/projects/{project_id}/api-keys">client.admin.api_keys.<a href="./src/cnos_hub/resources/admin/api_keys/api_keys.py">list_for_project</a>(project_id, \*\*<a href="src/cnos_hub/types/admin/api_key_list_for_project_params.py">params</a>) -> <a href="./src/cnos_hub/types/admin/api_key_list_for_project_response.py">SyncPage[APIKeyListForProjectResponse]</a></code>

### Key

Types:

```python
from cnos_hub.types.admin.api_keys import KeyRetrieveResponse, KeyUpdateResponse
```

Methods:

- <code title="get /v1/admin/api-keys/{key_id}">client.admin.api_keys.key.<a href="./src/cnos_hub/resources/admin/api_keys/key.py">retrieve</a>(key_id) -> <a href="./src/cnos_hub/types/admin/api_keys/key_retrieve_response.py">KeyRetrieveResponse</a></code>
- <code title="patch /v1/admin/api-keys/{key_id}">client.admin.api_keys.key.<a href="./src/cnos_hub/resources/admin/api_keys/key.py">update</a>(key_id, \*\*<a href="src/cnos_hub/types/admin/api_keys/key_update_params.py">params</a>) -> <a href="./src/cnos_hub/types/admin/api_keys/key_update_response.py">KeyUpdateResponse</a></code>
- <code title="delete /v1/admin/api-keys/{key_id}">client.admin.api_keys.key.<a href="./src/cnos_hub/resources/admin/api_keys/key.py">delete</a>(key_id) -> None</code>

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
from cnos_hub.types.admin.projects import ProjectRetrieveResponse, ProjectUpdateResponse
```

Methods:

- <code title="get /v1/admin/projects/{project_id}">client.admin.projects.project.<a href="./src/cnos_hub/resources/admin/projects/project.py">retrieve</a>(project_id) -> <a href="./src/cnos_hub/types/admin/projects/project_retrieve_response.py">ProjectRetrieveResponse</a></code>
- <code title="patch /v1/admin/projects/{project_id}">client.admin.projects.project.<a href="./src/cnos_hub/resources/admin/projects/project.py">update</a>(project_id, \*\*<a href="src/cnos_hub/types/admin/projects/project_update_params.py">params</a>) -> <a href="./src/cnos_hub/types/admin/projects/project_update_response.py">ProjectUpdateResponse</a></code>
- <code title="delete /v1/admin/projects/{project_id}">client.admin.projects.project.<a href="./src/cnos_hub/resources/admin/projects/project.py">delete</a>(project_id) -> None</code>

### Members

Types:

```python
from cnos_hub.types.admin.projects import MemberCreateResponse, MemberListResponse
```

Methods:

- <code title="post /v1/admin/projects/{project_id}/members/{user_id}">client.admin.projects.members.<a href="./src/cnos_hub/resources/admin/projects/members.py">create</a>(user_id, \*, project_id, \*\*<a href="src/cnos_hub/types/admin/projects/member_create_params.py">params</a>) -> <a href="./src/cnos_hub/types/admin/projects/member_create_response.py">MemberCreateResponse</a></code>
- <code title="get /v1/admin/projects/{project_id}/members">client.admin.projects.members.<a href="./src/cnos_hub/resources/admin/projects/members.py">list</a>(project_id, \*\*<a href="src/cnos_hub/types/admin/projects/member_list_params.py">params</a>) -> <a href="./src/cnos_hub/types/admin/projects/member_list_response.py">SyncPage[MemberListResponse]</a></code>
- <code title="delete /v1/admin/projects/{project_id}/members/{user_id}">client.admin.projects.members.<a href="./src/cnos_hub/resources/admin/projects/members.py">delete</a>(user_id, \*, project_id) -> None</code>

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

# Me

Types:

```python
from cnos_hub.types import MeOrgsResponse, MeProjectsResponse
```

Methods:

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
from cnos_hub.types import APIKeyListResponse
```

Methods:

- <code title="get /v1/api-keys">client.api_keys.<a href="./src/cnos_hub/resources/api_keys.py">list</a>(\*\*<a href="src/cnos_hub/types/api_key_list_params.py">params</a>) -> <a href="./src/cnos_hub/types/api_key_list_response.py">SyncPage[APIKeyListResponse]</a></code>

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
from cnos_hub.types.projects import CollectionDto, CollectionListResponse
```

Methods:

- <code title="post /v1/projects/{project_id}/collections">client.projects.collections.<a href="./src/cnos_hub/resources/projects/collections/collections.py">create</a>(project_id, \*\*<a href="src/cnos_hub/types/projects/collection_create_params.py">params</a>) -> <a href="./src/cnos_hub/types/projects/collection_dto.py">CollectionDto</a></code>
- <code title="get /v1/projects/{project_id}/collections/{name}">client.projects.collections.<a href="./src/cnos_hub/resources/projects/collections/collections.py">retrieve</a>(name, \*, project_id) -> <a href="./src/cnos_hub/types/projects/collection_dto.py">CollectionDto</a></code>
- <code title="get /v1/projects/{project_id}/collections">client.projects.collections.<a href="./src/cnos_hub/resources/projects/collections/collections.py">list</a>(project_id, \*\*<a href="src/cnos_hub/types/projects/collection_list_params.py">params</a>) -> <a href="./src/cnos_hub/types/projects/collection_list_response.py">SyncPage[CollectionListResponse]</a></code>
- <code title="delete /v1/projects/{project_id}/collections/{name}">client.projects.collections.<a href="./src/cnos_hub/resources/projects/collections/collections.py">delete</a>(name, \*, project_id) -> None</code>

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
from cnos_hub.types.projects import WorkspaceCheckResponse, WorkspacePatchResponse
```

Methods:

- <code title="post /v1/projects/{project_id}/workspace/check">client.projects.workspace.<a href="./src/cnos_hub/resources/projects/workspace.py">check</a>(project_id, \*\*<a href="src/cnos_hub/types/projects/workspace_check_params.py">params</a>) -> <a href="./src/cnos_hub/types/projects/workspace_check_response.py">WorkspaceCheckResponse</a></code>
- <code title="post /v1/projects/{project_id}/workspace/patch">client.projects.workspace.<a href="./src/cnos_hub/resources/projects/workspace.py">patch</a>(project_id, \*\*<a href="src/cnos_hub/types/projects/workspace_patch_params.py">params</a>) -> <a href="./src/cnos_hub/types/projects/workspace_patch_response.py">WorkspacePatchResponse</a></code>

## Budgets

Types:

```python
from cnos_hub.types.projects import BudgetResolveResponse, BudgetSettingsResponse
```

Methods:

- <code title="post /v1/projects/{project_id}/budgets/resolve">client.projects.budgets.<a href="./src/cnos_hub/resources/projects/budgets.py">resolve</a>(project_id, \*\*<a href="src/cnos_hub/types/projects/budget_resolve_params.py">params</a>) -> <a href="./src/cnos_hub/types/projects/budget_resolve_response.py">BudgetResolveResponse</a></code>
- <code title="get /v1/projects/{project_id}/budgets/settings">client.projects.budgets.<a href="./src/cnos_hub/resources/projects/budgets.py">settings</a>(project_id) -> <a href="./src/cnos_hub/types/projects/budget_settings_response.py">BudgetSettingsResponse</a></code>

## Config

Types:

```python
from cnos_hub.types.projects import ConfigRetrieveResponse, ConfigReplaceResponse
```

Methods:

- <code title="get /v1/projects/{project_id}/config">client.projects.config.<a href="./src/cnos_hub/resources/projects/config.py">retrieve</a>(project_id) -> <a href="./src/cnos_hub/types/projects/config_retrieve_response.py">ConfigRetrieveResponse</a></code>
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
- <code title="post /v1/projects/{project_id}/tasks/{task_id}/run">client.projects.tasks.<a href="./src/cnos_hub/resources/projects/tasks.py">run</a>(task_id, \*, project_id, \*\*<a href="src/cnos_hub/types/projects/task_run_params.py">params</a>) -> <a href="./src/cnos_hub/types/projects/task_run_response.py">TaskRunResponse</a></code>
- <code title="get /v1/projects/{project_id}/tasks/{task_id}/runs">client.projects.tasks.<a href="./src/cnos_hub/resources/projects/tasks.py">runs</a>(task_id, \*, project_id, \*\*<a href="src/cnos_hub/types/projects/task_runs_params.py">params</a>) -> <a href="./src/cnos_hub/types/projects/task_runs_response.py">SyncPage[TaskRunsResponse]</a></code>
