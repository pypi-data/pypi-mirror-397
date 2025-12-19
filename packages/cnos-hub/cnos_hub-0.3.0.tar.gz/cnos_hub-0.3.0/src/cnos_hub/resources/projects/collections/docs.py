# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Dict, Optional

import httpx

from ...._types import Body, Omit, Query, Headers, NoneType, NotGiven, omit, not_given
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
from ....types.projects.collections import (
    doc_list_params,
    doc_create_params,
    doc_delete_params,
    doc_replace_params,
    doc_retrieve_params,
)
from ....types.projects.collections.doc_list_response import DocListResponse
from ....types.projects.collections.doc_create_response import DocCreateResponse
from ....types.projects.collections.doc_replace_response import DocReplaceResponse
from ....types.projects.collections.doc_retrieve_response import DocRetrieveResponse

__all__ = ["DocsResource", "AsyncDocsResource"]


class DocsResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> DocsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/Synext-Solution/cnos-hub-gen-sdk-py#accessing-raw-response-data-eg-headers
        """
        return DocsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> DocsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/Synext-Solution/cnos-hub-gen-sdk-py#with_streaming_response
        """
        return DocsResourceWithStreamingResponse(self)

    def create(
        self,
        name: str,
        *,
        project_id: str,
        value: Dict[str, object],
        id: Optional[str] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> DocCreateResponse:
        """
        Create a document within a collection.

        Args:
          value: Document payload.

          id: Optional explicit ID (server generates ULID if omitted).

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not project_id:
            raise ValueError(f"Expected a non-empty value for `project_id` but received {project_id!r}")
        if not name:
            raise ValueError(f"Expected a non-empty value for `name` but received {name!r}")
        return self._post(
            f"/v1/projects/{project_id}/collections/{name}/docs",
            body=maybe_transform(
                {
                    "value": value,
                    "id": id,
                },
                doc_create_params.DocCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=DocCreateResponse,
        )

    def retrieve(
        self,
        doc_id: str,
        *,
        project_id: str,
        name: str,
        include_deleted: bool,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> DocRetrieveResponse:
        """
        Fetch a single document (optionally including soft-deleted entries).

        Args:
          include_deleted: Include soft-deleted documents

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not project_id:
            raise ValueError(f"Expected a non-empty value for `project_id` but received {project_id!r}")
        if not name:
            raise ValueError(f"Expected a non-empty value for `name` but received {name!r}")
        if not doc_id:
            raise ValueError(f"Expected a non-empty value for `doc_id` but received {doc_id!r}")
        return self._get(
            f"/v1/projects/{project_id}/collections/{name}/docs/{doc_id}",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform({"include_deleted": include_deleted}, doc_retrieve_params.DocRetrieveParams),
            ),
            cast_to=DocRetrieveResponse,
        )

    def list(
        self,
        name: str,
        *,
        project_id: str,
        include_deleted: bool,
        cursor: str | Omit = omit,
        limit: int | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> SyncPage[DocListResponse]:
        """
        List documents for a collection.

        Args:
          include_deleted: Include soft-deleted documents

          cursor: Pagination cursor

          limit: Page size (1-100, default 50)

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not project_id:
            raise ValueError(f"Expected a non-empty value for `project_id` but received {project_id!r}")
        if not name:
            raise ValueError(f"Expected a non-empty value for `name` but received {name!r}")
        return self._get_api_list(
            f"/v1/projects/{project_id}/collections/{name}/docs",
            page=SyncPage[DocListResponse],
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "include_deleted": include_deleted,
                        "cursor": cursor,
                        "limit": limit,
                    },
                    doc_list_params.DocListParams,
                ),
            ),
            model=DocListResponse,
        )

    def delete(
        self,
        doc_id: str,
        *,
        project_id: str,
        name: str,
        expected_version: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> None:
        """
        Delete a document using optimistic concurrency control.

        Args:
          expected_version: Required version token for optimistic concurrency.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not project_id:
            raise ValueError(f"Expected a non-empty value for `project_id` but received {project_id!r}")
        if not name:
            raise ValueError(f"Expected a non-empty value for `name` but received {name!r}")
        if not doc_id:
            raise ValueError(f"Expected a non-empty value for `doc_id` but received {doc_id!r}")
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        return self._delete(
            f"/v1/projects/{project_id}/collections/{name}/docs/{doc_id}",
            body=maybe_transform({"expected_version": expected_version}, doc_delete_params.DocDeleteParams),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=NoneType,
        )

    def replace(
        self,
        doc_id: str,
        *,
        project_id: str,
        name: str,
        expected_version: str,
        value: Dict[str, object],
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> DocReplaceResponse:
        """
        Replace a document with optimistic concurrency control.

        Args:
          expected_version: Required version token for optimistic concurrency.

          value: New payload.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not project_id:
            raise ValueError(f"Expected a non-empty value for `project_id` but received {project_id!r}")
        if not name:
            raise ValueError(f"Expected a non-empty value for `name` but received {name!r}")
        if not doc_id:
            raise ValueError(f"Expected a non-empty value for `doc_id` but received {doc_id!r}")
        return self._put(
            f"/v1/projects/{project_id}/collections/{name}/docs/{doc_id}",
            body=maybe_transform(
                {
                    "expected_version": expected_version,
                    "value": value,
                },
                doc_replace_params.DocReplaceParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=DocReplaceResponse,
        )


class AsyncDocsResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncDocsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/Synext-Solution/cnos-hub-gen-sdk-py#accessing-raw-response-data-eg-headers
        """
        return AsyncDocsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncDocsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/Synext-Solution/cnos-hub-gen-sdk-py#with_streaming_response
        """
        return AsyncDocsResourceWithStreamingResponse(self)

    async def create(
        self,
        name: str,
        *,
        project_id: str,
        value: Dict[str, object],
        id: Optional[str] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> DocCreateResponse:
        """
        Create a document within a collection.

        Args:
          value: Document payload.

          id: Optional explicit ID (server generates ULID if omitted).

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not project_id:
            raise ValueError(f"Expected a non-empty value for `project_id` but received {project_id!r}")
        if not name:
            raise ValueError(f"Expected a non-empty value for `name` but received {name!r}")
        return await self._post(
            f"/v1/projects/{project_id}/collections/{name}/docs",
            body=await async_maybe_transform(
                {
                    "value": value,
                    "id": id,
                },
                doc_create_params.DocCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=DocCreateResponse,
        )

    async def retrieve(
        self,
        doc_id: str,
        *,
        project_id: str,
        name: str,
        include_deleted: bool,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> DocRetrieveResponse:
        """
        Fetch a single document (optionally including soft-deleted entries).

        Args:
          include_deleted: Include soft-deleted documents

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not project_id:
            raise ValueError(f"Expected a non-empty value for `project_id` but received {project_id!r}")
        if not name:
            raise ValueError(f"Expected a non-empty value for `name` but received {name!r}")
        if not doc_id:
            raise ValueError(f"Expected a non-empty value for `doc_id` but received {doc_id!r}")
        return await self._get(
            f"/v1/projects/{project_id}/collections/{name}/docs/{doc_id}",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {"include_deleted": include_deleted}, doc_retrieve_params.DocRetrieveParams
                ),
            ),
            cast_to=DocRetrieveResponse,
        )

    def list(
        self,
        name: str,
        *,
        project_id: str,
        include_deleted: bool,
        cursor: str | Omit = omit,
        limit: int | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> AsyncPaginator[DocListResponse, AsyncPage[DocListResponse]]:
        """
        List documents for a collection.

        Args:
          include_deleted: Include soft-deleted documents

          cursor: Pagination cursor

          limit: Page size (1-100, default 50)

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not project_id:
            raise ValueError(f"Expected a non-empty value for `project_id` but received {project_id!r}")
        if not name:
            raise ValueError(f"Expected a non-empty value for `name` but received {name!r}")
        return self._get_api_list(
            f"/v1/projects/{project_id}/collections/{name}/docs",
            page=AsyncPage[DocListResponse],
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "include_deleted": include_deleted,
                        "cursor": cursor,
                        "limit": limit,
                    },
                    doc_list_params.DocListParams,
                ),
            ),
            model=DocListResponse,
        )

    async def delete(
        self,
        doc_id: str,
        *,
        project_id: str,
        name: str,
        expected_version: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> None:
        """
        Delete a document using optimistic concurrency control.

        Args:
          expected_version: Required version token for optimistic concurrency.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not project_id:
            raise ValueError(f"Expected a non-empty value for `project_id` but received {project_id!r}")
        if not name:
            raise ValueError(f"Expected a non-empty value for `name` but received {name!r}")
        if not doc_id:
            raise ValueError(f"Expected a non-empty value for `doc_id` but received {doc_id!r}")
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        return await self._delete(
            f"/v1/projects/{project_id}/collections/{name}/docs/{doc_id}",
            body=await async_maybe_transform({"expected_version": expected_version}, doc_delete_params.DocDeleteParams),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=NoneType,
        )

    async def replace(
        self,
        doc_id: str,
        *,
        project_id: str,
        name: str,
        expected_version: str,
        value: Dict[str, object],
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> DocReplaceResponse:
        """
        Replace a document with optimistic concurrency control.

        Args:
          expected_version: Required version token for optimistic concurrency.

          value: New payload.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not project_id:
            raise ValueError(f"Expected a non-empty value for `project_id` but received {project_id!r}")
        if not name:
            raise ValueError(f"Expected a non-empty value for `name` but received {name!r}")
        if not doc_id:
            raise ValueError(f"Expected a non-empty value for `doc_id` but received {doc_id!r}")
        return await self._put(
            f"/v1/projects/{project_id}/collections/{name}/docs/{doc_id}",
            body=await async_maybe_transform(
                {
                    "expected_version": expected_version,
                    "value": value,
                },
                doc_replace_params.DocReplaceParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=DocReplaceResponse,
        )


class DocsResourceWithRawResponse:
    def __init__(self, docs: DocsResource) -> None:
        self._docs = docs

        self.create = to_raw_response_wrapper(
            docs.create,
        )
        self.retrieve = to_raw_response_wrapper(
            docs.retrieve,
        )
        self.list = to_raw_response_wrapper(
            docs.list,
        )
        self.delete = to_raw_response_wrapper(
            docs.delete,
        )
        self.replace = to_raw_response_wrapper(
            docs.replace,
        )


class AsyncDocsResourceWithRawResponse:
    def __init__(self, docs: AsyncDocsResource) -> None:
        self._docs = docs

        self.create = async_to_raw_response_wrapper(
            docs.create,
        )
        self.retrieve = async_to_raw_response_wrapper(
            docs.retrieve,
        )
        self.list = async_to_raw_response_wrapper(
            docs.list,
        )
        self.delete = async_to_raw_response_wrapper(
            docs.delete,
        )
        self.replace = async_to_raw_response_wrapper(
            docs.replace,
        )


class DocsResourceWithStreamingResponse:
    def __init__(self, docs: DocsResource) -> None:
        self._docs = docs

        self.create = to_streamed_response_wrapper(
            docs.create,
        )
        self.retrieve = to_streamed_response_wrapper(
            docs.retrieve,
        )
        self.list = to_streamed_response_wrapper(
            docs.list,
        )
        self.delete = to_streamed_response_wrapper(
            docs.delete,
        )
        self.replace = to_streamed_response_wrapper(
            docs.replace,
        )


class AsyncDocsResourceWithStreamingResponse:
    def __init__(self, docs: AsyncDocsResource) -> None:
        self._docs = docs

        self.create = async_to_streamed_response_wrapper(
            docs.create,
        )
        self.retrieve = async_to_streamed_response_wrapper(
            docs.retrieve,
        )
        self.list = async_to_streamed_response_wrapper(
            docs.list,
        )
        self.delete = async_to_streamed_response_wrapper(
            docs.delete,
        )
        self.replace = async_to_streamed_response_wrapper(
            docs.replace,
        )
