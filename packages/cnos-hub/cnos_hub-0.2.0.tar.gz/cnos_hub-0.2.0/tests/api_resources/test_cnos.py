# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from cnos_hub import CnosHub, AsyncCnosHub
from tests.utils import assert_matches_type
from cnos_hub.types import (
    CnoAnalyzeResponse,
    CnoPrincipalResponse,
    CnoTemplatesResponse,
    CnoExecuteFunctionResponse,
)

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestCnos:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_analyze(self, client: CnosHub) -> None:
        cno = client.cnos.analyze(
            modules=[
                {
                    "path": "main",
                    "source": "pub fn add(a: number, b: number): number { a + b }",
                }
            ],
            root="main",
        )
        assert_matches_type(CnoAnalyzeResponse, cno, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_analyze_with_all_params(self, client: CnosHub) -> None:
        cno = client.cnos.analyze(
            modules=[
                {
                    "path": "main",
                    "source": "pub fn add(a: number, b: number): number { a + b }",
                }
            ],
            root="main",
            options={
                "include_entrypoints": True,
                "include_functions": True,
                "include_types": True,
                "runtime_lower": True,
            },
        )
        assert_matches_type(CnoAnalyzeResponse, cno, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_analyze(self, client: CnosHub) -> None:
        response = client.cnos.with_raw_response.analyze(
            modules=[
                {
                    "path": "main",
                    "source": "pub fn add(a: number, b: number): number { a + b }",
                }
            ],
            root="main",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        cno = response.parse()
        assert_matches_type(CnoAnalyzeResponse, cno, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_analyze(self, client: CnosHub) -> None:
        with client.cnos.with_streaming_response.analyze(
            modules=[
                {
                    "path": "main",
                    "source": "pub fn add(a: number, b: number): number { a + b }",
                }
            ],
            root="main",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            cno = response.parse()
            assert_matches_type(CnoAnalyzeResponse, cno, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_execute_function(self, client: CnosHub) -> None:
        cno = client.cnos.execute_function(
            function="greet",
            modules=[
                {
                    "path": "main",
                    "source": 'pub fn greet(name: string): string { "hi " + name }',
                }
            ],
            root="main",
        )
        assert_matches_type(CnoExecuteFunctionResponse, cno, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_execute_function_with_all_params(self, client: CnosHub) -> None:
        cno = client.cnos.execute_function(
            function="greet",
            modules=[
                {
                    "path": "main",
                    "source": 'pub fn greet(name: string): string { "hi " + name }',
                }
            ],
            root="main",
            args={"json": {"name": "bar"}},
            budget={
                "items": 0,
                "steps": 0,
                "time_ms": 5000,
            },
            result_encoding="json",
            trace=False,
            validate_as=["string"],
        )
        assert_matches_type(CnoExecuteFunctionResponse, cno, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_execute_function(self, client: CnosHub) -> None:
        response = client.cnos.with_raw_response.execute_function(
            function="greet",
            modules=[
                {
                    "path": "main",
                    "source": 'pub fn greet(name: string): string { "hi " + name }',
                }
            ],
            root="main",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        cno = response.parse()
        assert_matches_type(CnoExecuteFunctionResponse, cno, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_execute_function(self, client: CnosHub) -> None:
        with client.cnos.with_streaming_response.execute_function(
            function="greet",
            modules=[
                {
                    "path": "main",
                    "source": 'pub fn greet(name: string): string { "hi " + name }',
                }
            ],
            root="main",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            cno = response.parse()
            assert_matches_type(CnoExecuteFunctionResponse, cno, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_principal(self, client: CnosHub) -> None:
        cno = client.cnos.principal()
        assert_matches_type(CnoPrincipalResponse, cno, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_principal(self, client: CnosHub) -> None:
        response = client.cnos.with_raw_response.principal()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        cno = response.parse()
        assert_matches_type(CnoPrincipalResponse, cno, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_principal(self, client: CnosHub) -> None:
        with client.cnos.with_streaming_response.principal() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            cno = response.parse()
            assert_matches_type(CnoPrincipalResponse, cno, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_templates(self, client: CnosHub) -> None:
        cno = client.cnos.templates()
        assert_matches_type(CnoTemplatesResponse, cno, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_templates(self, client: CnosHub) -> None:
        response = client.cnos.with_raw_response.templates()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        cno = response.parse()
        assert_matches_type(CnoTemplatesResponse, cno, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_templates(self, client: CnosHub) -> None:
        with client.cnos.with_streaming_response.templates() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            cno = response.parse()
            assert_matches_type(CnoTemplatesResponse, cno, path=["response"])

        assert cast(Any, response.is_closed) is True


class TestAsyncCnos:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_analyze(self, async_client: AsyncCnosHub) -> None:
        cno = await async_client.cnos.analyze(
            modules=[
                {
                    "path": "main",
                    "source": "pub fn add(a: number, b: number): number { a + b }",
                }
            ],
            root="main",
        )
        assert_matches_type(CnoAnalyzeResponse, cno, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_analyze_with_all_params(self, async_client: AsyncCnosHub) -> None:
        cno = await async_client.cnos.analyze(
            modules=[
                {
                    "path": "main",
                    "source": "pub fn add(a: number, b: number): number { a + b }",
                }
            ],
            root="main",
            options={
                "include_entrypoints": True,
                "include_functions": True,
                "include_types": True,
                "runtime_lower": True,
            },
        )
        assert_matches_type(CnoAnalyzeResponse, cno, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_analyze(self, async_client: AsyncCnosHub) -> None:
        response = await async_client.cnos.with_raw_response.analyze(
            modules=[
                {
                    "path": "main",
                    "source": "pub fn add(a: number, b: number): number { a + b }",
                }
            ],
            root="main",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        cno = await response.parse()
        assert_matches_type(CnoAnalyzeResponse, cno, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_analyze(self, async_client: AsyncCnosHub) -> None:
        async with async_client.cnos.with_streaming_response.analyze(
            modules=[
                {
                    "path": "main",
                    "source": "pub fn add(a: number, b: number): number { a + b }",
                }
            ],
            root="main",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            cno = await response.parse()
            assert_matches_type(CnoAnalyzeResponse, cno, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_execute_function(self, async_client: AsyncCnosHub) -> None:
        cno = await async_client.cnos.execute_function(
            function="greet",
            modules=[
                {
                    "path": "main",
                    "source": 'pub fn greet(name: string): string { "hi " + name }',
                }
            ],
            root="main",
        )
        assert_matches_type(CnoExecuteFunctionResponse, cno, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_execute_function_with_all_params(self, async_client: AsyncCnosHub) -> None:
        cno = await async_client.cnos.execute_function(
            function="greet",
            modules=[
                {
                    "path": "main",
                    "source": 'pub fn greet(name: string): string { "hi " + name }',
                }
            ],
            root="main",
            args={"json": {"name": "bar"}},
            budget={
                "items": 0,
                "steps": 0,
                "time_ms": 5000,
            },
            result_encoding="json",
            trace=False,
            validate_as=["string"],
        )
        assert_matches_type(CnoExecuteFunctionResponse, cno, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_execute_function(self, async_client: AsyncCnosHub) -> None:
        response = await async_client.cnos.with_raw_response.execute_function(
            function="greet",
            modules=[
                {
                    "path": "main",
                    "source": 'pub fn greet(name: string): string { "hi " + name }',
                }
            ],
            root="main",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        cno = await response.parse()
        assert_matches_type(CnoExecuteFunctionResponse, cno, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_execute_function(self, async_client: AsyncCnosHub) -> None:
        async with async_client.cnos.with_streaming_response.execute_function(
            function="greet",
            modules=[
                {
                    "path": "main",
                    "source": 'pub fn greet(name: string): string { "hi " + name }',
                }
            ],
            root="main",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            cno = await response.parse()
            assert_matches_type(CnoExecuteFunctionResponse, cno, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_principal(self, async_client: AsyncCnosHub) -> None:
        cno = await async_client.cnos.principal()
        assert_matches_type(CnoPrincipalResponse, cno, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_principal(self, async_client: AsyncCnosHub) -> None:
        response = await async_client.cnos.with_raw_response.principal()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        cno = await response.parse()
        assert_matches_type(CnoPrincipalResponse, cno, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_principal(self, async_client: AsyncCnosHub) -> None:
        async with async_client.cnos.with_streaming_response.principal() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            cno = await response.parse()
            assert_matches_type(CnoPrincipalResponse, cno, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_templates(self, async_client: AsyncCnosHub) -> None:
        cno = await async_client.cnos.templates()
        assert_matches_type(CnoTemplatesResponse, cno, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_templates(self, async_client: AsyncCnosHub) -> None:
        response = await async_client.cnos.with_raw_response.templates()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        cno = await response.parse()
        assert_matches_type(CnoTemplatesResponse, cno, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_templates(self, async_client: AsyncCnosHub) -> None:
        async with async_client.cnos.with_streaming_response.templates() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            cno = await response.parse()
            assert_matches_type(CnoTemplatesResponse, cno, path=["response"])

        assert cast(Any, response.is_closed) is True
