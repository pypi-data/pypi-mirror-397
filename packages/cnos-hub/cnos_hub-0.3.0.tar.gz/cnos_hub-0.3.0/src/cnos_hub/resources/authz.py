# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Iterable

import httpx

from ..types import authz_test_params
from .._types import Body, Query, Headers, NotGiven, not_given
from .._utils import maybe_transform, async_maybe_transform
from .._compat import cached_property
from .._resource import SyncAPIResource, AsyncAPIResource
from .._response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from .._base_client import make_request_options
from ..types.authz_test_response import AuthzTestResponse

__all__ = ["AuthzResource", "AsyncAuthzResource"]


class AuthzResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AuthzResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/Synext-Solution/cnos-hub-gen-sdk-py#accessing-raw-response-data-eg-headers
        """
        return AuthzResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AuthzResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/Synext-Solution/cnos-hub-gen-sdk-py#with_streaming_response
        """
        return AuthzResourceWithStreamingResponse(self)

    def test(
        self,
        *,
        resources: Iterable[authz_test_params.Resource],
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> AuthzTestResponse:
        """
        Test authorization for a list of resources/actions.

        Args:
          resources: Resources to test.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/v1/authorize-test",
            body=maybe_transform({"resources": resources}, authz_test_params.AuthzTestParams),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=AuthzTestResponse,
        )


class AsyncAuthzResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncAuthzResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/Synext-Solution/cnos-hub-gen-sdk-py#accessing-raw-response-data-eg-headers
        """
        return AsyncAuthzResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncAuthzResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/Synext-Solution/cnos-hub-gen-sdk-py#with_streaming_response
        """
        return AsyncAuthzResourceWithStreamingResponse(self)

    async def test(
        self,
        *,
        resources: Iterable[authz_test_params.Resource],
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> AuthzTestResponse:
        """
        Test authorization for a list of resources/actions.

        Args:
          resources: Resources to test.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/v1/authorize-test",
            body=await async_maybe_transform({"resources": resources}, authz_test_params.AuthzTestParams),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=AuthzTestResponse,
        )


class AuthzResourceWithRawResponse:
    def __init__(self, authz: AuthzResource) -> None:
        self._authz = authz

        self.test = to_raw_response_wrapper(
            authz.test,
        )


class AsyncAuthzResourceWithRawResponse:
    def __init__(self, authz: AsyncAuthzResource) -> None:
        self._authz = authz

        self.test = async_to_raw_response_wrapper(
            authz.test,
        )


class AuthzResourceWithStreamingResponse:
    def __init__(self, authz: AuthzResource) -> None:
        self._authz = authz

        self.test = to_streamed_response_wrapper(
            authz.test,
        )


class AsyncAuthzResourceWithStreamingResponse:
    def __init__(self, authz: AsyncAuthzResource) -> None:
        self._authz = authz

        self.test = async_to_streamed_response_wrapper(
            authz.test,
        )
