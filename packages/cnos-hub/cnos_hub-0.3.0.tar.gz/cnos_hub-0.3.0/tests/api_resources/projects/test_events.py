# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from cnos_hub import CnosHub, AsyncCnosHub
from tests.utils import assert_matches_type
from cnos_hub.pagination import SyncPage, AsyncPage
from cnos_hub.types.projects import (
    EventListResponse,
    EventRetryResponse,
    EventCreateResponse,
    EventRetrieveResponse,
)

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestEvents:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_create(self, client: CnosHub) -> None:
        event = client.projects.events.create(
            project_id="project_id",
            type="type",
        )
        assert_matches_type(EventCreateResponse, event, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_create_with_all_params(self, client: CnosHub) -> None:
        event = client.projects.events.create(
            project_id="project_id",
            type="type",
            key="key",
            meta={"foo": "bar"},
            payload={"foo": "bar"},
        )
        assert_matches_type(EventCreateResponse, event, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_create(self, client: CnosHub) -> None:
        response = client.projects.events.with_raw_response.create(
            project_id="project_id",
            type="type",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        event = response.parse()
        assert_matches_type(EventCreateResponse, event, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_create(self, client: CnosHub) -> None:
        with client.projects.events.with_streaming_response.create(
            project_id="project_id",
            type="type",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            event = response.parse()
            assert_matches_type(EventCreateResponse, event, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_create(self, client: CnosHub) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `project_id` but received ''"):
            client.projects.events.with_raw_response.create(
                project_id="",
                type="type",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_retrieve(self, client: CnosHub) -> None:
        event = client.projects.events.retrieve(
            event_id="event_id",
            project_id="project_id",
        )
        assert_matches_type(EventRetrieveResponse, event, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_retrieve(self, client: CnosHub) -> None:
        response = client.projects.events.with_raw_response.retrieve(
            event_id="event_id",
            project_id="project_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        event = response.parse()
        assert_matches_type(EventRetrieveResponse, event, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_retrieve(self, client: CnosHub) -> None:
        with client.projects.events.with_streaming_response.retrieve(
            event_id="event_id",
            project_id="project_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            event = response.parse()
            assert_matches_type(EventRetrieveResponse, event, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_retrieve(self, client: CnosHub) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `project_id` but received ''"):
            client.projects.events.with_raw_response.retrieve(
                event_id="event_id",
                project_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `event_id` but received ''"):
            client.projects.events.with_raw_response.retrieve(
                event_id="",
                project_id="project_id",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_list(self, client: CnosHub) -> None:
        event = client.projects.events.list(
            project_id="project_id",
        )
        assert_matches_type(SyncPage[EventListResponse], event, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_list_with_all_params(self, client: CnosHub) -> None:
        event = client.projects.events.list(
            project_id="project_id",
            cursor="cursor",
            limit=0,
            status="pending",
            type="type",
        )
        assert_matches_type(SyncPage[EventListResponse], event, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_list(self, client: CnosHub) -> None:
        response = client.projects.events.with_raw_response.list(
            project_id="project_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        event = response.parse()
        assert_matches_type(SyncPage[EventListResponse], event, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_list(self, client: CnosHub) -> None:
        with client.projects.events.with_streaming_response.list(
            project_id="project_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            event = response.parse()
            assert_matches_type(SyncPage[EventListResponse], event, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_list(self, client: CnosHub) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `project_id` but received ''"):
            client.projects.events.with_raw_response.list(
                project_id="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_drop(self, client: CnosHub) -> None:
        event = client.projects.events.drop(
            event_id="event_id",
            project_id="project_id",
        )
        assert event is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_drop(self, client: CnosHub) -> None:
        response = client.projects.events.with_raw_response.drop(
            event_id="event_id",
            project_id="project_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        event = response.parse()
        assert event is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_drop(self, client: CnosHub) -> None:
        with client.projects.events.with_streaming_response.drop(
            event_id="event_id",
            project_id="project_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            event = response.parse()
            assert event is None

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_drop(self, client: CnosHub) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `project_id` but received ''"):
            client.projects.events.with_raw_response.drop(
                event_id="event_id",
                project_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `event_id` but received ''"):
            client.projects.events.with_raw_response.drop(
                event_id="",
                project_id="project_id",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_retry(self, client: CnosHub) -> None:
        event = client.projects.events.retry(
            event_id="event_id",
            project_id="project_id",
        )
        assert_matches_type(EventRetryResponse, event, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_retry(self, client: CnosHub) -> None:
        response = client.projects.events.with_raw_response.retry(
            event_id="event_id",
            project_id="project_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        event = response.parse()
        assert_matches_type(EventRetryResponse, event, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_retry(self, client: CnosHub) -> None:
        with client.projects.events.with_streaming_response.retry(
            event_id="event_id",
            project_id="project_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            event = response.parse()
            assert_matches_type(EventRetryResponse, event, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_retry(self, client: CnosHub) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `project_id` but received ''"):
            client.projects.events.with_raw_response.retry(
                event_id="event_id",
                project_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `event_id` but received ''"):
            client.projects.events.with_raw_response.retry(
                event_id="",
                project_id="project_id",
            )


class TestAsyncEvents:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_create(self, async_client: AsyncCnosHub) -> None:
        event = await async_client.projects.events.create(
            project_id="project_id",
            type="type",
        )
        assert_matches_type(EventCreateResponse, event, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_create_with_all_params(self, async_client: AsyncCnosHub) -> None:
        event = await async_client.projects.events.create(
            project_id="project_id",
            type="type",
            key="key",
            meta={"foo": "bar"},
            payload={"foo": "bar"},
        )
        assert_matches_type(EventCreateResponse, event, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_create(self, async_client: AsyncCnosHub) -> None:
        response = await async_client.projects.events.with_raw_response.create(
            project_id="project_id",
            type="type",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        event = await response.parse()
        assert_matches_type(EventCreateResponse, event, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_create(self, async_client: AsyncCnosHub) -> None:
        async with async_client.projects.events.with_streaming_response.create(
            project_id="project_id",
            type="type",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            event = await response.parse()
            assert_matches_type(EventCreateResponse, event, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_create(self, async_client: AsyncCnosHub) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `project_id` but received ''"):
            await async_client.projects.events.with_raw_response.create(
                project_id="",
                type="type",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_retrieve(self, async_client: AsyncCnosHub) -> None:
        event = await async_client.projects.events.retrieve(
            event_id="event_id",
            project_id="project_id",
        )
        assert_matches_type(EventRetrieveResponse, event, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_retrieve(self, async_client: AsyncCnosHub) -> None:
        response = await async_client.projects.events.with_raw_response.retrieve(
            event_id="event_id",
            project_id="project_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        event = await response.parse()
        assert_matches_type(EventRetrieveResponse, event, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_retrieve(self, async_client: AsyncCnosHub) -> None:
        async with async_client.projects.events.with_streaming_response.retrieve(
            event_id="event_id",
            project_id="project_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            event = await response.parse()
            assert_matches_type(EventRetrieveResponse, event, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_retrieve(self, async_client: AsyncCnosHub) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `project_id` but received ''"):
            await async_client.projects.events.with_raw_response.retrieve(
                event_id="event_id",
                project_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `event_id` but received ''"):
            await async_client.projects.events.with_raw_response.retrieve(
                event_id="",
                project_id="project_id",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_list(self, async_client: AsyncCnosHub) -> None:
        event = await async_client.projects.events.list(
            project_id="project_id",
        )
        assert_matches_type(AsyncPage[EventListResponse], event, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_list_with_all_params(self, async_client: AsyncCnosHub) -> None:
        event = await async_client.projects.events.list(
            project_id="project_id",
            cursor="cursor",
            limit=0,
            status="pending",
            type="type",
        )
        assert_matches_type(AsyncPage[EventListResponse], event, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_list(self, async_client: AsyncCnosHub) -> None:
        response = await async_client.projects.events.with_raw_response.list(
            project_id="project_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        event = await response.parse()
        assert_matches_type(AsyncPage[EventListResponse], event, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_list(self, async_client: AsyncCnosHub) -> None:
        async with async_client.projects.events.with_streaming_response.list(
            project_id="project_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            event = await response.parse()
            assert_matches_type(AsyncPage[EventListResponse], event, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_list(self, async_client: AsyncCnosHub) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `project_id` but received ''"):
            await async_client.projects.events.with_raw_response.list(
                project_id="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_drop(self, async_client: AsyncCnosHub) -> None:
        event = await async_client.projects.events.drop(
            event_id="event_id",
            project_id="project_id",
        )
        assert event is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_drop(self, async_client: AsyncCnosHub) -> None:
        response = await async_client.projects.events.with_raw_response.drop(
            event_id="event_id",
            project_id="project_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        event = await response.parse()
        assert event is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_drop(self, async_client: AsyncCnosHub) -> None:
        async with async_client.projects.events.with_streaming_response.drop(
            event_id="event_id",
            project_id="project_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            event = await response.parse()
            assert event is None

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_drop(self, async_client: AsyncCnosHub) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `project_id` but received ''"):
            await async_client.projects.events.with_raw_response.drop(
                event_id="event_id",
                project_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `event_id` but received ''"):
            await async_client.projects.events.with_raw_response.drop(
                event_id="",
                project_id="project_id",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_retry(self, async_client: AsyncCnosHub) -> None:
        event = await async_client.projects.events.retry(
            event_id="event_id",
            project_id="project_id",
        )
        assert_matches_type(EventRetryResponse, event, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_retry(self, async_client: AsyncCnosHub) -> None:
        response = await async_client.projects.events.with_raw_response.retry(
            event_id="event_id",
            project_id="project_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        event = await response.parse()
        assert_matches_type(EventRetryResponse, event, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_retry(self, async_client: AsyncCnosHub) -> None:
        async with async_client.projects.events.with_streaming_response.retry(
            event_id="event_id",
            project_id="project_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            event = await response.parse()
            assert_matches_type(EventRetryResponse, event, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_retry(self, async_client: AsyncCnosHub) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `project_id` but received ''"):
            await async_client.projects.events.with_raw_response.retry(
                event_id="event_id",
                project_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `event_id` but received ''"):
            await async_client.projects.events.with_raw_response.retry(
                event_id="",
                project_id="project_id",
            )
