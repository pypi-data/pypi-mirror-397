# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Optional
from typing_extensions import Literal

import httpx

from ...._types import Body, Omit, Query, Headers, NoneType, NotGiven, SequenceNotStr, omit, not_given
from ...._utils import maybe_transform, async_maybe_transform
from ...._compat import cached_property
from ...._resource import SyncAPIResource, AsyncAPIResource
from ...._response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from ...._base_client import make_request_options
from ....types.projects.views import view_update_params
from ....types.projects.views.view_update_response import ViewUpdateResponse
from ....types.projects.views.view_retrieve_response import ViewRetrieveResponse

__all__ = ["ViewResource", "AsyncViewResource"]


class ViewResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> ViewResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/Synext-Solution/cnos-hub-gen-sdk-py#accessing-raw-response-data-eg-headers
        """
        return ViewResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> ViewResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/Synext-Solution/cnos-hub-gen-sdk-py#with_streaming_response
        """
        return ViewResourceWithStreamingResponse(self)

    def retrieve(
        self,
        view_name: str,
        *,
        project_id: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ViewRetrieveResponse:
        """
        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not project_id:
            raise ValueError(f"Expected a non-empty value for `project_id` but received {project_id!r}")
        if not view_name:
            raise ValueError(f"Expected a non-empty value for `view_name` but received {view_name!r}")
        return self._get(
            f"/v1/projects/{project_id}/views/{view_name}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ViewRetrieveResponse,
        )

    def update(
        self,
        view_name: str,
        *,
        project_id: str,
        allowed_labels: Optional[SequenceNotStr[str]] | Omit = omit,
        allowed_roles: Optional[SequenceNotStr[str]] | Omit = omit,
        description: Optional[str] | Omit = omit,
        status: Optional[Literal["active", "disabled", "deleted"]] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ViewUpdateResponse:
        """
        Args:
          allowed_labels: Updated allowed labels.

          allowed_roles: Updated allowed roles.

          description: Updated description.

          status: Updated status.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not project_id:
            raise ValueError(f"Expected a non-empty value for `project_id` but received {project_id!r}")
        if not view_name:
            raise ValueError(f"Expected a non-empty value for `view_name` but received {view_name!r}")
        return self._patch(
            f"/v1/projects/{project_id}/views/{view_name}",
            body=maybe_transform(
                {
                    "allowed_labels": allowed_labels,
                    "allowed_roles": allowed_roles,
                    "description": description,
                    "status": status,
                },
                view_update_params.ViewUpdateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ViewUpdateResponse,
        )

    def delete(
        self,
        view_name: str,
        *,
        project_id: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> None:
        """
        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not project_id:
            raise ValueError(f"Expected a non-empty value for `project_id` but received {project_id!r}")
        if not view_name:
            raise ValueError(f"Expected a non-empty value for `view_name` but received {view_name!r}")
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        return self._delete(
            f"/v1/projects/{project_id}/views/{view_name}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=NoneType,
        )


class AsyncViewResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncViewResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/Synext-Solution/cnos-hub-gen-sdk-py#accessing-raw-response-data-eg-headers
        """
        return AsyncViewResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncViewResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/Synext-Solution/cnos-hub-gen-sdk-py#with_streaming_response
        """
        return AsyncViewResourceWithStreamingResponse(self)

    async def retrieve(
        self,
        view_name: str,
        *,
        project_id: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ViewRetrieveResponse:
        """
        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not project_id:
            raise ValueError(f"Expected a non-empty value for `project_id` but received {project_id!r}")
        if not view_name:
            raise ValueError(f"Expected a non-empty value for `view_name` but received {view_name!r}")
        return await self._get(
            f"/v1/projects/{project_id}/views/{view_name}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ViewRetrieveResponse,
        )

    async def update(
        self,
        view_name: str,
        *,
        project_id: str,
        allowed_labels: Optional[SequenceNotStr[str]] | Omit = omit,
        allowed_roles: Optional[SequenceNotStr[str]] | Omit = omit,
        description: Optional[str] | Omit = omit,
        status: Optional[Literal["active", "disabled", "deleted"]] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ViewUpdateResponse:
        """
        Args:
          allowed_labels: Updated allowed labels.

          allowed_roles: Updated allowed roles.

          description: Updated description.

          status: Updated status.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not project_id:
            raise ValueError(f"Expected a non-empty value for `project_id` but received {project_id!r}")
        if not view_name:
            raise ValueError(f"Expected a non-empty value for `view_name` but received {view_name!r}")
        return await self._patch(
            f"/v1/projects/{project_id}/views/{view_name}",
            body=await async_maybe_transform(
                {
                    "allowed_labels": allowed_labels,
                    "allowed_roles": allowed_roles,
                    "description": description,
                    "status": status,
                },
                view_update_params.ViewUpdateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ViewUpdateResponse,
        )

    async def delete(
        self,
        view_name: str,
        *,
        project_id: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> None:
        """
        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not project_id:
            raise ValueError(f"Expected a non-empty value for `project_id` but received {project_id!r}")
        if not view_name:
            raise ValueError(f"Expected a non-empty value for `view_name` but received {view_name!r}")
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        return await self._delete(
            f"/v1/projects/{project_id}/views/{view_name}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=NoneType,
        )


class ViewResourceWithRawResponse:
    def __init__(self, view: ViewResource) -> None:
        self._view = view

        self.retrieve = to_raw_response_wrapper(
            view.retrieve,
        )
        self.update = to_raw_response_wrapper(
            view.update,
        )
        self.delete = to_raw_response_wrapper(
            view.delete,
        )


class AsyncViewResourceWithRawResponse:
    def __init__(self, view: AsyncViewResource) -> None:
        self._view = view

        self.retrieve = async_to_raw_response_wrapper(
            view.retrieve,
        )
        self.update = async_to_raw_response_wrapper(
            view.update,
        )
        self.delete = async_to_raw_response_wrapper(
            view.delete,
        )


class ViewResourceWithStreamingResponse:
    def __init__(self, view: ViewResource) -> None:
        self._view = view

        self.retrieve = to_streamed_response_wrapper(
            view.retrieve,
        )
        self.update = to_streamed_response_wrapper(
            view.update,
        )
        self.delete = to_streamed_response_wrapper(
            view.delete,
        )


class AsyncViewResourceWithStreamingResponse:
    def __init__(self, view: AsyncViewResource) -> None:
        self._view = view

        self.retrieve = async_to_streamed_response_wrapper(
            view.retrieve,
        )
        self.update = async_to_streamed_response_wrapper(
            view.update,
        )
        self.delete = async_to_streamed_response_wrapper(
            view.delete,
        )
