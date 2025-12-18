# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from cnos_hub import CnosHub, AsyncCnosHub
from tests.utils import assert_matches_type
from cnos_hub.types import AuthzTestResponse

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestAuthz:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_test(self, client: CnosHub) -> None:
        authz = client.authz.test(
            resources=[{"kind": "kind"}],
        )
        assert_matches_type(AuthzTestResponse, authz, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_test(self, client: CnosHub) -> None:
        response = client.authz.with_raw_response.test(
            resources=[{"kind": "kind"}],
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        authz = response.parse()
        assert_matches_type(AuthzTestResponse, authz, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_test(self, client: CnosHub) -> None:
        with client.authz.with_streaming_response.test(
            resources=[{"kind": "kind"}],
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            authz = response.parse()
            assert_matches_type(AuthzTestResponse, authz, path=["response"])

        assert cast(Any, response.is_closed) is True


class TestAsyncAuthz:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_test(self, async_client: AsyncCnosHub) -> None:
        authz = await async_client.authz.test(
            resources=[{"kind": "kind"}],
        )
        assert_matches_type(AuthzTestResponse, authz, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_test(self, async_client: AsyncCnosHub) -> None:
        response = await async_client.authz.with_raw_response.test(
            resources=[{"kind": "kind"}],
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        authz = await response.parse()
        assert_matches_type(AuthzTestResponse, authz, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_test(self, async_client: AsyncCnosHub) -> None:
        async with async_client.authz.with_streaming_response.test(
            resources=[{"kind": "kind"}],
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            authz = await response.parse()
            assert_matches_type(AuthzTestResponse, authz, path=["response"])

        assert cast(Any, response.is_closed) is True
