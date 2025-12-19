# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Optional
from typing_extensions import Literal

import httpx

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
from ..._base_client import make_request_options
from ...types.projects import execute_create_params
from ...types.budgets_json_param import BudgetsJsonParam
from ...types.projects.execute_create_response import ExecuteCreateResponse

__all__ = ["ExecuteResource", "AsyncExecuteResource"]


class ExecuteResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> ExecuteResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/Synext-Solution/cnos-hub-gen-sdk-py#accessing-raw-response-data-eg-headers
        """
        return ExecuteResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> ExecuteResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/Synext-Solution/cnos-hub-gen-sdk-py#with_streaming_response
        """
        return ExecuteResourceWithStreamingResponse(self)

    def create(
        self,
        project_id: str,
        *,
        function: str,
        args: Optional[execute_create_params.Args] | Omit = omit,
        budget: Optional[BudgetsJsonParam] | Omit = omit,
        result_encoding: Optional[Literal["binary", "cnon", "json"]] | Omit = omit,
        trace: bool | Omit = omit,
        validate_as: Optional[SequenceNotStr[str]] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ExecuteCreateResponse:
        """
        Execute a function against the latest prepared program for the project.

        Args:
          function: Fully-qualified function name to invoke (e.g.,
              `custom.workflows.signup.handle`).

          args: Arguments encoded as JSON, CNON, or base64 binary. Provide exactly one encoding.

          budget: Optional runtime budget configuration.

          result_encoding: Desired result encoding. Defaults to binary (base64-wrapped) when omitted.

          trace: Whether to capture an execution trace.

          validate_as: Optional type aliases to validate each argument against (aligned to args).

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not project_id:
            raise ValueError(f"Expected a non-empty value for `project_id` but received {project_id!r}")
        return self._post(
            f"/v1/projects/{project_id}/execute",
            body=maybe_transform(
                {
                    "function": function,
                    "args": args,
                    "budget": budget,
                    "result_encoding": result_encoding,
                    "trace": trace,
                    "validate_as": validate_as,
                },
                execute_create_params.ExecuteCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ExecuteCreateResponse,
        )


class AsyncExecuteResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncExecuteResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/Synext-Solution/cnos-hub-gen-sdk-py#accessing-raw-response-data-eg-headers
        """
        return AsyncExecuteResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncExecuteResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/Synext-Solution/cnos-hub-gen-sdk-py#with_streaming_response
        """
        return AsyncExecuteResourceWithStreamingResponse(self)

    async def create(
        self,
        project_id: str,
        *,
        function: str,
        args: Optional[execute_create_params.Args] | Omit = omit,
        budget: Optional[BudgetsJsonParam] | Omit = omit,
        result_encoding: Optional[Literal["binary", "cnon", "json"]] | Omit = omit,
        trace: bool | Omit = omit,
        validate_as: Optional[SequenceNotStr[str]] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ExecuteCreateResponse:
        """
        Execute a function against the latest prepared program for the project.

        Args:
          function: Fully-qualified function name to invoke (e.g.,
              `custom.workflows.signup.handle`).

          args: Arguments encoded as JSON, CNON, or base64 binary. Provide exactly one encoding.

          budget: Optional runtime budget configuration.

          result_encoding: Desired result encoding. Defaults to binary (base64-wrapped) when omitted.

          trace: Whether to capture an execution trace.

          validate_as: Optional type aliases to validate each argument against (aligned to args).

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not project_id:
            raise ValueError(f"Expected a non-empty value for `project_id` but received {project_id!r}")
        return await self._post(
            f"/v1/projects/{project_id}/execute",
            body=await async_maybe_transform(
                {
                    "function": function,
                    "args": args,
                    "budget": budget,
                    "result_encoding": result_encoding,
                    "trace": trace,
                    "validate_as": validate_as,
                },
                execute_create_params.ExecuteCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ExecuteCreateResponse,
        )


class ExecuteResourceWithRawResponse:
    def __init__(self, execute: ExecuteResource) -> None:
        self._execute = execute

        self.create = to_raw_response_wrapper(
            execute.create,
        )


class AsyncExecuteResourceWithRawResponse:
    def __init__(self, execute: AsyncExecuteResource) -> None:
        self._execute = execute

        self.create = async_to_raw_response_wrapper(
            execute.create,
        )


class ExecuteResourceWithStreamingResponse:
    def __init__(self, execute: ExecuteResource) -> None:
        self._execute = execute

        self.create = to_streamed_response_wrapper(
            execute.create,
        )


class AsyncExecuteResourceWithStreamingResponse:
    def __init__(self, execute: AsyncExecuteResource) -> None:
        self._execute = execute

        self.create = async_to_streamed_response_wrapper(
            execute.create,
        )
