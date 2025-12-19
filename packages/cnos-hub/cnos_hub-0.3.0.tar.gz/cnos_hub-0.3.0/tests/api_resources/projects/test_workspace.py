# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from cnos_hub import CnosHub, AsyncCnosHub
from tests.utils import assert_matches_type
from cnos_hub.types.projects import (
    WorkspaceListResponse,
    WorkspaceCheckResponse,
    WorkspacePatchResponse,
    WorkspaceRetrieveFileResponse,
)

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestWorkspace:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_list(self, client: CnosHub) -> None:
        workspace = client.projects.workspace.list(
            "project_id",
        )
        assert_matches_type(WorkspaceListResponse, workspace, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_list(self, client: CnosHub) -> None:
        response = client.projects.workspace.with_raw_response.list(
            "project_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        workspace = response.parse()
        assert_matches_type(WorkspaceListResponse, workspace, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_list(self, client: CnosHub) -> None:
        with client.projects.workspace.with_streaming_response.list(
            "project_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            workspace = response.parse()
            assert_matches_type(WorkspaceListResponse, workspace, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_list(self, client: CnosHub) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `project_id` but received ''"):
            client.projects.workspace.with_raw_response.list(
                "",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_check(self, client: CnosHub) -> None:
        workspace = client.projects.workspace.check(
            project_id="project_id",
            changes=[{"path": "path"}],
        )
        assert_matches_type(WorkspaceCheckResponse, workspace, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_check(self, client: CnosHub) -> None:
        response = client.projects.workspace.with_raw_response.check(
            project_id="project_id",
            changes=[{"path": "path"}],
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        workspace = response.parse()
        assert_matches_type(WorkspaceCheckResponse, workspace, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_check(self, client: CnosHub) -> None:
        with client.projects.workspace.with_streaming_response.check(
            project_id="project_id",
            changes=[{"path": "path"}],
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            workspace = response.parse()
            assert_matches_type(WorkspaceCheckResponse, workspace, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_check(self, client: CnosHub) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `project_id` but received ''"):
            client.projects.workspace.with_raw_response.check(
                project_id="",
                changes=[{"path": "path"}],
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_patch(self, client: CnosHub) -> None:
        workspace = client.projects.workspace.patch(
            project_id="project_id",
            changes=[{"path": "path"}],
        )
        assert_matches_type(WorkspacePatchResponse, workspace, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_patch(self, client: CnosHub) -> None:
        response = client.projects.workspace.with_raw_response.patch(
            project_id="project_id",
            changes=[{"path": "path"}],
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        workspace = response.parse()
        assert_matches_type(WorkspacePatchResponse, workspace, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_patch(self, client: CnosHub) -> None:
        with client.projects.workspace.with_streaming_response.patch(
            project_id="project_id",
            changes=[{"path": "path"}],
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            workspace = response.parse()
            assert_matches_type(WorkspacePatchResponse, workspace, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_patch(self, client: CnosHub) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `project_id` but received ''"):
            client.projects.workspace.with_raw_response.patch(
                project_id="",
                changes=[{"path": "path"}],
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_retrieve_file(self, client: CnosHub) -> None:
        workspace = client.projects.workspace.retrieve_file(
            project_id="project_id",
            path="path",
        )
        assert_matches_type(WorkspaceRetrieveFileResponse, workspace, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_retrieve_file(self, client: CnosHub) -> None:
        response = client.projects.workspace.with_raw_response.retrieve_file(
            project_id="project_id",
            path="path",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        workspace = response.parse()
        assert_matches_type(WorkspaceRetrieveFileResponse, workspace, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_retrieve_file(self, client: CnosHub) -> None:
        with client.projects.workspace.with_streaming_response.retrieve_file(
            project_id="project_id",
            path="path",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            workspace = response.parse()
            assert_matches_type(WorkspaceRetrieveFileResponse, workspace, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_retrieve_file(self, client: CnosHub) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `project_id` but received ''"):
            client.projects.workspace.with_raw_response.retrieve_file(
                project_id="",
                path="path",
            )


class TestAsyncWorkspace:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_list(self, async_client: AsyncCnosHub) -> None:
        workspace = await async_client.projects.workspace.list(
            "project_id",
        )
        assert_matches_type(WorkspaceListResponse, workspace, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_list(self, async_client: AsyncCnosHub) -> None:
        response = await async_client.projects.workspace.with_raw_response.list(
            "project_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        workspace = await response.parse()
        assert_matches_type(WorkspaceListResponse, workspace, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_list(self, async_client: AsyncCnosHub) -> None:
        async with async_client.projects.workspace.with_streaming_response.list(
            "project_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            workspace = await response.parse()
            assert_matches_type(WorkspaceListResponse, workspace, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_list(self, async_client: AsyncCnosHub) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `project_id` but received ''"):
            await async_client.projects.workspace.with_raw_response.list(
                "",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_check(self, async_client: AsyncCnosHub) -> None:
        workspace = await async_client.projects.workspace.check(
            project_id="project_id",
            changes=[{"path": "path"}],
        )
        assert_matches_type(WorkspaceCheckResponse, workspace, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_check(self, async_client: AsyncCnosHub) -> None:
        response = await async_client.projects.workspace.with_raw_response.check(
            project_id="project_id",
            changes=[{"path": "path"}],
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        workspace = await response.parse()
        assert_matches_type(WorkspaceCheckResponse, workspace, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_check(self, async_client: AsyncCnosHub) -> None:
        async with async_client.projects.workspace.with_streaming_response.check(
            project_id="project_id",
            changes=[{"path": "path"}],
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            workspace = await response.parse()
            assert_matches_type(WorkspaceCheckResponse, workspace, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_check(self, async_client: AsyncCnosHub) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `project_id` but received ''"):
            await async_client.projects.workspace.with_raw_response.check(
                project_id="",
                changes=[{"path": "path"}],
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_patch(self, async_client: AsyncCnosHub) -> None:
        workspace = await async_client.projects.workspace.patch(
            project_id="project_id",
            changes=[{"path": "path"}],
        )
        assert_matches_type(WorkspacePatchResponse, workspace, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_patch(self, async_client: AsyncCnosHub) -> None:
        response = await async_client.projects.workspace.with_raw_response.patch(
            project_id="project_id",
            changes=[{"path": "path"}],
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        workspace = await response.parse()
        assert_matches_type(WorkspacePatchResponse, workspace, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_patch(self, async_client: AsyncCnosHub) -> None:
        async with async_client.projects.workspace.with_streaming_response.patch(
            project_id="project_id",
            changes=[{"path": "path"}],
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            workspace = await response.parse()
            assert_matches_type(WorkspacePatchResponse, workspace, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_patch(self, async_client: AsyncCnosHub) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `project_id` but received ''"):
            await async_client.projects.workspace.with_raw_response.patch(
                project_id="",
                changes=[{"path": "path"}],
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_retrieve_file(self, async_client: AsyncCnosHub) -> None:
        workspace = await async_client.projects.workspace.retrieve_file(
            project_id="project_id",
            path="path",
        )
        assert_matches_type(WorkspaceRetrieveFileResponse, workspace, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_retrieve_file(self, async_client: AsyncCnosHub) -> None:
        response = await async_client.projects.workspace.with_raw_response.retrieve_file(
            project_id="project_id",
            path="path",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        workspace = await response.parse()
        assert_matches_type(WorkspaceRetrieveFileResponse, workspace, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_retrieve_file(self, async_client: AsyncCnosHub) -> None:
        async with async_client.projects.workspace.with_streaming_response.retrieve_file(
            project_id="project_id",
            path="path",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            workspace = await response.parse()
            assert_matches_type(WorkspaceRetrieveFileResponse, workspace, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_retrieve_file(self, async_client: AsyncCnosHub) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `project_id` but received ''"):
            await async_client.projects.workspace.with_raw_response.retrieve_file(
                project_id="",
                path="path",
            )
