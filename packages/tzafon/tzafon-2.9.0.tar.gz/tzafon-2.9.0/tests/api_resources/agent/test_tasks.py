# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from tzafon import Computer, AsyncComputer
from tests.utils import assert_matches_type
from tzafon.types.agent import (
    TaskListResponse,
    TaskStartResponse,
    TaskGetStatusResponse,
    TaskStartByIDResponse,
    TaskSendMessageResponse,
)

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestTasks:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_list(self, client: Computer) -> None:
        task = client.agent.tasks.list()
        assert_matches_type(TaskListResponse, task, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_list(self, client: Computer) -> None:
        response = client.agent.tasks.with_raw_response.list()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        task = response.parse()
        assert_matches_type(TaskListResponse, task, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_list(self, client: Computer) -> None:
        with client.agent.tasks.with_streaming_response.list() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            task = response.parse()
            assert_matches_type(TaskListResponse, task, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_get_status(self, client: Computer) -> None:
        task = client.agent.tasks.get_status(
            "task_id",
        )
        assert_matches_type(TaskGetStatusResponse, task, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_get_status(self, client: Computer) -> None:
        response = client.agent.tasks.with_raw_response.get_status(
            "task_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        task = response.parse()
        assert_matches_type(TaskGetStatusResponse, task, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_get_status(self, client: Computer) -> None:
        with client.agent.tasks.with_streaming_response.get_status(
            "task_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            task = response.parse()
            assert_matches_type(TaskGetStatusResponse, task, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_get_status(self, client: Computer) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `task_id` but received ''"):
            client.agent.tasks.with_raw_response.get_status(
                "",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_send_message(self, client: Computer) -> None:
        task = client.agent.tasks.send_message(
            task_id="task_id",
            body={},
        )
        assert_matches_type(TaskSendMessageResponse, task, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_send_message(self, client: Computer) -> None:
        response = client.agent.tasks.with_raw_response.send_message(
            task_id="task_id",
            body={},
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        task = response.parse()
        assert_matches_type(TaskSendMessageResponse, task, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_send_message(self, client: Computer) -> None:
        with client.agent.tasks.with_streaming_response.send_message(
            task_id="task_id",
            body={},
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            task = response.parse()
            assert_matches_type(TaskSendMessageResponse, task, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_send_message(self, client: Computer) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `task_id` but received ''"):
            client.agent.tasks.with_raw_response.send_message(
                task_id="",
                body={},
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_start(self, client: Computer) -> None:
        task = client.agent.tasks.start(
            body={},
        )
        assert_matches_type(TaskStartResponse, task, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_start_with_all_params(self, client: Computer) -> None:
        task = client.agent.tasks.start(
            body={},
            stream=True,
        )
        assert_matches_type(TaskStartResponse, task, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_start(self, client: Computer) -> None:
        response = client.agent.tasks.with_raw_response.start(
            body={},
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        task = response.parse()
        assert_matches_type(TaskStartResponse, task, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_start(self, client: Computer) -> None:
        with client.agent.tasks.with_streaming_response.start(
            body={},
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            task = response.parse()
            assert_matches_type(TaskStartResponse, task, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_start_by_id(self, client: Computer) -> None:
        task = client.agent.tasks.start_by_id(
            task_id="task_id",
            body={},
        )
        assert_matches_type(TaskStartByIDResponse, task, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_start_by_id_with_all_params(self, client: Computer) -> None:
        task = client.agent.tasks.start_by_id(
            task_id="task_id",
            body={},
            stream=True,
        )
        assert_matches_type(TaskStartByIDResponse, task, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_start_by_id(self, client: Computer) -> None:
        response = client.agent.tasks.with_raw_response.start_by_id(
            task_id="task_id",
            body={},
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        task = response.parse()
        assert_matches_type(TaskStartByIDResponse, task, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_start_by_id(self, client: Computer) -> None:
        with client.agent.tasks.with_streaming_response.start_by_id(
            task_id="task_id",
            body={},
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            task = response.parse()
            assert_matches_type(TaskStartByIDResponse, task, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_start_by_id(self, client: Computer) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `task_id` but received ''"):
            client.agent.tasks.with_raw_response.start_by_id(
                task_id="",
                body={},
            )

    @pytest.mark.skip(reason="Prism doesn't support text/event-stream responses")
    @parametrize
    def test_method_stream_updates(self, client: Computer) -> None:
        task_stream = client.agent.tasks.stream_updates(
            "task_id",
        )
        task_stream.response.close()

    @pytest.mark.skip(reason="Prism doesn't support text/event-stream responses")
    @parametrize
    def test_raw_response_stream_updates(self, client: Computer) -> None:
        response = client.agent.tasks.with_raw_response.stream_updates(
            "task_id",
        )

        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        stream = response.parse()
        stream.close()

    @pytest.mark.skip(reason="Prism doesn't support text/event-stream responses")
    @parametrize
    def test_streaming_response_stream_updates(self, client: Computer) -> None:
        with client.agent.tasks.with_streaming_response.stream_updates(
            "task_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            stream = response.parse()
            stream.close()

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism doesn't support text/event-stream responses")
    @parametrize
    def test_path_params_stream_updates(self, client: Computer) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `task_id` but received ''"):
            client.agent.tasks.with_raw_response.stream_updates(
                "",
            )


class TestAsyncTasks:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_list(self, async_client: AsyncComputer) -> None:
        task = await async_client.agent.tasks.list()
        assert_matches_type(TaskListResponse, task, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_list(self, async_client: AsyncComputer) -> None:
        response = await async_client.agent.tasks.with_raw_response.list()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        task = await response.parse()
        assert_matches_type(TaskListResponse, task, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_list(self, async_client: AsyncComputer) -> None:
        async with async_client.agent.tasks.with_streaming_response.list() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            task = await response.parse()
            assert_matches_type(TaskListResponse, task, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_get_status(self, async_client: AsyncComputer) -> None:
        task = await async_client.agent.tasks.get_status(
            "task_id",
        )
        assert_matches_type(TaskGetStatusResponse, task, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_get_status(self, async_client: AsyncComputer) -> None:
        response = await async_client.agent.tasks.with_raw_response.get_status(
            "task_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        task = await response.parse()
        assert_matches_type(TaskGetStatusResponse, task, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_get_status(self, async_client: AsyncComputer) -> None:
        async with async_client.agent.tasks.with_streaming_response.get_status(
            "task_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            task = await response.parse()
            assert_matches_type(TaskGetStatusResponse, task, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_get_status(self, async_client: AsyncComputer) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `task_id` but received ''"):
            await async_client.agent.tasks.with_raw_response.get_status(
                "",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_send_message(self, async_client: AsyncComputer) -> None:
        task = await async_client.agent.tasks.send_message(
            task_id="task_id",
            body={},
        )
        assert_matches_type(TaskSendMessageResponse, task, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_send_message(self, async_client: AsyncComputer) -> None:
        response = await async_client.agent.tasks.with_raw_response.send_message(
            task_id="task_id",
            body={},
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        task = await response.parse()
        assert_matches_type(TaskSendMessageResponse, task, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_send_message(self, async_client: AsyncComputer) -> None:
        async with async_client.agent.tasks.with_streaming_response.send_message(
            task_id="task_id",
            body={},
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            task = await response.parse()
            assert_matches_type(TaskSendMessageResponse, task, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_send_message(self, async_client: AsyncComputer) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `task_id` but received ''"):
            await async_client.agent.tasks.with_raw_response.send_message(
                task_id="",
                body={},
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_start(self, async_client: AsyncComputer) -> None:
        task = await async_client.agent.tasks.start(
            body={},
        )
        assert_matches_type(TaskStartResponse, task, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_start_with_all_params(self, async_client: AsyncComputer) -> None:
        task = await async_client.agent.tasks.start(
            body={},
            stream=True,
        )
        assert_matches_type(TaskStartResponse, task, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_start(self, async_client: AsyncComputer) -> None:
        response = await async_client.agent.tasks.with_raw_response.start(
            body={},
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        task = await response.parse()
        assert_matches_type(TaskStartResponse, task, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_start(self, async_client: AsyncComputer) -> None:
        async with async_client.agent.tasks.with_streaming_response.start(
            body={},
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            task = await response.parse()
            assert_matches_type(TaskStartResponse, task, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_start_by_id(self, async_client: AsyncComputer) -> None:
        task = await async_client.agent.tasks.start_by_id(
            task_id="task_id",
            body={},
        )
        assert_matches_type(TaskStartByIDResponse, task, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_start_by_id_with_all_params(self, async_client: AsyncComputer) -> None:
        task = await async_client.agent.tasks.start_by_id(
            task_id="task_id",
            body={},
            stream=True,
        )
        assert_matches_type(TaskStartByIDResponse, task, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_start_by_id(self, async_client: AsyncComputer) -> None:
        response = await async_client.agent.tasks.with_raw_response.start_by_id(
            task_id="task_id",
            body={},
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        task = await response.parse()
        assert_matches_type(TaskStartByIDResponse, task, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_start_by_id(self, async_client: AsyncComputer) -> None:
        async with async_client.agent.tasks.with_streaming_response.start_by_id(
            task_id="task_id",
            body={},
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            task = await response.parse()
            assert_matches_type(TaskStartByIDResponse, task, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_start_by_id(self, async_client: AsyncComputer) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `task_id` but received ''"):
            await async_client.agent.tasks.with_raw_response.start_by_id(
                task_id="",
                body={},
            )

    @pytest.mark.skip(reason="Prism doesn't support text/event-stream responses")
    @parametrize
    async def test_method_stream_updates(self, async_client: AsyncComputer) -> None:
        task_stream = await async_client.agent.tasks.stream_updates(
            "task_id",
        )
        await task_stream.response.aclose()

    @pytest.mark.skip(reason="Prism doesn't support text/event-stream responses")
    @parametrize
    async def test_raw_response_stream_updates(self, async_client: AsyncComputer) -> None:
        response = await async_client.agent.tasks.with_raw_response.stream_updates(
            "task_id",
        )

        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        stream = await response.parse()
        await stream.close()

    @pytest.mark.skip(reason="Prism doesn't support text/event-stream responses")
    @parametrize
    async def test_streaming_response_stream_updates(self, async_client: AsyncComputer) -> None:
        async with async_client.agent.tasks.with_streaming_response.stream_updates(
            "task_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            stream = await response.parse()
            await stream.close()

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism doesn't support text/event-stream responses")
    @parametrize
    async def test_path_params_stream_updates(self, async_client: AsyncComputer) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `task_id` but received ''"):
            await async_client.agent.tasks.with_raw_response.stream_updates(
                "",
            )
