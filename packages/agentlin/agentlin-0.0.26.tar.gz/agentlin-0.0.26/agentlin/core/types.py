from abc import ABC
from enum import Enum
from typing import Iterator, TypeVar
from typing_extensions import Union, Any, Literal, List, Annotated, Optional, Dict, Set, TypeAlias, TypedDict
from pydantic import BaseModel, Field, TypeAdapter, ConfigDict, field_serializer
import datetime
import uuid

from openai.types.responses import ToolParam, ResponseInputItemParam, ResponseInputContentParam
from openai.types.chat import ChatCompletionMessageParam, ChatCompletionContentPartParam
from openai.types.chat.chat_completion_tool_param import (
    ChatCompletionFunctionToolParam,
)
from openai.types.chat.chat_completion_message_function_tool_call_param import (
    ChatCompletionMessageFunctionToolCallParam,
)

from openai.types.shared_params.function_definition import (
    FunctionParameters,
    FunctionDefinition,
)
from mcp.types import Tool as McpToolData

from agentlin.code_interpreter.types import Block, ToolResponse
from agentlin.core.usage import Usage
from agentlin.tools.validate import validate_function_call_arguments


STRUCTURED_OUTPUT_TYPE = TypeVar("STRUCTURED_OUTPUT_TYPE", bound=BaseModel)

ContentData: TypeAlias = ChatCompletionContentPartParam  # {"type": "text", "text": ""} | {"type": "image_url", "image_url": {"url": "", "detail": ""}} | {"type": "input_audio", "input_audio": {"data": "", "format": ""}} | {"type": "file", "file": {"file_data": "", "file_url": "", "filename": ""}}
DialogData: TypeAlias = ChatCompletionMessageParam  # {"role": "user", "content": str | list[ContentData]}
ToolData: TypeAlias = ChatCompletionFunctionToolParam  # {"type": "function", "function": FunctionDefinition}

ResponsesContentData: TypeAlias = ResponseInputContentParam  # {"type": "input_text", "text": ""}
ResponsesDialogData: TypeAlias = ResponseInputItemParam  # {"type": "message", "role": "user", "content": "" | [ContentData]}
ResponsesToolData: TypeAlias = ToolParam  # {"type": "function", "name": ...FunctionDefinition}

BlockData: TypeAlias = Block
ToolCallContentData: TypeAlias = ChatCompletionMessageFunctionToolCallParam

ToolParams: TypeAlias = Dict[str, Any]

class ToolResult(BaseModel):
    message_content: list[dict] = []
    block_list: list[dict] = []
    data: Optional[dict] = None

    @classmethod
    def from_dict(cls, data: ToolResponse) -> "ToolResult":
        return cls(
            message_content=data.get("message_content", []),
            block_list=data.get("block_list", []),
            data=data.get("data"),
        )

    def append_content(self, content: ContentData):
        """Append content to the message_content list."""
        self.message_content.append(content)

    def append_block(self, block: BlockData):
        """Append block to the block_list."""
        self.block_list.append(block)

    def extend_message_content(self, content_list: List[ContentData]):
        """Extend message_content with a list of ContentData."""
        if not content_list:
            return
        self.message_content.extend(content_list)

    def extend_block_list(self, block_list: List[BlockData]):
        """Extend block_list with a list of Block."""
        if not block_list:
            return
        self.block_list.extend(block_list)

    def extend_result(self, other: "ToolResult"):
        """Extend this ToolResult with another ToolResult."""
        self.extend_message_content(other.message_content)
        self.extend_block_list(other.block_list)


def sanitize_parameters(schema: Optional[FunctionDefinition]) -> None:
    _sanitize_parameters(schema, set())


def _sanitize_parameters(schema: Optional[FunctionDefinition], visited: Set[int]) -> None:
    if not schema or id(schema) in visited:
        return
    visited.add(id(schema))

    if "anyOf" in schema:
        schema.pop("default", None)
        for sub in schema["anyOf"]:
            if isinstance(sub, dict):
                _sanitize_parameters(sub, visited)

    if "items" in schema and isinstance(schema["items"], dict):
        _sanitize_parameters(schema["items"], visited)

    if "properties" in schema:
        for value in schema["properties"].values():
            if isinstance(value, dict):
                _sanitize_parameters(value, visited)

    if schema.get("type") == "string" and "format" in schema:
        if schema["format"] not in ("enum", "date-time"):
            schema["format"] = None


class BaseTool(ABC):
    def __init__(
        self,
        name: str,
        title: str,
        description: str,
        parameters: FunctionParameters,
        strict: bool = True,
    ):
        self.name = name
        self.title = title
        self.description = description
        self.parameters = parameters or {}
        self.strict = strict or True
        self.schema = FunctionDefinition(
            name=name,
            description=description,
            parameters=parameters,
            strict=strict,
        )

    @property
    def function_tool_schema(self) -> ToolData:
        return ToolData(
            type="function",
            function=self.schema,
        )

    async def execute(self, params: ToolParams) -> ToolResult:
        # Implement the tool's logic here
        raise NotImplementedError

    def validate_arguments(self, arguments: dict[str, Any]) -> Optional[dict[str, Any]]:
        """Validate and coerce the arguments according to the tool's parameter schema."""
        return validate_function_call_arguments(self.parameters, arguments)

    def to_mcp_tool(self) -> McpToolData:
        return McpToolData(
            name=self.name,
            title=self.title,
            description=self.description,
            inputSchema=self.parameters,
        )



class TaskStatus(str, Enum):
    """
    lifecycle states of a Task

    CREATED: The task has been created but not yet started.
    QUEUED: The task is queued and waiting to be processed.
    WORKING: The task is currently being processed.
    INPUT_REQUIRED: The task requires additional input to continue.
    PAUSED: The task is paused and will not continue until resumed.
    COMPLETED: The task has been completed successfully.
    CANCELED: The task has been canceled and will not be processed further.
    EXPIRED: The task has expired and will not be processed.
    FAILED: The task has failed during processing and will not be retried.

    Usual:
        1. CREATED -> WORKING -> COMPLETED|FAILED|CANCELED|EXPIRED
        2. CREATED -> WORKING -> INPUT_REQUIRED -> WORKING -> COMPLETED|FAILED|CANCELED|EXPIRED
        3. CREATED -> WORKING -> PAUSED -> WORKING -> COMPLETED|FAILED|CANCELED|EXPIRED
        4. CREATED -> QUEUED -> WORKING -> COMPLETED|FAILED|CANCELED|EXPIRED
        5. CREATED -> QUEUED -> WORKING -> INPUT_REQUIRED -> WORKING -> COMPLETED|FAILED|CANCELED|EXPIRED
        6. CREATED -> QUEUED -> WORKING -> PAUSED -> WORKING -> COMPLETED|FAILED|CANCELED|EXPIRED
    Canceled:
        1. CREATED -> CANCELED
        2. CREATED -> WORKING -> CANCELED
        3. CREATED -> QUEUED -> CANCELED
        4. CREATED -> QUEUED -> WORKING -> CANCELED
        5. CREATED -> QUEUED -> WORKING -> PAUSED -> CANCELED
        6. CREATED -> QUEUED -> WORKING -> INPUT_REQUIRED -> CANCELED
    Expired:
        1. CREATED -> WORKING -> EXPIRED
        2. CREATED -> WORKING -> INPUT_REQUIRED -> EXPIRED
        3. CREATED -> WORKING -> PAUSED -> EXPIRED
        4. CREATED -> QUEUED -> EXPIRED
        5. CREATED -> QUEUED -> WORKING -> EXPIRED
        6. CREATED -> QUEUED -> WORKING -> INPUT_REQUIRED -> EXPIRED
        7. CREATED -> QUEUED -> WORKING -> PAUSED -> EXPIRED
    """
    CREATED = "created"
    QUEUED = "queued"
    WORKING = "working"
    INPUT_REQUIRED = "input-required"
    PAUSED = "paused"
    COMPLETED = "completed"
    CANCELED = "canceled"
    EXPIRED = "expired"
    FAILED = "failed"

    def is_final(self) -> bool:
        return self in {
            TaskStatus.COMPLETED,
            TaskStatus.CANCELED,
            TaskStatus.EXPIRED,
            TaskStatus.FAILED,
        }


class JSONRPCError(BaseModel):
    code: int
    message: str
    data: Optional[Any] = None


#region Agent Responses
class AnnotationFileCitation(BaseModel):
    type: Literal["file_citation"] = "file_citation"
    file_url: str
    filename: str
    index: int


class AnnotationURLCitation(BaseModel):
    type: Literal["url_citation"] = "url_citation"
    start_index: int
    end_index: int
    title: str
    url: str


class AnnotationContainerFileCitation(BaseModel):
    type: Literal["container_file_citation"] = "container_file_citation"
    start_index: int
    end_index: int
    container_id: str
    file_url: str
    filename: str


class AnnotationFilePath(BaseModel):
    type: Literal["file_path"] = "file_path"
    index: int
    file_url: str


Annotation: TypeAlias = Annotated[
    Union[AnnotationFileCitation, AnnotationURLCitation, AnnotationContainerFileCitation, AnnotationFilePath],
    Field(discriminator="type"),
]


class LogprobTopLogprob(BaseModel):
    token: str
    bytes: List[int]
    logprob: float


class Logprob(BaseModel):
    token: str
    bytes: List[int]
    logprob: float
    top_logprobs: List[LogprobTopLogprob]


class TextContentItem(BaseModel):
    type: Literal["text", "input_text", "output_text", "reasoning_text", "summary_text", "refusal"] = "text"
    text: str
    id: Optional[int] = None  # 引用 id
    tags: Optional[list[str]] = None  # 用于标记内容来源等，如 "added_by_reference_manager"
    annotations: Optional[List[Annotation]] = None
    logprobs: Optional[List[Logprob]] = None


class ImageURL(BaseModel):
    url: str
    detail: Union[Literal["low", "high", "auto"], None] = None

class ImageContentItem(BaseModel):
    type: Literal["image", "input_image", "output_image", "image_url"] = "image_url"
    image_url: ImageURL


class InputAudio(BaseModel):
    data: str
    format: Literal["wav", "mp3"] = "wav"

class AudioContentItem(BaseModel):
    type: Literal["input_audio", "output_audio", "audio"] = "input_audio"
    input_audio: InputAudio


class FileDetail(BaseModel):
    file_data: Optional[str] = None # base64
    file_url: str
    filename: str

class FileContentItem(BaseModel):
    type: Literal["file"] = "file"
    file: FileDetail

ContentItem = Union[
    TextContentItem,
    ImageContentItem,
    AudioContentItem,
    FileContentItem,
    str,
]

class ItemStatus(str, Enum):
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    INCOMPLETE = "incomplete"  # failed, canceled, expired


class ReasoningItem(BaseModel):
    type: Literal["reasoning"] = "reasoning"
    id: str = Field(default_factory=lambda: f"rs_{uuid.uuid4().hex}")
    summary: list[TextContentItem] = []
    content: Optional[list[TextContentItem]] = None
    status: Optional[ItemStatus] = None


class MessageItem(BaseModel):
    type: Optional[Literal["message"]] = "message"
    id: Optional[str] = Field(default_factory=lambda: f"msg_{uuid.uuid4().hex}")
    status: Optional[ItemStatus] = None

    role: Literal["user", "assistant", "system", "developer"]
    agent_id: Optional[str] = None
    name: Optional[str] = None
    content: Union[list[ContentItem], str]
    call_id: Optional[str] = None
    message_content: Optional[list[dict]] = None
    block_list: Optional[list[dict]] = None


class ToolCallItem(BaseModel):
    type: Literal["tool_call"] = "tool_call"
    id: str = Field(default_factory=lambda: f"tc_{uuid.uuid4().hex}")
    status: Optional[ItemStatus] = None

    call_id: str  # = Field(default_factory=lambda: f"call_{uuid.uuid4().hex}")
    name: str
    arguments: str
    language: Optional[Literal["json", "yaml", "python", "javascript"]] = None


class ToolResultItem(BaseModel):
    type: Literal["tool_result"] = "tool_result"
    id: str = Field(default_factory=lambda: f"tr_{uuid.uuid4().hex}")
    status: Optional[ItemStatus] = None

    call_id: str  # = Field(default_factory=lambda: f"call_{uuid.uuid4().hex}")
    output: Union[list[ContentItem], str] = []
    message_content: list[dict] = []  # 必须支持工具结果协议，所以这个字段一定非空
    block_list: list[dict] = []


OutputItem: TypeAlias = Union[
    ReasoningItem,
    MessageItem,
    ToolCallItem,
    ToolResultItem,
]


class FunctionToolDefinition(BaseModel):
    type: Literal["function"] = "function"
    name: str
    parameters: dict  # this should be typed stricter if you add strict mode
    strict: bool = False  # change this if you support strict mode
    description: Optional[str] = ""

class TaskObject(BaseModel):
    object: str = "task"
    id: str = Field(default_factory=lambda: f"task_{uuid.uuid4().hex}")  # task_id
    session_id: str = Field(default_factory=lambda: f"sess_{uuid.uuid4().hex}")
    user_id: str = Field(default_factory=lambda: f"user_{uuid.uuid4().hex}")
    status: TaskStatus = TaskStatus.CREATED
    created_at: int = Field(default_factory=lambda: int(datetime.datetime.now(datetime.timezone.utc).timestamp()))
    output: list[OutputItem]
    usage: Usage = Field(default_factory=Usage)
    error: Optional[JSONRPCError] = None
    input_required: Optional[ToolCallItem] = None
    metadata: Optional[Dict[str, Any]] = None
    previous_task_id: Optional[str] = None
    rollouts: Optional[list["TaskRolloutEvent"]] = None

    def append_rollout(self, rollout: "TaskRolloutEvent"):
        if self.rollouts is None:
            self.rollouts = []
        self.rollouts.append(rollout)

    def is_final(self) -> bool:
        return self.status.is_final()


#region Agent Responses Events
class TaskEvent(BaseModel):
    sequence_number: Optional[int] = 1
    task_id: str = Field(default_factory=lambda: f"task_{uuid.uuid4().hex}")  # task_id

class TimeEvent(BaseModel):
    timestamp: datetime.datetime = Field(default_factory=lambda: datetime.datetime.now(datetime.timezone.utc))

    @field_serializer("timestamp")
    def serialize_dt(self, dt: datetime.datetime, _info):
        return dt.isoformat()

class ObjectEvent(BaseModel):
    task: TaskObject

# region status events
class TaskCreatedEvent(TaskEvent, TimeEvent, ObjectEvent):
    type: Literal["task.created"] = "task.created"

class TaskQueuedEvent(TaskEvent, TimeEvent):
    type: Literal["task.queued"] = "task.queued"

class TaskWorkingEvent(TaskEvent, TimeEvent):
    type: Literal["task.working"] = "task.working"

class TaskInputRequiredEvent(TaskEvent, TimeEvent, ObjectEvent):
    type: Literal["task.input_required"] = "task.input_required"
    input_required: ToolCallItem

class TaskPausedEvent(TaskEvent, TimeEvent, ObjectEvent):
    type: Literal["task.paused"] = "task.paused"

class TaskCompletedEvent(TaskEvent, TimeEvent, ObjectEvent):
    type: Literal["task.completed"] = "task.completed"

class TaskCanceledEvent(TaskEvent, TimeEvent, ObjectEvent):
    type: Literal["task.canceled"] = "task.canceled"

class TaskExpiredEvent(TaskEvent, TimeEvent, ObjectEvent):
    type: Literal["task.expired"] = "task.expired"

class TaskFailedEvent(TaskEvent, TimeEvent, ObjectEvent):
    type: Literal["task.failed"] = "task.failed"
    error: JSONRPCError

# endregion


class TaskToolsUpdatedEvent(TaskEvent):
    type: Literal["task.tools_updated"] = "task.tools_updated"
    tools: List[ToolData]

class TaskContextCompressionCreatedEvent(TaskEvent):
    type: Literal["task.context_compression.created"] = "task.context_compression.created"

class TaskContextCompressionInProgressEvent(TaskEvent):
    type: Literal["task.context_compression.in_progress"] = "task.context_compression.in_progress"

class TaskContextCompressionCompletedEvent(TaskEvent):
    type: Literal["task.context_compression.completed"] = "task.context_compression.completed"

class TaskOutputItemAddedEvent(TaskEvent):
    type: Literal["task.output_item.added"] = "task.output_item.added"
    agent_step: int = 0
    item: OutputItem

class TaskOutputItemDoneEvent(TaskEvent):
    type: Literal["task.output_item.done"] = "task.output_item.done"
    agent_step: int = 0
    item: OutputItem

class TaskContentPartAddedEvent(TaskEvent):
    type: Literal["task.content_part.added"] = "task.content_part.added"
    item_id: str  # 指向 ResponseOutputItemAdded 的 item.id
    agent_step: int = 0
    content_index: int = 0
    part: ContentItem

class TaskContentPartDoneEvent(TaskEvent):
    type: Literal["task.content_part.done"] = "task.content_part.done"
    item_id: str  # 指向 ResponseOutputItemAdded 的 item.id
    agent_step: int = 0
    content_index: int = 0
    part: ContentItem


class Part(BaseModel):
    type: Literal["summary_text"] = "summary_text"
    text: str

class TaskReasoningSummaryPartAddedEvent(TaskEvent):
    type: Literal["task.reasoning_summary_part.added"] = "task.reasoning_summary_part.added"
    item_id: str  # 指向 ResponseOutputItemAdded 的 item.id
    agent_step: int
    part: Part
    summary_index: int

class TaskReasoningSummaryPartDoneEvent(TaskEvent):
    type: Literal["task.reasoning_summary_part.done"] = "task.reasoning_summary_part.done"
    item_id: str  # 指向 ResponseOutputItemAdded 的 item.id
    agent_step: int
    part: Part
    summary_index: int

class TaskReasoningSummaryTextDeltaEvent(TaskEvent):
    type: Literal["task.reasoning_summary_text.delta"] = "task.reasoning_summary_text.delta"
    item_id: str  # 指向 ResponseOutputItemAdded 的 item.id
    agent_step: int = 0
    content_index: int = 0
    delta: str = ""

class TaskReasoningSummaryTextDoneEvent(TaskEvent):
    type: Literal["task.reasoning_summary_text.done"] = "task.reasoning_summary_text.done"
    item_id: str  # 指向 ResponseOutputItemAdded 的 item.id
    agent_step: int
    summary_index: int
    text: str

class TaskReasoningTextDeltaEvent(TaskEvent):
    type: Literal["task.reasoning_text.delta"] = "task.reasoning_text.delta"
    item_id: str  # 指向 ResponseOutputItemAdded 的 item.id
    agent_step: int = 0
    content_index: int = 0
    delta: str = ""


class TaskReasoningTextDoneEvent(TaskEvent):
    type: Literal["task.reasoning_text.done"] = "task.reasoning_text.done"
    item_id: str  # 指向 ResponseOutputItemAdded 的 item.id
    agent_step: int = 0
    content_index: int = 0
    text: str = ""

class TaskTextDeltaEvent(TaskEvent):
    type: Literal["task.text.delta"] = "task.text.delta"
    item_id: str  # 指向 ResponseOutputItemAdded 的 item.id
    agent_step: int = 0
    content_index: int = 0
    delta: str = ""
    logprobs: list = []

class TaskTextDoneEvent(TaskEvent):
    type: Literal["task.text.done"] = "task.text.done"
    item_id: str  # 指向 ResponseOutputItemAdded 的 item.id
    agent_step: int = 0
    content_index: int = 0
    text: str = ""
    logprobs: list = []

class TaskToolCallArgumentsDeltaEvent(TaskEvent):
    type: Literal["task.tool_call_arguments.delta"] = "task.tool_call_arguments.delta"
    item_id: str  # 指向 ResponseOutputItemAdded 的 item.id
    call_id: str
    agent_step: int
    delta: str

class TaskToolCallArgumentsDoneEvent(TaskEvent):
    type: Literal["task.tool_call_arguments.done"] = "task.tool_call_arguments.done"
    item_id: str  # 指向 ResponseOutputItemAdded 的 item.id
    call_id: str
    agent_step: int
    arguments: str

class TaskToolResultDeltaEvent(TaskEvent):
    type: Literal["task.tool_result.delta"] = "task.tool_result.delta"
    item_id: str  # 指向 ResponseOutputItemAdded 的 item.id
    call_id: str
    agent_step: int
    delta_message_content: list[dict] = []
    delta_block_list: list[dict] = []

class TaskToolResultDoneEvent(TaskEvent):
    type: Literal["task.tool_result.done"] = "task.tool_result.done"
    item_id: str  # 指向 ResponseOutputItemAdded 的 item.id
    call_id: str
    agent_step: int
    message_content: list[dict] = []
    block_list: list[dict] = []

class TaskBlockDeltaEvent(TaskEvent):
    type: Literal["task.block.delta"] = "task.block.delta"
    item_id: str  # 指向 ResponseOutputItemAdded 的 item.id
    agent_step: int
    block: dict

class TaskBlockDoneEvent(TaskEvent):
    type: Literal["task.block.done"] = "task.block.done"
    item_id: str  # 指向 ResponseOutputItemAdded 的 item.id
    agent_step: int
    block: dict

class TaskAudioDeltaEvent(TaskEvent):
    type: Literal["task.audio.delta"] = "task.audio.delta"
    delta: str
    """A chunk of Base64 encoded task audio bytes."""
    agent_step: int

class TaskAudioDoneEvent(TaskEvent):
    type: Literal["task.audio.done"] = "task.audio.done"
    agent_step: int


class TaskImageDeltaEvent(TaskEvent):
    type: Literal["task.image.delta"] = "task.image.delta"
    item_id: str  # 指向 ResponseOutputItemAdded 的 item.id
    agent_step: int
    partial_image_b64: str
    partial_image_index: int

class TaskImageDoneEvent(TaskEvent):
    type: Literal["task.image.done"] = "task.image.done"
    item_id: str  # 指向 ResponseOutputItemAdded 的 item.id
    agent_step: int

class TaskFileDeltaEvent(TaskEvent):
    type: Literal["task.file.delta"] = "task.file.delta"
    item_id: str  # 指向 ResponseOutputItemAdded 的 item.id
    agent_step: int
    partial_file_b64: str
    partial_file_index: int

class TaskFileDoneEvent(TaskEvent):
    type: Literal["task.file.done"] = "task.file.done"
    item_id: str  # 指向 ResponseOutputItemAdded 的 item.id
    agent_step: int

class TaskRolloutEvent(TaskEvent):
    type: Literal["task.rollout"] = "task.rollout"
    session_id: str = Field(default_factory=lambda: f"session_{uuid.uuid4().hex}")
    task_id: str = Field(default_factory=lambda: f"task_{uuid.uuid4().hex}")
    trace_id: str = Field(default_factory=lambda: f"trace_{uuid.uuid4().hex}")
    request_id: str = Field(default_factory=lambda: f"request_{uuid.uuid4().hex}")
    rollout_id: str = Field(default_factory=lambda: f"rollout_{uuid.uuid4().hex}")
    input_messages: List[dict]
    output_messages: List[dict]
    inference_args: dict[str, Any] = {}
    tools: list[ToolData] = []
    request: dict[str, Any] = {}
    is_answer: bool = False
    turn: int
    step: Optional[int] = None

AgentTaskEvent: TypeAlias = Union[
    TaskCreatedEvent,
    TaskWorkingEvent,
    TaskQueuedEvent,
    TaskInputRequiredEvent,
    TaskPausedEvent,
    TaskCanceledEvent,
    TaskExpiredEvent,
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
    # TaskBlockDeltaEvent,
    # TaskBlockDoneEvent,
    TaskTextDeltaEvent,
    TaskTextDoneEvent,
    TaskImageDeltaEvent,
    TaskImageDoneEvent,
    TaskAudioDeltaEvent,
    TaskAudioDoneEvent,
    TaskFileDeltaEvent,
    TaskFileDoneEvent,
    TaskRolloutEvent,
]
AgentTaskEventType = TypeAdapter(
    Annotated[
        AgentTaskEvent,
        Field(discriminator="type"),
    ]
)

# def check_stream(stream: Iterator[AgentTaskEvent]):
#     # 有限状态机
#     transition: list[dict[AgentTaskEvent, int]] = [
#         {}, # fail
#         # state 1
#         {TaskCreatedEvent: 2},
#         # state 2
#         {TaskInProgressEvent: 3},
#         # state 3
#         {TaskToolsUpdatedEvent: 3, TaskOutputItemAddedEvent: 4},  # -> reasoning, text/image/audio/file, tool_call, tool_call_result
#         # state 4
#         {
#             TaskContentPartAddedEvent: 5, # -> reasoning, text/image/audio/file, tool_call_result
#             TaskToolCallArgumentsDeltaEvent: 6, # -> tool_call
#         },
#         # state 5
#         {
#             TaskReasoningTextDeltaEvent: 7, # -> reasoning
#             TaskTextDeltaEvent: 8,
#             TaskImageDeltaEvent: 9,
#             TaskAudioDeltaEvent: 10,
#             TaskFileDeltaEvent: 11,
#             TaskToolCallResultDeltaEvent: 12,
#         },
#         # state 6
#         {TaskToolCallArgumentsDoneEvent: 13},
#         # state 7
#         {TaskReasoningTextDoneEvent: 14},
#         # state 8
#         {TaskTextDoneEvent: 15},
#         # state 9
#         {TaskImageDoneEvent: 15},
#         # state 10
#         {TaskAudioDoneEvent: 15},
#         # state 11
#         {TaskFileDoneEvent: 15},
#         # state 12
#         {TaskToolCallResultDoneEvent: 15},
#         # state 13
#         {TaskOutputItemDoneEvent: 3},
#         # state 14
#         {TaskContentPartDoneEvent: 17, TaskReasoningSummaryPartAddedEvent: 16},
#         # state 15
#         {TaskContentPartDoneEvent: 3},
#     ]
#     def event_to_action(event: AgentTaskEvent):
#         if isinstance(event, TaskCreatedEvent):
#             return TaskCreatedEvent
#     init_state = 1
#     stop_state = {}
#     current_state = init_state
#     for event in stream:
#         action = event_to_action(event)
#         next_state = transition[current_state]
#         if action not in next_state:
#             return False
#         current_state = next_state[action]
#     return current_state in stop_state

# endregion
#endregion
class AuthenticationInfo(BaseModel):
    model_config = ConfigDict(extra="allow")

    schemes: List[str]
    credentials: Optional[str] = None


class PushNotificationConfig(BaseModel):
    url: str
    token: Optional[str] = None
    authentication: Optional[AuthenticationInfo] = None


class TaskQueryParams(BaseModel):
    id: str
    metadata: Optional[dict[str, Any]] = None


class ListTasksParams(BaseModel):
    session_id: Optional[str] = None
    user_id: Optional[str] = None
    status: Optional[List[TaskStatus]] = None
    limit: Optional[int] = 10
    offset: Optional[int] = 0


class TaskParams(BaseModel):
    id: str = Field(default_factory=lambda: f"task_{uuid.uuid4().hex}")
    session_id: str = Field(default_factory=lambda: f"sess_{uuid.uuid4().hex}")
    user_id: str = Field(default_factory=lambda: f"user_{uuid.uuid4().hex}")
    payload: dict | BaseModel
    pushNotification: Optional[PushNotificationConfig] = None


class TaskPushNotificationConfig(BaseModel):
    id: str
    pushNotificationConfig: PushNotificationConfig


#region RPC Messages
class JSONRPCMessage(BaseModel):
    jsonrpc: Literal["2.0"] = "2.0"
    id: str = Field(default_factory=lambda: uuid.uuid4().hex)  # request_id or task_id


class JSONRPCRequest(JSONRPCMessage):
    method: str
    params: Optional[dict[str, Any]] = None


class JSONRPCResponse(JSONRPCMessage):
    result: Optional[Any] = None
    error: Optional[JSONRPCError] = None


class TaskInvokeRequest(JSONRPCRequest):
    method: Literal["tasks/create"] = "tasks/create"
    params: TaskParams


class TaskResponse(JSONRPCResponse):
    result: TaskObject


class TaskStreamingRequest(JSONRPCRequest):
    method: Literal["tasks/createSubscribe"] = "tasks/createSubscribe"
    params: TaskParams


class TaskStreamingResponse(JSONRPCResponse):
    result: Optional[AgentTaskEvent] = None


class ListTasksRequest(JSONRPCRequest):
    method: Literal["tasks/list"] = "tasks/list"
    params: Optional[ListTasksParams] = None


class ListTasksResponse(JSONRPCResponse):
    result: List[TaskObject] = []


class GetTaskRequest(JSONRPCRequest):
    method: Literal["tasks/get"] = "tasks/get"
    params: TaskQueryParams


class GetTaskResponse(JSONRPCResponse):
    result: Optional[TaskObject] = None


class CancelTaskRequest(JSONRPCRequest):
    method: Literal["tasks/cancel",] = "tasks/cancel"
    params: TaskQueryParams


class CancelTaskResponse(JSONRPCResponse):
    result: Optional[TaskObject] = None


class SetTaskPushNotificationRequest(JSONRPCRequest):
    method: Literal["tasks/pushNotification/set",] = "tasks/pushNotification/set"
    params: TaskPushNotificationConfig


class SetTaskPushNotificationResponse(JSONRPCResponse):
    result: Optional[TaskPushNotificationConfig] = None


class GetTaskPushNotificationRequest(JSONRPCRequest):
    method: Literal["tasks/pushNotification/get",] = "tasks/pushNotification/get"
    params: TaskQueryParams


class GetTaskPushNotificationResponse(JSONRPCResponse):
    result: Optional[TaskPushNotificationConfig] = None


class TaskResubscriptionRequest(JSONRPCRequest):
    method: Literal["tasks/resubscribe",] = "tasks/resubscribe"
    params: TaskQueryParams


TaskRequest = Union[
    TaskInvokeRequest,
    TaskStreamingRequest,
    GetTaskRequest,
    CancelTaskRequest,
    SetTaskPushNotificationRequest,
    GetTaskPushNotificationRequest,
    TaskResubscriptionRequest,
]
TaskRequestType = TypeAdapter(
    Annotated[
        TaskRequest,
        Field(discriminator="method"),
    ]
)
# endregion

#region Error types
class JSONParseError(JSONRPCError):
    code: int = -32700
    message: str = "Invalid JSON payload"
    data: Optional[Any] = None


class InvalidRequestError(JSONRPCError):
    code: int = -32600
    message: str = "Request payload validation error"
    data: Optional[Any] = None


class MethodNotFoundError(JSONRPCError):
    code: int = -32601
    message: str = "Method not found"
    data: None = None


class InvalidParamsError(JSONRPCError):
    code: int = -32602
    message: str = "Invalid parameters"
    data: Optional[Any] = None


class InternalError(JSONRPCError):
    code: int = -32603
    message: str = "Internal error"
    data: Optional[Any] = None


class TaskNotFoundError(JSONRPCError):
    code: int = -32001
    message: str = "Task not found"
    data: None = None


class TaskNotCancelableError(JSONRPCError):
    code: int = -32002
    message: str = "Task cannot be canceled"
    data: None = None


class PushNotificationNotSupportedError(JSONRPCError):
    code: int = -32003
    message: str = "Push Notification is not supported"
    data: None = None


class UnsupportedOperationError(JSONRPCError):
    code: int = -32004
    message: str = "This operation is not supported"
    data: None = None


class ContentTypeNotSupportedError(JSONRPCError):
    code: int = -32005
    message: str = "Incompatible content types"
    data: None = None


class RPCTimeoutError(JSONRPCError):
    code: int = -32006
    message: str = "RPC call timed out"
    data: None = None


class RPCMethodNotFoundError(JSONRPCError):
    code: int = -32007
    message: str = "RPC method not found"
    data: None = None


class RPCExecutionError(JSONRPCError):
    code: int = -32008
    message: str = "RPC method execution failed"
    data: Optional[Any] = None


## RPC-specific request/response types

class RPCCallRequest(JSONRPCRequest):
    """RPC方法调用请求"""
    method: Literal["rpc/call"] = "rpc/call"
    params: dict[str, Any]  # 包含 target_agent_id, rpc_method, args, kwargs


class RPCCallResponse(JSONRPCResponse):
    """RPC方法调用响应"""
    result: Optional[Any] = None
# endregion

def are_modalities_compatible(server_output_modes: List[str], client_output_modes: List[str]):
    """Modalities are compatible if they are both non-empty
    and there is at least one common element."""
    if client_output_modes is None or len(client_output_modes) == 0:
        return True

    if server_output_modes is None or len(server_output_modes) == 0:
        return True

    return any(x in server_output_modes for x in client_output_modes)


def append_metadata(metadata: dict[str, list], new_metadata: dict[str, Any]) -> None:
    """Append data to the metadata dictionary."""
    for key, value in new_metadata.items():
        if key not in metadata:
            metadata[key] = []
        if isinstance(value, list):
            metadata[key].extend(value)
        else:
            if not isinstance(metadata[key], list):
                metadata[key] = [metadata[key]]
            metadata[key].append(value)
