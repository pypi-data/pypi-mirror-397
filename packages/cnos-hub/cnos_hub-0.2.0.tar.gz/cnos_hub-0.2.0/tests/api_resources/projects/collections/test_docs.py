# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from cnos_hub import CnosHub, AsyncCnosHub
from tests.utils import assert_matches_type
from cnos_hub.pagination import SyncPage, AsyncPage
from cnos_hub.types.projects.collections import (
    DocListResponse,
    DocCreateResponse,
    DocReplaceResponse,
    DocRetrieveResponse,
)

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestDocs:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_create(self, client: CnosHub) -> None:
        doc = client.projects.collections.docs.create(
            name="name",
            project_id="project_id",
            value={"foo": "bar"},
        )
        assert_matches_type(DocCreateResponse, doc, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_create_with_all_params(self, client: CnosHub) -> None:
        doc = client.projects.collections.docs.create(
            name="name",
            project_id="project_id",
            value={"foo": "bar"},
            id="id",
        )
        assert_matches_type(DocCreateResponse, doc, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_create(self, client: CnosHub) -> None:
        response = client.projects.collections.docs.with_raw_response.create(
            name="name",
            project_id="project_id",
            value={"foo": "bar"},
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        doc = response.parse()
        assert_matches_type(DocCreateResponse, doc, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_create(self, client: CnosHub) -> None:
        with client.projects.collections.docs.with_streaming_response.create(
            name="name",
            project_id="project_id",
            value={"foo": "bar"},
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            doc = response.parse()
            assert_matches_type(DocCreateResponse, doc, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_create(self, client: CnosHub) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `project_id` but received ''"):
            client.projects.collections.docs.with_raw_response.create(
                name="name",
                project_id="",
                value={"foo": "bar"},
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `name` but received ''"):
            client.projects.collections.docs.with_raw_response.create(
                name="",
                project_id="project_id",
                value={"foo": "bar"},
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_retrieve(self, client: CnosHub) -> None:
        doc = client.projects.collections.docs.retrieve(
            doc_id="doc_id",
            project_id="project_id",
            name="name",
            include_deleted=True,
        )
        assert_matches_type(DocRetrieveResponse, doc, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_retrieve(self, client: CnosHub) -> None:
        response = client.projects.collections.docs.with_raw_response.retrieve(
            doc_id="doc_id",
            project_id="project_id",
            name="name",
            include_deleted=True,
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        doc = response.parse()
        assert_matches_type(DocRetrieveResponse, doc, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_retrieve(self, client: CnosHub) -> None:
        with client.projects.collections.docs.with_streaming_response.retrieve(
            doc_id="doc_id",
            project_id="project_id",
            name="name",
            include_deleted=True,
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            doc = response.parse()
            assert_matches_type(DocRetrieveResponse, doc, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_retrieve(self, client: CnosHub) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `project_id` but received ''"):
            client.projects.collections.docs.with_raw_response.retrieve(
                doc_id="doc_id",
                project_id="",
                name="name",
                include_deleted=True,
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `name` but received ''"):
            client.projects.collections.docs.with_raw_response.retrieve(
                doc_id="doc_id",
                project_id="project_id",
                name="",
                include_deleted=True,
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `doc_id` but received ''"):
            client.projects.collections.docs.with_raw_response.retrieve(
                doc_id="",
                project_id="project_id",
                name="name",
                include_deleted=True,
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_list(self, client: CnosHub) -> None:
        doc = client.projects.collections.docs.list(
            name="name",
            project_id="project_id",
            include_deleted=True,
        )
        assert_matches_type(SyncPage[DocListResponse], doc, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_list_with_all_params(self, client: CnosHub) -> None:
        doc = client.projects.collections.docs.list(
            name="name",
            project_id="project_id",
            include_deleted=True,
            cursor="cursor",
            limit=0,
        )
        assert_matches_type(SyncPage[DocListResponse], doc, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_list(self, client: CnosHub) -> None:
        response = client.projects.collections.docs.with_raw_response.list(
            name="name",
            project_id="project_id",
            include_deleted=True,
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        doc = response.parse()
        assert_matches_type(SyncPage[DocListResponse], doc, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_list(self, client: CnosHub) -> None:
        with client.projects.collections.docs.with_streaming_response.list(
            name="name",
            project_id="project_id",
            include_deleted=True,
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            doc = response.parse()
            assert_matches_type(SyncPage[DocListResponse], doc, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_list(self, client: CnosHub) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `project_id` but received ''"):
            client.projects.collections.docs.with_raw_response.list(
                name="name",
                project_id="",
                include_deleted=True,
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `name` but received ''"):
            client.projects.collections.docs.with_raw_response.list(
                name="",
                project_id="project_id",
                include_deleted=True,
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_delete(self, client: CnosHub) -> None:
        doc = client.projects.collections.docs.delete(
            doc_id="doc_id",
            project_id="project_id",
            name="name",
            expected_version="expected_version",
        )
        assert doc is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_delete(self, client: CnosHub) -> None:
        response = client.projects.collections.docs.with_raw_response.delete(
            doc_id="doc_id",
            project_id="project_id",
            name="name",
            expected_version="expected_version",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        doc = response.parse()
        assert doc is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_delete(self, client: CnosHub) -> None:
        with client.projects.collections.docs.with_streaming_response.delete(
            doc_id="doc_id",
            project_id="project_id",
            name="name",
            expected_version="expected_version",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            doc = response.parse()
            assert doc is None

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_delete(self, client: CnosHub) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `project_id` but received ''"):
            client.projects.collections.docs.with_raw_response.delete(
                doc_id="doc_id",
                project_id="",
                name="name",
                expected_version="expected_version",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `name` but received ''"):
            client.projects.collections.docs.with_raw_response.delete(
                doc_id="doc_id",
                project_id="project_id",
                name="",
                expected_version="expected_version",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `doc_id` but received ''"):
            client.projects.collections.docs.with_raw_response.delete(
                doc_id="",
                project_id="project_id",
                name="name",
                expected_version="expected_version",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_replace(self, client: CnosHub) -> None:
        doc = client.projects.collections.docs.replace(
            doc_id="doc_id",
            project_id="project_id",
            name="name",
            expected_version="expected_version",
            value={"foo": "bar"},
        )
        assert_matches_type(DocReplaceResponse, doc, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_replace(self, client: CnosHub) -> None:
        response = client.projects.collections.docs.with_raw_response.replace(
            doc_id="doc_id",
            project_id="project_id",
            name="name",
            expected_version="expected_version",
            value={"foo": "bar"},
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        doc = response.parse()
        assert_matches_type(DocReplaceResponse, doc, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_replace(self, client: CnosHub) -> None:
        with client.projects.collections.docs.with_streaming_response.replace(
            doc_id="doc_id",
            project_id="project_id",
            name="name",
            expected_version="expected_version",
            value={"foo": "bar"},
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            doc = response.parse()
            assert_matches_type(DocReplaceResponse, doc, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_replace(self, client: CnosHub) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `project_id` but received ''"):
            client.projects.collections.docs.with_raw_response.replace(
                doc_id="doc_id",
                project_id="",
                name="name",
                expected_version="expected_version",
                value={"foo": "bar"},
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `name` but received ''"):
            client.projects.collections.docs.with_raw_response.replace(
                doc_id="doc_id",
                project_id="project_id",
                name="",
                expected_version="expected_version",
                value={"foo": "bar"},
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `doc_id` but received ''"):
            client.projects.collections.docs.with_raw_response.replace(
                doc_id="",
                project_id="project_id",
                name="name",
                expected_version="expected_version",
                value={"foo": "bar"},
            )


class TestAsyncDocs:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_create(self, async_client: AsyncCnosHub) -> None:
        doc = await async_client.projects.collections.docs.create(
            name="name",
            project_id="project_id",
            value={"foo": "bar"},
        )
        assert_matches_type(DocCreateResponse, doc, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_create_with_all_params(self, async_client: AsyncCnosHub) -> None:
        doc = await async_client.projects.collections.docs.create(
            name="name",
            project_id="project_id",
            value={"foo": "bar"},
            id="id",
        )
        assert_matches_type(DocCreateResponse, doc, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_create(self, async_client: AsyncCnosHub) -> None:
        response = await async_client.projects.collections.docs.with_raw_response.create(
            name="name",
            project_id="project_id",
            value={"foo": "bar"},
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        doc = await response.parse()
        assert_matches_type(DocCreateResponse, doc, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_create(self, async_client: AsyncCnosHub) -> None:
        async with async_client.projects.collections.docs.with_streaming_response.create(
            name="name",
            project_id="project_id",
            value={"foo": "bar"},
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            doc = await response.parse()
            assert_matches_type(DocCreateResponse, doc, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_create(self, async_client: AsyncCnosHub) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `project_id` but received ''"):
            await async_client.projects.collections.docs.with_raw_response.create(
                name="name",
                project_id="",
                value={"foo": "bar"},
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `name` but received ''"):
            await async_client.projects.collections.docs.with_raw_response.create(
                name="",
                project_id="project_id",
                value={"foo": "bar"},
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_retrieve(self, async_client: AsyncCnosHub) -> None:
        doc = await async_client.projects.collections.docs.retrieve(
            doc_id="doc_id",
            project_id="project_id",
            name="name",
            include_deleted=True,
        )
        assert_matches_type(DocRetrieveResponse, doc, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_retrieve(self, async_client: AsyncCnosHub) -> None:
        response = await async_client.projects.collections.docs.with_raw_response.retrieve(
            doc_id="doc_id",
            project_id="project_id",
            name="name",
            include_deleted=True,
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        doc = await response.parse()
        assert_matches_type(DocRetrieveResponse, doc, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_retrieve(self, async_client: AsyncCnosHub) -> None:
        async with async_client.projects.collections.docs.with_streaming_response.retrieve(
            doc_id="doc_id",
            project_id="project_id",
            name="name",
            include_deleted=True,
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            doc = await response.parse()
            assert_matches_type(DocRetrieveResponse, doc, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_retrieve(self, async_client: AsyncCnosHub) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `project_id` but received ''"):
            await async_client.projects.collections.docs.with_raw_response.retrieve(
                doc_id="doc_id",
                project_id="",
                name="name",
                include_deleted=True,
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `name` but received ''"):
            await async_client.projects.collections.docs.with_raw_response.retrieve(
                doc_id="doc_id",
                project_id="project_id",
                name="",
                include_deleted=True,
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `doc_id` but received ''"):
            await async_client.projects.collections.docs.with_raw_response.retrieve(
                doc_id="",
                project_id="project_id",
                name="name",
                include_deleted=True,
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_list(self, async_client: AsyncCnosHub) -> None:
        doc = await async_client.projects.collections.docs.list(
            name="name",
            project_id="project_id",
            include_deleted=True,
        )
        assert_matches_type(AsyncPage[DocListResponse], doc, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_list_with_all_params(self, async_client: AsyncCnosHub) -> None:
        doc = await async_client.projects.collections.docs.list(
            name="name",
            project_id="project_id",
            include_deleted=True,
            cursor="cursor",
            limit=0,
        )
        assert_matches_type(AsyncPage[DocListResponse], doc, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_list(self, async_client: AsyncCnosHub) -> None:
        response = await async_client.projects.collections.docs.with_raw_response.list(
            name="name",
            project_id="project_id",
            include_deleted=True,
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        doc = await response.parse()
        assert_matches_type(AsyncPage[DocListResponse], doc, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_list(self, async_client: AsyncCnosHub) -> None:
        async with async_client.projects.collections.docs.with_streaming_response.list(
            name="name",
            project_id="project_id",
            include_deleted=True,
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            doc = await response.parse()
            assert_matches_type(AsyncPage[DocListResponse], doc, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_list(self, async_client: AsyncCnosHub) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `project_id` but received ''"):
            await async_client.projects.collections.docs.with_raw_response.list(
                name="name",
                project_id="",
                include_deleted=True,
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `name` but received ''"):
            await async_client.projects.collections.docs.with_raw_response.list(
                name="",
                project_id="project_id",
                include_deleted=True,
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_delete(self, async_client: AsyncCnosHub) -> None:
        doc = await async_client.projects.collections.docs.delete(
            doc_id="doc_id",
            project_id="project_id",
            name="name",
            expected_version="expected_version",
        )
        assert doc is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_delete(self, async_client: AsyncCnosHub) -> None:
        response = await async_client.projects.collections.docs.with_raw_response.delete(
            doc_id="doc_id",
            project_id="project_id",
            name="name",
            expected_version="expected_version",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        doc = await response.parse()
        assert doc is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_delete(self, async_client: AsyncCnosHub) -> None:
        async with async_client.projects.collections.docs.with_streaming_response.delete(
            doc_id="doc_id",
            project_id="project_id",
            name="name",
            expected_version="expected_version",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            doc = await response.parse()
            assert doc is None

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_delete(self, async_client: AsyncCnosHub) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `project_id` but received ''"):
            await async_client.projects.collections.docs.with_raw_response.delete(
                doc_id="doc_id",
                project_id="",
                name="name",
                expected_version="expected_version",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `name` but received ''"):
            await async_client.projects.collections.docs.with_raw_response.delete(
                doc_id="doc_id",
                project_id="project_id",
                name="",
                expected_version="expected_version",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `doc_id` but received ''"):
            await async_client.projects.collections.docs.with_raw_response.delete(
                doc_id="",
                project_id="project_id",
                name="name",
                expected_version="expected_version",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_replace(self, async_client: AsyncCnosHub) -> None:
        doc = await async_client.projects.collections.docs.replace(
            doc_id="doc_id",
            project_id="project_id",
            name="name",
            expected_version="expected_version",
            value={"foo": "bar"},
        )
        assert_matches_type(DocReplaceResponse, doc, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_replace(self, async_client: AsyncCnosHub) -> None:
        response = await async_client.projects.collections.docs.with_raw_response.replace(
            doc_id="doc_id",
            project_id="project_id",
            name="name",
            expected_version="expected_version",
            value={"foo": "bar"},
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        doc = await response.parse()
        assert_matches_type(DocReplaceResponse, doc, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_replace(self, async_client: AsyncCnosHub) -> None:
        async with async_client.projects.collections.docs.with_streaming_response.replace(
            doc_id="doc_id",
            project_id="project_id",
            name="name",
            expected_version="expected_version",
            value={"foo": "bar"},
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            doc = await response.parse()
            assert_matches_type(DocReplaceResponse, doc, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_replace(self, async_client: AsyncCnosHub) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `project_id` but received ''"):
            await async_client.projects.collections.docs.with_raw_response.replace(
                doc_id="doc_id",
                project_id="",
                name="name",
                expected_version="expected_version",
                value={"foo": "bar"},
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `name` but received ''"):
            await async_client.projects.collections.docs.with_raw_response.replace(
                doc_id="doc_id",
                project_id="project_id",
                name="",
                expected_version="expected_version",
                value={"foo": "bar"},
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `doc_id` but received ''"):
            await async_client.projects.collections.docs.with_raw_response.replace(
                doc_id="",
                project_id="project_id",
                name="name",
                expected_version="expected_version",
                value={"foo": "bar"},
            )
