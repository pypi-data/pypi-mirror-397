from datetime import datetime
from typing import AsyncIterator, Union

from chatkit.agents import (
    AgentContext,
    _AsyncQueueIterator,
    _EventWrapper,
    _merge_generators,
    # _convert_content,
    StreamingThoughtTracker,
    InputGuardrailTripwireTriggered,
    OutputGuardrailTripwireTriggered,
)
from chatkit.server import stream_widget
from chatkit.store import Store, StoreItemType
from chatkit.types import (
    Annotation,
    AssistantMessageContent,
    AssistantMessageContentPartAdded,
    AssistantMessageContentPartDone,
    AssistantMessageContentPartTextDelta,
    AssistantMessageItem,
    Attachment,
    ClientToolCallItem,
    DurationSummary,
    EndOfTurnItem,
    FileSource,
    HiddenContextItem,
    Task,
    TaskItem,
    ThoughtTask,
    ThreadItem,
    ThreadItemAddedEvent,
    ThreadItemDoneEvent,
    ThreadItemRemovedEvent,
    ThreadItemUpdated,
    ThreadMetadata,
    ThreadStreamEvent,
    URLSource,
    UserMessageItem,
    UserMessageTagContent,
    UserMessageTextContent,
    WidgetItem,
    Workflow,
    WorkflowItem,
    WorkflowSummary,
    WorkflowTaskAdded,
    WorkflowTaskUpdated,
)
from loguru import logger

from agentlin.core.types import AgentTaskEvent, ContentItem, TaskStreamingResponse

def _convert_content(content: Union[list[ContentItem], str]) -> list[AssistantMessageContent]:
    if isinstance(content, str):
        return [AssistantMessageContent(
            text=content,
            annotations=[],
        )]
    text = ""
    for item in content:
      if item.type == "text":
          text += item.text
    return [AssistantMessageContent(
        text=text,
        annotations=[],
    )]

async def stream_agent_response(context: AgentContext, stream: AsyncIterator[TaskStreamingResponse]) -> AsyncIterator[ThreadStreamEvent]:
    current_item_id = None
    current_tool_call = None
    ctx = context
    thread = context.thread
    queue_iterator = _AsyncQueueIterator(context._events)
    produced_items = set()
    streaming_thought: None | StreamingThoughtTracker = None

    # check if the last item in the thread was a workflow or a client tool call
    # if it was a client tool call, check if the second last item was a workflow
    # if either was, continue the workflow
    items = await context.store.load_thread_items(thread.id, None, 2, "desc", context.request_context)
    last_item = items.data[0] if len(items.data) > 0 else None
    second_last_item = items.data[1] if len(items.data) > 1 else None

    if last_item and last_item.type == "workflow":
        ctx.workflow_item = last_item
    elif last_item and last_item.type == "client_tool_call" and second_last_item and second_last_item.type == "workflow":
        ctx.workflow_item = second_last_item

    def end_workflow(item: WorkflowItem):
        if item == ctx.workflow_item:
            ctx.workflow_item = None
        delta = datetime.now() - item.created_at
        duration = int(delta.total_seconds())
        if item.workflow.summary is None:
            item.workflow.summary = DurationSummary(duration=duration)
        # Default to closing all workflows
        # To keep a workflow open on completion, close it explicitly with
        # AgentContext.end_workflow(expanded=True)
        item.workflow.expanded = False
        return ThreadItemDoneEvent(item=item)

    try:
        async for event in _merge_generators(stream, queue_iterator):
            # Events emitted from agent context helpers
            logger.debug(event)
            if isinstance(event, _EventWrapper):
                event = event.event
                if event.type == "thread.item.added" or event.type == "thread.item.done":
                    # End the current workflow if visual item is added after it
                    if ctx.workflow_item and ctx.workflow_item.id != event.item.id and event.item.type != "client_tool_call" and event.item.type != "hidden_context_item":
                        yield end_workflow(ctx.workflow_item)

                    # track the current workflow if one is added
                    if event.type == "thread.item.added" and event.item.type == "workflow":
                        ctx.workflow_item = event.item

                    # track integration produced items so we can clean them up if
                    # there is a guardrail tripwire
                    produced_items.add(event.item.id)
                yield event
                continue

            # Handle Responses events
            if not event.result:
                logger.error(f"AgentTaskEvent failed: {event.error}")
                continue
            event = event.result
            logger.debug(f"AgentTaskEvent received: {event.type}")
            if event.type == "task.content_part.added":
                if event.part.type == "reasoning_text":
                    continue
                content = _convert_content(event.part)
                yield ThreadItemUpdated(
                    item_id=event.item_id,
                    update=AssistantMessageContentPartAdded(
                        content_index=event.content_index,
                        content=content,
                    ),
                )
            elif event.type == "task.text.delta":
                yield ThreadItemUpdated(
                    item_id=event.item_id,
                    update=AssistantMessageContentPartTextDelta(
                        content_index=event.content_index,
                        delta=event.delta,
                    ),
                )
            elif event.type == "task.text.done":
                yield ThreadItemUpdated(
                    item_id=event.item_id,
                    update=AssistantMessageContentPartDone(
                        content_index=event.content_index,
                        content=AssistantMessageContent(
                            text=event.text,
                            annotations=[],
                        ),
                    ),
                )
            elif event.type == "task.text.annotation.added":
                # Ignore annotation-added events; annotations are reflected in the final item content.
                continue
            elif event.type == "task.output_item.added":
                item = event.item
                if item.type == "reasoning" and not ctx.workflow_item:
                    ctx.workflow_item = WorkflowItem(
                        id=ctx.generate_id("workflow"),
                        created_at=datetime.now(),
                        workflow=Workflow(type="reasoning", tasks=[]),
                        thread_id=thread.id,
                    )
                    produced_items.add(ctx.workflow_item.id)
                    yield ThreadItemAddedEvent(item=ctx.workflow_item)
                if item.type == "message":
                    if ctx.workflow_item:
                        yield end_workflow(ctx.workflow_item)
                    produced_items.add(item.id)
                    yield ThreadItemAddedEvent(
                        item=AssistantMessageItem(
                            # Reusing the Responses message ID
                            id=item.id,
                            thread_id=thread.id,
                            content=[_convert_content(c) for c in item.content],
                            created_at=datetime.now(),
                        ),
                    )
            elif event.type == "task.reasoning_summary_text.delta":
                if not ctx.workflow_item:
                    continue

                # stream the first thought in a new workflow so that we can show it earlier
                if ctx.workflow_item.workflow.type == "reasoning" and len(ctx.workflow_item.workflow.tasks) == 0:
                    streaming_thought = StreamingThoughtTracker(
                        item_id=event.item_id,
                        index=event.summary_index,
                        task=ThoughtTask(content=event.delta),
                    )
                    ctx.workflow_item.workflow.tasks.append(streaming_thought.task)
                    yield ThreadItemUpdated(
                        item_id=ctx.workflow_item.id,
                        update=WorkflowTaskAdded(
                            task=streaming_thought.task,
                            task_index=0,
                        ),
                    )
                elif streaming_thought and streaming_thought.task in ctx.workflow_item.workflow.tasks and event.item_id == streaming_thought.item_id and event.summary_index == streaming_thought.index:
                    streaming_thought.task.content += event.delta
                    yield ThreadItemUpdated(
                        item_id=ctx.workflow_item.id,
                        update=WorkflowTaskUpdated(
                            task=streaming_thought.task,
                            task_index=ctx.workflow_item.workflow.tasks.index(streaming_thought.task),
                        ),
                    )
            elif event.type == "task.reasoning_summary_text.done":
                if ctx.workflow_item:
                    if streaming_thought and streaming_thought.task in ctx.workflow_item.workflow.tasks and event.item_id == streaming_thought.item_id and event.summary_index == streaming_thought.index:
                        task = streaming_thought.task
                        task.content = event.text
                        streaming_thought = None
                        update = WorkflowTaskUpdated(
                            task=task,
                            task_index=ctx.workflow_item.workflow.tasks.index(task),
                        )
                    else:
                        task = ThoughtTask(content=event.text)
                        ctx.workflow_item.workflow.tasks.append(task)
                        update = WorkflowTaskAdded(
                            task=task,
                            task_index=ctx.workflow_item.workflow.tasks.index(task),
                        )
                    yield ThreadItemUpdated(
                        item_id=ctx.workflow_item.id,
                        update=update,
                    )
            elif event.type == "task.output_item.done":
                item = event.item
                logger.warning(f"Output item done received: {item}")
                if item.type == "message":
                    produced_items.add(item.id)
                    yield ThreadItemDoneEvent(
                        item=AssistantMessageItem(
                            # Reusing the Responses message ID
                            id=item.id,
                            thread_id=thread.id,
                            content=_convert_content(item.content),
                            created_at=datetime.now(),
                        ),
                    )

    except (InputGuardrailTripwireTriggered, OutputGuardrailTripwireTriggered):
        for item_id in produced_items:
            yield ThreadItemRemovedEvent(item_id=item_id)

        # Drain remaining events without processing them
        context._complete()
        queue_iterator.drain_and_complete()

        raise

    context._complete()

    # Drain remaining events
    async for event in queue_iterator:
        yield event.event

    # If there is still an active workflow at the end of the run, store
    # it's current state so that we can continue it in the next turn.
    if ctx.workflow_item:
        await ctx.store.add_thread_item(thread.id, ctx.workflow_item, ctx.request_context)

    if context.client_tool_call:
        yield ThreadItemDoneEvent(
            item=ClientToolCallItem(
                id=current_item_id or context.store.generate_item_id("tool_call", thread, context.request_context),
                thread_id=thread.id,
                name=context.client_tool_call.name,
                arguments=context.client_tool_call.arguments,
                created_at=datetime.now(),
                call_id=current_tool_call or context.store.generate_item_id("tool_call", thread, context.request_context),
            ),
        )

