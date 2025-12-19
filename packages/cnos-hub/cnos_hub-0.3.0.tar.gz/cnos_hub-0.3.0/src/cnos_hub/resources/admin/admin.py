# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from ..._compat import cached_property
from .orgs.orgs import (
    OrgsResource,
    AsyncOrgsResource,
    OrgsResourceWithRawResponse,
    AsyncOrgsResourceWithRawResponse,
    OrgsResourceWithStreamingResponse,
    AsyncOrgsResourceWithStreamingResponse,
)
from ..._resource import SyncAPIResource, AsyncAPIResource
from .api_keys.api_keys import (
    APIKeysResource,
    AsyncAPIKeysResource,
    APIKeysResourceWithRawResponse,
    AsyncAPIKeysResourceWithRawResponse,
    APIKeysResourceWithStreamingResponse,
    AsyncAPIKeysResourceWithStreamingResponse,
)
from .projects.projects import (
    ProjectsResource,
    AsyncProjectsResource,
    ProjectsResourceWithRawResponse,
    AsyncProjectsResourceWithRawResponse,
    ProjectsResourceWithStreamingResponse,
    AsyncProjectsResourceWithStreamingResponse,
)

__all__ = ["AdminResource", "AsyncAdminResource"]


class AdminResource(SyncAPIResource):
    @cached_property
    def orgs(self) -> OrgsResource:
        return OrgsResource(self._client)

    @cached_property
    def api_keys(self) -> APIKeysResource:
        return APIKeysResource(self._client)

    @cached_property
    def projects(self) -> ProjectsResource:
        return ProjectsResource(self._client)

    @cached_property
    def with_raw_response(self) -> AdminResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/Synext-Solution/cnos-hub-gen-sdk-py#accessing-raw-response-data-eg-headers
        """
        return AdminResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AdminResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/Synext-Solution/cnos-hub-gen-sdk-py#with_streaming_response
        """
        return AdminResourceWithStreamingResponse(self)


class AsyncAdminResource(AsyncAPIResource):
    @cached_property
    def orgs(self) -> AsyncOrgsResource:
        return AsyncOrgsResource(self._client)

    @cached_property
    def api_keys(self) -> AsyncAPIKeysResource:
        return AsyncAPIKeysResource(self._client)

    @cached_property
    def projects(self) -> AsyncProjectsResource:
        return AsyncProjectsResource(self._client)

    @cached_property
    def with_raw_response(self) -> AsyncAdminResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/Synext-Solution/cnos-hub-gen-sdk-py#accessing-raw-response-data-eg-headers
        """
        return AsyncAdminResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncAdminResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/Synext-Solution/cnos-hub-gen-sdk-py#with_streaming_response
        """
        return AsyncAdminResourceWithStreamingResponse(self)


class AdminResourceWithRawResponse:
    def __init__(self, admin: AdminResource) -> None:
        self._admin = admin

    @cached_property
    def orgs(self) -> OrgsResourceWithRawResponse:
        return OrgsResourceWithRawResponse(self._admin.orgs)

    @cached_property
    def api_keys(self) -> APIKeysResourceWithRawResponse:
        return APIKeysResourceWithRawResponse(self._admin.api_keys)

    @cached_property
    def projects(self) -> ProjectsResourceWithRawResponse:
        return ProjectsResourceWithRawResponse(self._admin.projects)


class AsyncAdminResourceWithRawResponse:
    def __init__(self, admin: AsyncAdminResource) -> None:
        self._admin = admin

    @cached_property
    def orgs(self) -> AsyncOrgsResourceWithRawResponse:
        return AsyncOrgsResourceWithRawResponse(self._admin.orgs)

    @cached_property
    def api_keys(self) -> AsyncAPIKeysResourceWithRawResponse:
        return AsyncAPIKeysResourceWithRawResponse(self._admin.api_keys)

    @cached_property
    def projects(self) -> AsyncProjectsResourceWithRawResponse:
        return AsyncProjectsResourceWithRawResponse(self._admin.projects)


class AdminResourceWithStreamingResponse:
    def __init__(self, admin: AdminResource) -> None:
        self._admin = admin

    @cached_property
    def orgs(self) -> OrgsResourceWithStreamingResponse:
        return OrgsResourceWithStreamingResponse(self._admin.orgs)

    @cached_property
    def api_keys(self) -> APIKeysResourceWithStreamingResponse:
        return APIKeysResourceWithStreamingResponse(self._admin.api_keys)

    @cached_property
    def projects(self) -> ProjectsResourceWithStreamingResponse:
        return ProjectsResourceWithStreamingResponse(self._admin.projects)


class AsyncAdminResourceWithStreamingResponse:
    def __init__(self, admin: AsyncAdminResource) -> None:
        self._admin = admin

    @cached_property
    def orgs(self) -> AsyncOrgsResourceWithStreamingResponse:
        return AsyncOrgsResourceWithStreamingResponse(self._admin.orgs)

    @cached_property
    def api_keys(self) -> AsyncAPIKeysResourceWithStreamingResponse:
        return AsyncAPIKeysResourceWithStreamingResponse(self._admin.api_keys)

    @cached_property
    def projects(self) -> AsyncProjectsResourceWithStreamingResponse:
        return AsyncProjectsResourceWithStreamingResponse(self._admin.projects)
