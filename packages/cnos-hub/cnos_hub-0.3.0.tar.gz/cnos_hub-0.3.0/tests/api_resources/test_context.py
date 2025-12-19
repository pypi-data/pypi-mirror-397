# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from cnos_hub import CnosHub, AsyncCnosHub
from tests.utils import assert_matches_type
from cnos_hub.types import ContextOrgResponse, ContextProjectResponse

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestContext:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_org(self, client: CnosHub) -> None:
        context = client.context.org()
        assert_matches_type(ContextOrgResponse, context, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_org(self, client: CnosHub) -> None:
        response = client.context.with_raw_response.org()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        context = response.parse()
        assert_matches_type(ContextOrgResponse, context, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_org(self, client: CnosHub) -> None:
        with client.context.with_streaming_response.org() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            context = response.parse()
            assert_matches_type(ContextOrgResponse, context, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_project(self, client: CnosHub) -> None:
        context = client.context.project()
        assert_matches_type(ContextProjectResponse, context, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_project(self, client: CnosHub) -> None:
        response = client.context.with_raw_response.project()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        context = response.parse()
        assert_matches_type(ContextProjectResponse, context, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_project(self, client: CnosHub) -> None:
        with client.context.with_streaming_response.project() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            context = response.parse()
            assert_matches_type(ContextProjectResponse, context, path=["response"])

        assert cast(Any, response.is_closed) is True


class TestAsyncContext:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_org(self, async_client: AsyncCnosHub) -> None:
        context = await async_client.context.org()
        assert_matches_type(ContextOrgResponse, context, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_org(self, async_client: AsyncCnosHub) -> None:
        response = await async_client.context.with_raw_response.org()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        context = await response.parse()
        assert_matches_type(ContextOrgResponse, context, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_org(self, async_client: AsyncCnosHub) -> None:
        async with async_client.context.with_streaming_response.org() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            context = await response.parse()
            assert_matches_type(ContextOrgResponse, context, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_project(self, async_client: AsyncCnosHub) -> None:
        context = await async_client.context.project()
        assert_matches_type(ContextProjectResponse, context, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_project(self, async_client: AsyncCnosHub) -> None:
        response = await async_client.context.with_raw_response.project()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        context = await response.parse()
        assert_matches_type(ContextProjectResponse, context, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_project(self, async_client: AsyncCnosHub) -> None:
        async with async_client.context.with_streaming_response.project() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            context = await response.parse()
            assert_matches_type(ContextProjectResponse, context, path=["response"])

        assert cast(Any, response.is_closed) is True
