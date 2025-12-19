# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from cnos_hub import CnosHub, AsyncCnosHub
from tests.utils import assert_matches_type
from cnos_hub.pagination import SyncPage, AsyncPage
from cnos_hub.types.projects import (
    TaskRunResponse,
    TaskListResponse,
    TaskRunsResponse,
    TaskCreateResponse,
    TaskUpdateResponse,
    TaskHistoryResponse,
    TaskRetrieveResponse,
)

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestTasks:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_create(self, client: CnosHub) -> None:
        task = client.projects.tasks.create(
            project_id="project_id",
            name="name",
            retry={
                "backoff": {
                    "delay_ms": 0,
                    "kind": "fixed",
                },
                "max_attempts": 0,
            },
            run_as={
                "capabilities": ["OrgRead"],
                "principal_id": "principal_id",
            },
            runner={
                "args_from": "empty",
                "function": "function",
                "kind": "cnos",
                "result_mode": "ignore",
            },
            trigger={"kind": "manual"},
        )
        assert_matches_type(TaskCreateResponse, task, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_create_with_all_params(self, client: CnosHub) -> None:
        task = client.projects.tasks.create(
            project_id="project_id",
            name="name",
            retry={
                "backoff": {
                    "delay_ms": 0,
                    "kind": "fixed",
                },
                "max_attempts": 0,
                "scope": "none",
            },
            run_as={
                "capabilities": ["OrgRead"],
                "principal_id": "principal_id",
                "labels": ["string"],
                "roles": ["string"],
            },
            runner={
                "args_from": "empty",
                "function": "function",
                "kind": "cnos",
                "result_mode": "ignore",
            },
            trigger={"kind": "manual"},
            description="description",
        )
        assert_matches_type(TaskCreateResponse, task, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_create(self, client: CnosHub) -> None:
        response = client.projects.tasks.with_raw_response.create(
            project_id="project_id",
            name="name",
            retry={
                "backoff": {
                    "delay_ms": 0,
                    "kind": "fixed",
                },
                "max_attempts": 0,
            },
            run_as={
                "capabilities": ["OrgRead"],
                "principal_id": "principal_id",
            },
            runner={
                "args_from": "empty",
                "function": "function",
                "kind": "cnos",
                "result_mode": "ignore",
            },
            trigger={"kind": "manual"},
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        task = response.parse()
        assert_matches_type(TaskCreateResponse, task, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_create(self, client: CnosHub) -> None:
        with client.projects.tasks.with_streaming_response.create(
            project_id="project_id",
            name="name",
            retry={
                "backoff": {
                    "delay_ms": 0,
                    "kind": "fixed",
                },
                "max_attempts": 0,
            },
            run_as={
                "capabilities": ["OrgRead"],
                "principal_id": "principal_id",
            },
            runner={
                "args_from": "empty",
                "function": "function",
                "kind": "cnos",
                "result_mode": "ignore",
            },
            trigger={"kind": "manual"},
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            task = response.parse()
            assert_matches_type(TaskCreateResponse, task, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_create(self, client: CnosHub) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `project_id` but received ''"):
            client.projects.tasks.with_raw_response.create(
                project_id="",
                name="name",
                retry={
                    "backoff": {
                        "delay_ms": 0,
                        "kind": "fixed",
                    },
                    "max_attempts": 0,
                },
                run_as={
                    "capabilities": ["OrgRead"],
                    "principal_id": "principal_id",
                },
                runner={
                    "args_from": "empty",
                    "function": "function",
                    "kind": "cnos",
                    "result_mode": "ignore",
                },
                trigger={"kind": "manual"},
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_retrieve(self, client: CnosHub) -> None:
        task = client.projects.tasks.retrieve(
            task_id="task_id",
            project_id="project_id",
        )
        assert_matches_type(TaskRetrieveResponse, task, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_retrieve(self, client: CnosHub) -> None:
        response = client.projects.tasks.with_raw_response.retrieve(
            task_id="task_id",
            project_id="project_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        task = response.parse()
        assert_matches_type(TaskRetrieveResponse, task, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_retrieve(self, client: CnosHub) -> None:
        with client.projects.tasks.with_streaming_response.retrieve(
            task_id="task_id",
            project_id="project_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            task = response.parse()
            assert_matches_type(TaskRetrieveResponse, task, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_retrieve(self, client: CnosHub) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `project_id` but received ''"):
            client.projects.tasks.with_raw_response.retrieve(
                task_id="task_id",
                project_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `task_id` but received ''"):
            client.projects.tasks.with_raw_response.retrieve(
                task_id="",
                project_id="project_id",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_update(self, client: CnosHub) -> None:
        task = client.projects.tasks.update(
            task_id="task_id",
            project_id="project_id",
        )
        assert_matches_type(TaskUpdateResponse, task, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_update_with_all_params(self, client: CnosHub) -> None:
        task = client.projects.tasks.update(
            task_id="task_id",
            project_id="project_id",
            description="description",
            name="name",
            retry={
                "backoff": {
                    "delay_ms": 0,
                    "kind": "fixed",
                },
                "max_attempts": 0,
                "scope": "none",
            },
            run_as={
                "capabilities": ["OrgRead"],
                "principal_id": "principal_id",
                "labels": ["string"],
                "roles": ["string"],
            },
            runner={
                "args_from": "empty",
                "function": "function",
                "kind": "cnos",
                "result_mode": "ignore",
            },
            status="active",
            trigger={"kind": "manual"},
        )
        assert_matches_type(TaskUpdateResponse, task, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_update(self, client: CnosHub) -> None:
        response = client.projects.tasks.with_raw_response.update(
            task_id="task_id",
            project_id="project_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        task = response.parse()
        assert_matches_type(TaskUpdateResponse, task, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_update(self, client: CnosHub) -> None:
        with client.projects.tasks.with_streaming_response.update(
            task_id="task_id",
            project_id="project_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            task = response.parse()
            assert_matches_type(TaskUpdateResponse, task, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_update(self, client: CnosHub) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `project_id` but received ''"):
            client.projects.tasks.with_raw_response.update(
                task_id="task_id",
                project_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `task_id` but received ''"):
            client.projects.tasks.with_raw_response.update(
                task_id="",
                project_id="project_id",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_list(self, client: CnosHub) -> None:
        task = client.projects.tasks.list(
            project_id="project_id",
        )
        assert_matches_type(SyncPage[TaskListResponse], task, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_list_with_all_params(self, client: CnosHub) -> None:
        task = client.projects.tasks.list(
            project_id="project_id",
            cursor="cursor",
            limit=0,
            status="active",
            trigger_kind="trigger_kind",
        )
        assert_matches_type(SyncPage[TaskListResponse], task, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_list(self, client: CnosHub) -> None:
        response = client.projects.tasks.with_raw_response.list(
            project_id="project_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        task = response.parse()
        assert_matches_type(SyncPage[TaskListResponse], task, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_list(self, client: CnosHub) -> None:
        with client.projects.tasks.with_streaming_response.list(
            project_id="project_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            task = response.parse()
            assert_matches_type(SyncPage[TaskListResponse], task, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_list(self, client: CnosHub) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `project_id` but received ''"):
            client.projects.tasks.with_raw_response.list(
                project_id="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_delete(self, client: CnosHub) -> None:
        task = client.projects.tasks.delete(
            task_id="task_id",
            project_id="project_id",
        )
        assert task is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_delete(self, client: CnosHub) -> None:
        response = client.projects.tasks.with_raw_response.delete(
            task_id="task_id",
            project_id="project_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        task = response.parse()
        assert task is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_delete(self, client: CnosHub) -> None:
        with client.projects.tasks.with_streaming_response.delete(
            task_id="task_id",
            project_id="project_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            task = response.parse()
            assert task is None

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_delete(self, client: CnosHub) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `project_id` but received ''"):
            client.projects.tasks.with_raw_response.delete(
                task_id="task_id",
                project_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `task_id` but received ''"):
            client.projects.tasks.with_raw_response.delete(
                task_id="",
                project_id="project_id",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_history(self, client: CnosHub) -> None:
        task = client.projects.tasks.history(
            task_id="task_id",
            project_id="project_id",
        )
        assert_matches_type(SyncPage[TaskHistoryResponse], task, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_history_with_all_params(self, client: CnosHub) -> None:
        task = client.projects.tasks.history(
            task_id="task_id",
            project_id="project_id",
            cursor="cursor",
            limit=0,
        )
        assert_matches_type(SyncPage[TaskHistoryResponse], task, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_history(self, client: CnosHub) -> None:
        response = client.projects.tasks.with_raw_response.history(
            task_id="task_id",
            project_id="project_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        task = response.parse()
        assert_matches_type(SyncPage[TaskHistoryResponse], task, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_history(self, client: CnosHub) -> None:
        with client.projects.tasks.with_streaming_response.history(
            task_id="task_id",
            project_id="project_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            task = response.parse()
            assert_matches_type(SyncPage[TaskHistoryResponse], task, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_history(self, client: CnosHub) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `project_id` but received ''"):
            client.projects.tasks.with_raw_response.history(
                task_id="task_id",
                project_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `task_id` but received ''"):
            client.projects.tasks.with_raw_response.history(
                task_id="",
                project_id="project_id",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_run(self, client: CnosHub) -> None:
        task = client.projects.tasks.run(
            task_id="task_id",
            project_id="project_id",
        )
        assert_matches_type(TaskRunResponse, task, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_run_with_all_params(self, client: CnosHub) -> None:
        task = client.projects.tasks.run(
            task_id="task_id",
            project_id="project_id",
            payload={"foo": "bar"},
        )
        assert_matches_type(TaskRunResponse, task, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_run(self, client: CnosHub) -> None:
        response = client.projects.tasks.with_raw_response.run(
            task_id="task_id",
            project_id="project_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        task = response.parse()
        assert_matches_type(TaskRunResponse, task, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_run(self, client: CnosHub) -> None:
        with client.projects.tasks.with_streaming_response.run(
            task_id="task_id",
            project_id="project_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            task = response.parse()
            assert_matches_type(TaskRunResponse, task, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_run(self, client: CnosHub) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `project_id` but received ''"):
            client.projects.tasks.with_raw_response.run(
                task_id="task_id",
                project_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `task_id` but received ''"):
            client.projects.tasks.with_raw_response.run(
                task_id="",
                project_id="project_id",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_runs(self, client: CnosHub) -> None:
        task = client.projects.tasks.runs(
            task_id="task_id",
            project_id="project_id",
        )
        assert_matches_type(SyncPage[TaskRunsResponse], task, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_runs_with_all_params(self, client: CnosHub) -> None:
        task = client.projects.tasks.runs(
            task_id="task_id",
            project_id="project_id",
            cursor="cursor",
            limit=0,
            status="running",
        )
        assert_matches_type(SyncPage[TaskRunsResponse], task, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_runs(self, client: CnosHub) -> None:
        response = client.projects.tasks.with_raw_response.runs(
            task_id="task_id",
            project_id="project_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        task = response.parse()
        assert_matches_type(SyncPage[TaskRunsResponse], task, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_runs(self, client: CnosHub) -> None:
        with client.projects.tasks.with_streaming_response.runs(
            task_id="task_id",
            project_id="project_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            task = response.parse()
            assert_matches_type(SyncPage[TaskRunsResponse], task, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_runs(self, client: CnosHub) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `project_id` but received ''"):
            client.projects.tasks.with_raw_response.runs(
                task_id="task_id",
                project_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `task_id` but received ''"):
            client.projects.tasks.with_raw_response.runs(
                task_id="",
                project_id="project_id",
            )


class TestAsyncTasks:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_create(self, async_client: AsyncCnosHub) -> None:
        task = await async_client.projects.tasks.create(
            project_id="project_id",
            name="name",
            retry={
                "backoff": {
                    "delay_ms": 0,
                    "kind": "fixed",
                },
                "max_attempts": 0,
            },
            run_as={
                "capabilities": ["OrgRead"],
                "principal_id": "principal_id",
            },
            runner={
                "args_from": "empty",
                "function": "function",
                "kind": "cnos",
                "result_mode": "ignore",
            },
            trigger={"kind": "manual"},
        )
        assert_matches_type(TaskCreateResponse, task, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_create_with_all_params(self, async_client: AsyncCnosHub) -> None:
        task = await async_client.projects.tasks.create(
            project_id="project_id",
            name="name",
            retry={
                "backoff": {
                    "delay_ms": 0,
                    "kind": "fixed",
                },
                "max_attempts": 0,
                "scope": "none",
            },
            run_as={
                "capabilities": ["OrgRead"],
                "principal_id": "principal_id",
                "labels": ["string"],
                "roles": ["string"],
            },
            runner={
                "args_from": "empty",
                "function": "function",
                "kind": "cnos",
                "result_mode": "ignore",
            },
            trigger={"kind": "manual"},
            description="description",
        )
        assert_matches_type(TaskCreateResponse, task, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_create(self, async_client: AsyncCnosHub) -> None:
        response = await async_client.projects.tasks.with_raw_response.create(
            project_id="project_id",
            name="name",
            retry={
                "backoff": {
                    "delay_ms": 0,
                    "kind": "fixed",
                },
                "max_attempts": 0,
            },
            run_as={
                "capabilities": ["OrgRead"],
                "principal_id": "principal_id",
            },
            runner={
                "args_from": "empty",
                "function": "function",
                "kind": "cnos",
                "result_mode": "ignore",
            },
            trigger={"kind": "manual"},
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        task = await response.parse()
        assert_matches_type(TaskCreateResponse, task, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_create(self, async_client: AsyncCnosHub) -> None:
        async with async_client.projects.tasks.with_streaming_response.create(
            project_id="project_id",
            name="name",
            retry={
                "backoff": {
                    "delay_ms": 0,
                    "kind": "fixed",
                },
                "max_attempts": 0,
            },
            run_as={
                "capabilities": ["OrgRead"],
                "principal_id": "principal_id",
            },
            runner={
                "args_from": "empty",
                "function": "function",
                "kind": "cnos",
                "result_mode": "ignore",
            },
            trigger={"kind": "manual"},
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            task = await response.parse()
            assert_matches_type(TaskCreateResponse, task, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_create(self, async_client: AsyncCnosHub) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `project_id` but received ''"):
            await async_client.projects.tasks.with_raw_response.create(
                project_id="",
                name="name",
                retry={
                    "backoff": {
                        "delay_ms": 0,
                        "kind": "fixed",
                    },
                    "max_attempts": 0,
                },
                run_as={
                    "capabilities": ["OrgRead"],
                    "principal_id": "principal_id",
                },
                runner={
                    "args_from": "empty",
                    "function": "function",
                    "kind": "cnos",
                    "result_mode": "ignore",
                },
                trigger={"kind": "manual"},
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_retrieve(self, async_client: AsyncCnosHub) -> None:
        task = await async_client.projects.tasks.retrieve(
            task_id="task_id",
            project_id="project_id",
        )
        assert_matches_type(TaskRetrieveResponse, task, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_retrieve(self, async_client: AsyncCnosHub) -> None:
        response = await async_client.projects.tasks.with_raw_response.retrieve(
            task_id="task_id",
            project_id="project_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        task = await response.parse()
        assert_matches_type(TaskRetrieveResponse, task, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_retrieve(self, async_client: AsyncCnosHub) -> None:
        async with async_client.projects.tasks.with_streaming_response.retrieve(
            task_id="task_id",
            project_id="project_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            task = await response.parse()
            assert_matches_type(TaskRetrieveResponse, task, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_retrieve(self, async_client: AsyncCnosHub) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `project_id` but received ''"):
            await async_client.projects.tasks.with_raw_response.retrieve(
                task_id="task_id",
                project_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `task_id` but received ''"):
            await async_client.projects.tasks.with_raw_response.retrieve(
                task_id="",
                project_id="project_id",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_update(self, async_client: AsyncCnosHub) -> None:
        task = await async_client.projects.tasks.update(
            task_id="task_id",
            project_id="project_id",
        )
        assert_matches_type(TaskUpdateResponse, task, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_update_with_all_params(self, async_client: AsyncCnosHub) -> None:
        task = await async_client.projects.tasks.update(
            task_id="task_id",
            project_id="project_id",
            description="description",
            name="name",
            retry={
                "backoff": {
                    "delay_ms": 0,
                    "kind": "fixed",
                },
                "max_attempts": 0,
                "scope": "none",
            },
            run_as={
                "capabilities": ["OrgRead"],
                "principal_id": "principal_id",
                "labels": ["string"],
                "roles": ["string"],
            },
            runner={
                "args_from": "empty",
                "function": "function",
                "kind": "cnos",
                "result_mode": "ignore",
            },
            status="active",
            trigger={"kind": "manual"},
        )
        assert_matches_type(TaskUpdateResponse, task, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_update(self, async_client: AsyncCnosHub) -> None:
        response = await async_client.projects.tasks.with_raw_response.update(
            task_id="task_id",
            project_id="project_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        task = await response.parse()
        assert_matches_type(TaskUpdateResponse, task, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_update(self, async_client: AsyncCnosHub) -> None:
        async with async_client.projects.tasks.with_streaming_response.update(
            task_id="task_id",
            project_id="project_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            task = await response.parse()
            assert_matches_type(TaskUpdateResponse, task, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_update(self, async_client: AsyncCnosHub) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `project_id` but received ''"):
            await async_client.projects.tasks.with_raw_response.update(
                task_id="task_id",
                project_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `task_id` but received ''"):
            await async_client.projects.tasks.with_raw_response.update(
                task_id="",
                project_id="project_id",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_list(self, async_client: AsyncCnosHub) -> None:
        task = await async_client.projects.tasks.list(
            project_id="project_id",
        )
        assert_matches_type(AsyncPage[TaskListResponse], task, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_list_with_all_params(self, async_client: AsyncCnosHub) -> None:
        task = await async_client.projects.tasks.list(
            project_id="project_id",
            cursor="cursor",
            limit=0,
            status="active",
            trigger_kind="trigger_kind",
        )
        assert_matches_type(AsyncPage[TaskListResponse], task, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_list(self, async_client: AsyncCnosHub) -> None:
        response = await async_client.projects.tasks.with_raw_response.list(
            project_id="project_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        task = await response.parse()
        assert_matches_type(AsyncPage[TaskListResponse], task, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_list(self, async_client: AsyncCnosHub) -> None:
        async with async_client.projects.tasks.with_streaming_response.list(
            project_id="project_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            task = await response.parse()
            assert_matches_type(AsyncPage[TaskListResponse], task, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_list(self, async_client: AsyncCnosHub) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `project_id` but received ''"):
            await async_client.projects.tasks.with_raw_response.list(
                project_id="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_delete(self, async_client: AsyncCnosHub) -> None:
        task = await async_client.projects.tasks.delete(
            task_id="task_id",
            project_id="project_id",
        )
        assert task is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_delete(self, async_client: AsyncCnosHub) -> None:
        response = await async_client.projects.tasks.with_raw_response.delete(
            task_id="task_id",
            project_id="project_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        task = await response.parse()
        assert task is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_delete(self, async_client: AsyncCnosHub) -> None:
        async with async_client.projects.tasks.with_streaming_response.delete(
            task_id="task_id",
            project_id="project_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            task = await response.parse()
            assert task is None

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_delete(self, async_client: AsyncCnosHub) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `project_id` but received ''"):
            await async_client.projects.tasks.with_raw_response.delete(
                task_id="task_id",
                project_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `task_id` but received ''"):
            await async_client.projects.tasks.with_raw_response.delete(
                task_id="",
                project_id="project_id",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_history(self, async_client: AsyncCnosHub) -> None:
        task = await async_client.projects.tasks.history(
            task_id="task_id",
            project_id="project_id",
        )
        assert_matches_type(AsyncPage[TaskHistoryResponse], task, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_history_with_all_params(self, async_client: AsyncCnosHub) -> None:
        task = await async_client.projects.tasks.history(
            task_id="task_id",
            project_id="project_id",
            cursor="cursor",
            limit=0,
        )
        assert_matches_type(AsyncPage[TaskHistoryResponse], task, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_history(self, async_client: AsyncCnosHub) -> None:
        response = await async_client.projects.tasks.with_raw_response.history(
            task_id="task_id",
            project_id="project_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        task = await response.parse()
        assert_matches_type(AsyncPage[TaskHistoryResponse], task, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_history(self, async_client: AsyncCnosHub) -> None:
        async with async_client.projects.tasks.with_streaming_response.history(
            task_id="task_id",
            project_id="project_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            task = await response.parse()
            assert_matches_type(AsyncPage[TaskHistoryResponse], task, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_history(self, async_client: AsyncCnosHub) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `project_id` but received ''"):
            await async_client.projects.tasks.with_raw_response.history(
                task_id="task_id",
                project_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `task_id` but received ''"):
            await async_client.projects.tasks.with_raw_response.history(
                task_id="",
                project_id="project_id",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_run(self, async_client: AsyncCnosHub) -> None:
        task = await async_client.projects.tasks.run(
            task_id="task_id",
            project_id="project_id",
        )
        assert_matches_type(TaskRunResponse, task, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_run_with_all_params(self, async_client: AsyncCnosHub) -> None:
        task = await async_client.projects.tasks.run(
            task_id="task_id",
            project_id="project_id",
            payload={"foo": "bar"},
        )
        assert_matches_type(TaskRunResponse, task, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_run(self, async_client: AsyncCnosHub) -> None:
        response = await async_client.projects.tasks.with_raw_response.run(
            task_id="task_id",
            project_id="project_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        task = await response.parse()
        assert_matches_type(TaskRunResponse, task, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_run(self, async_client: AsyncCnosHub) -> None:
        async with async_client.projects.tasks.with_streaming_response.run(
            task_id="task_id",
            project_id="project_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            task = await response.parse()
            assert_matches_type(TaskRunResponse, task, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_run(self, async_client: AsyncCnosHub) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `project_id` but received ''"):
            await async_client.projects.tasks.with_raw_response.run(
                task_id="task_id",
                project_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `task_id` but received ''"):
            await async_client.projects.tasks.with_raw_response.run(
                task_id="",
                project_id="project_id",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_runs(self, async_client: AsyncCnosHub) -> None:
        task = await async_client.projects.tasks.runs(
            task_id="task_id",
            project_id="project_id",
        )
        assert_matches_type(AsyncPage[TaskRunsResponse], task, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_runs_with_all_params(self, async_client: AsyncCnosHub) -> None:
        task = await async_client.projects.tasks.runs(
            task_id="task_id",
            project_id="project_id",
            cursor="cursor",
            limit=0,
            status="running",
        )
        assert_matches_type(AsyncPage[TaskRunsResponse], task, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_runs(self, async_client: AsyncCnosHub) -> None:
        response = await async_client.projects.tasks.with_raw_response.runs(
            task_id="task_id",
            project_id="project_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        task = await response.parse()
        assert_matches_type(AsyncPage[TaskRunsResponse], task, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_runs(self, async_client: AsyncCnosHub) -> None:
        async with async_client.projects.tasks.with_streaming_response.runs(
            task_id="task_id",
            project_id="project_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            task = await response.parse()
            assert_matches_type(AsyncPage[TaskRunsResponse], task, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_runs(self, async_client: AsyncCnosHub) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `project_id` but received ''"):
            await async_client.projects.tasks.with_raw_response.runs(
                task_id="task_id",
                project_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `task_id` but received ''"):
            await async_client.projects.tasks.with_raw_response.runs(
                task_id="",
                project_id="project_id",
            )
