"""
Task Manager Module

This module provides abstract base class and concrete implementation for task management,
including task creation, status updates, notifications, and streaming responses.
"""

from abc import ABC, abstractmethod
import asyncio
from collections import defaultdict
import json
import os
import sys
import traceback
from typing import Any, Dict, List, Optional

from fastapi import Request
from fastapi.responses import JSONResponse
from loguru import logger
from pydantic import ValidationError
from sse_starlette.sse import EventSourceResponse
from typing_extensions import AsyncIterable, Union

from agentlin.core.agent_schema import content_data_to_content_item
from agentlin.core.types import *
from agentlin.store.task_store import InMemoryTaskStore
from agentlin.tools.core import tool_result_of_internal_error


class SequenceCounter(BaseModel):
    sequence_number: int = 0

    current_content_index: int = 0
    current_output_index: int = 0

    # we use this to track the current output text content for things
    # like providing the right indices in citations
    # 蓝链的 offset
    # 引用[^1] 的 offset
    current_output_text_content: str = ""

    def counting_event(self, event: TaskEvent):
        event.sequence_number = self.sequence_number
        self.sequence_number += 1
        return event


class StreamableTaskParser:
    def __init__(self, initial_task: TaskObject):
        self.output_item_id2idx: dict[str, int] = {}
        self.task = initial_task
        for idx, item in enumerate(self.task.output):
            self.output_item_id2idx[item.id] = idx

    def update_item(self, updated_item: OutputItem):
        if updated_item.id in self.output_item_id2idx:
            idx = self.output_item_id2idx[updated_item.id]
            item = self.task.output[idx]
            if item == updated_item:
                return
            self.task.output[idx] = updated_item
            return
        self.task.output.append(updated_item)
        self.output_item_id2idx[updated_item.id] = len(self.task.output) - 1

    def process(self, event: AgentTaskEvent) -> Optional[TaskObject]:
        # 如果有更新，则返回 self.task，否则返回 None
        if not event:
            return None
        if event.task_id != self.task.id:
            logger.warning(f"Event task_id {event.task_id} does not match parser task id {self.task.id}")
            return None
        if isinstance(
            event,
            (
                TaskOutputItemAddedEvent,
                TaskOutputItemDoneEvent,
            ),
        ):
            self.update_item(event.item)
            return self.task
        elif isinstance(event, TaskRolloutEvent):
            self.task.append_rollout(event)
            return self.task
        elif isinstance(event, ObjectEvent):
            # object is always updated self.task
            self.task = event.task
            if isinstance(event, TaskCreatedEvent):
                self.task.status = TaskStatus.CREATED
            elif isinstance(event, TaskQueuedEvent):
                self.task.status = TaskStatus.QUEUED
            elif isinstance(event, TaskWorkingEvent):
                self.task.status = TaskStatus.WORKING
            elif isinstance(event, TaskInputRequiredEvent):
                self.task.status = TaskStatus.INPUT_REQUIRED
                self.task.input_required = event.input_required
            elif isinstance(event, TaskPausedEvent):
                self.task.status = TaskStatus.PAUSED
            elif isinstance(event, TaskCompletedEvent):
                self.task.status = TaskStatus.COMPLETED
            elif isinstance(event, TaskCanceledEvent):
                self.task.status = TaskStatus.CANCELED
            elif isinstance(event, TaskExpiredEvent):
                self.task.status = TaskStatus.EXPIRED
            elif isinstance(event, TaskFailedEvent):
                self.task.status = TaskStatus.FAILED
                self.task.error = event.error
            return self.task
        return None

    def process_error(self, error: JSONRPCError):
        self.task.error = error
        return self.task


async def _stream_to_task_object(
    stream: AsyncIterable[TaskStreamingResponse],
    initial_task: TaskObject,
) -> TaskObject:
    parser = StreamableTaskParser(initial_task)
    async for item in stream:
        if isinstance(item, TaskStreamingResponse):
            if item.error:
                parser.process_error(item.error)
                continue
            event = item.result
            if event is None:
                continue
            parser.process(event)
    return parser.task


class TaskManager(ABC):
    """
    Abstract base class for task management.

    Defines the interface for task operations including creation, retrieval,
    cancellation, and notification management.
    """

    @abstractmethod
    async def on_get_task(self, request: GetTaskRequest) -> GetTaskResponse:
        """Retrieve a task by ID."""
        pass

    @abstractmethod
    async def on_cancel_task(self, request: CancelTaskRequest) -> CancelTaskResponse:
        """Cancel a task by ID."""
        pass

    @abstractmethod
    async def on_task_invoke(self, request: TaskInvokeRequest) -> TaskResponse:
        """create a new task."""
        pass

    @abstractmethod
    async def on_task_subscribe(self, request: TaskStreamingRequest) -> Union[AsyncIterable[TaskStreamingResponse], JSONRPCResponse]:
        """Subscribe to task updates with streaming response."""
        pass

    @abstractmethod
    async def on_set_task_push_notification(self, request: SetTaskPushNotificationRequest) -> SetTaskPushNotificationResponse:
        """Configure push notifications for a task."""
        pass

    @abstractmethod
    async def on_get_task_push_notification(self, request: GetTaskPushNotificationRequest) -> GetTaskPushNotificationResponse:
        """Retrieve push notification configuration for a task."""
        pass

    @abstractmethod
    async def on_resubscribe_to_task(self, request: TaskResubscriptionRequest) -> Union[AsyncIterable[TaskResponse], JSONRPCResponse]:
        """Resubscribe to an existing task."""
        pass


class InMemoryTaskManager(TaskManager):
    """
    In-memory implementation of TaskManager.

    Stores tasks and related data in memory with thread-safe operations.
    Suitable for development and testing environments.
    """

    def __init__(self, task_store: Optional[InMemoryTaskStore]=None) -> None:
        """Initialize the in-memory task manager."""
        self.task_store = task_store or InMemoryTaskStore()
        self.push_notification_infos: Dict[str, PushNotificationConfig] = {}
        self.task_sse_subscribers: Dict[str, List[asyncio.Queue]] = {}

        # Locks for thread safety
        self.lock = asyncio.Lock()
        self.subscriber_lock = asyncio.Lock()

    async def on_list_tasks(self, request: ListTasksRequest) -> ListTasksResponse:
        """List tasks based on query parameters."""
        logger.info(f"Listing tasks with params: {request.params}")
        list_params: ListTasksParams = request.params or ListTasksParams()
        tasks = await self.task_store.list(list_params)

        return ListTasksResponse(id=request.id, result=tasks)

    async def on_get_task(self, request: GetTaskRequest) -> GetTaskResponse:
        """Retrieve a task by ID."""
        logger.info(f"Getting task {request.params.id}")
        task_query_params: TaskQueryParams = request.params

        task = await self.task_store.get(task_query_params.id)
        if task is None:
            logger.warning(f"Task {task_query_params.id} not found")
            return GetTaskResponse(id=request.id, error=TaskNotFoundError())

        return GetTaskResponse(id=request.id, result=task)

    async def on_cancel_task(self, request: CancelTaskRequest) -> CancelTaskResponse:
        """Cancel a task by ID."""
        logger.info(f"Cancelling task {request.params.id}")
        task_query_params: TaskQueryParams = request.params

        task = await self.task_store.get(task_query_params.id)
        if task is None:
            logger.warning(f"Task {task_query_params.id} not found for cancellation")
            return CancelTaskResponse(id=request.id, error=TaskNotFoundError())

        # TODO: Implement actual task cancellation logic
        logger.warning(f"Task cancellation not implemented for {task_query_params.id}")
        return CancelTaskResponse(id=request.id, error=TaskNotCancelableError())

    async def on_task_invoke(self, request: TaskInvokeRequest) -> TaskResponse:
        subscribe_request = TaskStreamingRequest(
            id=request.id,
            params=request.params,
        )
        stream = await self.on_task_subscribe(subscribe_request)
        task_object = None
        async for chunk in stream:
            # 处理流响应
            if chunk.error:
                return TaskResponse(id=request.id, error=chunk.error, result=task_object)
            event = chunk.result
            if isinstance(event, ObjectEvent):
                task_object = event.task
        # 最终返回一个完整的任务响应
        return TaskResponse(id=request.id, result=task_object)

    @abstractmethod
    async def on_task_subscribe(self, request: TaskStreamingRequest) -> AsyncIterable[TaskStreamingResponse]:
        pass

    async def set_push_notification_info(self, task_id: str, notification_config: PushNotificationConfig) -> None:
        """Set push notification configuration for a task."""
        task = await self.task_store.get(task_id)
        if task is None:
            raise ValueError(f"Task not found for {task_id}")

        async with self.lock:
            self.push_notification_infos[task_id] = notification_config

    async def get_push_notification_info(self, task_id: str) -> PushNotificationConfig:
        """Get push notification configuration for a task."""
        task = await self.task_store.get(task_id)
        if task is None:
            raise ValueError(f"Task not found for {task_id}")

        async with self.lock:
            return self.push_notification_infos.get(task_id)

    async def has_push_notification_info(self, task_id: str) -> bool:
        """Check if push notification configuration exists for a task."""
        async with self.lock:
            return task_id in self.push_notification_infos

    async def on_set_task_push_notification(self, request: SetTaskPushNotificationRequest) -> SetTaskPushNotificationResponse:
        """Configure push notifications for a task."""
        logger.info(f"Setting task push notification {request.params.id}")
        task_notification_params: TaskPushNotificationConfig = request.params

        try:
            await self.set_push_notification_info(
                task_notification_params.id,
                task_notification_params.pushNotificationConfig,
            )
        except Exception as e:
            logger.error(f"Error while setting push notification info: {e}")
            return SetTaskPushNotificationResponse(
                id=request.id,
                error=InternalError(message="An error occurred while setting push notification info"),
            )

        return SetTaskPushNotificationResponse(
            id=request.id,
            result=task_notification_params,
        )

    async def on_get_task_push_notification(self, request: GetTaskPushNotificationRequest) -> GetTaskPushNotificationResponse:
        """Retrieve push notification configuration for a task."""
        logger.info(f"Getting task push notification {request.params.id}")
        task_params: TaskQueryParams = request.params

        try:
            notification_info = await self.get_push_notification_info(task_params.id)
        except Exception as e:
            logger.error(f"Error while getting push notification info: {e}")
            return GetTaskPushNotificationResponse(
                id=request.id,
                error=InternalError(message="An error occurred while getting push notification info"),
            )

        return GetTaskPushNotificationResponse(
            id=request.id,
            result=TaskPushNotificationConfig(id=task_params.id, pushNotificationConfig=notification_info),
        )

    async def on_resubscribe_to_task(self, request: TaskResubscriptionRequest) -> Union[AsyncIterable[TaskStreamingResponse], JSONRPCResponse]:
        """Resubscribe to an existing task."""
        logger.info(f"Resubscription requested for task: {request}")
        return JSONRPCResponse(id=request.id, error=UnsupportedOperationError())

    async def setup_sse_consumer(self, task_id: str, is_resubscribe: bool = False) -> asyncio.Queue:
        """Set up a Server-Sent Events consumer for a task."""
        async with self.subscriber_lock:
            if task_id not in self.task_sse_subscribers:
                if is_resubscribe:
                    raise ValueError("Task not found for resubscription")
                self.task_sse_subscribers[task_id] = []

            sse_event_queue = asyncio.Queue(maxsize=0)  # Unlimited queue size
            self.task_sse_subscribers[task_id].append(sse_event_queue)
            return sse_event_queue

    async def enqueue_events_for_sse(self, task_id: str, task_update_event: Any) -> None:
        """Enqueue events for all SSE subscribers of a task."""
        async with self.subscriber_lock:
            if task_id not in self.task_sse_subscribers:
                logger.debug(f"No SSE subscribers found for task {task_id}")
                return

            current_subscribers = self.task_sse_subscribers[task_id]
            for subscriber in current_subscribers:
                try:
                    await subscriber.put(task_update_event)
                except Exception as e:
                    logger.error(f"Failed to enqueue event for subscriber: {e}")

    async def dequeue_events_for_sse(self, request_id: str, task_id: str, sse_event_queue: asyncio.Queue) -> AsyncIterable[TaskStreamingResponse]:
        """Dequeue events for SSE streaming response."""
        try:
            while True:
                event = await sse_event_queue.get()

                if isinstance(event, JSONRPCError):
                    yield TaskStreamingResponse(id=request_id, error=event)
                    break

                yield TaskStreamingResponse(id=request_id, result=event)

                if isinstance(event, ObjectEvent) and event.task.is_final():
                    break
        except Exception as e:
            logger.error(f"Error in SSE event dequeue: {e}")
            yield TaskStreamingResponse(id=request_id, error=InternalError(message=f"SSE streaming error: {str(e)}"))
        finally:
            # Clean up subscriber when done
            async with self.subscriber_lock:
                if task_id in self.task_sse_subscribers:
                    try:
                        self.task_sse_subscribers[task_id].remove(sse_event_queue)
                    except ValueError:
                        logger.warning(f"SSE queue not found in subscribers for task {task_id}")

    def create_task_object(
        self,
        task_id: Optional[str] = None,
        session_id: Optional[str] = None,
        user_id: Optional[str] = None,
        previous_task_id: Optional[str] = None,
        usage: Optional[Usage] = None,
    ) -> TaskObject:
        if not task_id:
            task_id = str(f"task_{uuid.uuid4()}")
        if not usage:
            usage = Usage()
        task = TaskObject(
            id=task_id,
            session_id=session_id,
            user_id=user_id,
            output=[],
            status=TaskStatus.CREATED,
            previous_task_id=previous_task_id,
            usage=usage,
        )
        return task

    async def upsert_task(self, task: TaskObject) -> TaskObject:
        """Create or update a task."""
        return await self.task_store.upsert(task)

    async def update_store(self, task: TaskObject) -> TaskObject:
        """Update task status and metadata in the store."""
        return await self.task_store.upsert(task)

    async def streaming_request(
        self,
        request_id: str,
        task_id: str,
        session_id: str,
        user_id: str,
        payload: dict | BaseModel,
    ) -> TaskStreamingRequest:
        return TaskStreamingRequest(
            id=request_id,
            params=TaskParams(
                id=task_id,
                session_id=session_id,
                user_id=user_id,
                payload=payload,
            ),
        )

    async def invoke_request(
        self,
        request_id: str,
        task_id: str,
        session_id: str,
        user_id: str,
        payload: dict | BaseModel,
    ) -> TaskInvokeRequest:
        return TaskInvokeRequest(
            id=request_id,
            params=TaskParams(
                id=task_id,
                session_id=session_id,
                user_id=user_id,
                payload=payload,
            ),
        )

    async def _stream_error(
        self,
        request_id: str,
        error: Union[JSONRPCError, str],
    ) -> AsyncIterable[TaskStreamingResponse]:
        if isinstance(error, str):
            error = JSONRPCError(code=-32000, message=error)
        yield TaskStreamingResponse(
            id=request_id,
            error=error,
        )

    async def counting_event_streaming_response(
        self,
        request_id: str,
        parser: StreamableTaskParser,
        seq_counter: SequenceCounter,
        event: AgentTaskEvent,
    ) -> TaskStreamingResponse:
        event.task_id = parser.task.id
        event = seq_counter.counting_event(event)
        if isinstance(event, TaskContentPartDoneEvent):
            seq_counter.current_content_index += 1
        if isinstance(event, TaskOutputItemDoneEvent):
            seq_counter.current_content_index = 0
            seq_counter.current_output_index += 1
        task = parser.process(event)
        error = None
        if task is not None:
            error = task.error
            # 只有在 task 有更新时才更新 store
            parser.task = await self.update_store(task)
            if isinstance(event, ObjectEvent):
                event.task = parser.task
        return TaskStreamingResponse(
            id=request_id,
            result=event,
            error=error,
        )

    async def created_streaming_response(
        self,
        request_id: str,
        parser: StreamableTaskParser,
        seq_counter: SequenceCounter,
    ) -> TaskStreamingResponse:
        return await self.counting_event_streaming_response(
            request_id=request_id,
            parser=parser,
            seq_counter=seq_counter,
            event=TaskCreatedEvent(
                task=parser.task,
            ),
        )

    async def queued_streaming_response(
        self,
        request_id: str,
        parser: StreamableTaskParser,
        seq_counter: SequenceCounter,
    ) -> TaskStreamingResponse:
        return await self.counting_event_streaming_response(
            request_id=request_id,
            parser=parser,
            seq_counter=seq_counter,
            event=TaskQueuedEvent(),
        )

    async def working_streaming_response(
        self,
        request_id: str,
        parser: StreamableTaskParser,
        seq_counter: SequenceCounter,
    ) -> TaskStreamingResponse:
        return await self.counting_event_streaming_response(
            request_id=request_id,
            parser=parser,
            seq_counter=seq_counter,
            event=TaskWorkingEvent(),
        )

    async def paused_streaming_response(
        self,
        request_id: str,
        parser: StreamableTaskParser,
        seq_counter: SequenceCounter,
    ) -> TaskStreamingResponse:
        return await self.counting_event_streaming_response(
            request_id=request_id,
            parser=parser,
            seq_counter=seq_counter,
            event=TaskPausedEvent(task=parser.task),
        )

    async def input_required_streaming_response(
        self,
        request_id: str,
        parser: StreamableTaskParser,
        seq_counter: SequenceCounter,
        input_required: ToolCallItem,
    ) -> TaskStreamingResponse:
        return await self.counting_event_streaming_response(
            request_id=request_id,
            parser=parser,
            seq_counter=seq_counter,
            event=TaskInputRequiredEvent(task=parser.task, input_required=input_required),
        )

    async def complete_streaming_response(
        self,
        request_id: str,
        parser: StreamableTaskParser,
        seq_counter: SequenceCounter,
    ) -> TaskStreamingResponse:
        return await self.counting_event_streaming_response(
            request_id=request_id,
            parser=parser,
            seq_counter=seq_counter,
            event=TaskCompletedEvent(task=parser.task),
        )

    async def canceled_streaming_response(
        self,
        request_id: str,
        parser: StreamableTaskParser,
        seq_counter: SequenceCounter,
    ) -> TaskStreamingResponse:
        return await self.counting_event_streaming_response(
            request_id=request_id,
            parser=parser,
            seq_counter=seq_counter,
            event=TaskCanceledEvent(task=parser.task),
        )

    async def expired_streaming_response(
        self,
        request_id: str,
        parser: StreamableTaskParser,
        seq_counter: SequenceCounter,
    ) -> TaskStreamingResponse:
        return await self.counting_event_streaming_response(
            request_id=request_id,
            parser=parser,
            seq_counter=seq_counter,
            event=TaskExpiredEvent(task=parser.task),
        )

    async def fail_streaming_response(
        self,
        request_id: str,
        parser: StreamableTaskParser,
        seq_counter: SequenceCounter,
        error: Union[JSONRPCError, str],
    ) -> TaskStreamingResponse:
        if isinstance(error, str):
            error = JSONRPCError(code=-32000, message=error)
        return await self.counting_event_streaming_response(
            request_id=request_id,
            parser=parser,
            seq_counter=seq_counter,
            event=TaskFailedEvent(task=parser.task, error=error),
        )

    async def tool_result_stream_generator(
        self,
        request_id: str,
        task_id: str,
        tool_result: ToolResult,
        parser: StreamableTaskParser,
        seq_counter: SequenceCounter,
    ) -> AsyncIterable[TaskStreamingResponse]:
        resp = await self.created_streaming_response(request_id=request_id, parser=parser, seq_counter=seq_counter)
        yield resp
        resp = await self.working_streaming_response(request_id=request_id, parser=parser, seq_counter=seq_counter)
        yield resp

        current_step = 0
        output_item = ToolResultItem(
            call_id=task_id,
            output=[],
            message_content=[],
            block_list=[],
        )
        resp = await self.counting_event_streaming_response(
            request_id=request_id,
            parser=parser,
            seq_counter=seq_counter,
            event=TaskOutputItemAddedEvent(
                agent_step=current_step,
                item=output_item,
            ),
        )
        yield resp

        resp = await self.counting_event_streaming_response(
            request_id=request_id,
            parser=parser,
            seq_counter=seq_counter,
            event=TaskToolResultDeltaEvent(
                item_id=output_item.id,
                call_id=output_item.call_id,
                agent_step=current_step,
                delta_message_content=tool_result.message_content,
                delta_block_list=tool_result.block_list,
            ),
        )
        yield resp

        resp = await self.counting_event_streaming_response(
            request_id=request_id,
            parser=parser,
            seq_counter=seq_counter,
            event=TaskToolResultDoneEvent(
                item_id=output_item.id,
                call_id=output_item.call_id,
                agent_step=current_step,
                message_content=tool_result.message_content,
                block_list=tool_result.block_list,
            ),
        )
        yield resp
        output_item.message_content = tool_result.message_content
        output_item.block_list = tool_result.block_list
        output_item.output = content_data_to_content_item(tool_result.message_content)
        resp = await self.counting_event_streaming_response(
            request_id=request_id,
            task_id=task_id,
            parser=parser,
            seq_counter=seq_counter,
            event=TaskOutputItemDoneEvent(
                agent_step=current_step,
                item=output_item,
            ),
        )
        yield resp

        resp = await self.complete_streaming_response(request_id=request_id, parser=parser, seq_counter=seq_counter)
        yield resp

    async def tool_result_of_internal_error_stream_generator(
        self,
        request_id: str,
        call_id: str,
        session_id: str,
        user_id: str,
        error_message: str,
    ) -> AsyncIterable[TaskStreamingResponse]:
        parser = StreamableTaskParser()
        task = self.create_task_object(
            task_id=call_id,
            session_id=session_id,
            user_id=user_id,
        )
        seq_counter = SequenceCounter()
        stream = self.tool_result_stream_generator(
            request_id=request_id,
            task_id=call_id,
            tool_result=tool_result_of_internal_error(error_message),
            parser=parser,
            seq_counter=seq_counter,
        )
        async for resp in stream:
            yield resp


async def merge_streams(*streams: AsyncIterable[TaskStreamingResponse]) -> AsyncIterable[TaskStreamingResponse]:
    """
    Merge multiple asynchronous streams into a single stream.

    Args:
        *streams: Asynchronous streams to merge.

    Yields:
        Items from the merged streams.

    Example:
        async for item in merge_streams(stream1, stream2):
            process(item)
    """
    queue = asyncio.Queue()
    active_streams = len(streams)

    async def feed_queue(stream: AsyncIterable[TaskStreamingResponse]) -> None:
        """Feed items from a stream into the queue."""
        try:
            async for item in stream:
                await queue.put(item)
        except Exception as e:
            logger.error(f"Error in stream feeder: {e}\n{traceback.format_exc()}")
        finally:
            await queue.put(None)  # Signal stream end

    # Start tasks for all streams
    tasks = [asyncio.create_task(feed_queue(stream)) for stream in streams]

    try:
        # Consume queue until all streams are done
        while active_streams > 0:
            item = await queue.get()
            if item is None:
                active_streams -= 1
                continue
            yield item
    finally:
        # Ensure all tasks are properly cleaned up
        for task in tasks:
            if not task.done():
                task.cancel()
        await asyncio.gather(*tasks, return_exceptions=True)


async def _process_request(task_manager: TaskManager, request: Request) -> JSONResponse | EventSourceResponse:
    """
    Process incoming task management requests.

    Args:
        task_manager: The task manager instance to handle the request
        request: The incoming FastAPI request

    Returns:
        JSON response or Server-Sent Events response
    """
    logger.debug("Processing task management request")
    try:
        body = await request.json()
        json_rpc_request: TaskRequest = TaskRequestType.validate_python(body)

        # Route request to appropriate handler
        handler_map = {
            GetTaskRequest: task_manager.on_get_task,
            TaskInvokeRequest: task_manager.on_task_invoke,
            TaskStreamingRequest: task_manager.on_task_subscribe,
            CancelTaskRequest: task_manager.on_cancel_task,
            SetTaskPushNotificationRequest: task_manager.on_set_task_push_notification,
            GetTaskPushNotificationRequest: task_manager.on_get_task_push_notification,
            TaskResubscriptionRequest: task_manager.on_resubscribe_to_task,
        }

        handler = handler_map.get(type(json_rpc_request))
        if handler is None:
            logger.warning(f"Unexpected request type: {type(json_rpc_request)}")
            raise ValueError(f"Unexpected request type: {type(json_rpc_request)}")

        result = await handler(json_rpc_request)
        return _create_response(result)

    except Exception as e:
        logger.error(f"Error processing request: {e}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        return _handle_exception(e)


def _create_response(result: Any) -> JSONResponse | EventSourceResponse:
    """
    Create appropriate response based on result type.

    Args:
        result: The result from task manager operation

    Returns:
        JSON response for regular results, SSE response for async iterables
    """
    if isinstance(result, AsyncIterable):

        async def event_generator(result: AsyncIterable) -> AsyncIterable[Dict[str, str]]:
            """Generate SSE events from async iterable result."""
            async for item in result:
                yield {"data": item.model_dump_json(exclude_none=True)}

        return EventSourceResponse(event_generator(result))

    elif isinstance(result, JSONRPCResponse):
        return JSONResponse(result.model_dump(exclude_none=True))

    else:
        logger.error(f"Unexpected result type: {type(result)}")
        raise ValueError(f"Unexpected result type: {type(result)}")


def _handle_exception(e: Exception) -> JSONResponse:
    """
    Handle exceptions and create appropriate JSON-RPC error responses.

    Args:
        e: The exception to handle

    Returns:
        JSON response with appropriate error code and message
    """
    if isinstance(e, json.decoder.JSONDecodeError):
        json_rpc_error = JSONParseError()
    elif isinstance(e, ValidationError):
        json_rpc_error = InvalidRequestError(data=json.loads(e.json()))
    else:
        logger.error(f"Unhandled exception: {e}")
        json_rpc_error = InternalError()

    response = JSONRPCResponse(id=None, error=json_rpc_error)
    return JSONResponse(response.model_dump(exclude_none=True), status_code=400)


async def event_generator(result: AsyncIterable[TaskStreamingResponse]) -> AsyncIterable[dict[str, str]]:
    """Generate SSE events from async iterable result."""
    async for item in result:
        yield {"data": item.model_dump_json(exclude_none=True)}

