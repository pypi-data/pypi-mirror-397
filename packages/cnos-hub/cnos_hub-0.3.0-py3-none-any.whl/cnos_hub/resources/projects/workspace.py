# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Iterable

import httpx

from ..._types import Body, Query, Headers, NotGiven, not_given
from ..._utils import maybe_transform, async_maybe_transform
from ..._compat import cached_property
from ..._resource import SyncAPIResource, AsyncAPIResource
from ..._response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from ..._base_client import make_request_options
from ...types.projects import workspace_check_params, workspace_patch_params, workspace_retrieve_file_params
from ...types.projects.workspace_list_response import WorkspaceListResponse
from ...types.projects.workspace_check_response import WorkspaceCheckResponse
from ...types.projects.workspace_patch_response import WorkspacePatchResponse
from ...types.projects.workspace_retrieve_file_response import WorkspaceRetrieveFileResponse

__all__ = ["WorkspaceResource", "AsyncWorkspaceResource"]


class WorkspaceResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> WorkspaceResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/Synext-Solution/cnos-hub-gen-sdk-py#accessing-raw-response-data-eg-headers
        """
        return WorkspaceResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> WorkspaceResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/Synext-Solution/cnos-hub-gen-sdk-py#with_streaming_response
        """
        return WorkspaceResourceWithStreamingResponse(self)

    def list(
        self,
        project_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> WorkspaceListResponse:
        """
        List workspace files (metadata only).

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not project_id:
            raise ValueError(f"Expected a non-empty value for `project_id` but received {project_id!r}")
        return self._get(
            f"/v1/projects/{project_id}/workspace",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=WorkspaceListResponse,
        )

    def check(
        self,
        project_id: str,
        *,
        changes: Iterable[workspace_check_params.Change],
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> WorkspaceCheckResponse:
        """
        Dry-run validation for workspace changes.

        Args:
          changes: Set of file changes to validate.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not project_id:
            raise ValueError(f"Expected a non-empty value for `project_id` but received {project_id!r}")
        return self._post(
            f"/v1/projects/{project_id}/workspace/check",
            body=maybe_transform({"changes": changes}, workspace_check_params.WorkspaceCheckParams),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=WorkspaceCheckResponse,
        )

    def patch(
        self,
        project_id: str,
        *,
        changes: Iterable[workspace_patch_params.Change],
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> WorkspacePatchResponse:
        """
        Atomically apply and validate workspace changes.

        Args:
          changes: Set of file changes to apply atomically.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not project_id:
            raise ValueError(f"Expected a non-empty value for `project_id` but received {project_id!r}")
        return self._post(
            f"/v1/projects/{project_id}/workspace/patch",
            body=maybe_transform({"changes": changes}, workspace_patch_params.WorkspacePatchParams),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=WorkspacePatchResponse,
        )

    def retrieve_file(
        self,
        project_id: str,
        *,
        path: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> WorkspaceRetrieveFileResponse:
        """
        Fetch a workspace file by path.

        Args:
          path: Workspace file path

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not project_id:
            raise ValueError(f"Expected a non-empty value for `project_id` but received {project_id!r}")
        return self._get(
            f"/v1/projects/{project_id}/workspace/file",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform({"path": path}, workspace_retrieve_file_params.WorkspaceRetrieveFileParams),
            ),
            cast_to=WorkspaceRetrieveFileResponse,
        )


class AsyncWorkspaceResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncWorkspaceResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/Synext-Solution/cnos-hub-gen-sdk-py#accessing-raw-response-data-eg-headers
        """
        return AsyncWorkspaceResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncWorkspaceResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/Synext-Solution/cnos-hub-gen-sdk-py#with_streaming_response
        """
        return AsyncWorkspaceResourceWithStreamingResponse(self)

    async def list(
        self,
        project_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> WorkspaceListResponse:
        """
        List workspace files (metadata only).

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not project_id:
            raise ValueError(f"Expected a non-empty value for `project_id` but received {project_id!r}")
        return await self._get(
            f"/v1/projects/{project_id}/workspace",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=WorkspaceListResponse,
        )

    async def check(
        self,
        project_id: str,
        *,
        changes: Iterable[workspace_check_params.Change],
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> WorkspaceCheckResponse:
        """
        Dry-run validation for workspace changes.

        Args:
          changes: Set of file changes to validate.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not project_id:
            raise ValueError(f"Expected a non-empty value for `project_id` but received {project_id!r}")
        return await self._post(
            f"/v1/projects/{project_id}/workspace/check",
            body=await async_maybe_transform({"changes": changes}, workspace_check_params.WorkspaceCheckParams),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=WorkspaceCheckResponse,
        )

    async def patch(
        self,
        project_id: str,
        *,
        changes: Iterable[workspace_patch_params.Change],
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> WorkspacePatchResponse:
        """
        Atomically apply and validate workspace changes.

        Args:
          changes: Set of file changes to apply atomically.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not project_id:
            raise ValueError(f"Expected a non-empty value for `project_id` but received {project_id!r}")
        return await self._post(
            f"/v1/projects/{project_id}/workspace/patch",
            body=await async_maybe_transform({"changes": changes}, workspace_patch_params.WorkspacePatchParams),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=WorkspacePatchResponse,
        )

    async def retrieve_file(
        self,
        project_id: str,
        *,
        path: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> WorkspaceRetrieveFileResponse:
        """
        Fetch a workspace file by path.

        Args:
          path: Workspace file path

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not project_id:
            raise ValueError(f"Expected a non-empty value for `project_id` but received {project_id!r}")
        return await self._get(
            f"/v1/projects/{project_id}/workspace/file",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {"path": path}, workspace_retrieve_file_params.WorkspaceRetrieveFileParams
                ),
            ),
            cast_to=WorkspaceRetrieveFileResponse,
        )


class WorkspaceResourceWithRawResponse:
    def __init__(self, workspace: WorkspaceResource) -> None:
        self._workspace = workspace

        self.list = to_raw_response_wrapper(
            workspace.list,
        )
        self.check = to_raw_response_wrapper(
            workspace.check,
        )
        self.patch = to_raw_response_wrapper(
            workspace.patch,
        )
        self.retrieve_file = to_raw_response_wrapper(
            workspace.retrieve_file,
        )


class AsyncWorkspaceResourceWithRawResponse:
    def __init__(self, workspace: AsyncWorkspaceResource) -> None:
        self._workspace = workspace

        self.list = async_to_raw_response_wrapper(
            workspace.list,
        )
        self.check = async_to_raw_response_wrapper(
            workspace.check,
        )
        self.patch = async_to_raw_response_wrapper(
            workspace.patch,
        )
        self.retrieve_file = async_to_raw_response_wrapper(
            workspace.retrieve_file,
        )


class WorkspaceResourceWithStreamingResponse:
    def __init__(self, workspace: WorkspaceResource) -> None:
        self._workspace = workspace

        self.list = to_streamed_response_wrapper(
            workspace.list,
        )
        self.check = to_streamed_response_wrapper(
            workspace.check,
        )
        self.patch = to_streamed_response_wrapper(
            workspace.patch,
        )
        self.retrieve_file = to_streamed_response_wrapper(
            workspace.retrieve_file,
        )


class AsyncWorkspaceResourceWithStreamingResponse:
    def __init__(self, workspace: AsyncWorkspaceResource) -> None:
        self._workspace = workspace

        self.list = async_to_streamed_response_wrapper(
            workspace.list,
        )
        self.check = async_to_streamed_response_wrapper(
            workspace.check,
        )
        self.patch = async_to_streamed_response_wrapper(
            workspace.patch,
        )
        self.retrieve_file = async_to_streamed_response_wrapper(
            workspace.retrieve_file,
        )
