# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import List, Union, Optional
from datetime import datetime
from typing_extensions import Literal

import httpx

from .key import (
    KeyResource,
    AsyncKeyResource,
    KeyResourceWithRawResponse,
    AsyncKeyResourceWithRawResponse,
    KeyResourceWithStreamingResponse,
    AsyncKeyResourceWithStreamingResponse,
)
from ...types import api_key_list_params, api_key_create_params
from ..._types import Body, Omit, Query, Headers, NotGiven, SequenceNotStr, omit, not_given
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
from ...types.api_key_list_response import APIKeyListResponse
from ...types.shared.api_key_status import APIKeyStatus
from ...types.api_key_create_response import APIKeyCreateResponse

__all__ = ["APIKeysResource", "AsyncAPIKeysResource"]


class APIKeysResource(SyncAPIResource):
    @cached_property
    def key(self) -> KeyResource:
        return KeyResource(self._client)

    @cached_property
    def with_raw_response(self) -> APIKeysResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/Synext-Solution/cnos-hub-gen-sdk-py#accessing-raw-response-data-eg-headers
        """
        return APIKeysResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> APIKeysResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/Synext-Solution/cnos-hub-gen-sdk-py#with_streaming_response
        """
        return APIKeysResourceWithStreamingResponse(self)

    def create(
        self,
        *,
        name: str,
        capabilities: List[
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
        | Omit = omit,
        description: Optional[str] | Omit = omit,
        expires_at: Union[str, datetime, None] | Omit = omit,
        roles: SequenceNotStr[str] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> APIKeyCreateResponse:
        """
        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/v1/api-keys",
            body=maybe_transform(
                {
                    "name": name,
                    "capabilities": capabilities,
                    "description": description,
                    "expires_at": expires_at,
                    "roles": roles,
                },
                api_key_create_params.APIKeyCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=APIKeyCreateResponse,
        )

    def list(
        self,
        *,
        cursor: str | Omit = omit,
        limit: int | Omit = omit,
        status: APIKeyStatus | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> SyncPage[APIKeyListResponse]:
        """
        Args:
          cursor: Pagination cursor

          limit: Page size (1-100, default 50)

          status: Filter by status

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._get_api_list(
            "/v1/api-keys",
            page=SyncPage[APIKeyListResponse],
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
                    api_key_list_params.APIKeyListParams,
                ),
            ),
            model=APIKeyListResponse,
        )


class AsyncAPIKeysResource(AsyncAPIResource):
    @cached_property
    def key(self) -> AsyncKeyResource:
        return AsyncKeyResource(self._client)

    @cached_property
    def with_raw_response(self) -> AsyncAPIKeysResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/Synext-Solution/cnos-hub-gen-sdk-py#accessing-raw-response-data-eg-headers
        """
        return AsyncAPIKeysResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncAPIKeysResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/Synext-Solution/cnos-hub-gen-sdk-py#with_streaming_response
        """
        return AsyncAPIKeysResourceWithStreamingResponse(self)

    async def create(
        self,
        *,
        name: str,
        capabilities: List[
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
        | Omit = omit,
        description: Optional[str] | Omit = omit,
        expires_at: Union[str, datetime, None] | Omit = omit,
        roles: SequenceNotStr[str] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> APIKeyCreateResponse:
        """
        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/v1/api-keys",
            body=await async_maybe_transform(
                {
                    "name": name,
                    "capabilities": capabilities,
                    "description": description,
                    "expires_at": expires_at,
                    "roles": roles,
                },
                api_key_create_params.APIKeyCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=APIKeyCreateResponse,
        )

    def list(
        self,
        *,
        cursor: str | Omit = omit,
        limit: int | Omit = omit,
        status: APIKeyStatus | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> AsyncPaginator[APIKeyListResponse, AsyncPage[APIKeyListResponse]]:
        """
        Args:
          cursor: Pagination cursor

          limit: Page size (1-100, default 50)

          status: Filter by status

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._get_api_list(
            "/v1/api-keys",
            page=AsyncPage[APIKeyListResponse],
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
                    api_key_list_params.APIKeyListParams,
                ),
            ),
            model=APIKeyListResponse,
        )


class APIKeysResourceWithRawResponse:
    def __init__(self, api_keys: APIKeysResource) -> None:
        self._api_keys = api_keys

        self.create = to_raw_response_wrapper(
            api_keys.create,
        )
        self.list = to_raw_response_wrapper(
            api_keys.list,
        )

    @cached_property
    def key(self) -> KeyResourceWithRawResponse:
        return KeyResourceWithRawResponse(self._api_keys.key)


class AsyncAPIKeysResourceWithRawResponse:
    def __init__(self, api_keys: AsyncAPIKeysResource) -> None:
        self._api_keys = api_keys

        self.create = async_to_raw_response_wrapper(
            api_keys.create,
        )
        self.list = async_to_raw_response_wrapper(
            api_keys.list,
        )

    @cached_property
    def key(self) -> AsyncKeyResourceWithRawResponse:
        return AsyncKeyResourceWithRawResponse(self._api_keys.key)


class APIKeysResourceWithStreamingResponse:
    def __init__(self, api_keys: APIKeysResource) -> None:
        self._api_keys = api_keys

        self.create = to_streamed_response_wrapper(
            api_keys.create,
        )
        self.list = to_streamed_response_wrapper(
            api_keys.list,
        )

    @cached_property
    def key(self) -> KeyResourceWithStreamingResponse:
        return KeyResourceWithStreamingResponse(self._api_keys.key)


class AsyncAPIKeysResourceWithStreamingResponse:
    def __init__(self, api_keys: AsyncAPIKeysResource) -> None:
        self._api_keys = api_keys

        self.create = async_to_streamed_response_wrapper(
            api_keys.create,
        )
        self.list = async_to_streamed_response_wrapper(
            api_keys.list,
        )

    @cached_property
    def key(self) -> AsyncKeyResourceWithStreamingResponse:
        return AsyncKeyResourceWithStreamingResponse(self._api_keys.key)
