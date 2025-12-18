# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Iterable

import httpx

from .files import (
    FilesResource,
    AsyncFilesResource,
    FilesResourceWithRawResponse,
    AsyncFilesResourceWithRawResponse,
    FilesResourceWithStreamingResponse,
    AsyncFilesResourceWithStreamingResponse,
)
from .tasks import (
    TasksResource,
    AsyncTasksResource,
    TasksResourceWithRawResponse,
    AsyncTasksResourceWithRawResponse,
    TasksResourceWithStreamingResponse,
    AsyncTasksResourceWithStreamingResponse,
)
from .config import (
    ConfigResource,
    AsyncConfigResource,
    ConfigResourceWithRawResponse,
    AsyncConfigResourceWithRawResponse,
    ConfigResourceWithStreamingResponse,
    AsyncConfigResourceWithStreamingResponse,
)
from .events import (
    EventsResource,
    AsyncEventsResource,
    EventsResourceWithRawResponse,
    AsyncEventsResourceWithRawResponse,
    EventsResourceWithStreamingResponse,
    AsyncEventsResourceWithStreamingResponse,
)
from ...types import project_transaction_params
from .budgets import (
    BudgetsResource,
    AsyncBudgetsResource,
    BudgetsResourceWithRawResponse,
    AsyncBudgetsResourceWithRawResponse,
    BudgetsResourceWithStreamingResponse,
    AsyncBudgetsResourceWithStreamingResponse,
)
from .execute import (
    ExecuteResource,
    AsyncExecuteResource,
    ExecuteResourceWithRawResponse,
    AsyncExecuteResourceWithRawResponse,
    ExecuteResourceWithStreamingResponse,
    AsyncExecuteResourceWithStreamingResponse,
)
from ..._types import Body, Omit, Query, Headers, NotGiven, omit, not_given
from ..._utils import maybe_transform, async_maybe_transform
from ..._compat import cached_property
from .workspace import (
    WorkspaceResource,
    AsyncWorkspaceResource,
    WorkspaceResourceWithRawResponse,
    AsyncWorkspaceResourceWithRawResponse,
    WorkspaceResourceWithStreamingResponse,
    AsyncWorkspaceResourceWithStreamingResponse,
)
from ..._resource import SyncAPIResource, AsyncAPIResource
from ..._response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from .views.views import (
    ViewsResource,
    AsyncViewsResource,
    ViewsResourceWithRawResponse,
    AsyncViewsResourceWithRawResponse,
    ViewsResourceWithStreamingResponse,
    AsyncViewsResourceWithStreamingResponse,
)
from ..._base_client import make_request_options
from .webhooks.webhooks import (
    WebhooksResource,
    AsyncWebhooksResource,
    WebhooksResourceWithRawResponse,
    AsyncWebhooksResourceWithRawResponse,
    WebhooksResourceWithStreamingResponse,
    AsyncWebhooksResourceWithStreamingResponse,
)
from .collections.collections import (
    CollectionsResource,
    AsyncCollectionsResource,
    CollectionsResourceWithRawResponse,
    AsyncCollectionsResourceWithRawResponse,
    CollectionsResourceWithStreamingResponse,
    AsyncCollectionsResourceWithStreamingResponse,
)
from ...types.project_transaction_response import ProjectTransactionResponse

__all__ = ["ProjectsResource", "AsyncProjectsResource"]


class ProjectsResource(SyncAPIResource):
    @cached_property
    def collections(self) -> CollectionsResource:
        return CollectionsResource(self._client)

    @cached_property
    def workspace(self) -> WorkspaceResource:
        return WorkspaceResource(self._client)

    @cached_property
    def budgets(self) -> BudgetsResource:
        return BudgetsResource(self._client)

    @cached_property
    def config(self) -> ConfigResource:
        return ConfigResource(self._client)

    @cached_property
    def events(self) -> EventsResource:
        return EventsResource(self._client)

    @cached_property
    def execute(self) -> ExecuteResource:
        return ExecuteResource(self._client)

    @cached_property
    def files(self) -> FilesResource:
        return FilesResource(self._client)

    @cached_property
    def tasks(self) -> TasksResource:
        return TasksResource(self._client)

    @cached_property
    def views(self) -> ViewsResource:
        return ViewsResource(self._client)

    @cached_property
    def webhooks(self) -> WebhooksResource:
        return WebhooksResource(self._client)

    @cached_property
    def with_raw_response(self) -> ProjectsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/Synext-Solution/cnos-hub-gen-sdk-py#accessing-raw-response-data-eg-headers
        """
        return ProjectsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> ProjectsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/Synext-Solution/cnos-hub-gen-sdk-py#with_streaming_response
        """
        return ProjectsResourceWithStreamingResponse(self)

    def transaction(
        self,
        project_id: str,
        *,
        operations: Iterable[project_transaction_params.Operation],
        events: Iterable[project_transaction_params.Event] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ProjectTransactionResponse:
        """
        Execute a batch of collection and document mutations inside a hub transaction.

        Args:
          operations: Operations to execute atomically.

          events: Optional events to emit within the same transaction.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not project_id:
            raise ValueError(f"Expected a non-empty value for `project_id` but received {project_id!r}")
        return self._post(
            f"/v1/projects/{project_id}/tx",
            body=maybe_transform(
                {
                    "operations": operations,
                    "events": events,
                },
                project_transaction_params.ProjectTransactionParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ProjectTransactionResponse,
        )


class AsyncProjectsResource(AsyncAPIResource):
    @cached_property
    def collections(self) -> AsyncCollectionsResource:
        return AsyncCollectionsResource(self._client)

    @cached_property
    def workspace(self) -> AsyncWorkspaceResource:
        return AsyncWorkspaceResource(self._client)

    @cached_property
    def budgets(self) -> AsyncBudgetsResource:
        return AsyncBudgetsResource(self._client)

    @cached_property
    def config(self) -> AsyncConfigResource:
        return AsyncConfigResource(self._client)

    @cached_property
    def events(self) -> AsyncEventsResource:
        return AsyncEventsResource(self._client)

    @cached_property
    def execute(self) -> AsyncExecuteResource:
        return AsyncExecuteResource(self._client)

    @cached_property
    def files(self) -> AsyncFilesResource:
        return AsyncFilesResource(self._client)

    @cached_property
    def tasks(self) -> AsyncTasksResource:
        return AsyncTasksResource(self._client)

    @cached_property
    def views(self) -> AsyncViewsResource:
        return AsyncViewsResource(self._client)

    @cached_property
    def webhooks(self) -> AsyncWebhooksResource:
        return AsyncWebhooksResource(self._client)

    @cached_property
    def with_raw_response(self) -> AsyncProjectsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/Synext-Solution/cnos-hub-gen-sdk-py#accessing-raw-response-data-eg-headers
        """
        return AsyncProjectsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncProjectsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/Synext-Solution/cnos-hub-gen-sdk-py#with_streaming_response
        """
        return AsyncProjectsResourceWithStreamingResponse(self)

    async def transaction(
        self,
        project_id: str,
        *,
        operations: Iterable[project_transaction_params.Operation],
        events: Iterable[project_transaction_params.Event] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ProjectTransactionResponse:
        """
        Execute a batch of collection and document mutations inside a hub transaction.

        Args:
          operations: Operations to execute atomically.

          events: Optional events to emit within the same transaction.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not project_id:
            raise ValueError(f"Expected a non-empty value for `project_id` but received {project_id!r}")
        return await self._post(
            f"/v1/projects/{project_id}/tx",
            body=await async_maybe_transform(
                {
                    "operations": operations,
                    "events": events,
                },
                project_transaction_params.ProjectTransactionParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ProjectTransactionResponse,
        )


class ProjectsResourceWithRawResponse:
    def __init__(self, projects: ProjectsResource) -> None:
        self._projects = projects

        self.transaction = to_raw_response_wrapper(
            projects.transaction,
        )

    @cached_property
    def collections(self) -> CollectionsResourceWithRawResponse:
        return CollectionsResourceWithRawResponse(self._projects.collections)

    @cached_property
    def workspace(self) -> WorkspaceResourceWithRawResponse:
        return WorkspaceResourceWithRawResponse(self._projects.workspace)

    @cached_property
    def budgets(self) -> BudgetsResourceWithRawResponse:
        return BudgetsResourceWithRawResponse(self._projects.budgets)

    @cached_property
    def config(self) -> ConfigResourceWithRawResponse:
        return ConfigResourceWithRawResponse(self._projects.config)

    @cached_property
    def events(self) -> EventsResourceWithRawResponse:
        return EventsResourceWithRawResponse(self._projects.events)

    @cached_property
    def execute(self) -> ExecuteResourceWithRawResponse:
        return ExecuteResourceWithRawResponse(self._projects.execute)

    @cached_property
    def files(self) -> FilesResourceWithRawResponse:
        return FilesResourceWithRawResponse(self._projects.files)

    @cached_property
    def tasks(self) -> TasksResourceWithRawResponse:
        return TasksResourceWithRawResponse(self._projects.tasks)

    @cached_property
    def views(self) -> ViewsResourceWithRawResponse:
        return ViewsResourceWithRawResponse(self._projects.views)

    @cached_property
    def webhooks(self) -> WebhooksResourceWithRawResponse:
        return WebhooksResourceWithRawResponse(self._projects.webhooks)


class AsyncProjectsResourceWithRawResponse:
    def __init__(self, projects: AsyncProjectsResource) -> None:
        self._projects = projects

        self.transaction = async_to_raw_response_wrapper(
            projects.transaction,
        )

    @cached_property
    def collections(self) -> AsyncCollectionsResourceWithRawResponse:
        return AsyncCollectionsResourceWithRawResponse(self._projects.collections)

    @cached_property
    def workspace(self) -> AsyncWorkspaceResourceWithRawResponse:
        return AsyncWorkspaceResourceWithRawResponse(self._projects.workspace)

    @cached_property
    def budgets(self) -> AsyncBudgetsResourceWithRawResponse:
        return AsyncBudgetsResourceWithRawResponse(self._projects.budgets)

    @cached_property
    def config(self) -> AsyncConfigResourceWithRawResponse:
        return AsyncConfigResourceWithRawResponse(self._projects.config)

    @cached_property
    def events(self) -> AsyncEventsResourceWithRawResponse:
        return AsyncEventsResourceWithRawResponse(self._projects.events)

    @cached_property
    def execute(self) -> AsyncExecuteResourceWithRawResponse:
        return AsyncExecuteResourceWithRawResponse(self._projects.execute)

    @cached_property
    def files(self) -> AsyncFilesResourceWithRawResponse:
        return AsyncFilesResourceWithRawResponse(self._projects.files)

    @cached_property
    def tasks(self) -> AsyncTasksResourceWithRawResponse:
        return AsyncTasksResourceWithRawResponse(self._projects.tasks)

    @cached_property
    def views(self) -> AsyncViewsResourceWithRawResponse:
        return AsyncViewsResourceWithRawResponse(self._projects.views)

    @cached_property
    def webhooks(self) -> AsyncWebhooksResourceWithRawResponse:
        return AsyncWebhooksResourceWithRawResponse(self._projects.webhooks)


class ProjectsResourceWithStreamingResponse:
    def __init__(self, projects: ProjectsResource) -> None:
        self._projects = projects

        self.transaction = to_streamed_response_wrapper(
            projects.transaction,
        )

    @cached_property
    def collections(self) -> CollectionsResourceWithStreamingResponse:
        return CollectionsResourceWithStreamingResponse(self._projects.collections)

    @cached_property
    def workspace(self) -> WorkspaceResourceWithStreamingResponse:
        return WorkspaceResourceWithStreamingResponse(self._projects.workspace)

    @cached_property
    def budgets(self) -> BudgetsResourceWithStreamingResponse:
        return BudgetsResourceWithStreamingResponse(self._projects.budgets)

    @cached_property
    def config(self) -> ConfigResourceWithStreamingResponse:
        return ConfigResourceWithStreamingResponse(self._projects.config)

    @cached_property
    def events(self) -> EventsResourceWithStreamingResponse:
        return EventsResourceWithStreamingResponse(self._projects.events)

    @cached_property
    def execute(self) -> ExecuteResourceWithStreamingResponse:
        return ExecuteResourceWithStreamingResponse(self._projects.execute)

    @cached_property
    def files(self) -> FilesResourceWithStreamingResponse:
        return FilesResourceWithStreamingResponse(self._projects.files)

    @cached_property
    def tasks(self) -> TasksResourceWithStreamingResponse:
        return TasksResourceWithStreamingResponse(self._projects.tasks)

    @cached_property
    def views(self) -> ViewsResourceWithStreamingResponse:
        return ViewsResourceWithStreamingResponse(self._projects.views)

    @cached_property
    def webhooks(self) -> WebhooksResourceWithStreamingResponse:
        return WebhooksResourceWithStreamingResponse(self._projects.webhooks)


class AsyncProjectsResourceWithStreamingResponse:
    def __init__(self, projects: AsyncProjectsResource) -> None:
        self._projects = projects

        self.transaction = async_to_streamed_response_wrapper(
            projects.transaction,
        )

    @cached_property
    def collections(self) -> AsyncCollectionsResourceWithStreamingResponse:
        return AsyncCollectionsResourceWithStreamingResponse(self._projects.collections)

    @cached_property
    def workspace(self) -> AsyncWorkspaceResourceWithStreamingResponse:
        return AsyncWorkspaceResourceWithStreamingResponse(self._projects.workspace)

    @cached_property
    def budgets(self) -> AsyncBudgetsResourceWithStreamingResponse:
        return AsyncBudgetsResourceWithStreamingResponse(self._projects.budgets)

    @cached_property
    def config(self) -> AsyncConfigResourceWithStreamingResponse:
        return AsyncConfigResourceWithStreamingResponse(self._projects.config)

    @cached_property
    def events(self) -> AsyncEventsResourceWithStreamingResponse:
        return AsyncEventsResourceWithStreamingResponse(self._projects.events)

    @cached_property
    def execute(self) -> AsyncExecuteResourceWithStreamingResponse:
        return AsyncExecuteResourceWithStreamingResponse(self._projects.execute)

    @cached_property
    def files(self) -> AsyncFilesResourceWithStreamingResponse:
        return AsyncFilesResourceWithStreamingResponse(self._projects.files)

    @cached_property
    def tasks(self) -> AsyncTasksResourceWithStreamingResponse:
        return AsyncTasksResourceWithStreamingResponse(self._projects.tasks)

    @cached_property
    def views(self) -> AsyncViewsResourceWithStreamingResponse:
        return AsyncViewsResourceWithStreamingResponse(self._projects.views)

    @cached_property
    def webhooks(self) -> AsyncWebhooksResourceWithStreamingResponse:
        return AsyncWebhooksResourceWithStreamingResponse(self._projects.webhooks)
