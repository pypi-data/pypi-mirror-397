# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from cnos_hub import CnosHub, AsyncCnosHub
from tests.utils import assert_matches_type
from cnos_hub.types.projects.views import ViewUpdateResponse, ViewRetrieveResponse

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestView:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_retrieve(self, client: CnosHub) -> None:
        view = client.projects.views.view.retrieve(
            view_name="view_name",
            project_id="project_id",
        )
        assert_matches_type(ViewRetrieveResponse, view, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_retrieve(self, client: CnosHub) -> None:
        response = client.projects.views.view.with_raw_response.retrieve(
            view_name="view_name",
            project_id="project_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        view = response.parse()
        assert_matches_type(ViewRetrieveResponse, view, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_retrieve(self, client: CnosHub) -> None:
        with client.projects.views.view.with_streaming_response.retrieve(
            view_name="view_name",
            project_id="project_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            view = response.parse()
            assert_matches_type(ViewRetrieveResponse, view, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_retrieve(self, client: CnosHub) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `project_id` but received ''"):
            client.projects.views.view.with_raw_response.retrieve(
                view_name="view_name",
                project_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `view_name` but received ''"):
            client.projects.views.view.with_raw_response.retrieve(
                view_name="",
                project_id="project_id",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_update(self, client: CnosHub) -> None:
        view = client.projects.views.view.update(
            view_name="view_name",
            project_id="project_id",
        )
        assert_matches_type(ViewUpdateResponse, view, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_update_with_all_params(self, client: CnosHub) -> None:
        view = client.projects.views.view.update(
            view_name="view_name",
            project_id="project_id",
            allowed_labels=["string"],
            allowed_roles=["string"],
            description="description",
            status="active",
        )
        assert_matches_type(ViewUpdateResponse, view, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_update(self, client: CnosHub) -> None:
        response = client.projects.views.view.with_raw_response.update(
            view_name="view_name",
            project_id="project_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        view = response.parse()
        assert_matches_type(ViewUpdateResponse, view, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_update(self, client: CnosHub) -> None:
        with client.projects.views.view.with_streaming_response.update(
            view_name="view_name",
            project_id="project_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            view = response.parse()
            assert_matches_type(ViewUpdateResponse, view, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_update(self, client: CnosHub) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `project_id` but received ''"):
            client.projects.views.view.with_raw_response.update(
                view_name="view_name",
                project_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `view_name` but received ''"):
            client.projects.views.view.with_raw_response.update(
                view_name="",
                project_id="project_id",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_delete(self, client: CnosHub) -> None:
        view = client.projects.views.view.delete(
            view_name="view_name",
            project_id="project_id",
        )
        assert view is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_delete(self, client: CnosHub) -> None:
        response = client.projects.views.view.with_raw_response.delete(
            view_name="view_name",
            project_id="project_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        view = response.parse()
        assert view is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_delete(self, client: CnosHub) -> None:
        with client.projects.views.view.with_streaming_response.delete(
            view_name="view_name",
            project_id="project_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            view = response.parse()
            assert view is None

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_delete(self, client: CnosHub) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `project_id` but received ''"):
            client.projects.views.view.with_raw_response.delete(
                view_name="view_name",
                project_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `view_name` but received ''"):
            client.projects.views.view.with_raw_response.delete(
                view_name="",
                project_id="project_id",
            )


class TestAsyncView:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_retrieve(self, async_client: AsyncCnosHub) -> None:
        view = await async_client.projects.views.view.retrieve(
            view_name="view_name",
            project_id="project_id",
        )
        assert_matches_type(ViewRetrieveResponse, view, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_retrieve(self, async_client: AsyncCnosHub) -> None:
        response = await async_client.projects.views.view.with_raw_response.retrieve(
            view_name="view_name",
            project_id="project_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        view = await response.parse()
        assert_matches_type(ViewRetrieveResponse, view, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_retrieve(self, async_client: AsyncCnosHub) -> None:
        async with async_client.projects.views.view.with_streaming_response.retrieve(
            view_name="view_name",
            project_id="project_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            view = await response.parse()
            assert_matches_type(ViewRetrieveResponse, view, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_retrieve(self, async_client: AsyncCnosHub) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `project_id` but received ''"):
            await async_client.projects.views.view.with_raw_response.retrieve(
                view_name="view_name",
                project_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `view_name` but received ''"):
            await async_client.projects.views.view.with_raw_response.retrieve(
                view_name="",
                project_id="project_id",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_update(self, async_client: AsyncCnosHub) -> None:
        view = await async_client.projects.views.view.update(
            view_name="view_name",
            project_id="project_id",
        )
        assert_matches_type(ViewUpdateResponse, view, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_update_with_all_params(self, async_client: AsyncCnosHub) -> None:
        view = await async_client.projects.views.view.update(
            view_name="view_name",
            project_id="project_id",
            allowed_labels=["string"],
            allowed_roles=["string"],
            description="description",
            status="active",
        )
        assert_matches_type(ViewUpdateResponse, view, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_update(self, async_client: AsyncCnosHub) -> None:
        response = await async_client.projects.views.view.with_raw_response.update(
            view_name="view_name",
            project_id="project_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        view = await response.parse()
        assert_matches_type(ViewUpdateResponse, view, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_update(self, async_client: AsyncCnosHub) -> None:
        async with async_client.projects.views.view.with_streaming_response.update(
            view_name="view_name",
            project_id="project_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            view = await response.parse()
            assert_matches_type(ViewUpdateResponse, view, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_update(self, async_client: AsyncCnosHub) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `project_id` but received ''"):
            await async_client.projects.views.view.with_raw_response.update(
                view_name="view_name",
                project_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `view_name` but received ''"):
            await async_client.projects.views.view.with_raw_response.update(
                view_name="",
                project_id="project_id",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_delete(self, async_client: AsyncCnosHub) -> None:
        view = await async_client.projects.views.view.delete(
            view_name="view_name",
            project_id="project_id",
        )
        assert view is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_delete(self, async_client: AsyncCnosHub) -> None:
        response = await async_client.projects.views.view.with_raw_response.delete(
            view_name="view_name",
            project_id="project_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        view = await response.parse()
        assert view is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_delete(self, async_client: AsyncCnosHub) -> None:
        async with async_client.projects.views.view.with_streaming_response.delete(
            view_name="view_name",
            project_id="project_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            view = await response.parse()
            assert view is None

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_delete(self, async_client: AsyncCnosHub) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `project_id` but received ''"):
            await async_client.projects.views.view.with_raw_response.delete(
                view_name="view_name",
                project_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `view_name` but received ''"):
            await async_client.projects.views.view.with_raw_response.delete(
                view_name="",
                project_id="project_id",
            )
