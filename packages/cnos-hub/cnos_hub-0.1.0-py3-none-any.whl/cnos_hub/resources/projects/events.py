# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Dict, Optional
from typing_extensions import Literal

import httpx

from ..._types import Body, Omit, Query, Headers, NoneType, NotGiven, omit, not_given
from ..._utils import maybe_transform, async_maybe_transform
from ..._compat import cached_property
from ..._resource import SyncAPIResource, AsyncAPIResource
from ..._response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from ...pagination import SyncPage, AsyncPage
from ..._base_client import AsyncPaginator, make_request_options
from ...types.projects import event_list_params, event_create_params
from ...types.projects.event_list_response import EventListResponse
from ...types.projects.event_retry_response import EventRetryResponse
from ...types.projects.event_create_response import EventCreateResponse
from ...types.projects.event_retrieve_response import EventRetrieveResponse

__all__ = ["EventsResource", "AsyncEventsResource"]


class EventsResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> EventsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/Synext-Solution/cnos-hub-gen-sdk-py#accessing-raw-response-data-eg-headers
        """
        return EventsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> EventsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/Synext-Solution/cnos-hub-gen-sdk-py#with_streaming_response
        """
        return EventsResourceWithStreamingResponse(self)

    def create(
        self,
        project_id: str,
        *,
        type: str,
        key: Optional[str] | Omit = omit,
        meta: Dict[str, object] | Omit = omit,
        payload: Dict[str, object] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> EventCreateResponse:
        """
        Emit a custom event into the project's queue.

        Args:
          type: Event type (e.g., `cnos.custom.example`).

          key: Optional partitioning key for deduplication.

          meta: Additional metadata merged with org/project identifiers.

          payload: Event payload.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not project_id:
            raise ValueError(f"Expected a non-empty value for `project_id` but received {project_id!r}")
        return self._post(
            f"/v1/projects/{project_id}/events",
            body=maybe_transform(
                {
                    "type": type,
                    "key": key,
                    "meta": meta,
                    "payload": payload,
                },
                event_create_params.EventCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=EventCreateResponse,
        )

    def retrieve(
        self,
        event_id: str,
        *,
        project_id: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> EventRetrieveResponse:
        """
        Get a single event by ID.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not project_id:
            raise ValueError(f"Expected a non-empty value for `project_id` but received {project_id!r}")
        if not event_id:
            raise ValueError(f"Expected a non-empty value for `event_id` but received {event_id!r}")
        return self._get(
            f"/v1/projects/{project_id}/events/{event_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=EventRetrieveResponse,
        )

    def list(
        self,
        project_id: str,
        *,
        cursor: str | Omit = omit,
        limit: int | Omit = omit,
        status: Literal["pending", "processing", "succeeded", "failed", "dead_letter"] | Omit = omit,
        type: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> SyncPage[EventListResponse]:
        """
        List events for a project.

        Args:
          cursor: Pagination cursor.

          limit: Maximum items to return.

          status: Optional status filter.

          type: Optional type filter.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not project_id:
            raise ValueError(f"Expected a non-empty value for `project_id` but received {project_id!r}")
        return self._get_api_list(
            f"/v1/projects/{project_id}/events",
            page=SyncPage[EventListResponse],
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
                        "type": type,
                    },
                    event_list_params.EventListParams,
                ),
            ),
            model=EventListResponse,
        )

    def drop(
        self,
        event_id: str,
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
        Drop (cancel) an event.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not project_id:
            raise ValueError(f"Expected a non-empty value for `project_id` but received {project_id!r}")
        if not event_id:
            raise ValueError(f"Expected a non-empty value for `event_id` but received {event_id!r}")
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        return self._post(
            f"/v1/projects/{project_id}/events/{event_id}/drop",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=NoneType,
        )

    def retry(
        self,
        event_id: str,
        *,
        project_id: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> EventRetryResponse:
        """
        Retry a failed event.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not project_id:
            raise ValueError(f"Expected a non-empty value for `project_id` but received {project_id!r}")
        if not event_id:
            raise ValueError(f"Expected a non-empty value for `event_id` but received {event_id!r}")
        return self._post(
            f"/v1/projects/{project_id}/events/{event_id}/retry",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=EventRetryResponse,
        )


class AsyncEventsResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncEventsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/Synext-Solution/cnos-hub-gen-sdk-py#accessing-raw-response-data-eg-headers
        """
        return AsyncEventsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncEventsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/Synext-Solution/cnos-hub-gen-sdk-py#with_streaming_response
        """
        return AsyncEventsResourceWithStreamingResponse(self)

    async def create(
        self,
        project_id: str,
        *,
        type: str,
        key: Optional[str] | Omit = omit,
        meta: Dict[str, object] | Omit = omit,
        payload: Dict[str, object] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> EventCreateResponse:
        """
        Emit a custom event into the project's queue.

        Args:
          type: Event type (e.g., `cnos.custom.example`).

          key: Optional partitioning key for deduplication.

          meta: Additional metadata merged with org/project identifiers.

          payload: Event payload.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not project_id:
            raise ValueError(f"Expected a non-empty value for `project_id` but received {project_id!r}")
        return await self._post(
            f"/v1/projects/{project_id}/events",
            body=await async_maybe_transform(
                {
                    "type": type,
                    "key": key,
                    "meta": meta,
                    "payload": payload,
                },
                event_create_params.EventCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=EventCreateResponse,
        )

    async def retrieve(
        self,
        event_id: str,
        *,
        project_id: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> EventRetrieveResponse:
        """
        Get a single event by ID.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not project_id:
            raise ValueError(f"Expected a non-empty value for `project_id` but received {project_id!r}")
        if not event_id:
            raise ValueError(f"Expected a non-empty value for `event_id` but received {event_id!r}")
        return await self._get(
            f"/v1/projects/{project_id}/events/{event_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=EventRetrieveResponse,
        )

    def list(
        self,
        project_id: str,
        *,
        cursor: str | Omit = omit,
        limit: int | Omit = omit,
        status: Literal["pending", "processing", "succeeded", "failed", "dead_letter"] | Omit = omit,
        type: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> AsyncPaginator[EventListResponse, AsyncPage[EventListResponse]]:
        """
        List events for a project.

        Args:
          cursor: Pagination cursor.

          limit: Maximum items to return.

          status: Optional status filter.

          type: Optional type filter.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not project_id:
            raise ValueError(f"Expected a non-empty value for `project_id` but received {project_id!r}")
        return self._get_api_list(
            f"/v1/projects/{project_id}/events",
            page=AsyncPage[EventListResponse],
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
                        "type": type,
                    },
                    event_list_params.EventListParams,
                ),
            ),
            model=EventListResponse,
        )

    async def drop(
        self,
        event_id: str,
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
        Drop (cancel) an event.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not project_id:
            raise ValueError(f"Expected a non-empty value for `project_id` but received {project_id!r}")
        if not event_id:
            raise ValueError(f"Expected a non-empty value for `event_id` but received {event_id!r}")
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        return await self._post(
            f"/v1/projects/{project_id}/events/{event_id}/drop",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=NoneType,
        )

    async def retry(
        self,
        event_id: str,
        *,
        project_id: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> EventRetryResponse:
        """
        Retry a failed event.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not project_id:
            raise ValueError(f"Expected a non-empty value for `project_id` but received {project_id!r}")
        if not event_id:
            raise ValueError(f"Expected a non-empty value for `event_id` but received {event_id!r}")
        return await self._post(
            f"/v1/projects/{project_id}/events/{event_id}/retry",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=EventRetryResponse,
        )


class EventsResourceWithRawResponse:
    def __init__(self, events: EventsResource) -> None:
        self._events = events

        self.create = to_raw_response_wrapper(
            events.create,
        )
        self.retrieve = to_raw_response_wrapper(
            events.retrieve,
        )
        self.list = to_raw_response_wrapper(
            events.list,
        )
        self.drop = to_raw_response_wrapper(
            events.drop,
        )
        self.retry = to_raw_response_wrapper(
            events.retry,
        )


class AsyncEventsResourceWithRawResponse:
    def __init__(self, events: AsyncEventsResource) -> None:
        self._events = events

        self.create = async_to_raw_response_wrapper(
            events.create,
        )
        self.retrieve = async_to_raw_response_wrapper(
            events.retrieve,
        )
        self.list = async_to_raw_response_wrapper(
            events.list,
        )
        self.drop = async_to_raw_response_wrapper(
            events.drop,
        )
        self.retry = async_to_raw_response_wrapper(
            events.retry,
        )


class EventsResourceWithStreamingResponse:
    def __init__(self, events: EventsResource) -> None:
        self._events = events

        self.create = to_streamed_response_wrapper(
            events.create,
        )
        self.retrieve = to_streamed_response_wrapper(
            events.retrieve,
        )
        self.list = to_streamed_response_wrapper(
            events.list,
        )
        self.drop = to_streamed_response_wrapper(
            events.drop,
        )
        self.retry = to_streamed_response_wrapper(
            events.retry,
        )


class AsyncEventsResourceWithStreamingResponse:
    def __init__(self, events: AsyncEventsResource) -> None:
        self._events = events

        self.create = async_to_streamed_response_wrapper(
            events.create,
        )
        self.retrieve = async_to_streamed_response_wrapper(
            events.retrieve,
        )
        self.list = async_to_streamed_response_wrapper(
            events.list,
        )
        self.drop = async_to_streamed_response_wrapper(
            events.drop,
        )
        self.retry = async_to_streamed_response_wrapper(
            events.retry,
        )
