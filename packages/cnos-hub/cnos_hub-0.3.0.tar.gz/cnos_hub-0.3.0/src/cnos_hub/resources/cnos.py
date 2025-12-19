# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Iterable, Optional
from typing_extensions import Literal

import httpx

from ..types import cno_analyze_params, cno_execute_function_params
from .._types import Body, Omit, Query, Headers, NotGiven, SequenceNotStr, omit, not_given
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
from ..types.budgets_json_param import BudgetsJsonParam
from ..types.cno_analyze_response import CnoAnalyzeResponse
from ..types.cno_principal_response import CnoPrincipalResponse
from ..types.cno_templates_response import CnoTemplatesResponse
from ..types.cno_execute_function_response import CnoExecuteFunctionResponse

__all__ = ["CnosResource", "AsyncCnosResource"]


class CnosResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> CnosResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/Synext-Solution/cnos-hub-gen-sdk-py#accessing-raw-response-data-eg-headers
        """
        return CnosResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> CnosResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/Synext-Solution/cnos-hub-gen-sdk-py#with_streaming_response
        """
        return CnosResourceWithStreamingResponse(self)

    def analyze(
        self,
        *,
        modules: Iterable[cno_analyze_params.Module],
        root: str,
        options: cno_analyze_params.Options | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> CnoAnalyzeResponse:
        """
        Handler that performs typed analysis over provided modules and surfaces
        diagnostics and metadata.

        Args:
          modules: Modules to analyze.

          root: Path of the root module to analyze.

          options: Optional flags controlling output.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/v1/cnos/check",
            body=maybe_transform(
                {
                    "modules": modules,
                    "root": root,
                    "options": options,
                },
                cno_analyze_params.CnoAnalyzeParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=CnoAnalyzeResponse,
        )

    def execute_function(
        self,
        *,
        function: str,
        modules: Iterable[cno_execute_function_params.Module],
        root: str,
        args: Optional[cno_execute_function_params.Args] | Omit = omit,
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
    ) -> CnoExecuteFunctionResponse:
        """
        Handler that prepares modules and executes a function with JSON arguments.

        Args:
          function: Dotted function path relative to the root module.

          modules: Modules to prepare and run.

          root: Path of the root module to analyze.

          args: Arguments encoded as JSON, CNON, or base64 binary. Provide exactly one encoding.

          budget: Optional runtime budget configuration.

          result_encoding: Desired result encoding. Defaults to binary (base64-wrapped) when omitted.
              Clients should set this instead of relying on Accept overrides.

          trace: Whether to capture an execution trace.

          validate_as: Optional type aliases to validate each argument against (aligned to args).

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/v1/cnos/execute",
            body=maybe_transform(
                {
                    "function": function,
                    "modules": modules,
                    "root": root,
                    "args": args,
                    "budget": budget,
                    "result_encoding": result_encoding,
                    "trace": trace,
                    "validate_as": validate_as,
                },
                cno_execute_function_params.CnoExecuteFunctionParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=CnoExecuteFunctionResponse,
        )

    def principal(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> CnoPrincipalResponse:
        """Return the authenticated principal for the current request."""
        return self._get(
            "/v1/principal",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=CnoPrincipalResponse,
        )

    def templates(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> CnoTemplatesResponse:
        """List available CNOS templates (auth required)."""
        return self._get(
            "/v1/cnos/templates",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=CnoTemplatesResponse,
        )


class AsyncCnosResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncCnosResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/Synext-Solution/cnos-hub-gen-sdk-py#accessing-raw-response-data-eg-headers
        """
        return AsyncCnosResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncCnosResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/Synext-Solution/cnos-hub-gen-sdk-py#with_streaming_response
        """
        return AsyncCnosResourceWithStreamingResponse(self)

    async def analyze(
        self,
        *,
        modules: Iterable[cno_analyze_params.Module],
        root: str,
        options: cno_analyze_params.Options | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> CnoAnalyzeResponse:
        """
        Handler that performs typed analysis over provided modules and surfaces
        diagnostics and metadata.

        Args:
          modules: Modules to analyze.

          root: Path of the root module to analyze.

          options: Optional flags controlling output.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/v1/cnos/check",
            body=await async_maybe_transform(
                {
                    "modules": modules,
                    "root": root,
                    "options": options,
                },
                cno_analyze_params.CnoAnalyzeParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=CnoAnalyzeResponse,
        )

    async def execute_function(
        self,
        *,
        function: str,
        modules: Iterable[cno_execute_function_params.Module],
        root: str,
        args: Optional[cno_execute_function_params.Args] | Omit = omit,
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
    ) -> CnoExecuteFunctionResponse:
        """
        Handler that prepares modules and executes a function with JSON arguments.

        Args:
          function: Dotted function path relative to the root module.

          modules: Modules to prepare and run.

          root: Path of the root module to analyze.

          args: Arguments encoded as JSON, CNON, or base64 binary. Provide exactly one encoding.

          budget: Optional runtime budget configuration.

          result_encoding: Desired result encoding. Defaults to binary (base64-wrapped) when omitted.
              Clients should set this instead of relying on Accept overrides.

          trace: Whether to capture an execution trace.

          validate_as: Optional type aliases to validate each argument against (aligned to args).

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/v1/cnos/execute",
            body=await async_maybe_transform(
                {
                    "function": function,
                    "modules": modules,
                    "root": root,
                    "args": args,
                    "budget": budget,
                    "result_encoding": result_encoding,
                    "trace": trace,
                    "validate_as": validate_as,
                },
                cno_execute_function_params.CnoExecuteFunctionParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=CnoExecuteFunctionResponse,
        )

    async def principal(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> CnoPrincipalResponse:
        """Return the authenticated principal for the current request."""
        return await self._get(
            "/v1/principal",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=CnoPrincipalResponse,
        )

    async def templates(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> CnoTemplatesResponse:
        """List available CNOS templates (auth required)."""
        return await self._get(
            "/v1/cnos/templates",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=CnoTemplatesResponse,
        )


class CnosResourceWithRawResponse:
    def __init__(self, cnos: CnosResource) -> None:
        self._cnos = cnos

        self.analyze = to_raw_response_wrapper(
            cnos.analyze,
        )
        self.execute_function = to_raw_response_wrapper(
            cnos.execute_function,
        )
        self.principal = to_raw_response_wrapper(
            cnos.principal,
        )
        self.templates = to_raw_response_wrapper(
            cnos.templates,
        )


class AsyncCnosResourceWithRawResponse:
    def __init__(self, cnos: AsyncCnosResource) -> None:
        self._cnos = cnos

        self.analyze = async_to_raw_response_wrapper(
            cnos.analyze,
        )
        self.execute_function = async_to_raw_response_wrapper(
            cnos.execute_function,
        )
        self.principal = async_to_raw_response_wrapper(
            cnos.principal,
        )
        self.templates = async_to_raw_response_wrapper(
            cnos.templates,
        )


class CnosResourceWithStreamingResponse:
    def __init__(self, cnos: CnosResource) -> None:
        self._cnos = cnos

        self.analyze = to_streamed_response_wrapper(
            cnos.analyze,
        )
        self.execute_function = to_streamed_response_wrapper(
            cnos.execute_function,
        )
        self.principal = to_streamed_response_wrapper(
            cnos.principal,
        )
        self.templates = to_streamed_response_wrapper(
            cnos.templates,
        )


class AsyncCnosResourceWithStreamingResponse:
    def __init__(self, cnos: AsyncCnosResource) -> None:
        self._cnos = cnos

        self.analyze = async_to_streamed_response_wrapper(
            cnos.analyze,
        )
        self.execute_function = async_to_streamed_response_wrapper(
            cnos.execute_function,
        )
        self.principal = async_to_streamed_response_wrapper(
            cnos.principal,
        )
        self.templates = async_to_streamed_response_wrapper(
            cnos.templates,
        )
