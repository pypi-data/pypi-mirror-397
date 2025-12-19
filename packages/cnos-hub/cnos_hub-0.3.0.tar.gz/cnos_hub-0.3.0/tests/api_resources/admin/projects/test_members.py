# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from cnos_hub import CnosHub, AsyncCnosHub
from tests.utils import assert_matches_type
from cnos_hub.pagination import SyncPage, AsyncPage
from cnos_hub.types.admin.projects import (
    MemberListResponse,
    MemberCreateResponse,
    MemberHistoryResponse,
)

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestMembers:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_create(self, client: CnosHub) -> None:
        member = client.admin.projects.members.create(
            user_id="user_id",
            project_id="project_id",
        )
        assert_matches_type(MemberCreateResponse, member, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_create_with_all_params(self, client: CnosHub) -> None:
        member = client.admin.projects.members.create(
            user_id="user_id",
            project_id="project_id",
            roles=["string"],
        )
        assert_matches_type(MemberCreateResponse, member, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_create(self, client: CnosHub) -> None:
        response = client.admin.projects.members.with_raw_response.create(
            user_id="user_id",
            project_id="project_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        member = response.parse()
        assert_matches_type(MemberCreateResponse, member, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_create(self, client: CnosHub) -> None:
        with client.admin.projects.members.with_streaming_response.create(
            user_id="user_id",
            project_id="project_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            member = response.parse()
            assert_matches_type(MemberCreateResponse, member, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_create(self, client: CnosHub) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `project_id` but received ''"):
            client.admin.projects.members.with_raw_response.create(
                user_id="user_id",
                project_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `user_id` but received ''"):
            client.admin.projects.members.with_raw_response.create(
                user_id="",
                project_id="project_id",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_list(self, client: CnosHub) -> None:
        member = client.admin.projects.members.list(
            project_id="project_id",
        )
        assert_matches_type(SyncPage[MemberListResponse], member, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_list_with_all_params(self, client: CnosHub) -> None:
        member = client.admin.projects.members.list(
            project_id="project_id",
            cursor="cursor",
            limit=0,
        )
        assert_matches_type(SyncPage[MemberListResponse], member, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_list(self, client: CnosHub) -> None:
        response = client.admin.projects.members.with_raw_response.list(
            project_id="project_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        member = response.parse()
        assert_matches_type(SyncPage[MemberListResponse], member, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_list(self, client: CnosHub) -> None:
        with client.admin.projects.members.with_streaming_response.list(
            project_id="project_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            member = response.parse()
            assert_matches_type(SyncPage[MemberListResponse], member, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_list(self, client: CnosHub) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `project_id` but received ''"):
            client.admin.projects.members.with_raw_response.list(
                project_id="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_delete(self, client: CnosHub) -> None:
        member = client.admin.projects.members.delete(
            user_id="user_id",
            project_id="project_id",
        )
        assert member is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_delete(self, client: CnosHub) -> None:
        response = client.admin.projects.members.with_raw_response.delete(
            user_id="user_id",
            project_id="project_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        member = response.parse()
        assert member is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_delete(self, client: CnosHub) -> None:
        with client.admin.projects.members.with_streaming_response.delete(
            user_id="user_id",
            project_id="project_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            member = response.parse()
            assert member is None

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_delete(self, client: CnosHub) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `project_id` but received ''"):
            client.admin.projects.members.with_raw_response.delete(
                user_id="user_id",
                project_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `user_id` but received ''"):
            client.admin.projects.members.with_raw_response.delete(
                user_id="",
                project_id="project_id",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_history(self, client: CnosHub) -> None:
        member = client.admin.projects.members.history(
            user_id="user_id",
            project_id="project_id",
        )
        assert_matches_type(SyncPage[MemberHistoryResponse], member, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_history_with_all_params(self, client: CnosHub) -> None:
        member = client.admin.projects.members.history(
            user_id="user_id",
            project_id="project_id",
            cursor="cursor",
            limit=0,
        )
        assert_matches_type(SyncPage[MemberHistoryResponse], member, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_history(self, client: CnosHub) -> None:
        response = client.admin.projects.members.with_raw_response.history(
            user_id="user_id",
            project_id="project_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        member = response.parse()
        assert_matches_type(SyncPage[MemberHistoryResponse], member, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_history(self, client: CnosHub) -> None:
        with client.admin.projects.members.with_streaming_response.history(
            user_id="user_id",
            project_id="project_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            member = response.parse()
            assert_matches_type(SyncPage[MemberHistoryResponse], member, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_history(self, client: CnosHub) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `project_id` but received ''"):
            client.admin.projects.members.with_raw_response.history(
                user_id="user_id",
                project_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `user_id` but received ''"):
            client.admin.projects.members.with_raw_response.history(
                user_id="",
                project_id="project_id",
            )


class TestAsyncMembers:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_create(self, async_client: AsyncCnosHub) -> None:
        member = await async_client.admin.projects.members.create(
            user_id="user_id",
            project_id="project_id",
        )
        assert_matches_type(MemberCreateResponse, member, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_create_with_all_params(self, async_client: AsyncCnosHub) -> None:
        member = await async_client.admin.projects.members.create(
            user_id="user_id",
            project_id="project_id",
            roles=["string"],
        )
        assert_matches_type(MemberCreateResponse, member, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_create(self, async_client: AsyncCnosHub) -> None:
        response = await async_client.admin.projects.members.with_raw_response.create(
            user_id="user_id",
            project_id="project_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        member = await response.parse()
        assert_matches_type(MemberCreateResponse, member, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_create(self, async_client: AsyncCnosHub) -> None:
        async with async_client.admin.projects.members.with_streaming_response.create(
            user_id="user_id",
            project_id="project_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            member = await response.parse()
            assert_matches_type(MemberCreateResponse, member, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_create(self, async_client: AsyncCnosHub) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `project_id` but received ''"):
            await async_client.admin.projects.members.with_raw_response.create(
                user_id="user_id",
                project_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `user_id` but received ''"):
            await async_client.admin.projects.members.with_raw_response.create(
                user_id="",
                project_id="project_id",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_list(self, async_client: AsyncCnosHub) -> None:
        member = await async_client.admin.projects.members.list(
            project_id="project_id",
        )
        assert_matches_type(AsyncPage[MemberListResponse], member, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_list_with_all_params(self, async_client: AsyncCnosHub) -> None:
        member = await async_client.admin.projects.members.list(
            project_id="project_id",
            cursor="cursor",
            limit=0,
        )
        assert_matches_type(AsyncPage[MemberListResponse], member, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_list(self, async_client: AsyncCnosHub) -> None:
        response = await async_client.admin.projects.members.with_raw_response.list(
            project_id="project_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        member = await response.parse()
        assert_matches_type(AsyncPage[MemberListResponse], member, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_list(self, async_client: AsyncCnosHub) -> None:
        async with async_client.admin.projects.members.with_streaming_response.list(
            project_id="project_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            member = await response.parse()
            assert_matches_type(AsyncPage[MemberListResponse], member, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_list(self, async_client: AsyncCnosHub) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `project_id` but received ''"):
            await async_client.admin.projects.members.with_raw_response.list(
                project_id="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_delete(self, async_client: AsyncCnosHub) -> None:
        member = await async_client.admin.projects.members.delete(
            user_id="user_id",
            project_id="project_id",
        )
        assert member is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_delete(self, async_client: AsyncCnosHub) -> None:
        response = await async_client.admin.projects.members.with_raw_response.delete(
            user_id="user_id",
            project_id="project_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        member = await response.parse()
        assert member is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_delete(self, async_client: AsyncCnosHub) -> None:
        async with async_client.admin.projects.members.with_streaming_response.delete(
            user_id="user_id",
            project_id="project_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            member = await response.parse()
            assert member is None

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_delete(self, async_client: AsyncCnosHub) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `project_id` but received ''"):
            await async_client.admin.projects.members.with_raw_response.delete(
                user_id="user_id",
                project_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `user_id` but received ''"):
            await async_client.admin.projects.members.with_raw_response.delete(
                user_id="",
                project_id="project_id",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_history(self, async_client: AsyncCnosHub) -> None:
        member = await async_client.admin.projects.members.history(
            user_id="user_id",
            project_id="project_id",
        )
        assert_matches_type(AsyncPage[MemberHistoryResponse], member, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_history_with_all_params(self, async_client: AsyncCnosHub) -> None:
        member = await async_client.admin.projects.members.history(
            user_id="user_id",
            project_id="project_id",
            cursor="cursor",
            limit=0,
        )
        assert_matches_type(AsyncPage[MemberHistoryResponse], member, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_history(self, async_client: AsyncCnosHub) -> None:
        response = await async_client.admin.projects.members.with_raw_response.history(
            user_id="user_id",
            project_id="project_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        member = await response.parse()
        assert_matches_type(AsyncPage[MemberHistoryResponse], member, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_history(self, async_client: AsyncCnosHub) -> None:
        async with async_client.admin.projects.members.with_streaming_response.history(
            user_id="user_id",
            project_id="project_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            member = await response.parse()
            assert_matches_type(AsyncPage[MemberHistoryResponse], member, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_history(self, async_client: AsyncCnosHub) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `project_id` but received ''"):
            await async_client.admin.projects.members.with_raw_response.history(
                user_id="user_id",
                project_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `user_id` but received ''"):
            await async_client.admin.projects.members.with_raw_response.history(
                user_id="",
                project_id="project_id",
            )
