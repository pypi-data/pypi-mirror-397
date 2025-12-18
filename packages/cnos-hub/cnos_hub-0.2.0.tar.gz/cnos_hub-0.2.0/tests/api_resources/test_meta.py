# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from cnos_hub import CnosHub, AsyncCnosHub
from tests.utils import assert_matches_type
from cnos_hub.types import MetaGetResponse, MetaEndpointsResponse, MetaCapabilitiesResponse

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestMeta:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_capabilities(self, client: CnosHub) -> None:
        meta = client.meta.capabilities()
        assert_matches_type(MetaCapabilitiesResponse, meta, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_capabilities(self, client: CnosHub) -> None:
        response = client.meta.with_raw_response.capabilities()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        meta = response.parse()
        assert_matches_type(MetaCapabilitiesResponse, meta, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_capabilities(self, client: CnosHub) -> None:
        with client.meta.with_streaming_response.capabilities() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            meta = response.parse()
            assert_matches_type(MetaCapabilitiesResponse, meta, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_endpoints(self, client: CnosHub) -> None:
        meta = client.meta.endpoints()
        assert_matches_type(MetaEndpointsResponse, meta, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_endpoints(self, client: CnosHub) -> None:
        response = client.meta.with_raw_response.endpoints()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        meta = response.parse()
        assert_matches_type(MetaEndpointsResponse, meta, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_endpoints(self, client: CnosHub) -> None:
        with client.meta.with_streaming_response.endpoints() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            meta = response.parse()
            assert_matches_type(MetaEndpointsResponse, meta, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_get(self, client: CnosHub) -> None:
        meta = client.meta.get()
        assert_matches_type(MetaGetResponse, meta, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_get(self, client: CnosHub) -> None:
        response = client.meta.with_raw_response.get()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        meta = response.parse()
        assert_matches_type(MetaGetResponse, meta, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_get(self, client: CnosHub) -> None:
        with client.meta.with_streaming_response.get() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            meta = response.parse()
            assert_matches_type(MetaGetResponse, meta, path=["response"])

        assert cast(Any, response.is_closed) is True


class TestAsyncMeta:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_capabilities(self, async_client: AsyncCnosHub) -> None:
        meta = await async_client.meta.capabilities()
        assert_matches_type(MetaCapabilitiesResponse, meta, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_capabilities(self, async_client: AsyncCnosHub) -> None:
        response = await async_client.meta.with_raw_response.capabilities()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        meta = await response.parse()
        assert_matches_type(MetaCapabilitiesResponse, meta, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_capabilities(self, async_client: AsyncCnosHub) -> None:
        async with async_client.meta.with_streaming_response.capabilities() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            meta = await response.parse()
            assert_matches_type(MetaCapabilitiesResponse, meta, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_endpoints(self, async_client: AsyncCnosHub) -> None:
        meta = await async_client.meta.endpoints()
        assert_matches_type(MetaEndpointsResponse, meta, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_endpoints(self, async_client: AsyncCnosHub) -> None:
        response = await async_client.meta.with_raw_response.endpoints()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        meta = await response.parse()
        assert_matches_type(MetaEndpointsResponse, meta, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_endpoints(self, async_client: AsyncCnosHub) -> None:
        async with async_client.meta.with_streaming_response.endpoints() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            meta = await response.parse()
            assert_matches_type(MetaEndpointsResponse, meta, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_get(self, async_client: AsyncCnosHub) -> None:
        meta = await async_client.meta.get()
        assert_matches_type(MetaGetResponse, meta, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_get(self, async_client: AsyncCnosHub) -> None:
        response = await async_client.meta.with_raw_response.get()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        meta = await response.parse()
        assert_matches_type(MetaGetResponse, meta, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_get(self, async_client: AsyncCnosHub) -> None:
        async with async_client.meta.with_streaming_response.get() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            meta = await response.parse()
            assert_matches_type(MetaGetResponse, meta, path=["response"])

        assert cast(Any, response.is_closed) is True
