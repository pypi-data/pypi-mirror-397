from collections import defaultdict
import os
import json
from datetime import datetime
import traceback
from typing import Any, AsyncIterator, Literal, Union

from fastapi import FastAPI, APIRouter, Request
from fastapi.responses import StreamingResponse, FileResponse, Response
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv
from loguru import logger


# ChatKit core types and server base
from chatkit.server import ChatKitServer, StreamingResult
from chatkit.types import (
    ThreadStreamEvent,
    ThreadItemDoneEvent,
    ThreadItemAddedEvent,
    ThreadItemUpdated,
    WidgetComponentUpdated,
    ThreadItemRemovedEvent,
    WidgetItem,
)
from chatkit.types import (
    Thread,
    ThreadMetadata,
    UserMessageItem,
    AssistantMessageItem,
    AssistantMessageContent,
)
from chatkit.widgets import (
    WidgetComponentBase,
    Card,
    ListView,
    Text,
    Badge,
    Markdown,
    Box,
    Row,
    Divider,
    Icon,
    Image,
    Spacer,
    WidgetStatusWithIcon,
)

# Minimal in-memory store for demo purposes only
# NOTE: For production use, implement a persistent Store (e.g., SQLite/PostgreSQL)
from chatkit.store import Store, Page, Attachment


from agentlin.core.agent_schema import responses_content_to_completion_content
from agentlin.core.types import (
    AgentTaskEvent,
    AgentTaskEventType,
    ContentItem,
    TextContentItem,
    ImageContentItem,
    AudioContentItem,
    FileContentItem,
    ToolCallItem,
    ToolResultItem,
    MessageItem,
    ReasoningItem,
    TaskObject,
    TaskStreamingResponse,
    TaskCreatedEvent,
    TaskWorkingEvent,
    TaskCompletedEvent,
    TaskFailedEvent,
    TaskToolsUpdatedEvent,
    TaskContextCompressionCreatedEvent,
    TaskContextCompressionInProgressEvent,
    TaskContextCompressionCompletedEvent,
    TaskOutputItemAddedEvent,
    TaskOutputItemDoneEvent,
    TaskContentPartAddedEvent,
    TaskContentPartDoneEvent,
    TaskReasoningSummaryPartAddedEvent,
    TaskReasoningSummaryPartDoneEvent,
    TaskReasoningSummaryTextDeltaEvent,
    TaskReasoningSummaryTextDoneEvent,
    TaskReasoningTextDeltaEvent,
    TaskReasoningTextDoneEvent,
    TaskToolCallArgumentsDeltaEvent,
    TaskToolCallArgumentsDoneEvent,
    TaskToolResultDeltaEvent,
    TaskToolResultDoneEvent,
    TaskBlockDeltaEvent,
    TaskBlockDoneEvent,
    TaskTextDeltaEvent,
    TaskTextDoneEvent,
    TaskImageDeltaEvent,
    TaskImageDoneEvent,
    TaskAudioDeltaEvent,
    TaskAudioDoneEvent,
    TaskFileDeltaEvent,
    TaskFileDoneEvent,
    TaskRolloutEvent,
)
from agentlin.route.agent_config import load_agent_config
from agentlin.route.task_agent_manager import TaskAgentManager
from agentlin.store.task_store import InMemoryTaskStore


load_dotenv()


class InMemoryStore(Store[Any]):
    def __init__(self) -> None:
        self.threads: dict[str, Thread] = {}
        self.items_by_thread: dict[str, list] = {}
        self.attachments: dict[str, Attachment] = {}

    async def load_thread(self, thread_id: str, context: Any) -> ThreadMetadata:
        thread = self.threads.get(thread_id)
        if not thread:
            raise ValueError(f"Thread not found: {thread_id}")
        return ThreadMetadata(
            id=thread.id,
            title=thread.title,
            created_at=thread.created_at,
            status=thread.status,
            metadata=thread.metadata,
        )

    async def save_thread(self, thread: Thread | ThreadMetadata, context: Any) -> None:
        if isinstance(thread, ThreadMetadata):
            # Promote to Thread with empty page if needed
            existing = self.threads.get(thread.id)
            items = existing.items if existing else Page()
            self.threads[thread.id] = Thread(
                id=thread.id,
                title=thread.title,
                created_at=thread.created_at,
                status=thread.status,
                metadata=thread.metadata,
                items=items,
            )
        else:
            self.threads[thread.id] = thread
        self.items_by_thread.setdefault(thread.id, [])

    async def load_thread_items(
        self,
        thread_id: str,
        after: str | None,
        limit: int,
        order: str,
        context: Any,
    ) -> Page:
        items = self.items_by_thread.get(thread_id, [])
        # Simple ordering and pagination
        if order == "desc":
            items = list(reversed(items))
        start = 0
        if after:
            try:
                idx = next(i for i, it in enumerate(items) if it.id == after)
                start = idx + 1
            except StopIteration:
                start = 0
        selected = items[start : start + (limit or len(items))]
        page = Page()
        page.data = list(reversed(selected)) if order == "desc" else selected
        return page

    async def save_attachment(self, attachment: Attachment, context: Any) -> None:
        self.attachments[attachment.id] = attachment

    async def load_attachment(self, attachment_id: str, context: Any) -> Attachment:
        att = self.attachments.get(attachment_id)
        if not att:
            raise ValueError("Attachment not found")
        return att

    async def delete_attachment(self, attachment_id: str, context: Any) -> None:
        self.attachments.pop(attachment_id, None)

    async def load_threads(self, limit: int, after: str | None, order: str, context: Any) -> Page[ThreadMetadata]:
        threads = list(self.threads.values())
        if order == "desc":
            threads = list(reversed(threads))
        start = 0
        if after:
            try:
                idx = next(i for i, th in enumerate(threads) if th.id == after)
                start = idx + 1
            except StopIteration:
                start = 0
        selected = threads[start : start + (limit or len(threads))]
        page: Page[ThreadMetadata] = Page()
        page.data = [
            ThreadMetadata(
                id=t.id,
                title=t.title,
                created_at=t.created_at,
                status=t.status,
                metadata=t.metadata,
            )
            for t in selected
        ]
        return page

    async def add_thread_item(self, thread_id: str, item, context: Any) -> None:
        self.items_by_thread.setdefault(thread_id, [])
        self.items_by_thread[thread_id].append(item)
        # Reflect into Thread.items Page for completeness
        t = self.threads.get(thread_id)
        if t:
            t.items.data.append(item)

    async def save_item(self, thread_id: str, item, context: Any) -> None:
        items = self.items_by_thread.setdefault(thread_id, [])
        for i, it in enumerate(items):
            if it.id == item.id:
                items[i] = item
                break
        # Also update Thread.items
        t = self.threads.get(thread_id)
        if t:
            for i, it in enumerate(t.items.data):
                if it.id == item.id:
                    t.items.data[i] = item
                    break

    async def load_item(self, thread_id: str, item_id: str, context: Any):
        items = self.items_by_thread.get(thread_id, [])
        for it in items:
            if it.id == item_id:
                return it
        raise ValueError("Item not found")

    async def delete_thread(self, thread_id: str, context: Any) -> None:
        self.threads.pop(thread_id, None)
        self.items_by_thread.pop(thread_id, None)

    async def delete_thread_item(self, thread_id: str, item_id: str, context: Any) -> None:
        items = self.items_by_thread.get(thread_id, [])
        self.items_by_thread[thread_id] = [it for it in items if it.id != item_id]
        t = self.threads.get(thread_id)
        if t:
            t.items.data = [it for it in t.items.data if it.id != item_id]


icon_list = [
    "agent",
    "analytics",
    "atom",
    "bolt",
    "book-open",
    "book-clock",
    "book-closed",
    "calendar",
    "chart",
    "check",
    "check-circle",
    "check-circle-filled",
    "chevron-left",
    "chevron-right",
    "circle-question",
    "compass",
    "confetti",
    "cube",
    "desktop",
    "document",
    "dot",
    "dots-horizontal",
    "dots-vertical",
    "empty-circle",
    "external-link",
    "globe",
    "keys",
    "lab",
    "images",
    "info",
    "lifesaver",
    "lightbulb",
    "mail",
    "map-pin",
    "maps",
    "mobile",
    "name",
    "notebook",
    "notebook-pencil",
    "page-blank",
    "phone",
    "play",
    "plus",
    "profile",
    "profile-card",
    "reload",
    "star",
    "star-filled",
    "search",
    "sparkle",
    "sparkle-double",
    "square-code",
    "square-image",
    "square-text",
    "suitcase",
    "settings-slider",
    "user",
    "wreath",
    "write",
    "write-alt",
    "write-alt2",
]


def tool_icon(name: str) -> str:
    if name == "CodeInterpreter":
        return "square-code"
    elif name == "Task":
        return "agent"
    return icon_list[hash(name) % len(icon_list)]


class AgentChatKitServer(ChatKitServer[Any]):
    def __init__(self, store: Store[Any], debug=False, use_message_queue=False):
        super().__init__(store=store, attachment_store=None)
        self.agent = "assets/simple"
        self.agent_config = None
        self.tools = []
        task_store = InMemoryTaskStore()
        self.task_agent_manager = TaskAgentManager(
            debug=debug,
            use_message_queue=use_message_queue,
            task_store=task_store,
        )

    async def respond(
        self,
        thread: ThreadMetadata,
        input_user_message: UserMessageItem | None,
        context: Any,
    ) -> AsyncIterator[ThreadStreamEvent]:
        session_id = thread.id
        task_id = thread.id

        # 1) Respond with a short assistant message
        # yield ThreadItemDoneEvent(
        #     item=AssistantMessageItem(
        #         id=self.store.generate_item_id("message", thread, context),
        #         thread_id=thread.id,
        #         created_at=datetime.now(),
        #         content=[AssistantMessageContent(text=thread.model_dump_json(indent=2))],
        #     )
        # )
        print("Thread:", thread)
        print("Input user message:", input_user_message)
        print("Context:", context)

        message_content = []
        if input_user_message:
            message_content = [responses_content_to_completion_content(c.model_dump()) for c in input_user_message.content]
        if not message_content:
            text = f"input_user_message={input_user_message}"
            yield ThreadItemDoneEvent(
                item=AssistantMessageItem(
                    id=self.store.generate_item_id("message", thread, context),
                    thread_id=thread.id,
                    created_at=datetime.now(),
                    content=[AssistantMessageContent(text=text)],
                )
            )
            return

        if not self.agent_config:
            self.agent_config = await load_agent_config(self.agent)
            logger.info(f"Loaded agent config from {self.agent}")
        logger.info(f"Starting session for thread {thread.id} with agent {self.agent}")
        stream = await self.task_agent_manager(
            request_id=session_id,
            session_id=session_id,
            task_id=task_id,
            user_id=session_id,
            user_message_content=message_content,
            stream=True,
            agent_config=self.agent_config,
            return_rollout=True,
        )

        # 2) Stream a small widget change to show updates
        task2event_id2widget: dict[str, dict[str, WidgetItem]] = defaultdict(lambda: {})
        try:
            async for resp in stream:
                event = resp.result
                print(type(event))
                cur_task_id = resp.id
                event_id2widget = task2event_id2widget[cur_task_id]
                # print(result)
                if cur_task_id != task_id:
                    # TODO 暂时只考虑主 agent 的输出
                    continue
                # logger.info(event)
                if isinstance(event, TaskCreatedEvent):
                    task_item = event.task
                elif isinstance(event, TaskCompletedEvent):
                    task_item = event.task
                elif isinstance(event, TaskFailedEvent):
                    task_item = event.task
                elif isinstance(event, TaskToolsUpdatedEvent):
                    tools = event.tools
                    item_id = f"{cur_task_id}_{event.type}_tools"
                    text = f"Tools updated: {', '.join([t['function']['name'] for t in tools])}"
                    widget = Card(
                        id=f"{item_id}_card",
                        children=[
                            Row(
                                id=f"{item_id}_row",
                                children=[
                                    Box(
                                        id=f"{item_id}_icon_card",
                                        children=[
                                            Row(
                                                id=f"{item_id}_icon_row",
                                                children=[
                                                    Spacer(size="xs"),
                                                    Icon(id=f"{item_id}_icon_spacer", name=tool_icon(tool["function"]["name"]), size="md"),
                                                    Spacer(size="xs"),
                                                    Text(id=f"{item_id}_icon_text", value=tool["function"]["name"], size="sm", weight="bold"),
                                                    Spacer(size="xs"),
                                                ],
                                                align="center",
                                                justify="center",
                                            ),
                                        ],
                                        size="sm",
                                        align="center",
                                        justify="center",
                                        wrap="wrap",
                                        # status=WidgetStatusWithIcon(text="info", icon="info-circle"),
                                    )
                                    for tool in tools
                                ],
                            ),
                        ],
                        size="full",
                    )
                    item = WidgetItem(
                        id=item_id,
                        created_at=datetime.now(),
                        widget=widget,
                        copy_text=text,
                        thread_id=thread.id,
                    )

                    yield ThreadItemDoneEvent(item=item)

                elif isinstance(event, TaskContextCompressionCreatedEvent):
                    copy_text = "Context compression started."
                    component_id = f"{cur_task_id}_{event.type}_text"
                    widget = Card(children=[Text(id=component_id, value=copy_text)])
                    item = WidgetItem(
                        id=event.type,
                        created_at=datetime.now(),
                        widget=widget,
                        copy_text=copy_text,
                        thread_id=thread.id,
                    )
                    event_id2widget[item.id] = item

                    yield ThreadItemAddedEvent(item=item)
                elif isinstance(event, TaskContextCompressionInProgressEvent):
                    item = event_id2widget.get(event.type)
                    if not item:
                        continue
                    copy_text = f"Context compression in progress"
                    component_id = f"{item.id}_text"
                    item.widget = Card(children=[Text(id=component_id, value=copy_text)])
                    item.copy_text = copy_text

                    yield ThreadItemUpdated(item_id=item.id, update=WidgetComponentUpdated(component_id=component_id, widget=item.widget))
                elif isinstance(event, TaskContextCompressionCompletedEvent):
                    item = event_id2widget.get(event.type)
                    if not item:
                        continue
                    copy_text = "Context compression completed."
                    component_id = f"{item.id}_text"
                    item.widget = Card(children=[Text(id=component_id, value=copy_text)])
                    item.copy_text = copy_text

                    yield ThreadItemUpdated(item=item)
                elif isinstance(event, TaskOutputItemAddedEvent):
                    output_item = event.item
                    item = None
                    if isinstance(output_item, ToolResultItem):
                        call_id = output_item.call_id
                        item = event_id2widget.get(call_id)
                    if item:
                        # Update existing function call item with output
                        tool_result_widget = output_item_to_widget(output_item)
                        item.widget.children.append(Divider(spacing=2))
                        item.widget.children.append(tool_result_widget)
                    else:
                        widget = output_item_to_widget(output_item)
                        item = WidgetItem(
                            id=output_item.id,
                            created_at=datetime.now(),
                            widget=widget,
                            copy_text=output_item.id,
                            thread_id=thread.id,
                        )
                    if isinstance(output_item, (ToolCallItem, ToolResultItem)):
                        call_id = output_item.call_id
                        item.id = call_id
                    event_id2widget[item.id] = item

                    yield ThreadItemAddedEvent(item=item)
                elif isinstance(event, TaskOutputItemDoneEvent):
                    output_item = event.item
                    if isinstance(output_item, (ToolCallItem, ToolResultItem)):
                        call_id = output_item.call_id
                        item = event_id2widget.get(call_id)
                    else:
                        item = event_id2widget.get(output_item.id)
                    if not item:
                        continue
                    # AssistantMessageItem
                    if isinstance(output_item, MessageItem) and output_item.role == "assistant":
                        yield ThreadItemRemovedEvent(item_id=item.id)
                        content = message_content_to_assistant_message_content(output_item.content)
                        assistant_message = AssistantMessageItem(
                            id=self.store.generate_item_id("message", thread, context),
                            thread_id=thread.id,
                            created_at=datetime.now(),
                            content=content,
                        )
                        yield ThreadItemDoneEvent(item=assistant_message)
                        continue
                    if isinstance(output_item, ToolResultItem):
                        call_id = output_item.call_id
                        tool_result_widget = output_item_to_widget(output_item)
                        if item.widget.children:
                            # widget = item.widget.children[-1]
                            item.widget.children[-1] = tool_result_widget
                        else:
                            item.widget.children.append(Divider(spacing=2))
                            item.widget.children.append(tool_result_widget)
                        yield ThreadItemDoneEvent(item=item)
                        continue
                    widget = output_item_to_widget(output_item)
                    item.widget = widget
                    item.copy_text = output_item.id
                    if isinstance(output_item, ToolCallItem):
                        call_id = output_item.call_id
                        event_id2widget[call_id] = item
                    else:
                        event_id2widget[item.id] = item
                    yield ThreadItemDoneEvent(item=item)
                elif isinstance(event, TaskContentPartAddedEvent):
                    pass
                elif isinstance(event, TaskContentPartDoneEvent):
                    pass
                elif isinstance(event, TaskReasoningSummaryPartAddedEvent):
                    pass
                elif isinstance(event, TaskReasoningSummaryPartDoneEvent):
                    pass
                elif isinstance(event, TaskReasoningSummaryTextDeltaEvent):
                    pass
                elif isinstance(event, TaskReasoningSummaryTextDoneEvent):
                    pass
                elif isinstance(event, TaskReasoningTextDeltaEvent):
                    pass
                elif isinstance(event, TaskReasoningTextDoneEvent):
                    pass
                elif isinstance(event, TaskToolCallArgumentsDeltaEvent):
                    pass
                elif isinstance(event, TaskToolCallArgumentsDoneEvent):
                    pass
                elif isinstance(event, TaskToolResultDeltaEvent):
                    pass
                elif isinstance(event, TaskToolResultDoneEvent):
                    pass
                elif isinstance(event, TaskBlockDeltaEvent):
                    pass
                elif isinstance(event, TaskBlockDoneEvent):
                    pass
                elif isinstance(event, TaskTextDeltaEvent):
                    pass
                elif isinstance(event, TaskTextDoneEvent):
                    pass
                elif isinstance(event, TaskImageDeltaEvent):
                    pass
                elif isinstance(event, TaskImageDoneEvent):
                    pass
                elif isinstance(event, TaskAudioDeltaEvent):
                    pass
                elif isinstance(event, TaskAudioDoneEvent):
                    pass
                elif isinstance(event, TaskFileDeltaEvent):
                    pass
                elif isinstance(event, TaskFileDoneEvent):
                    pass
                elif isinstance(event, TaskRolloutEvent):
                    pass
        except Exception as e:
            logger.error(f"Failed: {e}\n{traceback.format_exc()}")
        finally:
            self.task_agent_manager.delete_session(session_id)

        # async def widget_generator():
        #     yield Card(children=[Text(id="say", value="Thinking…")])
        #     await asyncio.sleep(0.1)
        #     yield Card(children=[Text(id="say", value="Done!")])

        # async for e in stream_widget(thread, widget_generator()):
        #     yield e


def status_to_widget(status: Literal["completed", "failed", "incomplete", "in_progress"]) -> WidgetStatusWithIcon:
    icon = "empty-circle"
    if status == "completed":
        icon = "check-circle"
    elif status == "in_progress":
        icon = "reload"
    return WidgetStatusWithIcon(text=status, icon=icon)


def task_output_to_widget(
    task_id: str,
    output: list[
        Union[
            MessageItem,
            ReasoningItem,
            ToolCallItem,
            ToolResultItem,
        ]
    ],
) -> Row:
    items = [output_item_to_widget(item) for item in output]
    return Row(
        id=f"task-{task_id}",
        children=items,
    )


def reasoning_to_widget(reasoning: ReasoningItem) -> Card:
    rows = []
    if reasoning.summary:
        for i, part in enumerate(reasoning.summary):
            rows.append(Markdown(id=f"{reasoning.id}_summary_{i}", value=part.text))
    return Card(id=f"{reasoning.id}_card", children=rows)


def tool_call_to_widget(tool_call: ToolCallItem) -> Card:
    name: str = tool_call.name
    args: dict[str, Any] = json.loads(tool_call.arguments)
    if name == "CodeInterpreter":
        code = args.get("code", "")
        return Card(
            id=str(tool_call.id),
            children=[
                Row(
                    id=f"{tool_call.id}_row",
                    children=[
                        Icon(id=f"{tool_call.id}_icon", name=tool_icon(name), size="md"),
                        Text(id=f"{tool_call.id}_text", value="Writing Code", size="sm", weight="bold"),
                        Spacer(),
                        Badge(id=f"{tool_call.id}_badge", label="Tool Call", color="secondary"),
                    ],
                ),
                Spacer(),
                Markdown(id=f"{tool_call.id}_code", value=f"```python\n{code}\n```"),
            ],
            size="full",
        )
    elif "query" in args:
        query = args.get("query", "")
        return Card(
            id=str(tool_call.id),
            children=[
                Row(
                    id=f"{tool_call.id}_row",
                    children=[
                        Icon(id=f"{tool_call.id}_icon", name=tool_icon(name), size="md"),
                        Text(id=f"{tool_call.id}_title", value=name, size="sm", weight="bold"),
                        Text(id=f"{tool_call.id}_args", value=query),
                        Spacer(),
                        Badge(id=f"{tool_call.id}_badge", label="Tool Call", color="secondary"),
                    ],
                ),
            ],
            size="full",
        )
    return Card(
        id=str(tool_call.id),
        children=[
            Row(
                id=f"{tool_call.id}_row",
                children=[
                    Icon(id=f"{tool_call.id}_icon", name=tool_icon(name), size="md"),
                    Text(id=f"{tool_call.id}_title", value=f"{tool_call.name}", size="sm", weight="bold"),
                    Text(id=f"{tool_call.id}_args", value=tool_call.arguments),
                    Spacer(),
                    Badge(id=f"{tool_call.id}_badge", label="Tool Call", color="secondary"),
                ],
            ),
        ],
        size="full",
    )


def message_content_to_assistant_message_content(content: list[Union[str, ContentItem]]):
    if isinstance(content, str):
        return [AssistantMessageContent(text=content)]
    assistant_content = []
    for c in content:
        if isinstance(c, str):
            assistant_content.append(AssistantMessageContent(text=c))
        elif isinstance(c, TextContentItem):
            assistant_content.append(AssistantMessageContent(text=c.text))
        elif isinstance(c, ImageContentItem):
            assistant_content.append(AssistantMessageContent(text=c.image_url if isinstance(c.image_url, str) else c.image_url.url))
        elif isinstance(c, AudioContentItem):
            assistant_content.append(AssistantMessageContent(text="[Audio]"))
        elif isinstance(c, FileContentItem):
            assistant_content.append(AssistantMessageContent(text=f"File: {c.file.file_url}"))
    return assistant_content


def message_content_to_widget(content_id: str, content: list[Union[str, ContentItem]]):
    if isinstance(content, str):
        return [Markdown(id=f"content_{content_id}_0", value=content)]
    widgets = []
    for i, c in enumerate(content):
        if isinstance(c, str):
            widgets.append(Text(id=f"content_{content_id}_{i}", value=c))
        elif isinstance(c, TextContentItem):
            widgets.append(Text(id=f"content_{content_id}_{i}", value=c.text))
        elif isinstance(c, ImageContentItem):
            widgets.append(Image(id=f"content_{content_id}_{i}", src=c.image_url if isinstance(c.image_url, str) else c.image_url.url))
        elif isinstance(c, AudioContentItem):
            widgets.append(Text(id=f"content_{content_id}_{i}", value="[Audio]"))
        elif isinstance(c, FileContentItem):
            widgets.append(Text(id=f"content_{content_id}_{i}", value=f"File: {c.file.file_url}"))
    return widgets


def tool_result_to_widget(tool_result_item: ToolResultItem) -> Card:
    output = tool_result_item.output
    rows = message_content_to_widget(str(tool_result_item.id), output)
    return Card(
        id=str(tool_result_item.id),
        children=rows,
        size="full",
    )


def message_item_to_widget(message: MessageItem) -> Card:
    card = Card(
        id=str(message.id),
        children=[],
        size="full",
    )
    content = message.content
    if not content:
        return card
    items = message_content_to_widget(str(message.id), content)
    card.children.extend(items)
    return card


def output_item_to_widget(item: Union[MessageItem, ReasoningItem, ToolCallItem, ToolResultItem]) -> WidgetComponentBase:
    if isinstance(item, MessageItem):
        return message_item_to_widget(item)
    elif isinstance(item, ReasoningItem):
        return reasoning_to_widget(item)
    elif isinstance(item, ToolCallItem):
        return tool_call_to_widget(item)
    elif isinstance(item, ToolResultItem):
        return tool_result_to_widget(item)
    raise ValueError(f"Unknown output item type: {item}")


def task_to_widget(task_object: TaskObject) -> ListView:
    task_id = task_object.id
    output = task_object.output
    status = task_object.status
    status_view = status_to_widget(status)
    output_listview = task_output_to_widget(task_id, output)
    output_list = ListView(
        id=task_id,
        status=status_view,
        children=output_listview,
    )
    return output_list


def create_chatkit_router(server: AgentChatKitServer) -> APIRouter:
    app = APIRouter()

    @app.post("/chatkit")
    async def chatkit_endpoint(req: Request):
        result = await server.process(await req.body(), {})
        if isinstance(result, StreamingResult):
            return StreamingResponse(result, media_type="text/event-stream")
        return Response(content=result.json, media_type="application/json")

    return app


def create_chatkit_app() -> FastAPI:
    app = FastAPI()

    # Static files: mount at /public to avoid intercepting /chatkit, and serve / with index.html.
    static_dir = os.path.join(os.path.dirname(__file__), "public")
    app.mount("/public", StaticFiles(directory=static_dir), name="public")

    @app.get("/")
    async def root_index():
        return FileResponse(os.path.join(static_dir, "index.html"))

    return app
