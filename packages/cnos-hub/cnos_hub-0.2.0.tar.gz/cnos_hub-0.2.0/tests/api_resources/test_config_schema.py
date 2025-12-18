# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from cnos_hub import CnosHub, AsyncCnosHub
from tests.utils import assert_matches_type
from cnos_hub.types import ConfigSchemaOrgResponse, ConfigSchemaSystemResponse, ConfigSchemaProjectResponse

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestConfigSchema:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_org(self, client: CnosHub) -> None:
        config_schema = client.config_schema.org()
        assert_matches_type(ConfigSchemaOrgResponse, config_schema, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_org(self, client: CnosHub) -> None:
        response = client.config_schema.with_raw_response.org()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        config_schema = response.parse()
        assert_matches_type(ConfigSchemaOrgResponse, config_schema, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_org(self, client: CnosHub) -> None:
        with client.config_schema.with_streaming_response.org() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            config_schema = response.parse()
            assert_matches_type(ConfigSchemaOrgResponse, config_schema, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_project(self, client: CnosHub) -> None:
        config_schema = client.config_schema.project()
        assert_matches_type(ConfigSchemaProjectResponse, config_schema, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_project(self, client: CnosHub) -> None:
        response = client.config_schema.with_raw_response.project()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        config_schema = response.parse()
        assert_matches_type(ConfigSchemaProjectResponse, config_schema, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_project(self, client: CnosHub) -> None:
        with client.config_schema.with_streaming_response.project() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            config_schema = response.parse()
            assert_matches_type(ConfigSchemaProjectResponse, config_schema, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_system(self, client: CnosHub) -> None:
        config_schema = client.config_schema.system()
        assert_matches_type(ConfigSchemaSystemResponse, config_schema, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_system(self, client: CnosHub) -> None:
        response = client.config_schema.with_raw_response.system()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        config_schema = response.parse()
        assert_matches_type(ConfigSchemaSystemResponse, config_schema, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_system(self, client: CnosHub) -> None:
        with client.config_schema.with_streaming_response.system() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            config_schema = response.parse()
            assert_matches_type(ConfigSchemaSystemResponse, config_schema, path=["response"])

        assert cast(Any, response.is_closed) is True


class TestAsyncConfigSchema:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_org(self, async_client: AsyncCnosHub) -> None:
        config_schema = await async_client.config_schema.org()
        assert_matches_type(ConfigSchemaOrgResponse, config_schema, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_org(self, async_client: AsyncCnosHub) -> None:
        response = await async_client.config_schema.with_raw_response.org()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        config_schema = await response.parse()
        assert_matches_type(ConfigSchemaOrgResponse, config_schema, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_org(self, async_client: AsyncCnosHub) -> None:
        async with async_client.config_schema.with_streaming_response.org() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            config_schema = await response.parse()
            assert_matches_type(ConfigSchemaOrgResponse, config_schema, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_project(self, async_client: AsyncCnosHub) -> None:
        config_schema = await async_client.config_schema.project()
        assert_matches_type(ConfigSchemaProjectResponse, config_schema, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_project(self, async_client: AsyncCnosHub) -> None:
        response = await async_client.config_schema.with_raw_response.project()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        config_schema = await response.parse()
        assert_matches_type(ConfigSchemaProjectResponse, config_schema, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_project(self, async_client: AsyncCnosHub) -> None:
        async with async_client.config_schema.with_streaming_response.project() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            config_schema = await response.parse()
            assert_matches_type(ConfigSchemaProjectResponse, config_schema, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_system(self, async_client: AsyncCnosHub) -> None:
        config_schema = await async_client.config_schema.system()
        assert_matches_type(ConfigSchemaSystemResponse, config_schema, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_system(self, async_client: AsyncCnosHub) -> None:
        response = await async_client.config_schema.with_raw_response.system()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        config_schema = await response.parse()
        assert_matches_type(ConfigSchemaSystemResponse, config_schema, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_system(self, async_client: AsyncCnosHub) -> None:
        async with async_client.config_schema.with_streaming_response.system() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            config_schema = await response.parse()
            assert_matches_type(ConfigSchemaSystemResponse, config_schema, path=["response"])

        assert cast(Any, response.is_closed) is True
