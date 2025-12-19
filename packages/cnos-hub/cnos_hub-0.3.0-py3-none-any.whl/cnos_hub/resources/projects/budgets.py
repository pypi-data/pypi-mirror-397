# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Optional

import httpx

from ..._types import Body, Omit, Query, Headers, NotGiven, omit, not_given
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
from ...types.projects import budget_resolve_params
from ...types.budgets_json_param import BudgetsJsonParam
from ...types.projects.budget_limits_response import BudgetLimitsResponse
from ...types.projects.budget_resolve_response import BudgetResolveResponse
from ...types.projects.budget_settings_response import BudgetSettingsResponse

__all__ = ["BudgetsResource", "AsyncBudgetsResource"]


class BudgetsResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> BudgetsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/Synext-Solution/cnos-hub-gen-sdk-py#accessing-raw-response-data-eg-headers
        """
        return BudgetsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> BudgetsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/Synext-Solution/cnos-hub-gen-sdk-py#with_streaming_response
        """
        return BudgetsResourceWithStreamingResponse(self)

    def limits(
        self,
        project_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> BudgetLimitsResponse:
        """
        Get effective project limits.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not project_id:
            raise ValueError(f"Expected a non-empty value for `project_id` but received {project_id!r}")
        return self._get(
            f"/v1/projects/{project_id}/limits",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=BudgetLimitsResponse,
        )

    def resolve(
        self,
        project_id: str,
        *,
        requested: Optional[BudgetsJsonParam] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> BudgetResolveResponse:
        """
        Resolve a budget against project/org/system limits.

        Args:
          requested: Requested budget to resolve.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not project_id:
            raise ValueError(f"Expected a non-empty value for `project_id` but received {project_id!r}")
        return self._post(
            f"/v1/projects/{project_id}/budgets/resolve",
            body=maybe_transform({"requested": requested}, budget_resolve_params.BudgetResolveParams),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=BudgetResolveResponse,
        )

    def settings(
        self,
        project_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> BudgetSettingsResponse:
        """
        Get budget settings for a project.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not project_id:
            raise ValueError(f"Expected a non-empty value for `project_id` but received {project_id!r}")
        return self._get(
            f"/v1/projects/{project_id}/budgets/settings",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=BudgetSettingsResponse,
        )


class AsyncBudgetsResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncBudgetsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/Synext-Solution/cnos-hub-gen-sdk-py#accessing-raw-response-data-eg-headers
        """
        return AsyncBudgetsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncBudgetsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/Synext-Solution/cnos-hub-gen-sdk-py#with_streaming_response
        """
        return AsyncBudgetsResourceWithStreamingResponse(self)

    async def limits(
        self,
        project_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> BudgetLimitsResponse:
        """
        Get effective project limits.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not project_id:
            raise ValueError(f"Expected a non-empty value for `project_id` but received {project_id!r}")
        return await self._get(
            f"/v1/projects/{project_id}/limits",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=BudgetLimitsResponse,
        )

    async def resolve(
        self,
        project_id: str,
        *,
        requested: Optional[BudgetsJsonParam] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> BudgetResolveResponse:
        """
        Resolve a budget against project/org/system limits.

        Args:
          requested: Requested budget to resolve.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not project_id:
            raise ValueError(f"Expected a non-empty value for `project_id` but received {project_id!r}")
        return await self._post(
            f"/v1/projects/{project_id}/budgets/resolve",
            body=await async_maybe_transform({"requested": requested}, budget_resolve_params.BudgetResolveParams),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=BudgetResolveResponse,
        )

    async def settings(
        self,
        project_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> BudgetSettingsResponse:
        """
        Get budget settings for a project.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not project_id:
            raise ValueError(f"Expected a non-empty value for `project_id` but received {project_id!r}")
        return await self._get(
            f"/v1/projects/{project_id}/budgets/settings",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=BudgetSettingsResponse,
        )


class BudgetsResourceWithRawResponse:
    def __init__(self, budgets: BudgetsResource) -> None:
        self._budgets = budgets

        self.limits = to_raw_response_wrapper(
            budgets.limits,
        )
        self.resolve = to_raw_response_wrapper(
            budgets.resolve,
        )
        self.settings = to_raw_response_wrapper(
            budgets.settings,
        )


class AsyncBudgetsResourceWithRawResponse:
    def __init__(self, budgets: AsyncBudgetsResource) -> None:
        self._budgets = budgets

        self.limits = async_to_raw_response_wrapper(
            budgets.limits,
        )
        self.resolve = async_to_raw_response_wrapper(
            budgets.resolve,
        )
        self.settings = async_to_raw_response_wrapper(
            budgets.settings,
        )


class BudgetsResourceWithStreamingResponse:
    def __init__(self, budgets: BudgetsResource) -> None:
        self._budgets = budgets

        self.limits = to_streamed_response_wrapper(
            budgets.limits,
        )
        self.resolve = to_streamed_response_wrapper(
            budgets.resolve,
        )
        self.settings = to_streamed_response_wrapper(
            budgets.settings,
        )


class AsyncBudgetsResourceWithStreamingResponse:
    def __init__(self, budgets: AsyncBudgetsResource) -> None:
        self._budgets = budgets

        self.limits = async_to_streamed_response_wrapper(
            budgets.limits,
        )
        self.resolve = async_to_streamed_response_wrapper(
            budgets.resolve,
        )
        self.settings = async_to_streamed_response_wrapper(
            budgets.settings,
        )
