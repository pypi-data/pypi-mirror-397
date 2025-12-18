# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from cnos_hub import CnosHub, AsyncCnosHub
from tests.utils import assert_matches_type
from cnos_hub.types.projects import ExecuteCreateResponse

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestExecute:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_create(self, client: CnosHub) -> None:
        execute = client.projects.execute.create(
            project_id="project_id",
            function="function",
        )
        assert_matches_type(ExecuteCreateResponse, execute, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_create_with_all_params(self, client: CnosHub) -> None:
        execute = client.projects.execute.create(
            project_id="project_id",
            function="function",
            args={"json": [{}]},
            budget={
                "items": 0,
                "steps": 0,
                "time_ms": 0,
            },
            result_encoding="binary",
            trace=True,
            validate_as=["string"],
        )
        assert_matches_type(ExecuteCreateResponse, execute, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_create(self, client: CnosHub) -> None:
        response = client.projects.execute.with_raw_response.create(
            project_id="project_id",
            function="function",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        execute = response.parse()
        assert_matches_type(ExecuteCreateResponse, execute, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_create(self, client: CnosHub) -> None:
        with client.projects.execute.with_streaming_response.create(
            project_id="project_id",
            function="function",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            execute = response.parse()
            assert_matches_type(ExecuteCreateResponse, execute, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_create(self, client: CnosHub) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `project_id` but received ''"):
            client.projects.execute.with_raw_response.create(
                project_id="",
                function="function",
            )


class TestAsyncExecute:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_create(self, async_client: AsyncCnosHub) -> None:
        execute = await async_client.projects.execute.create(
            project_id="project_id",
            function="function",
        )
        assert_matches_type(ExecuteCreateResponse, execute, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_create_with_all_params(self, async_client: AsyncCnosHub) -> None:
        execute = await async_client.projects.execute.create(
            project_id="project_id",
            function="function",
            args={"json": [{}]},
            budget={
                "items": 0,
                "steps": 0,
                "time_ms": 0,
            },
            result_encoding="binary",
            trace=True,
            validate_as=["string"],
        )
        assert_matches_type(ExecuteCreateResponse, execute, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_create(self, async_client: AsyncCnosHub) -> None:
        response = await async_client.projects.execute.with_raw_response.create(
            project_id="project_id",
            function="function",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        execute = await response.parse()
        assert_matches_type(ExecuteCreateResponse, execute, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_create(self, async_client: AsyncCnosHub) -> None:
        async with async_client.projects.execute.with_streaming_response.create(
            project_id="project_id",
            function="function",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            execute = await response.parse()
            assert_matches_type(ExecuteCreateResponse, execute, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_create(self, async_client: AsyncCnosHub) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `project_id` but received ''"):
            await async_client.projects.execute.with_raw_response.create(
                project_id="",
                function="function",
            )
