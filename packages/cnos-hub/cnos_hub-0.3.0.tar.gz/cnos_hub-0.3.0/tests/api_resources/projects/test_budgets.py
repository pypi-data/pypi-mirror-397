# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from cnos_hub import CnosHub, AsyncCnosHub
from tests.utils import assert_matches_type
from cnos_hub.types.projects import (
    BudgetLimitsResponse,
    BudgetResolveResponse,
    BudgetSettingsResponse,
)

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestBudgets:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_limits(self, client: CnosHub) -> None:
        budget = client.projects.budgets.limits(
            "project_id",
        )
        assert_matches_type(BudgetLimitsResponse, budget, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_limits(self, client: CnosHub) -> None:
        response = client.projects.budgets.with_raw_response.limits(
            "project_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        budget = response.parse()
        assert_matches_type(BudgetLimitsResponse, budget, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_limits(self, client: CnosHub) -> None:
        with client.projects.budgets.with_streaming_response.limits(
            "project_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            budget = response.parse()
            assert_matches_type(BudgetLimitsResponse, budget, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_limits(self, client: CnosHub) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `project_id` but received ''"):
            client.projects.budgets.with_raw_response.limits(
                "",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_resolve(self, client: CnosHub) -> None:
        budget = client.projects.budgets.resolve(
            project_id="project_id",
        )
        assert_matches_type(BudgetResolveResponse, budget, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_resolve_with_all_params(self, client: CnosHub) -> None:
        budget = client.projects.budgets.resolve(
            project_id="project_id",
            requested={
                "items": 0,
                "steps": 0,
                "time_ms": 0,
            },
        )
        assert_matches_type(BudgetResolveResponse, budget, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_resolve(self, client: CnosHub) -> None:
        response = client.projects.budgets.with_raw_response.resolve(
            project_id="project_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        budget = response.parse()
        assert_matches_type(BudgetResolveResponse, budget, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_resolve(self, client: CnosHub) -> None:
        with client.projects.budgets.with_streaming_response.resolve(
            project_id="project_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            budget = response.parse()
            assert_matches_type(BudgetResolveResponse, budget, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_resolve(self, client: CnosHub) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `project_id` but received ''"):
            client.projects.budgets.with_raw_response.resolve(
                project_id="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_settings(self, client: CnosHub) -> None:
        budget = client.projects.budgets.settings(
            "project_id",
        )
        assert_matches_type(BudgetSettingsResponse, budget, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_settings(self, client: CnosHub) -> None:
        response = client.projects.budgets.with_raw_response.settings(
            "project_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        budget = response.parse()
        assert_matches_type(BudgetSettingsResponse, budget, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_settings(self, client: CnosHub) -> None:
        with client.projects.budgets.with_streaming_response.settings(
            "project_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            budget = response.parse()
            assert_matches_type(BudgetSettingsResponse, budget, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_settings(self, client: CnosHub) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `project_id` but received ''"):
            client.projects.budgets.with_raw_response.settings(
                "",
            )


class TestAsyncBudgets:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_limits(self, async_client: AsyncCnosHub) -> None:
        budget = await async_client.projects.budgets.limits(
            "project_id",
        )
        assert_matches_type(BudgetLimitsResponse, budget, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_limits(self, async_client: AsyncCnosHub) -> None:
        response = await async_client.projects.budgets.with_raw_response.limits(
            "project_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        budget = await response.parse()
        assert_matches_type(BudgetLimitsResponse, budget, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_limits(self, async_client: AsyncCnosHub) -> None:
        async with async_client.projects.budgets.with_streaming_response.limits(
            "project_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            budget = await response.parse()
            assert_matches_type(BudgetLimitsResponse, budget, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_limits(self, async_client: AsyncCnosHub) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `project_id` but received ''"):
            await async_client.projects.budgets.with_raw_response.limits(
                "",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_resolve(self, async_client: AsyncCnosHub) -> None:
        budget = await async_client.projects.budgets.resolve(
            project_id="project_id",
        )
        assert_matches_type(BudgetResolveResponse, budget, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_resolve_with_all_params(self, async_client: AsyncCnosHub) -> None:
        budget = await async_client.projects.budgets.resolve(
            project_id="project_id",
            requested={
                "items": 0,
                "steps": 0,
                "time_ms": 0,
            },
        )
        assert_matches_type(BudgetResolveResponse, budget, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_resolve(self, async_client: AsyncCnosHub) -> None:
        response = await async_client.projects.budgets.with_raw_response.resolve(
            project_id="project_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        budget = await response.parse()
        assert_matches_type(BudgetResolveResponse, budget, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_resolve(self, async_client: AsyncCnosHub) -> None:
        async with async_client.projects.budgets.with_streaming_response.resolve(
            project_id="project_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            budget = await response.parse()
            assert_matches_type(BudgetResolveResponse, budget, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_resolve(self, async_client: AsyncCnosHub) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `project_id` but received ''"):
            await async_client.projects.budgets.with_raw_response.resolve(
                project_id="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_settings(self, async_client: AsyncCnosHub) -> None:
        budget = await async_client.projects.budgets.settings(
            "project_id",
        )
        assert_matches_type(BudgetSettingsResponse, budget, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_settings(self, async_client: AsyncCnosHub) -> None:
        response = await async_client.projects.budgets.with_raw_response.settings(
            "project_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        budget = await response.parse()
        assert_matches_type(BudgetSettingsResponse, budget, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_settings(self, async_client: AsyncCnosHub) -> None:
        async with async_client.projects.budgets.with_streaming_response.settings(
            "project_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            budget = await response.parse()
            assert_matches_type(BudgetSettingsResponse, budget, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_settings(self, async_client: AsyncCnosHub) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `project_id` but received ''"):
            await async_client.projects.budgets.with_raw_response.settings(
                "",
            )
