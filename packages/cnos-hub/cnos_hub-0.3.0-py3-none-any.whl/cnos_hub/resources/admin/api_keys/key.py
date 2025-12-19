# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import List, Optional
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
from ....types.admin.api_keys import key_update_params
from ....types.shared.api_key_dto import APIKeyDto
from ....types.admin.api_keys.key_rotate_response import KeyRotateResponse

__all__ = ["KeyResource", "AsyncKeyResource"]


class KeyResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> KeyResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/Synext-Solution/cnos-hub-gen-sdk-py#accessing-raw-response-data-eg-headers
        """
        return KeyResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> KeyResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/Synext-Solution/cnos-hub-gen-sdk-py#with_streaming_response
        """
        return KeyResourceWithStreamingResponse(self)

    def retrieve(
        self,
        key_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> APIKeyDto:
        """
        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not key_id:
            raise ValueError(f"Expected a non-empty value for `key_id` but received {key_id!r}")
        return self._get(
            f"/v1/admin/api-keys/{key_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=APIKeyDto,
        )

    def update(
        self,
        key_id: str,
        *,
        capabilities: Optional[
            List[
                Literal[
                    "OrgRead",
                    "OrgWrite",
                    "OrgDelete",
                    "OrgConfigRead",
                    "OrgConfigWrite",
                    "ProjectRead",
                    "ProjectWrite",
                    "ProjectDelete",
                    "ProjectConfigRead",
                    "ProjectConfigWrite",
                    "CnosCheck",
                    "CnosExecute",
                    "PrincipalRead",
                    "CollectionsRead",
                    "CollectionsWrite",
                    "CollectionsAdmin",
                    "DataRead",
                    "DataWrite",
                    "FilesRead",
                    "FilesWrite",
                    "TasksRead",
                    "TasksWrite",
                    "EventsRead",
                    "EventsWrite",
                    "WebhooksRead",
                    "WebhooksWrite",
                    "ViewsRead",
                    "ViewsWrite",
                    "ViewsExecute",
                    "ViewsGrant",
                    "ApiKeysRead",
                    "ApiKeysWrite",
                    "OrgMembersRead",
                    "OrgMembersWrite",
                    "OrgMembersManage",
                    "ProjectMembersRead",
                    "ProjectMembersWrite",
                    "ProjectMembersManage",
                    "PlatformOrgAdmin",
                    "PlatformSystemConfigAdmin",
                    "ImpersonatePrincipal",
                ]
            ]
        ]
        | Omit = omit,
        description: str | Omit = omit,
        name: Optional[str] | Omit = omit,
        roles: Optional[SequenceNotStr[str]] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> APIKeyDto:
        """
        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not key_id:
            raise ValueError(f"Expected a non-empty value for `key_id` but received {key_id!r}")
        return self._patch(
            f"/v1/admin/api-keys/{key_id}",
            body=maybe_transform(
                {
                    "capabilities": capabilities,
                    "description": description,
                    "name": name,
                    "roles": roles,
                },
                key_update_params.KeyUpdateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=APIKeyDto,
        )

    def delete(
        self,
        key_id: str,
        *,
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
        if not key_id:
            raise ValueError(f"Expected a non-empty value for `key_id` but received {key_id!r}")
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        return self._delete(
            f"/v1/admin/api-keys/{key_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=NoneType,
        )

    def rotate(
        self,
        key_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> KeyRotateResponse:
        """
        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not key_id:
            raise ValueError(f"Expected a non-empty value for `key_id` but received {key_id!r}")
        return self._post(
            f"/v1/admin/api-keys/{key_id}/rotate",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=KeyRotateResponse,
        )


class AsyncKeyResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncKeyResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/Synext-Solution/cnos-hub-gen-sdk-py#accessing-raw-response-data-eg-headers
        """
        return AsyncKeyResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncKeyResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/Synext-Solution/cnos-hub-gen-sdk-py#with_streaming_response
        """
        return AsyncKeyResourceWithStreamingResponse(self)

    async def retrieve(
        self,
        key_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> APIKeyDto:
        """
        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not key_id:
            raise ValueError(f"Expected a non-empty value for `key_id` but received {key_id!r}")
        return await self._get(
            f"/v1/admin/api-keys/{key_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=APIKeyDto,
        )

    async def update(
        self,
        key_id: str,
        *,
        capabilities: Optional[
            List[
                Literal[
                    "OrgRead",
                    "OrgWrite",
                    "OrgDelete",
                    "OrgConfigRead",
                    "OrgConfigWrite",
                    "ProjectRead",
                    "ProjectWrite",
                    "ProjectDelete",
                    "ProjectConfigRead",
                    "ProjectConfigWrite",
                    "CnosCheck",
                    "CnosExecute",
                    "PrincipalRead",
                    "CollectionsRead",
                    "CollectionsWrite",
                    "CollectionsAdmin",
                    "DataRead",
                    "DataWrite",
                    "FilesRead",
                    "FilesWrite",
                    "TasksRead",
                    "TasksWrite",
                    "EventsRead",
                    "EventsWrite",
                    "WebhooksRead",
                    "WebhooksWrite",
                    "ViewsRead",
                    "ViewsWrite",
                    "ViewsExecute",
                    "ViewsGrant",
                    "ApiKeysRead",
                    "ApiKeysWrite",
                    "OrgMembersRead",
                    "OrgMembersWrite",
                    "OrgMembersManage",
                    "ProjectMembersRead",
                    "ProjectMembersWrite",
                    "ProjectMembersManage",
                    "PlatformOrgAdmin",
                    "PlatformSystemConfigAdmin",
                    "ImpersonatePrincipal",
                ]
            ]
        ]
        | Omit = omit,
        description: str | Omit = omit,
        name: Optional[str] | Omit = omit,
        roles: Optional[SequenceNotStr[str]] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> APIKeyDto:
        """
        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not key_id:
            raise ValueError(f"Expected a non-empty value for `key_id` but received {key_id!r}")
        return await self._patch(
            f"/v1/admin/api-keys/{key_id}",
            body=await async_maybe_transform(
                {
                    "capabilities": capabilities,
                    "description": description,
                    "name": name,
                    "roles": roles,
                },
                key_update_params.KeyUpdateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=APIKeyDto,
        )

    async def delete(
        self,
        key_id: str,
        *,
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
        if not key_id:
            raise ValueError(f"Expected a non-empty value for `key_id` but received {key_id!r}")
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        return await self._delete(
            f"/v1/admin/api-keys/{key_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=NoneType,
        )

    async def rotate(
        self,
        key_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> KeyRotateResponse:
        """
        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not key_id:
            raise ValueError(f"Expected a non-empty value for `key_id` but received {key_id!r}")
        return await self._post(
            f"/v1/admin/api-keys/{key_id}/rotate",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=KeyRotateResponse,
        )


class KeyResourceWithRawResponse:
    def __init__(self, key: KeyResource) -> None:
        self._key = key

        self.retrieve = to_raw_response_wrapper(
            key.retrieve,
        )
        self.update = to_raw_response_wrapper(
            key.update,
        )
        self.delete = to_raw_response_wrapper(
            key.delete,
        )
        self.rotate = to_raw_response_wrapper(
            key.rotate,
        )


class AsyncKeyResourceWithRawResponse:
    def __init__(self, key: AsyncKeyResource) -> None:
        self._key = key

        self.retrieve = async_to_raw_response_wrapper(
            key.retrieve,
        )
        self.update = async_to_raw_response_wrapper(
            key.update,
        )
        self.delete = async_to_raw_response_wrapper(
            key.delete,
        )
        self.rotate = async_to_raw_response_wrapper(
            key.rotate,
        )


class KeyResourceWithStreamingResponse:
    def __init__(self, key: KeyResource) -> None:
        self._key = key

        self.retrieve = to_streamed_response_wrapper(
            key.retrieve,
        )
        self.update = to_streamed_response_wrapper(
            key.update,
        )
        self.delete = to_streamed_response_wrapper(
            key.delete,
        )
        self.rotate = to_streamed_response_wrapper(
            key.rotate,
        )


class AsyncKeyResourceWithStreamingResponse:
    def __init__(self, key: AsyncKeyResource) -> None:
        self._key = key

        self.retrieve = async_to_streamed_response_wrapper(
            key.retrieve,
        )
        self.update = async_to_streamed_response_wrapper(
            key.update,
        )
        self.delete = async_to_streamed_response_wrapper(
            key.delete,
        )
        self.rotate = async_to_streamed_response_wrapper(
            key.rotate,
        )
