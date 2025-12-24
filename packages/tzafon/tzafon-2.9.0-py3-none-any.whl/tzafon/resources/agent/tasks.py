# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import httpx

from ..._types import Body, Omit, Query, Headers, NotGiven, omit, not_given
from ..._utils import maybe_transform, async_maybe_transform
from ..._compat import cached_property
from ..._resource import SyncAPIResource, AsyncAPIResource
from ..._response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from ..._streaming import Stream, AsyncStream
from ...types.agent import task_start_params, task_start_by_id_params, task_send_message_params
from ..._base_client import make_request_options
from ...types.agent.task_list_response import TaskListResponse
from ...types.agent.task_start_response import TaskStartResponse
from ...types.agent.task_get_status_response import TaskGetStatusResponse
from ...types.agent.task_start_by_id_response import TaskStartByIDResponse
from ...types.agent.task_send_message_response import TaskSendMessageResponse
from ...types.agent.task_stream_updates_response import TaskStreamUpdatesResponse

__all__ = ["TasksResource", "AsyncTasksResource"]


class TasksResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> TasksResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/tzafon/computer-python#accessing-raw-response-data-eg-headers
        """
        return TasksResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> TasksResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/tzafon/computer-python#with_streaming_response
        """
        return TasksResourceWithStreamingResponse(self)

    def list(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> TaskListResponse:
        """Get a list of all agent tasks for the authenticated user."""
        return self._get(
            "/agent/tasks",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=TaskListResponse,
        )

    def get_status(
        self,
        task_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> TaskGetStatusResponse:
        """
        Get the current status and metadata of an agent task.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not task_id:
            raise ValueError(f"Expected a non-empty value for `task_id` but received {task_id!r}")
        return self._get(
            f"/agent/tasks/{task_id}/status",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=TaskGetStatusResponse,
        )

    def send_message(
        self,
        task_id: str,
        *,
        body: object,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> TaskSendMessageResponse:
        """
        Inject a user message into a running agent task with debouncing and rate
        limiting. The message will interrupt the agent's current workflow and be
        processed after a 2-second debounce window.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not task_id:
            raise ValueError(f"Expected a non-empty value for `task_id` but received {task_id!r}")
        return self._post(
            f"/agent/tasks/{task_id}/messages",
            body=maybe_transform(body, task_send_message_params.TaskSendMessageParams),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=TaskSendMessageResponse,
        )

    def start(
        self,
        *,
        body: object,
        stream: bool | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> TaskStartResponse:
        """Start a freeform agent task with custom instruction or structured messages.

        The
        task will execute browser automation actions based on the provided instruction
        or conversation history.

        Args:
          stream: Enable streaming via Server-Sent Events (SSE)

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/agent/tasks",
            body=maybe_transform(body, task_start_params.TaskStartParams),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform({"stream": stream}, task_start_params.TaskStartParams),
            ),
            cast_to=TaskStartResponse,
        )

    def start_by_id(
        self,
        task_id: str,
        *,
        body: object,
        stream: bool | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> TaskStartByIDResponse:
        """Start a task by predefined task ID.

        Currently unused - intended for OSWorld
        benchmark tasks with predefined IDs.

        Args:
          stream: Enable streaming via Server-Sent Events (SSE)

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not task_id:
            raise ValueError(f"Expected a non-empty value for `task_id` but received {task_id!r}")
        return self._post(
            f"/agent/tasks/{task_id}",
            body=maybe_transform(body, task_start_by_id_params.TaskStartByIDParams),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform({"stream": stream}, task_start_by_id_params.TaskStartByIDParams),
            ),
            cast_to=TaskStartByIDResponse,
        )

    def stream_updates(
        self,
        task_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> Stream[TaskStreamUpdatesResponse]:
        """
        Stream real-time updates for an agent task using Server-Sent Events (SSE).
        Returns events such as setup progress, agent actions, observations, and task
        completion.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not task_id:
            raise ValueError(f"Expected a non-empty value for `task_id` but received {task_id!r}")
        extra_headers = {"Accept": "text/event-stream", **(extra_headers or {})}
        return self._get(
            f"/agent/tasks/{task_id}/stream",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=str,
            stream=True,
            stream_cls=Stream[TaskStreamUpdatesResponse],
        )


class AsyncTasksResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncTasksResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/tzafon/computer-python#accessing-raw-response-data-eg-headers
        """
        return AsyncTasksResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncTasksResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/tzafon/computer-python#with_streaming_response
        """
        return AsyncTasksResourceWithStreamingResponse(self)

    async def list(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> TaskListResponse:
        """Get a list of all agent tasks for the authenticated user."""
        return await self._get(
            "/agent/tasks",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=TaskListResponse,
        )

    async def get_status(
        self,
        task_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> TaskGetStatusResponse:
        """
        Get the current status and metadata of an agent task.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not task_id:
            raise ValueError(f"Expected a non-empty value for `task_id` but received {task_id!r}")
        return await self._get(
            f"/agent/tasks/{task_id}/status",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=TaskGetStatusResponse,
        )

    async def send_message(
        self,
        task_id: str,
        *,
        body: object,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> TaskSendMessageResponse:
        """
        Inject a user message into a running agent task with debouncing and rate
        limiting. The message will interrupt the agent's current workflow and be
        processed after a 2-second debounce window.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not task_id:
            raise ValueError(f"Expected a non-empty value for `task_id` but received {task_id!r}")
        return await self._post(
            f"/agent/tasks/{task_id}/messages",
            body=await async_maybe_transform(body, task_send_message_params.TaskSendMessageParams),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=TaskSendMessageResponse,
        )

    async def start(
        self,
        *,
        body: object,
        stream: bool | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> TaskStartResponse:
        """Start a freeform agent task with custom instruction or structured messages.

        The
        task will execute browser automation actions based on the provided instruction
        or conversation history.

        Args:
          stream: Enable streaming via Server-Sent Events (SSE)

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/agent/tasks",
            body=await async_maybe_transform(body, task_start_params.TaskStartParams),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform({"stream": stream}, task_start_params.TaskStartParams),
            ),
            cast_to=TaskStartResponse,
        )

    async def start_by_id(
        self,
        task_id: str,
        *,
        body: object,
        stream: bool | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> TaskStartByIDResponse:
        """Start a task by predefined task ID.

        Currently unused - intended for OSWorld
        benchmark tasks with predefined IDs.

        Args:
          stream: Enable streaming via Server-Sent Events (SSE)

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not task_id:
            raise ValueError(f"Expected a non-empty value for `task_id` but received {task_id!r}")
        return await self._post(
            f"/agent/tasks/{task_id}",
            body=await async_maybe_transform(body, task_start_by_id_params.TaskStartByIDParams),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform({"stream": stream}, task_start_by_id_params.TaskStartByIDParams),
            ),
            cast_to=TaskStartByIDResponse,
        )

    async def stream_updates(
        self,
        task_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> AsyncStream[TaskStreamUpdatesResponse]:
        """
        Stream real-time updates for an agent task using Server-Sent Events (SSE).
        Returns events such as setup progress, agent actions, observations, and task
        completion.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not task_id:
            raise ValueError(f"Expected a non-empty value for `task_id` but received {task_id!r}")
        extra_headers = {"Accept": "text/event-stream", **(extra_headers or {})}
        return await self._get(
            f"/agent/tasks/{task_id}/stream",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=str,
            stream=True,
            stream_cls=AsyncStream[TaskStreamUpdatesResponse],
        )


class TasksResourceWithRawResponse:
    def __init__(self, tasks: TasksResource) -> None:
        self._tasks = tasks

        self.list = to_raw_response_wrapper(
            tasks.list,
        )
        self.get_status = to_raw_response_wrapper(
            tasks.get_status,
        )
        self.send_message = to_raw_response_wrapper(
            tasks.send_message,
        )
        self.start = to_raw_response_wrapper(
            tasks.start,
        )
        self.start_by_id = to_raw_response_wrapper(
            tasks.start_by_id,
        )
        self.stream_updates = to_raw_response_wrapper(
            tasks.stream_updates,
        )


class AsyncTasksResourceWithRawResponse:
    def __init__(self, tasks: AsyncTasksResource) -> None:
        self._tasks = tasks

        self.list = async_to_raw_response_wrapper(
            tasks.list,
        )
        self.get_status = async_to_raw_response_wrapper(
            tasks.get_status,
        )
        self.send_message = async_to_raw_response_wrapper(
            tasks.send_message,
        )
        self.start = async_to_raw_response_wrapper(
            tasks.start,
        )
        self.start_by_id = async_to_raw_response_wrapper(
            tasks.start_by_id,
        )
        self.stream_updates = async_to_raw_response_wrapper(
            tasks.stream_updates,
        )


class TasksResourceWithStreamingResponse:
    def __init__(self, tasks: TasksResource) -> None:
        self._tasks = tasks

        self.list = to_streamed_response_wrapper(
            tasks.list,
        )
        self.get_status = to_streamed_response_wrapper(
            tasks.get_status,
        )
        self.send_message = to_streamed_response_wrapper(
            tasks.send_message,
        )
        self.start = to_streamed_response_wrapper(
            tasks.start,
        )
        self.start_by_id = to_streamed_response_wrapper(
            tasks.start_by_id,
        )
        self.stream_updates = to_streamed_response_wrapper(
            tasks.stream_updates,
        )


class AsyncTasksResourceWithStreamingResponse:
    def __init__(self, tasks: AsyncTasksResource) -> None:
        self._tasks = tasks

        self.list = async_to_streamed_response_wrapper(
            tasks.list,
        )
        self.get_status = async_to_streamed_response_wrapper(
            tasks.get_status,
        )
        self.send_message = async_to_streamed_response_wrapper(
            tasks.send_message,
        )
        self.start = async_to_streamed_response_wrapper(
            tasks.start,
        )
        self.start_by_id = async_to_streamed_response_wrapper(
            tasks.start_by_id,
        )
        self.stream_updates = async_to_streamed_response_wrapper(
            tasks.stream_updates,
        )
