# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from .key import (
    KeyResource,
    AsyncKeyResource,
    KeyResourceWithRawResponse,
    AsyncKeyResourceWithRawResponse,
    KeyResourceWithStreamingResponse,
    AsyncKeyResourceWithStreamingResponse,
)
from ...._compat import cached_property
from ...._resource import SyncAPIResource, AsyncAPIResource

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


class APIKeysResourceWithRawResponse:
    def __init__(self, api_keys: APIKeysResource) -> None:
        self._api_keys = api_keys

    @cached_property
    def key(self) -> KeyResourceWithRawResponse:
        return KeyResourceWithRawResponse(self._api_keys.key)


class AsyncAPIKeysResourceWithRawResponse:
    def __init__(self, api_keys: AsyncAPIKeysResource) -> None:
        self._api_keys = api_keys

    @cached_property
    def key(self) -> AsyncKeyResourceWithRawResponse:
        return AsyncKeyResourceWithRawResponse(self._api_keys.key)


class APIKeysResourceWithStreamingResponse:
    def __init__(self, api_keys: APIKeysResource) -> None:
        self._api_keys = api_keys

    @cached_property
    def key(self) -> KeyResourceWithStreamingResponse:
        return KeyResourceWithStreamingResponse(self._api_keys.key)


class AsyncAPIKeysResourceWithStreamingResponse:
    def __init__(self, api_keys: AsyncAPIKeysResource) -> None:
        self._api_keys = api_keys

    @cached_property
    def key(self) -> AsyncKeyResourceWithStreamingResponse:
        return AsyncKeyResourceWithStreamingResponse(self._api_keys.key)
