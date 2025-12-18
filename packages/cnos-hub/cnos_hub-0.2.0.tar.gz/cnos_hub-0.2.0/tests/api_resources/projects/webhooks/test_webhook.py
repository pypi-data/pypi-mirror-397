# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from cnos_hub import CnosHub, AsyncCnosHub
from tests.utils import assert_matches_type
from cnos_hub.pagination import SyncPage, AsyncPage
from cnos_hub.types.projects.webhooks import (
    WebhookUpdateResponse,
    WebhookRetrieveResponse,
    WebhookDeliveriesResponse,
)

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestWebhook:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_retrieve(self, client: CnosHub) -> None:
        webhook = client.projects.webhooks.webhook.retrieve(
            webhook_id="webhook_id",
            project_id="project_id",
        )
        assert_matches_type(WebhookRetrieveResponse, webhook, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_retrieve(self, client: CnosHub) -> None:
        response = client.projects.webhooks.webhook.with_raw_response.retrieve(
            webhook_id="webhook_id",
            project_id="project_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        webhook = response.parse()
        assert_matches_type(WebhookRetrieveResponse, webhook, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_retrieve(self, client: CnosHub) -> None:
        with client.projects.webhooks.webhook.with_streaming_response.retrieve(
            webhook_id="webhook_id",
            project_id="project_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            webhook = response.parse()
            assert_matches_type(WebhookRetrieveResponse, webhook, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_retrieve(self, client: CnosHub) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `project_id` but received ''"):
            client.projects.webhooks.webhook.with_raw_response.retrieve(
                webhook_id="webhook_id",
                project_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `webhook_id` but received ''"):
            client.projects.webhooks.webhook.with_raw_response.retrieve(
                webhook_id="",
                project_id="project_id",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_update(self, client: CnosHub) -> None:
        webhook = client.projects.webhooks.webhook.update(
            webhook_id="webhook_id",
            project_id="project_id",
        )
        assert_matches_type(WebhookUpdateResponse, webhook, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_update_with_all_params(self, client: CnosHub) -> None:
        webhook = client.projects.webhooks.webhook.update(
            webhook_id="webhook_id",
            project_id="project_id",
            description="description",
            event_pattern="event_pattern",
            name="name",
            status="active",
            url="url",
        )
        assert_matches_type(WebhookUpdateResponse, webhook, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_update(self, client: CnosHub) -> None:
        response = client.projects.webhooks.webhook.with_raw_response.update(
            webhook_id="webhook_id",
            project_id="project_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        webhook = response.parse()
        assert_matches_type(WebhookUpdateResponse, webhook, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_update(self, client: CnosHub) -> None:
        with client.projects.webhooks.webhook.with_streaming_response.update(
            webhook_id="webhook_id",
            project_id="project_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            webhook = response.parse()
            assert_matches_type(WebhookUpdateResponse, webhook, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_update(self, client: CnosHub) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `project_id` but received ''"):
            client.projects.webhooks.webhook.with_raw_response.update(
                webhook_id="webhook_id",
                project_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `webhook_id` but received ''"):
            client.projects.webhooks.webhook.with_raw_response.update(
                webhook_id="",
                project_id="project_id",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_delete(self, client: CnosHub) -> None:
        webhook = client.projects.webhooks.webhook.delete(
            webhook_id="webhook_id",
            project_id="project_id",
        )
        assert webhook is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_delete(self, client: CnosHub) -> None:
        response = client.projects.webhooks.webhook.with_raw_response.delete(
            webhook_id="webhook_id",
            project_id="project_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        webhook = response.parse()
        assert webhook is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_delete(self, client: CnosHub) -> None:
        with client.projects.webhooks.webhook.with_streaming_response.delete(
            webhook_id="webhook_id",
            project_id="project_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            webhook = response.parse()
            assert webhook is None

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_delete(self, client: CnosHub) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `project_id` but received ''"):
            client.projects.webhooks.webhook.with_raw_response.delete(
                webhook_id="webhook_id",
                project_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `webhook_id` but received ''"):
            client.projects.webhooks.webhook.with_raw_response.delete(
                webhook_id="",
                project_id="project_id",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_deliveries(self, client: CnosHub) -> None:
        webhook = client.projects.webhooks.webhook.deliveries(
            webhook_id="webhook_id",
            project_id="project_id",
        )
        assert_matches_type(SyncPage[WebhookDeliveriesResponse], webhook, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_deliveries_with_all_params(self, client: CnosHub) -> None:
        webhook = client.projects.webhooks.webhook.deliveries(
            webhook_id="webhook_id",
            project_id="project_id",
            cursor="cursor",
            limit=0,
            status="pending",
        )
        assert_matches_type(SyncPage[WebhookDeliveriesResponse], webhook, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_deliveries(self, client: CnosHub) -> None:
        response = client.projects.webhooks.webhook.with_raw_response.deliveries(
            webhook_id="webhook_id",
            project_id="project_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        webhook = response.parse()
        assert_matches_type(SyncPage[WebhookDeliveriesResponse], webhook, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_deliveries(self, client: CnosHub) -> None:
        with client.projects.webhooks.webhook.with_streaming_response.deliveries(
            webhook_id="webhook_id",
            project_id="project_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            webhook = response.parse()
            assert_matches_type(SyncPage[WebhookDeliveriesResponse], webhook, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_deliveries(self, client: CnosHub) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `project_id` but received ''"):
            client.projects.webhooks.webhook.with_raw_response.deliveries(
                webhook_id="webhook_id",
                project_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `webhook_id` but received ''"):
            client.projects.webhooks.webhook.with_raw_response.deliveries(
                webhook_id="",
                project_id="project_id",
            )


class TestAsyncWebhook:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_retrieve(self, async_client: AsyncCnosHub) -> None:
        webhook = await async_client.projects.webhooks.webhook.retrieve(
            webhook_id="webhook_id",
            project_id="project_id",
        )
        assert_matches_type(WebhookRetrieveResponse, webhook, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_retrieve(self, async_client: AsyncCnosHub) -> None:
        response = await async_client.projects.webhooks.webhook.with_raw_response.retrieve(
            webhook_id="webhook_id",
            project_id="project_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        webhook = await response.parse()
        assert_matches_type(WebhookRetrieveResponse, webhook, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_retrieve(self, async_client: AsyncCnosHub) -> None:
        async with async_client.projects.webhooks.webhook.with_streaming_response.retrieve(
            webhook_id="webhook_id",
            project_id="project_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            webhook = await response.parse()
            assert_matches_type(WebhookRetrieveResponse, webhook, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_retrieve(self, async_client: AsyncCnosHub) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `project_id` but received ''"):
            await async_client.projects.webhooks.webhook.with_raw_response.retrieve(
                webhook_id="webhook_id",
                project_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `webhook_id` but received ''"):
            await async_client.projects.webhooks.webhook.with_raw_response.retrieve(
                webhook_id="",
                project_id="project_id",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_update(self, async_client: AsyncCnosHub) -> None:
        webhook = await async_client.projects.webhooks.webhook.update(
            webhook_id="webhook_id",
            project_id="project_id",
        )
        assert_matches_type(WebhookUpdateResponse, webhook, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_update_with_all_params(self, async_client: AsyncCnosHub) -> None:
        webhook = await async_client.projects.webhooks.webhook.update(
            webhook_id="webhook_id",
            project_id="project_id",
            description="description",
            event_pattern="event_pattern",
            name="name",
            status="active",
            url="url",
        )
        assert_matches_type(WebhookUpdateResponse, webhook, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_update(self, async_client: AsyncCnosHub) -> None:
        response = await async_client.projects.webhooks.webhook.with_raw_response.update(
            webhook_id="webhook_id",
            project_id="project_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        webhook = await response.parse()
        assert_matches_type(WebhookUpdateResponse, webhook, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_update(self, async_client: AsyncCnosHub) -> None:
        async with async_client.projects.webhooks.webhook.with_streaming_response.update(
            webhook_id="webhook_id",
            project_id="project_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            webhook = await response.parse()
            assert_matches_type(WebhookUpdateResponse, webhook, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_update(self, async_client: AsyncCnosHub) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `project_id` but received ''"):
            await async_client.projects.webhooks.webhook.with_raw_response.update(
                webhook_id="webhook_id",
                project_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `webhook_id` but received ''"):
            await async_client.projects.webhooks.webhook.with_raw_response.update(
                webhook_id="",
                project_id="project_id",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_delete(self, async_client: AsyncCnosHub) -> None:
        webhook = await async_client.projects.webhooks.webhook.delete(
            webhook_id="webhook_id",
            project_id="project_id",
        )
        assert webhook is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_delete(self, async_client: AsyncCnosHub) -> None:
        response = await async_client.projects.webhooks.webhook.with_raw_response.delete(
            webhook_id="webhook_id",
            project_id="project_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        webhook = await response.parse()
        assert webhook is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_delete(self, async_client: AsyncCnosHub) -> None:
        async with async_client.projects.webhooks.webhook.with_streaming_response.delete(
            webhook_id="webhook_id",
            project_id="project_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            webhook = await response.parse()
            assert webhook is None

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_delete(self, async_client: AsyncCnosHub) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `project_id` but received ''"):
            await async_client.projects.webhooks.webhook.with_raw_response.delete(
                webhook_id="webhook_id",
                project_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `webhook_id` but received ''"):
            await async_client.projects.webhooks.webhook.with_raw_response.delete(
                webhook_id="",
                project_id="project_id",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_deliveries(self, async_client: AsyncCnosHub) -> None:
        webhook = await async_client.projects.webhooks.webhook.deliveries(
            webhook_id="webhook_id",
            project_id="project_id",
        )
        assert_matches_type(AsyncPage[WebhookDeliveriesResponse], webhook, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_deliveries_with_all_params(self, async_client: AsyncCnosHub) -> None:
        webhook = await async_client.projects.webhooks.webhook.deliveries(
            webhook_id="webhook_id",
            project_id="project_id",
            cursor="cursor",
            limit=0,
            status="pending",
        )
        assert_matches_type(AsyncPage[WebhookDeliveriesResponse], webhook, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_deliveries(self, async_client: AsyncCnosHub) -> None:
        response = await async_client.projects.webhooks.webhook.with_raw_response.deliveries(
            webhook_id="webhook_id",
            project_id="project_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        webhook = await response.parse()
        assert_matches_type(AsyncPage[WebhookDeliveriesResponse], webhook, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_deliveries(self, async_client: AsyncCnosHub) -> None:
        async with async_client.projects.webhooks.webhook.with_streaming_response.deliveries(
            webhook_id="webhook_id",
            project_id="project_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            webhook = await response.parse()
            assert_matches_type(AsyncPage[WebhookDeliveriesResponse], webhook, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_deliveries(self, async_client: AsyncCnosHub) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `project_id` but received ''"):
            await async_client.projects.webhooks.webhook.with_raw_response.deliveries(
                webhook_id="webhook_id",
                project_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `webhook_id` but received ''"):
            await async_client.projects.webhooks.webhook.with_raw_response.deliveries(
                webhook_id="",
                project_id="project_id",
            )
