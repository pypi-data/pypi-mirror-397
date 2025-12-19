# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from cnos_hub import CnosHub, AsyncCnosHub
from tests.utils import assert_matches_type
from cnos_hub.pagination import SyncPage, AsyncPage
from cnos_hub.types.projects import (
    FileListResponse,
    FileCreateResponse,
    FileRetrieveResponse,
)

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestFiles:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_create(self, client: CnosHub) -> None:
        file = client.projects.files.create(
            project_id="project_id",
            name="name",
        )
        assert_matches_type(FileCreateResponse, file, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_create_with_all_params(self, client: CnosHub) -> None:
        file = client.projects.files.create(
            project_id="project_id",
            name="name",
            content_type="content_type",
            data="data",
            data_base64="data_base64",
        )
        assert_matches_type(FileCreateResponse, file, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_create(self, client: CnosHub) -> None:
        response = client.projects.files.with_raw_response.create(
            project_id="project_id",
            name="name",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        file = response.parse()
        assert_matches_type(FileCreateResponse, file, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_create(self, client: CnosHub) -> None:
        with client.projects.files.with_streaming_response.create(
            project_id="project_id",
            name="name",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            file = response.parse()
            assert_matches_type(FileCreateResponse, file, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_create(self, client: CnosHub) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `project_id` but received ''"):
            client.projects.files.with_raw_response.create(
                project_id="",
                name="name",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_retrieve(self, client: CnosHub) -> None:
        file = client.projects.files.retrieve(
            file_id="file_id",
            project_id="project_id",
        )
        assert_matches_type(FileRetrieveResponse, file, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_retrieve(self, client: CnosHub) -> None:
        response = client.projects.files.with_raw_response.retrieve(
            file_id="file_id",
            project_id="project_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        file = response.parse()
        assert_matches_type(FileRetrieveResponse, file, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_retrieve(self, client: CnosHub) -> None:
        with client.projects.files.with_streaming_response.retrieve(
            file_id="file_id",
            project_id="project_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            file = response.parse()
            assert_matches_type(FileRetrieveResponse, file, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_retrieve(self, client: CnosHub) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `project_id` but received ''"):
            client.projects.files.with_raw_response.retrieve(
                file_id="file_id",
                project_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `file_id` but received ''"):
            client.projects.files.with_raw_response.retrieve(
                file_id="",
                project_id="project_id",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_list(self, client: CnosHub) -> None:
        file = client.projects.files.list(
            project_id="project_id",
        )
        assert_matches_type(SyncPage[FileListResponse], file, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_list_with_all_params(self, client: CnosHub) -> None:
        file = client.projects.files.list(
            project_id="project_id",
            cursor="cursor",
            limit=0,
        )
        assert_matches_type(SyncPage[FileListResponse], file, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_list(self, client: CnosHub) -> None:
        response = client.projects.files.with_raw_response.list(
            project_id="project_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        file = response.parse()
        assert_matches_type(SyncPage[FileListResponse], file, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_list(self, client: CnosHub) -> None:
        with client.projects.files.with_streaming_response.list(
            project_id="project_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            file = response.parse()
            assert_matches_type(SyncPage[FileListResponse], file, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_list(self, client: CnosHub) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `project_id` but received ''"):
            client.projects.files.with_raw_response.list(
                project_id="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_delete(self, client: CnosHub) -> None:
        file = client.projects.files.delete(
            file_id="file_id",
            project_id="project_id",
        )
        assert file is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_delete(self, client: CnosHub) -> None:
        response = client.projects.files.with_raw_response.delete(
            file_id="file_id",
            project_id="project_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        file = response.parse()
        assert file is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_delete(self, client: CnosHub) -> None:
        with client.projects.files.with_streaming_response.delete(
            file_id="file_id",
            project_id="project_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            file = response.parse()
            assert file is None

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_delete(self, client: CnosHub) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `project_id` but received ''"):
            client.projects.files.with_raw_response.delete(
                file_id="file_id",
                project_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `file_id` but received ''"):
            client.projects.files.with_raw_response.delete(
                file_id="",
                project_id="project_id",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_content(self, client: CnosHub) -> None:
        file = client.projects.files.content(
            file_id="file_id",
            project_id="project_id",
        )
        assert file is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_content(self, client: CnosHub) -> None:
        response = client.projects.files.with_raw_response.content(
            file_id="file_id",
            project_id="project_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        file = response.parse()
        assert file is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_content(self, client: CnosHub) -> None:
        with client.projects.files.with_streaming_response.content(
            file_id="file_id",
            project_id="project_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            file = response.parse()
            assert file is None

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_content(self, client: CnosHub) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `project_id` but received ''"):
            client.projects.files.with_raw_response.content(
                file_id="file_id",
                project_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `file_id` but received ''"):
            client.projects.files.with_raw_response.content(
                file_id="",
                project_id="project_id",
            )


class TestAsyncFiles:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_create(self, async_client: AsyncCnosHub) -> None:
        file = await async_client.projects.files.create(
            project_id="project_id",
            name="name",
        )
        assert_matches_type(FileCreateResponse, file, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_create_with_all_params(self, async_client: AsyncCnosHub) -> None:
        file = await async_client.projects.files.create(
            project_id="project_id",
            name="name",
            content_type="content_type",
            data="data",
            data_base64="data_base64",
        )
        assert_matches_type(FileCreateResponse, file, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_create(self, async_client: AsyncCnosHub) -> None:
        response = await async_client.projects.files.with_raw_response.create(
            project_id="project_id",
            name="name",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        file = await response.parse()
        assert_matches_type(FileCreateResponse, file, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_create(self, async_client: AsyncCnosHub) -> None:
        async with async_client.projects.files.with_streaming_response.create(
            project_id="project_id",
            name="name",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            file = await response.parse()
            assert_matches_type(FileCreateResponse, file, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_create(self, async_client: AsyncCnosHub) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `project_id` but received ''"):
            await async_client.projects.files.with_raw_response.create(
                project_id="",
                name="name",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_retrieve(self, async_client: AsyncCnosHub) -> None:
        file = await async_client.projects.files.retrieve(
            file_id="file_id",
            project_id="project_id",
        )
        assert_matches_type(FileRetrieveResponse, file, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_retrieve(self, async_client: AsyncCnosHub) -> None:
        response = await async_client.projects.files.with_raw_response.retrieve(
            file_id="file_id",
            project_id="project_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        file = await response.parse()
        assert_matches_type(FileRetrieveResponse, file, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_retrieve(self, async_client: AsyncCnosHub) -> None:
        async with async_client.projects.files.with_streaming_response.retrieve(
            file_id="file_id",
            project_id="project_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            file = await response.parse()
            assert_matches_type(FileRetrieveResponse, file, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_retrieve(self, async_client: AsyncCnosHub) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `project_id` but received ''"):
            await async_client.projects.files.with_raw_response.retrieve(
                file_id="file_id",
                project_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `file_id` but received ''"):
            await async_client.projects.files.with_raw_response.retrieve(
                file_id="",
                project_id="project_id",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_list(self, async_client: AsyncCnosHub) -> None:
        file = await async_client.projects.files.list(
            project_id="project_id",
        )
        assert_matches_type(AsyncPage[FileListResponse], file, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_list_with_all_params(self, async_client: AsyncCnosHub) -> None:
        file = await async_client.projects.files.list(
            project_id="project_id",
            cursor="cursor",
            limit=0,
        )
        assert_matches_type(AsyncPage[FileListResponse], file, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_list(self, async_client: AsyncCnosHub) -> None:
        response = await async_client.projects.files.with_raw_response.list(
            project_id="project_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        file = await response.parse()
        assert_matches_type(AsyncPage[FileListResponse], file, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_list(self, async_client: AsyncCnosHub) -> None:
        async with async_client.projects.files.with_streaming_response.list(
            project_id="project_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            file = await response.parse()
            assert_matches_type(AsyncPage[FileListResponse], file, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_list(self, async_client: AsyncCnosHub) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `project_id` but received ''"):
            await async_client.projects.files.with_raw_response.list(
                project_id="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_delete(self, async_client: AsyncCnosHub) -> None:
        file = await async_client.projects.files.delete(
            file_id="file_id",
            project_id="project_id",
        )
        assert file is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_delete(self, async_client: AsyncCnosHub) -> None:
        response = await async_client.projects.files.with_raw_response.delete(
            file_id="file_id",
            project_id="project_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        file = await response.parse()
        assert file is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_delete(self, async_client: AsyncCnosHub) -> None:
        async with async_client.projects.files.with_streaming_response.delete(
            file_id="file_id",
            project_id="project_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            file = await response.parse()
            assert file is None

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_delete(self, async_client: AsyncCnosHub) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `project_id` but received ''"):
            await async_client.projects.files.with_raw_response.delete(
                file_id="file_id",
                project_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `file_id` but received ''"):
            await async_client.projects.files.with_raw_response.delete(
                file_id="",
                project_id="project_id",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_content(self, async_client: AsyncCnosHub) -> None:
        file = await async_client.projects.files.content(
            file_id="file_id",
            project_id="project_id",
        )
        assert file is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_content(self, async_client: AsyncCnosHub) -> None:
        response = await async_client.projects.files.with_raw_response.content(
            file_id="file_id",
            project_id="project_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        file = await response.parse()
        assert file is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_content(self, async_client: AsyncCnosHub) -> None:
        async with async_client.projects.files.with_streaming_response.content(
            file_id="file_id",
            project_id="project_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            file = await response.parse()
            assert file is None

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_content(self, async_client: AsyncCnosHub) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `project_id` but received ''"):
            await async_client.projects.files.with_raw_response.content(
                file_id="file_id",
                project_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `file_id` but received ''"):
            await async_client.projects.files.with_raw_response.content(
                file_id="",
                project_id="project_id",
            )
