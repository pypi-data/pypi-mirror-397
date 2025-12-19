# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Optional
from typing_extensions import Literal

import httpx

from .view import (
    ViewResource,
    AsyncViewResource,
    ViewResourceWithRawResponse,
    AsyncViewResourceWithRawResponse,
    ViewResourceWithStreamingResponse,
    AsyncViewResourceWithStreamingResponse,
)
from ...._types import Body, Omit, Query, Headers, NotGiven, SequenceNotStr, omit, not_given
from ...._utils import maybe_transform, async_maybe_transform
from ...._compat import cached_property
from ...._resource import SyncAPIResource, AsyncAPIResource
from ...._response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from ....pagination import SyncPage, AsyncPage
from ...._base_client import AsyncPaginator, make_request_options
from ....types.projects import view_list_params, view_create_params
from ....types.projects.view_list_response import ViewListResponse
from ....types.projects.view_create_response import ViewCreateResponse

__all__ = ["ViewsResource", "AsyncViewsResource"]


class ViewsResource(SyncAPIResource):
    @cached_property
    def view(self) -> ViewResource:
        return ViewResource(self._client)

    @cached_property
    def with_raw_response(self) -> ViewsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/Synext-Solution/cnos-hub-gen-sdk-py#accessing-raw-response-data-eg-headers
        """
        return ViewsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> ViewsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/Synext-Solution/cnos-hub-gen-sdk-py#with_streaming_response
        """
        return ViewsResourceWithStreamingResponse(self)

    def create(
        self,
        project_id: str,
        *,
        function_name: str,
        module_path: str,
        name: str,
        allowed_labels: SequenceNotStr[str] | Omit = omit,
        allowed_roles: SequenceNotStr[str] | Omit = omit,
        description: Optional[str] | Omit = omit,
        security_mode: Literal["definer", "invoker"] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ViewCreateResponse:
        """
        Args:
          function_name: Target function name.

          module_path: Target CNOS module path.

          name: Human-readable name (unique within project).

          allowed_labels: Labels allowed to execute.

          allowed_roles: Roles allowed to execute.

          description: Optional description.

          security_mode: Security mode: "definer" or "invoker".

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not project_id:
            raise ValueError(f"Expected a non-empty value for `project_id` but received {project_id!r}")
        return self._post(
            f"/v1/projects/{project_id}/views",
            body=maybe_transform(
                {
                    "function_name": function_name,
                    "module_path": module_path,
                    "name": name,
                    "allowed_labels": allowed_labels,
                    "allowed_roles": allowed_roles,
                    "description": description,
                    "security_mode": security_mode,
                },
                view_create_params.ViewCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ViewCreateResponse,
        )

    def list(
        self,
        project_id: str,
        *,
        cursor: str | Omit = omit,
        limit: int | Omit = omit,
        status: Literal["active", "disabled", "deleted"] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> SyncPage[ViewListResponse]:
        """
        Args:
          cursor: Pagination cursor.

          limit: Maximum items to return.

          status: Optional status filter.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not project_id:
            raise ValueError(f"Expected a non-empty value for `project_id` but received {project_id!r}")
        return self._get_api_list(
            f"/v1/projects/{project_id}/views",
            page=SyncPage[ViewListResponse],
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "cursor": cursor,
                        "limit": limit,
                        "status": status,
                    },
                    view_list_params.ViewListParams,
                ),
            ),
            model=ViewListResponse,
        )


class AsyncViewsResource(AsyncAPIResource):
    @cached_property
    def view(self) -> AsyncViewResource:
        return AsyncViewResource(self._client)

    @cached_property
    def with_raw_response(self) -> AsyncViewsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/Synext-Solution/cnos-hub-gen-sdk-py#accessing-raw-response-data-eg-headers
        """
        return AsyncViewsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncViewsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/Synext-Solution/cnos-hub-gen-sdk-py#with_streaming_response
        """
        return AsyncViewsResourceWithStreamingResponse(self)

    async def create(
        self,
        project_id: str,
        *,
        function_name: str,
        module_path: str,
        name: str,
        allowed_labels: SequenceNotStr[str] | Omit = omit,
        allowed_roles: SequenceNotStr[str] | Omit = omit,
        description: Optional[str] | Omit = omit,
        security_mode: Literal["definer", "invoker"] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ViewCreateResponse:
        """
        Args:
          function_name: Target function name.

          module_path: Target CNOS module path.

          name: Human-readable name (unique within project).

          allowed_labels: Labels allowed to execute.

          allowed_roles: Roles allowed to execute.

          description: Optional description.

          security_mode: Security mode: "definer" or "invoker".

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not project_id:
            raise ValueError(f"Expected a non-empty value for `project_id` but received {project_id!r}")
        return await self._post(
            f"/v1/projects/{project_id}/views",
            body=await async_maybe_transform(
                {
                    "function_name": function_name,
                    "module_path": module_path,
                    "name": name,
                    "allowed_labels": allowed_labels,
                    "allowed_roles": allowed_roles,
                    "description": description,
                    "security_mode": security_mode,
                },
                view_create_params.ViewCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ViewCreateResponse,
        )

    def list(
        self,
        project_id: str,
        *,
        cursor: str | Omit = omit,
        limit: int | Omit = omit,
        status: Literal["active", "disabled", "deleted"] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> AsyncPaginator[ViewListResponse, AsyncPage[ViewListResponse]]:
        """
        Args:
          cursor: Pagination cursor.

          limit: Maximum items to return.

          status: Optional status filter.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not project_id:
            raise ValueError(f"Expected a non-empty value for `project_id` but received {project_id!r}")
        return self._get_api_list(
            f"/v1/projects/{project_id}/views",
            page=AsyncPage[ViewListResponse],
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "cursor": cursor,
                        "limit": limit,
                        "status": status,
                    },
                    view_list_params.ViewListParams,
                ),
            ),
            model=ViewListResponse,
        )


class ViewsResourceWithRawResponse:
    def __init__(self, views: ViewsResource) -> None:
        self._views = views

        self.create = to_raw_response_wrapper(
            views.create,
        )
        self.list = to_raw_response_wrapper(
            views.list,
        )

    @cached_property
    def view(self) -> ViewResourceWithRawResponse:
        return ViewResourceWithRawResponse(self._views.view)


class AsyncViewsResourceWithRawResponse:
    def __init__(self, views: AsyncViewsResource) -> None:
        self._views = views

        self.create = async_to_raw_response_wrapper(
            views.create,
        )
        self.list = async_to_raw_response_wrapper(
            views.list,
        )

    @cached_property
    def view(self) -> AsyncViewResourceWithRawResponse:
        return AsyncViewResourceWithRawResponse(self._views.view)


class ViewsResourceWithStreamingResponse:
    def __init__(self, views: ViewsResource) -> None:
        self._views = views

        self.create = to_streamed_response_wrapper(
            views.create,
        )
        self.list = to_streamed_response_wrapper(
            views.list,
        )

    @cached_property
    def view(self) -> ViewResourceWithStreamingResponse:
        return ViewResourceWithStreamingResponse(self._views.view)


class AsyncViewsResourceWithStreamingResponse:
    def __init__(self, views: AsyncViewsResource) -> None:
        self._views = views

        self.create = async_to_streamed_response_wrapper(
            views.create,
        )
        self.list = async_to_streamed_response_wrapper(
            views.list,
        )

    @cached_property
    def view(self) -> AsyncViewResourceWithStreamingResponse:
        return AsyncViewResourceWithStreamingResponse(self._views.view)
