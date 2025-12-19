# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import httpx

from .._types import Body, Query, Headers, NotGiven, not_given
from .._compat import cached_property
from .._resource import SyncAPIResource, AsyncAPIResource
from .._response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from .._base_client import make_request_options
from ..types.meta_get_response import MetaGetResponse
from ..types.meta_endpoints_response import MetaEndpointsResponse
from ..types.meta_capabilities_response import MetaCapabilitiesResponse

__all__ = ["MetaResource", "AsyncMetaResource"]


class MetaResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> MetaResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/Synext-Solution/cnos-hub-gen-sdk-py#accessing-raw-response-data-eg-headers
        """
        return MetaResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> MetaResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/Synext-Solution/cnos-hub-gen-sdk-py#with_streaming_response
        """
        return MetaResourceWithStreamingResponse(self)

    def capabilities(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> MetaCapabilitiesResponse:
        """Return the list of available capabilities."""
        return self._get(
            "/v1/meta/capabilities",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=MetaCapabilitiesResponse,
        )

    def endpoints(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> MetaEndpointsResponse:
        """Return the endpoint capability mapping (platform admin only)."""
        return self._get(
            "/v1/meta/endpoints",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=MetaEndpointsResponse,
        )

    def get(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> MetaGetResponse:
        """Return basic service metadata and enabled features."""
        return self._get(
            "/v1/meta",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=MetaGetResponse,
        )


class AsyncMetaResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncMetaResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/Synext-Solution/cnos-hub-gen-sdk-py#accessing-raw-response-data-eg-headers
        """
        return AsyncMetaResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncMetaResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/Synext-Solution/cnos-hub-gen-sdk-py#with_streaming_response
        """
        return AsyncMetaResourceWithStreamingResponse(self)

    async def capabilities(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> MetaCapabilitiesResponse:
        """Return the list of available capabilities."""
        return await self._get(
            "/v1/meta/capabilities",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=MetaCapabilitiesResponse,
        )

    async def endpoints(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> MetaEndpointsResponse:
        """Return the endpoint capability mapping (platform admin only)."""
        return await self._get(
            "/v1/meta/endpoints",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=MetaEndpointsResponse,
        )

    async def get(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> MetaGetResponse:
        """Return basic service metadata and enabled features."""
        return await self._get(
            "/v1/meta",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=MetaGetResponse,
        )


class MetaResourceWithRawResponse:
    def __init__(self, meta: MetaResource) -> None:
        self._meta = meta

        self.capabilities = to_raw_response_wrapper(
            meta.capabilities,
        )
        self.endpoints = to_raw_response_wrapper(
            meta.endpoints,
        )
        self.get = to_raw_response_wrapper(
            meta.get,
        )


class AsyncMetaResourceWithRawResponse:
    def __init__(self, meta: AsyncMetaResource) -> None:
        self._meta = meta

        self.capabilities = async_to_raw_response_wrapper(
            meta.capabilities,
        )
        self.endpoints = async_to_raw_response_wrapper(
            meta.endpoints,
        )
        self.get = async_to_raw_response_wrapper(
            meta.get,
        )


class MetaResourceWithStreamingResponse:
    def __init__(self, meta: MetaResource) -> None:
        self._meta = meta

        self.capabilities = to_streamed_response_wrapper(
            meta.capabilities,
        )
        self.endpoints = to_streamed_response_wrapper(
            meta.endpoints,
        )
        self.get = to_streamed_response_wrapper(
            meta.get,
        )


class AsyncMetaResourceWithStreamingResponse:
    def __init__(self, meta: AsyncMetaResource) -> None:
        self._meta = meta

        self.capabilities = async_to_streamed_response_wrapper(
            meta.capabilities,
        )
        self.endpoints = async_to_streamed_response_wrapper(
            meta.endpoints,
        )
        self.get = async_to_streamed_response_wrapper(
            meta.get,
        )
