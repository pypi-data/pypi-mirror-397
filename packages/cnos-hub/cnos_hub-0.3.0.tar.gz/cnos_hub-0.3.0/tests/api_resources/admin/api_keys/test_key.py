# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from cnos_hub import CnosHub, AsyncCnosHub
from tests.utils import assert_matches_type
from cnos_hub.types.shared import APIKeyDto
from cnos_hub.types.admin.api_keys import KeyRotateResponse

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestKey:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_retrieve(self, client: CnosHub) -> None:
        key = client.admin.api_keys.key.retrieve(
            "key_id",
        )
        assert_matches_type(APIKeyDto, key, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_retrieve(self, client: CnosHub) -> None:
        response = client.admin.api_keys.key.with_raw_response.retrieve(
            "key_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        key = response.parse()
        assert_matches_type(APIKeyDto, key, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_retrieve(self, client: CnosHub) -> None:
        with client.admin.api_keys.key.with_streaming_response.retrieve(
            "key_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            key = response.parse()
            assert_matches_type(APIKeyDto, key, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_retrieve(self, client: CnosHub) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `key_id` but received ''"):
            client.admin.api_keys.key.with_raw_response.retrieve(
                "",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_update(self, client: CnosHub) -> None:
        key = client.admin.api_keys.key.update(
            key_id="key_id",
        )
        assert_matches_type(APIKeyDto, key, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_update_with_all_params(self, client: CnosHub) -> None:
        key = client.admin.api_keys.key.update(
            key_id="key_id",
            capabilities=["OrgRead"],
            description="description",
            name="name",
            roles=["string"],
        )
        assert_matches_type(APIKeyDto, key, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_update(self, client: CnosHub) -> None:
        response = client.admin.api_keys.key.with_raw_response.update(
            key_id="key_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        key = response.parse()
        assert_matches_type(APIKeyDto, key, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_update(self, client: CnosHub) -> None:
        with client.admin.api_keys.key.with_streaming_response.update(
            key_id="key_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            key = response.parse()
            assert_matches_type(APIKeyDto, key, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_update(self, client: CnosHub) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `key_id` but received ''"):
            client.admin.api_keys.key.with_raw_response.update(
                key_id="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_delete(self, client: CnosHub) -> None:
        key = client.admin.api_keys.key.delete(
            "key_id",
        )
        assert key is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_delete(self, client: CnosHub) -> None:
        response = client.admin.api_keys.key.with_raw_response.delete(
            "key_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        key = response.parse()
        assert key is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_delete(self, client: CnosHub) -> None:
        with client.admin.api_keys.key.with_streaming_response.delete(
            "key_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            key = response.parse()
            assert key is None

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_delete(self, client: CnosHub) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `key_id` but received ''"):
            client.admin.api_keys.key.with_raw_response.delete(
                "",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_rotate(self, client: CnosHub) -> None:
        key = client.admin.api_keys.key.rotate(
            "key_id",
        )
        assert_matches_type(KeyRotateResponse, key, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_rotate(self, client: CnosHub) -> None:
        response = client.admin.api_keys.key.with_raw_response.rotate(
            "key_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        key = response.parse()
        assert_matches_type(KeyRotateResponse, key, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_rotate(self, client: CnosHub) -> None:
        with client.admin.api_keys.key.with_streaming_response.rotate(
            "key_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            key = response.parse()
            assert_matches_type(KeyRotateResponse, key, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_rotate(self, client: CnosHub) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `key_id` but received ''"):
            client.admin.api_keys.key.with_raw_response.rotate(
                "",
            )


class TestAsyncKey:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_retrieve(self, async_client: AsyncCnosHub) -> None:
        key = await async_client.admin.api_keys.key.retrieve(
            "key_id",
        )
        assert_matches_type(APIKeyDto, key, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_retrieve(self, async_client: AsyncCnosHub) -> None:
        response = await async_client.admin.api_keys.key.with_raw_response.retrieve(
            "key_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        key = await response.parse()
        assert_matches_type(APIKeyDto, key, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_retrieve(self, async_client: AsyncCnosHub) -> None:
        async with async_client.admin.api_keys.key.with_streaming_response.retrieve(
            "key_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            key = await response.parse()
            assert_matches_type(APIKeyDto, key, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_retrieve(self, async_client: AsyncCnosHub) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `key_id` but received ''"):
            await async_client.admin.api_keys.key.with_raw_response.retrieve(
                "",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_update(self, async_client: AsyncCnosHub) -> None:
        key = await async_client.admin.api_keys.key.update(
            key_id="key_id",
        )
        assert_matches_type(APIKeyDto, key, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_update_with_all_params(self, async_client: AsyncCnosHub) -> None:
        key = await async_client.admin.api_keys.key.update(
            key_id="key_id",
            capabilities=["OrgRead"],
            description="description",
            name="name",
            roles=["string"],
        )
        assert_matches_type(APIKeyDto, key, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_update(self, async_client: AsyncCnosHub) -> None:
        response = await async_client.admin.api_keys.key.with_raw_response.update(
            key_id="key_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        key = await response.parse()
        assert_matches_type(APIKeyDto, key, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_update(self, async_client: AsyncCnosHub) -> None:
        async with async_client.admin.api_keys.key.with_streaming_response.update(
            key_id="key_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            key = await response.parse()
            assert_matches_type(APIKeyDto, key, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_update(self, async_client: AsyncCnosHub) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `key_id` but received ''"):
            await async_client.admin.api_keys.key.with_raw_response.update(
                key_id="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_delete(self, async_client: AsyncCnosHub) -> None:
        key = await async_client.admin.api_keys.key.delete(
            "key_id",
        )
        assert key is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_delete(self, async_client: AsyncCnosHub) -> None:
        response = await async_client.admin.api_keys.key.with_raw_response.delete(
            "key_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        key = await response.parse()
        assert key is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_delete(self, async_client: AsyncCnosHub) -> None:
        async with async_client.admin.api_keys.key.with_streaming_response.delete(
            "key_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            key = await response.parse()
            assert key is None

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_delete(self, async_client: AsyncCnosHub) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `key_id` but received ''"):
            await async_client.admin.api_keys.key.with_raw_response.delete(
                "",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_rotate(self, async_client: AsyncCnosHub) -> None:
        key = await async_client.admin.api_keys.key.rotate(
            "key_id",
        )
        assert_matches_type(KeyRotateResponse, key, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_rotate(self, async_client: AsyncCnosHub) -> None:
        response = await async_client.admin.api_keys.key.with_raw_response.rotate(
            "key_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        key = await response.parse()
        assert_matches_type(KeyRotateResponse, key, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_rotate(self, async_client: AsyncCnosHub) -> None:
        async with async_client.admin.api_keys.key.with_streaming_response.rotate(
            "key_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            key = await response.parse()
            assert_matches_type(KeyRotateResponse, key, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_rotate(self, async_client: AsyncCnosHub) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `key_id` but received ''"):
            await async_client.admin.api_keys.key.with_raw_response.rotate(
                "",
            )
