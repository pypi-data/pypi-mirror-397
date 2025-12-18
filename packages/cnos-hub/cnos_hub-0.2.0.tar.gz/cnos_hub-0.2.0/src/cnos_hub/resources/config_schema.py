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
from ..types.config_schema_org_response import ConfigSchemaOrgResponse
from ..types.config_schema_system_response import ConfigSchemaSystemResponse
from ..types.config_schema_project_response import ConfigSchemaProjectResponse

__all__ = ["ConfigSchemaResource", "AsyncConfigSchemaResource"]


class ConfigSchemaResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> ConfigSchemaResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/Synext-Solution/cnos-hub-gen-sdk-py#accessing-raw-response-data-eg-headers
        """
        return ConfigSchemaResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> ConfigSchemaResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/Synext-Solution/cnos-hub-gen-sdk-py#with_streaming_response
        """
        return ConfigSchemaResourceWithStreamingResponse(self)

    def org(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ConfigSchemaOrgResponse:
        return self._get(
            "/v1/config/schema/org",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ConfigSchemaOrgResponse,
        )

    def project(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ConfigSchemaProjectResponse:
        return self._get(
            "/v1/config/schema/project",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ConfigSchemaProjectResponse,
        )

    def system(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ConfigSchemaSystemResponse:
        return self._get(
            "/v1/config/schema/system",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ConfigSchemaSystemResponse,
        )


class AsyncConfigSchemaResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncConfigSchemaResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/Synext-Solution/cnos-hub-gen-sdk-py#accessing-raw-response-data-eg-headers
        """
        return AsyncConfigSchemaResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncConfigSchemaResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/Synext-Solution/cnos-hub-gen-sdk-py#with_streaming_response
        """
        return AsyncConfigSchemaResourceWithStreamingResponse(self)

    async def org(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ConfigSchemaOrgResponse:
        return await self._get(
            "/v1/config/schema/org",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ConfigSchemaOrgResponse,
        )

    async def project(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ConfigSchemaProjectResponse:
        return await self._get(
            "/v1/config/schema/project",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ConfigSchemaProjectResponse,
        )

    async def system(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ConfigSchemaSystemResponse:
        return await self._get(
            "/v1/config/schema/system",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ConfigSchemaSystemResponse,
        )


class ConfigSchemaResourceWithRawResponse:
    def __init__(self, config_schema: ConfigSchemaResource) -> None:
        self._config_schema = config_schema

        self.org = to_raw_response_wrapper(
            config_schema.org,
        )
        self.project = to_raw_response_wrapper(
            config_schema.project,
        )
        self.system = to_raw_response_wrapper(
            config_schema.system,
        )


class AsyncConfigSchemaResourceWithRawResponse:
    def __init__(self, config_schema: AsyncConfigSchemaResource) -> None:
        self._config_schema = config_schema

        self.org = async_to_raw_response_wrapper(
            config_schema.org,
        )
        self.project = async_to_raw_response_wrapper(
            config_schema.project,
        )
        self.system = async_to_raw_response_wrapper(
            config_schema.system,
        )


class ConfigSchemaResourceWithStreamingResponse:
    def __init__(self, config_schema: ConfigSchemaResource) -> None:
        self._config_schema = config_schema

        self.org = to_streamed_response_wrapper(
            config_schema.org,
        )
        self.project = to_streamed_response_wrapper(
            config_schema.project,
        )
        self.system = to_streamed_response_wrapper(
            config_schema.system,
        )


class AsyncConfigSchemaResourceWithStreamingResponse:
    def __init__(self, config_schema: AsyncConfigSchemaResource) -> None:
        self._config_schema = config_schema

        self.org = async_to_streamed_response_wrapper(
            config_schema.org,
        )
        self.project = async_to_streamed_response_wrapper(
            config_schema.project,
        )
        self.system = async_to_streamed_response_wrapper(
            config_schema.system,
        )
