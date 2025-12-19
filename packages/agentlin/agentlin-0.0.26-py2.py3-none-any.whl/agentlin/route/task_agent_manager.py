import asyncio
import os
import time
import json
import traceback
import uuid
import copy
from typing_extensions import Any, AsyncIterable, TypeVar, overload, NoReturn, Type, TypedDict
from collections import defaultdict
from loguru import logger
from pathlib import Path
from openai.types.chat.chat_completion_chunk import ChatCompletionChunk
from openai.types.chat.chat_completion import ChatCompletion

from xlin import append_to_json_list, load_text
from agentlin.code_interpreter.types import ToolResponse
from agentlin.core.config import apply_env, apply_env_to_text
from agentlin.core.multimodal import is_text_content
from agentlin.core.types import *
from agentlin.core.agent_schema import (
    content_data_to_content_item,
    content_datas_to_content_items,
    content_items_to_text,
    content_to_text,
    extract_apply,
    extract_apply_block,
    extract_citations,
    extract_code,
    extract_thought,
    get_assistant_content,
    parse_function_call_response,
    parse_text_with_apply,
    remove_citations_in_messages,
    remove_thoughts,
    messages_to_text,
    create_logger,
    remove_thoughts_in_messages,
    replace_citations,
    replace_citations_in_message_content,
)
from agentlin.core.usage import Usage
from agentlin.route.agent_config import SubAgentConfig, AgentConfig, get_agent_id, get_agent_config
from agentlin.route.user_manager import UserStore
from agentlin.route.reference_manager import ReferenceManager, group_by_ref_id
from agentlin.route.task_manager import InMemoryTaskManager, SequenceCounter, StreamableTaskParser, merge_streams
from agentlin.route.task_tool_manager import TaskToolManager, CallToolRequest
from agentlin.route.task_code_manager import TaskCodeManager, ExecuteCodeRequest
from agentlin.route.task_model_manager import TaskModelManager, ModelRequest
from agentlin.skills.core import SkillConfig
from agentlin.store.task_store import InMemoryTaskStore
from agentlin.tools.core import GenerateStructuredOutputTool, tool_result_of_internal_error
from agentlin.tools.stateful_memory.memory_tool import MemorySessionState, MemoryTool
from agentlin.tools.stateful_memory.todo_tool import TodoSessionState, TodoWriteTool
from agentlin.tools.tool_calendar import format_datetime_with_holiday
from agentlin.tools.validate import validate_function_call_arguments_str, get_validation_error_message_str


class SessionState(BaseModel):
    session_id: str
    user_id: str
    client_id: str
    main_agent_id: str
    host_code_kernel_id: Optional[str] = None
    agent_config: AgentConfig

    # 短期记忆
    history_messages: list[DialogData] = []
    thought_messages: list[DialogData] = []
    usage: Usage = Field(default_factory=Usage)

    # 工具记忆
    developer_level_tools: list[ToolData] = []  # 已注册的工具列表
    todo_state: TodoSessionState = Field(default_factory=TodoSessionState)  # 待办事项状态
    memory_state: MemorySessionState = Field(default_factory=MemorySessionState)  # 记忆状态

    # 运行时 - 这些属性不参与 BaseModel 的序列化和验证
    model_config = {"arbitrary_types_allowed": True, "extra": "allow"}

    def __init__(self, **data):
        # 提取运行时管理器，避免传入 BaseModel 验证
        task_model_manager = data.pop("task_model_manager", None)
        task_tool_manager = data.pop("task_tool_manager", None)
        task_code_manager = data.pop("task_code_manager", None)

        # 先调用父类的 __init__
        super().__init__(**data)

        # 然后设置运行时属性
        self.task_model_manager: TaskModelManager = task_model_manager
        self.task_tool_manager: TaskToolManager = task_tool_manager
        self.task_code_manager: TaskCodeManager = task_code_manager

    def get_subagent_by_name(self, name: str) -> Optional[SubAgentConfig]:
        for subagent in self.agent_config.builtin_subagents:
            if subagent.name == name:
                return subagent
        return None

    def get_skill_by_name(self, name: str) -> Optional[SkillConfig]:
        for skill in self.agent_config.builtin_skills:
            if skill.name == name:
                return skill
        return None

    async def init(self):
        await self.task_tool_manager.discover_tools(self)
        self.developer_level_tools = await self.task_tool_manager.get_tools()

    async def start(self):
        self.tool_task = None
        if self.task_tool_manager:
            await self.task_tool_manager.initialize()
            self.tool_task = asyncio.create_task(self.task_tool_manager.run())

    def stop(self):
        if self.task_code_manager:
            kernel_id = self.host_code_kernel_id
            if kernel_id:
                self.task_code_manager.delete_kernel(kernel_id)
        if self.task_tool_manager:
            self.task_tool_manager.stop()
            if hasattr(self, "tool_task") and self.tool_task:
                if self.tool_task.done():
                    self.tool_task = None
                else:
                    logger.warning(f"Failed to stop tool task for session {self.session_id}")


def get_task_object(response: TaskResponse) -> Optional[TaskObject]:
    if response.error:
        logger.error(f"Error in tool task: {response.error}")
        return None
    task_obj = response.result
    if not task_obj:
        logger.error(f"Error in tool task: no result")
        return None
    return task_obj


def get_tool_call_item(resp: Union[TaskResponse, TaskObject]) -> Optional[ToolCallItem]:
    if isinstance(resp, TaskResponse):
        task = get_task_object(resp)
    else:
        task = resp
    if not task:
        return None
    if not task.output or len(task.output) == 0:
        logger.error(f"Error in tool task: no output")
        return None
    tool_call_item = None
    for item in reversed(task.output):
        if not isinstance(item, (ToolCallItem, ToolResultItem)):
            # FunctionCallItem 后面只能是 FunctionCallOutputItem。如果不是，说明可能是上一步的 function call 了，模型已经进入回答阶段。我们要的是命中 stop_tools 的最后一个 function call。
            break
        if isinstance(item, ToolCallItem):
            tool_call_item = item
            break
    if not isinstance(tool_call_item, ToolCallItem):
        logger.error(f"Error in tool task: last output is not function call")
        return None
    return tool_call_item


def get_tool_result_item(resp: Union[TaskResponse, TaskObject]) -> Optional[ToolResultItem]:
    if isinstance(resp, TaskResponse):
        task = get_task_object(resp)
    else:
        task = resp
    if not task:
        return None
    if not task.output or len(task.output) == 0:
        logger.error(f"Error in tool task: no output")
        return None
    tool_result_item = None
    for item in reversed(task.output):
        if isinstance(item, ToolResultItem):
            tool_result_item = item
            break
    if not isinstance(tool_result_item, ToolResultItem):
        logger.error(f"Error in tool task: no tool result item found")
        return None
    return tool_result_item


@overload
def get_structured_output(
    resp: Union[TaskResponse, TaskObject],
    structured_output: Type[STRUCTURED_OUTPUT_TYPE],
) -> Optional[Union[STRUCTURED_OUTPUT_TYPE]]: ...


@overload
def get_structured_output(
    resp: Union[TaskResponse, TaskObject],
    structured_output: dict[str, Any],
) -> Optional[dict[str, Any]]: ...


def get_structured_output(
    resp: Union[TaskResponse, TaskObject],
    structured_output: Union[Type[STRUCTURED_OUTPUT_TYPE], dict[str, Any]],
) -> Optional[Union[STRUCTURED_OUTPUT_TYPE, dict[str, Any]]]:
    tool_call_item = get_tool_call_item(resp)
    if not tool_call_item:
        logger.error(f"Error in structured output task: no function call item")
        return None
    validated_call_args = None
    try:
        if isinstance(structured_output, dict):
            validated_call_args = validate_function_call_arguments_str(structured_output, tool_call_item.arguments)
        else:
            validated_call_args = validate_function_call_arguments_str(structured_output.model_json_schema(), tool_call_item.arguments)
    except Exception as e:
        logger.error(f"Error in structured output task: failed to validate function call arguments: {e}")
        return None
    if not validated_call_args:
        # 获取详细的验证错误信息
        parameters_schema = structured_output if isinstance(structured_output, dict) else structured_output.model_json_schema()
        validation_error = get_validation_error_message_str(parameters_schema, tool_call_item.arguments)
        logger.error(f"Error in structured output task: validation failed.\n\nValidation errors:\n{validation_error}\n\nReceived arguments:\n{tool_call_item.arguments}")
        return None
    if isinstance(structured_output, dict):
        return validated_call_args
    structured_output_instance = None
    try:
        structured_output_instance = structured_output.model_validate(validated_call_args)
    except Exception as e:
        logger.error(f"Error in structured output task: failed to create structured output instance: {e}")
        return None
    if not structured_output_instance:
        logger.error(f"Error in structured output task: structured output instance is None")
        return None
    return structured_output_instance


class SessionRequest(BaseModel):
    client_id: str
    user_message_content: Union[list[ContentData], str]

    agent_config: Optional[AgentConfig] = None
    allowed_tools: Optional[list[str]] = None  # 允许的工具列表. None 为允许所有，[] 为不允许任何
    disallowed_tools: Optional[list[str]] = None  # 不允许的工具列表. None 和 [] 不进行处理
    allowed_subagents: Optional[list[str]] = None  # 允许的子代理列表. None 为允许所有，[] 为不允许任何
    stop_tools: Optional[list[str]] = None  # 遇到 stop_tools 时终止. None 和 [] 不进行处理
    client_tools: Optional[list[ToolData]] = None  # 客户端的工具定义，遇到客户端工具时一定终止，等用户执行完客户端工具后再在下一个请求中继续执行。客户端工具都是 stop_tools。

    # agent 级的 completion 模式：
    # 存在 history_messages 或 thought_messages 非空时，不清空驻留在内存中的 thought_messages 栈，
    # 而是将传进来的 history_messages 或 thought_messages 拼到末尾，继续 agent 循环
    history_messages: list[dict] = []
    thought_messages: list[dict] = []
    previous_task_id: Optional[str] = None  # 上一次 task 的 id，用于续写
    store: bool = False  # 是否存储到历史消息中

    # agent 的环境
    workspace_dir: Optional[str] = None  # 当前工作目录, 用于 file_system_mcp 和代码解释器
    env: Optional[dict[str, str]] = None  # 环境变量
    subagent_prompt_template: Optional[str] = None  # 子代理的 prompt template

    # 推理参数
    inference_args: Optional[dict[str, Any]] = None

    # 输出
    structured_output: Optional[Union[Type[STRUCTURED_OUTPUT_TYPE], dict[str, Any]]] = None

    log_dir: Optional[str] = None
    rollout_save_dir: Optional[str] = None
    return_rollout: bool = False  # 是否返回 rollout 的结果
    include_compress_model_rollout: bool = False  # 是否包含 compress model 的 rollout 结果
    include_subagent_rollout: bool = False  # 是否包含子 agent 的 rollout 结果


class ExecuteSubAgentRequest(BaseModel):
    name: str
    description: str
    prompt: str


class TaskAgentManager(InMemoryTaskManager):
    def __init__(
        self,
        debug=False,
        use_message_queue=False,
        user_file: Optional[str] = None,
        builtin_tools: list[BaseTool] = [],
        task_store: Optional[InMemoryTaskStore] = None,
    ):
        """Initialize the session task manager.

        Args:
            debug (bool, optional): Enable debug mode. Defaults to False.
            use_message_queue (bool, optional): Use message queue for task management. Defaults to False.
            user_file (str, optional): Path to the user file. Defaults to None.
        """
        super().__init__(task_store=task_store)
        self.sessions: dict[str, SessionState] = {}
        self.debug = debug
        self.use_message_queue = use_message_queue
        self.user_store = UserStore()
        self.builtin_tools = builtin_tools
        if user_file:
            self.user_store.load_from_file(user_file)

    def build_system_content(self, session_id: str, session_state: SessionState, env: dict[str, Any]) -> str:
        developer_prompt = session_state.agent_config.developer_prompt
        code_for_agent = session_state.agent_config.code_for_agent

        developer_prompt, _, _ = apply_env(env=env, prompt=developer_prompt, code_for_agent=code_for_agent, code_for_interpreter=None)
        system_content = [
            {"type": "text", "text": developer_prompt},
        ]
        return system_content

    async def query_nlu(self, query: str):
        # 这里可以调用 NLU 服务进行查询
        return ""

    async def get_previous_task(self, task_id: str) -> Optional[TaskObject]:
        self.on_get_task()
        return None

    def build_system_code_for_interpreter(self, session_state: SessionState, env: dict[str, Any]) -> str:
        code_for_interpreter = session_state.agent_config.code_for_interpreter
        code = apply_env_to_text(env=env, text=code_for_interpreter)

        if self.debug:
            logger.debug(f"Total system code for session {session_state.session_id}:\n{code}")
        return code

    def merge_env(self, session_state: SessionState, req: SessionRequest) -> dict[str, str]:
        user_id = session_state.user_id
        user_data = self.user_store.get_user(user_id)
        user_profile = user_data.user_profile if user_data else ""
        merged_env: dict[str, str] = {
            "session_id": session_state.session_id,
            "main_agent_id": session_state.main_agent_id,
            "client_id": req.client_id,
            "user_id": user_id,
            "user_profile": user_profile,
        }
        if req.env:
            merged_env.update(req.env)
        return merged_env

    async def execute_code(
        self,
        request_id: str,
        session_id: str,
        user_id: str,
        kernel_id: str,
        code: str,
        task_code_manager: TaskCodeManager,
    ) -> Optional[ToolResultItem]:
        req = ExecuteCodeRequest(
            kernel_id=kernel_id,
            code=code,
            mode="full",
        )
        request = TaskInvokeRequest(
            id=request_id,
            params=TaskParams(
                id=f"task-{uuid.uuid4().hex}",
                session_id=session_id,
                user_id=user_id,
                payload=req,
            )
        )
        resp = await task_code_manager.on_task_invoke(request)
        if resp.error:
            logger.error(f"Failed to execute code: {resp.error}")
            return None
        code_result = get_tool_result_item(resp)
        return code_result

    async def lazy_init_kernel(self, request_id: str, session_state: SessionState, task_code_manager: TaskCodeManager, env: dict[str, Any]) -> str:
        kernel_id = session_state.host_code_kernel_id
        if kernel_id:
            return kernel_id
        kernel_id = task_code_manager.create_kernel()
        session_state.host_code_kernel_id = kernel_id
        code = self.build_system_code_for_interpreter(session_state, env)
        tool_result = await self.execute_code(
            request_id,
            session_state.session_id,
            session_state.user_id,
            kernel_id,
            code,
            task_code_manager,
        )
        if not tool_result:
            logger.warning(f"Failed to initialize code interpreter kernel for session {session_state.session_id}")
        else:
            logger.debug(f"Initialized code interpreter kernel {kernel_id} for session {session_state.session_id}\n{content_to_text(tool_result.message_content)}")
        return kernel_id

    async def extract_variable(self, request_id: str, session_id: str, variable_name: str, task_code_manager: TaskCodeManager, env: dict[str, Any]) -> Optional[ToolResultItem]:
        session_state = self.get_session(session_id)
        if not session_state:
            logger.error(f"Session {session_id} not found for extracting variable {variable_name}")
            return None
        kernel_id = await self.lazy_init_kernel(request_id, session_state, task_code_manager, env)
        code = f"{variable_name}"
        code_result = await self.execute_code(
            request_id,
            session_state.session_id,
            session_state.user_id,
            kernel_id,
            code,
            task_code_manager,
        )
        return code_result

    async def load_code(self, request_id: str, session_id: str, code: str, task_code_manager: TaskCodeManager, env: dict[str, Any]) -> Optional[ToolResultItem]:
        session_state = self.get_session(session_id)
        if not session_state:
            logger.error(f"Session {session_id} not found for loading code")
            return None
        kernel_id = await self.lazy_init_kernel(request_id, session_state, task_code_manager, env)
        code_result = await self.execute_code(
            request_id,
            session_state.session_id,
            session_state.user_id,
            kernel_id,
            code,
            task_code_manager,
        )
        return code_result

    async def create_session(
        self,
        session_id: str,
        user_id: str,
        client_id: str,
        agent_config: Optional[AgentConfig] = None,
        workspace_dir: Optional[str] = None,
        log_dir: Optional[str] = None,
    ) -> SessionState:
        if agent_config is None:
            main_agent_id = await get_agent_id(client_id)
            agent_config = await get_agent_config(main_agent_id)
        main_agent_id = agent_config.agent_id

        model = agent_config.model
        agent_config.inference_args.setdefault("max_tokens", 10 * 1024)  # 设置默认最大 token 数量
        agent_config.inference_args.setdefault("model", model)  # 设置默认模型
        task_model_manager = TaskModelManager(
            agent_id=main_agent_id,
            log_dir=log_dir,
        )
        tool_mcp_config = agent_config.tool_mcp_config
        task_tool_manager = TaskToolManager(
            client_id=client_id,
            agent_id=main_agent_id,
            mcp_config=tool_mcp_config,
            workspace_dir=workspace_dir,
            log_dir=log_dir,
            builtin_tools=self.builtin_tools,
            task_store=self.task_store,
        )

        code_interpreter_config = agent_config.code_interpreter_config
        if not code_interpreter_config:
            raise ValueError("Code interpreter configuration is required for TaskCodeManager.")
        task_code_manager = TaskCodeManager(
            agent_id=main_agent_id,
            jupyter_host=code_interpreter_config.jupyter_host,
            jupyter_port=code_interpreter_config.jupyter_port,
            jupyter_token=code_interpreter_config.jupyter_token,
            jupyter_timeout=code_interpreter_config.jupyter_timeout,
            jupyter_username=code_interpreter_config.jupyter_username,
            log_dir=log_dir,
            task_store=self.task_store,
        )
        usage = Usage()
        state = SessionState(
            session_id=session_id,
            user_id=user_id,
            client_id=client_id,
            main_agent_id=main_agent_id,
            host_code_kernel_id=None,
            agent_config=agent_config,
            developer_level_tools=[],  # 初始化为空，后续 init() 时填充
            usage=usage,
            task_tool_manager=task_tool_manager,
            task_code_manager=task_code_manager,
            task_model_manager=task_model_manager,
        )
        await state.init()
        if self.use_message_queue:
            await state.start()
        self.sessions[session_id] = state
        return state

    def get_session(self, session_id: str):
        return self.sessions.get(session_id, None)

    def delete_session(self, session_id: str):
        if session_id in self.sessions:
            session_state = self.sessions[session_id]
            # if self.use_message_queue:
            session_state.stop()
            del self.sessions[session_id]

    @overload
    async def __call__(
        self,
        user_message_content: Union[list[ContentData], str],
        structured_output: None = None,
        stream: Literal[False] = False,
        client_id: Optional[str] = None,
        request_id: Optional[str] = None,
        session_id: Optional[str] = None,
        task_id: Optional[str] = None,
        user_id: Optional[str] = None,
        agent_config: Optional[AgentConfig] = None,
        allowed_tools: Optional[list[str]] = None,
        disallowed_tools: Optional[list[str]] = None,
        allowed_subagents: Optional[list[str]] = None,
        stop_tools: Optional[list[str]] = None,
        client_tools: Optional[list[ToolData]] = None,
        history_messages: Optional[list[DialogData]] = None,
        thought_messages: Optional[list[DialogData]] = None,
        inference_args: Optional[dict[str, Any]] = None,
        workspace_dir: Optional[str] = None,
        subagent_prompt_template: Optional[str] = None,
        env: Optional[dict[str, str]] = None,
        log_dir: Optional[str] = None,
        rollout_save_dir: Optional[str] = None,
        return_rollout: bool = False,
        include_compress_model_rollout: bool = False,
        include_subagent_rollout: bool = False
    ) -> TaskResponse: ...

    @overload
    async def __call__(
        self,
        user_message_content: Union[list[ContentData], str],
        structured_output: Type[STRUCTURED_OUTPUT_TYPE],
        stream: Literal[False] = False,
        client_id: Optional[str] = None,
        request_id: Optional[str] = None,
        session_id: Optional[str] = None,
        task_id: Optional[str] = None,
        user_id: Optional[str] = None,
        agent_config: Optional[AgentConfig] = None,
        allowed_tools: Optional[list[str]] = None,
        disallowed_tools: Optional[list[str]] = None,
        allowed_subagents: Optional[list[str]] = None,
        stop_tools: Optional[list[str]] = None,
        client_tools: Optional[list[ToolData]] = None,
        history_messages: Optional[list[DialogData]] = None,
        thought_messages: Optional[list[DialogData]] = None,
        inference_args: Optional[dict[str, Any]] = None,
        workspace_dir: Optional[str] = None,
        subagent_prompt_template: Optional[str] = None,
        env: Optional[dict[str, str]] = None,
        log_dir: Optional[str] = None,
        rollout_save_dir: Optional[str] = None,
        return_rollout: bool = False,
        include_compress_model_rollout: bool = False,
        include_subagent_rollout: bool = False
    ) -> Optional[STRUCTURED_OUTPUT_TYPE]: ...

    @overload
    async def __call__(
        self,
        user_message_content: Union[list[ContentData], str],
        structured_output: dict[str, Any],  # output schema as dict
        stream: Literal[False] = False,
        client_id: Optional[str] = None,
        request_id: Optional[str] = None,
        session_id: Optional[str] = None,
        task_id: Optional[str] = None,
        user_id: Optional[str] = None,
        agent_config: Optional[AgentConfig] = None,
        allowed_tools: Optional[list[str]] = None,
        disallowed_tools: Optional[list[str]] = None,
        allowed_subagents: Optional[list[str]] = None,
        stop_tools: Optional[list[str]] = None,
        client_tools: Optional[list[ToolData]] = None,
        history_messages: Optional[list[DialogData]] = None,
        thought_messages: Optional[list[DialogData]] = None,
        inference_args: Optional[dict[str, Any]] = None,
        workspace_dir: Optional[str] = None,
        subagent_prompt_template: Optional[str] = None,
        env: Optional[dict[str, str]] = None,
        log_dir: Optional[str] = None,
        rollout_save_dir: Optional[str] = None,
        return_rollout: bool = False,
        include_compress_model_rollout: bool = False,
        include_subagent_rollout: bool = False
    ) -> Optional[dict[str, Any]]: ...

    @overload
    async def __call__(
        self,
        user_message_content: Union[list[ContentData], str],
        structured_output: None = None,
        stream: Literal[True] = True,
        client_id: Optional[str] = None,
        request_id: Optional[str] = None,
        session_id: Optional[str] = None,
        task_id: Optional[str] = None,
        user_id: Optional[str] = None,
        agent_config: Optional[AgentConfig] = None,
        allowed_tools: Optional[list[str]] = None,
        disallowed_tools: Optional[list[str]] = None,
        allowed_subagents: Optional[list[str]] = None,
        stop_tools: Optional[list[str]] = None,
        client_tools: Optional[list[ToolData]] = None,
        history_messages: Optional[list[DialogData]] = None,
        thought_messages: Optional[list[DialogData]] = None,
        inference_args: Optional[dict[str, Any]] = None,
        workspace_dir: Optional[str] = None,
        subagent_prompt_template: Optional[str] = None,
        env: Optional[dict[str, str]] = None,
        log_dir: Optional[str] = None,
        rollout_save_dir: Optional[str] = None,
        return_rollout: bool = False,
        include_compress_model_rollout: bool = False,
        include_subagent_rollout: bool = False
    ) -> AsyncIterable[TaskStreamingResponse]: ...

    @overload
    async def __call__(
        self,
        user_message_content: Union[list[ContentData], str],
        structured_output: Type[STRUCTURED_OUTPUT_TYPE],
        stream: Literal[True] = True,
        client_id: Optional[str] = None,
        request_id: Optional[str] = None,
        session_id: Optional[str] = None,
        task_id: Optional[str] = None,
        user_id: Optional[str] = None,
        agent_config: Optional[AgentConfig] = None,
        allowed_tools: Optional[list[str]] = None,
        disallowed_tools: Optional[list[str]] = None,
        allowed_subagents: Optional[list[str]] = None,
        stop_tools: Optional[list[str]] = None,
        client_tools: Optional[list[ToolData]] = None,
        history_messages: Optional[list[DialogData]] = None,
        thought_messages: Optional[list[DialogData]] = None,
        inference_args: Optional[dict[str, Any]] = None,
        workspace_dir: Optional[str] = None,
        subagent_prompt_template: Optional[str] = None,
        env: Optional[dict[str, str]] = None,
        log_dir: Optional[str] = None,
        rollout_save_dir: Optional[str] = None,
        return_rollout: bool = False,
        include_compress_model_rollout: bool = False,
        include_subagent_rollout: bool = False
    ): ...

    async def __call__(
        self,
        user_message_content: Union[list[ContentData], str],
        structured_output: Optional[Union[Type[STRUCTURED_OUTPUT_TYPE], dict[str, Any]]] = None,
        stream: bool = False,
        client_id: Optional[str] = None,
        request_id: Optional[str] = None,
        session_id: Optional[str] = None,
        task_id: Optional[str] = None,
        user_id: Optional[str] = None,
        agent_config: Optional[AgentConfig] = None,
        allowed_tools: Optional[list[str]] = None,
        disallowed_tools: Optional[list[str]] = None,
        allowed_subagents: Optional[list[str]] = None,
        stop_tools: Optional[list[str]] = None,
        client_tools: Optional[list[ToolData]] = None,
        history_messages: Optional[list[DialogData]] = None,
        thought_messages: Optional[list[DialogData]] = None,
        inference_args: Optional[dict[str, Any]] = None,
        workspace_dir: Optional[str] = None,
        subagent_prompt_template: Optional[str] = None,
        env: Optional[dict[str, str]] = None,
        log_dir: Optional[str] = None,
        rollout_save_dir: Optional[str] = None,
        return_rollout: bool = False,
        include_compress_model_rollout: bool = False,
        include_subagent_rollout: bool = False
    ):
        """
        向 SessionTaskManager 发送一个任务请求，开始一个会话。
        统一实现：
        stream=True 时，structured_output 必须为 None，返回 AsyncIterable[TaskStreamingResponse]
        stream=False 且 structured_output 为 None 时，返回 TaskResponse
        stream=False 且 structured_output 不为 None 时，返回结构化输出结果：structured_output 类型的实例，或 structured_output dict 指定结构的 dict
        Args:
            user_message_content: 用户消息内容
            client_id: 前端 ID, 可选 AInvest, iWencai 等
            request_id: 跟踪 ID
            session_id: 会话 ID
            task_id: 任务 ID
            user_id: 用户 ID
            agent_config: 主机代理配置
            allowed_tools: 允许的工具列表. None 为允许所有，[] 为不允许任何
            disallowed_tools: 不允许的工具列表. None 和 [] 不进行处理
            allowed_subagents: 允许的子代理列表. None 为允许所有，[] 为不允许任何
            stop_tools: 遇到 stop_tools 时终止. None 和 [] 不进行处理
            client_tools: 客户端工具列表
            inference_args: 推理参数
            workspace_dir: 当前工作目录, 用于 file_system_mcp 和代码解释器
            subagent_prompt_template: 子代理的 prompt template
            env: 环境变量
            structured_output: 结构化输出模型
            log_dir: 日志保存路径
            rollout_save_dir: rollout 保存路径
            return_rollout: 是否返回 rollout 的结果
            include_compress_model_rollout: 是否包含 compress model 的 rollout 结果
            include_subagent_rollout: 是否包含子 agent 的 rollout 结果
        Returns:
            AsyncIterable[TaskStreamingResponse | JSONRPCResponse]: 任务流响应
            TaskResponse | JSONRPCResponse: 任务响应
            结构化输出结果：structured_output 类型的实例，或 structured_output dict 指定结构的 dict
        """
        request_id = request_id if request_id else uuid.uuid4().hex  # 用于将所有复杂的链路串起来，复杂的 api 调用都共享同一个 request_id
        task_id = task_id if task_id else uuid.uuid4().hex  # 作为 task_id，会用于区分 main agent task 和 subagent task 的结果
        session_id = session_id if session_id else uuid.uuid4().hex  # 用于绑定上下文缓存，用在继续交互的场景，同一个会话共享同一个上下文
        user_id = user_id if user_id else uuid.uuid4().hex  # 生命周期长度 user_id >= session_id >= request_id >= task_id
        client_id = client_id if client_id else "AIME"
        history_messages = history_messages if history_messages is not None else []
        thought_messages = thought_messages if thought_messages is not None else []

        req = SessionRequest(
            client_id=client_id,
            user_message_content=user_message_content,
            agent_config=agent_config,
            allowed_tools=allowed_tools,
            disallowed_tools=disallowed_tools,
            allowed_subagents=allowed_subagents,
            stop_tools=stop_tools,
            client_tools=client_tools,
            history_messages=history_messages,
            thought_messages=thought_messages,
            inference_args=inference_args,
            workspace_dir=workspace_dir,
            subagent_prompt_template=subagent_prompt_template,
            env=env,
            structured_output=structured_output,
            log_dir=log_dir,
            rollout_save_dir=rollout_save_dir,
            return_rollout=return_rollout,
            include_compress_model_rollout=include_compress_model_rollout,
            include_subagent_rollout=include_subagent_rollout,
        )
        if stream:
            if structured_output is not None:
                logger.warning("stream=True and structured_output is not None, structured_output will be ignored in streaming mode.")
                raise ValueError("stream=True and structured_output is not None, structured_output will be ignored in streaming mode.")
            request = TaskStreamingRequest(
                id=request_id,
                params=TaskParams(
                    id=task_id,
                    session_id=session_id,
                    user_id=user_id,
                    payload=req,
                ),
            )
            response = await self.on_task_subscribe(request)
        else:
            request = TaskInvokeRequest(
                id=request_id,
                params=TaskParams(
                    id=task_id,
                    session_id=session_id,
                    user_id=user_id,
                    payload=req,
                ),
            )
            response = await self.on_task_invoke(request)
            if structured_output is not None:
                response = get_structured_output(response, structured_output)
        return response

    def get_assistant_content(self, response: TaskResponse) -> Optional[str]:
        task_obj = get_task_object(response)
        if not task_obj:
            return None
        content = get_assistant_content(task_obj)
        return content

    async def on_task_subscribe(self, request: TaskStreamingRequest) -> AsyncIterable[TaskStreamingResponse]:
        task_params: TaskParams = request.params
        request_id = request.id
        task_id = task_params.id
        session_id = task_params.session_id
        user_id = task_params.user_id
        # 参数校验
        req = self._validate_request(request)
        if isinstance(req, JSONRPCError):
            logger.error(f"Error in tool task: {req}")
            return self._stream_error(request_id=request_id, error=req)
        return self._stream_generator(req, request_id, task_id, session_id, user_id)

    async def _stream_generator(
        self,
        req: SessionRequest,
        request_id: str,
        task_id: str,
        session_id: str,
        user_id: str,
    ) -> AsyncIterable[TaskStreamingResponse]:
        # 创建任务
        initial_task = self.create_task_object(
            task_id=task_id,  # task_id 可能是 call_id，这是合理的，用于区分是 main agent 的 delta 还是 subagent 的 delta。
            session_id=session_id,
            user_id=user_id,
            previous_task_id=req.previous_task_id,
        )
        initial_task = await self.upsert_task(initial_task)
        parser = StreamableTaskParser(initial_task)
        seq_counter = SequenceCounter()
        resp = await self.created_streaming_response(request_id=request_id, parser=parser, seq_counter=seq_counter)
        yield resp

        try:

            # 开始分配资源，开始处理任务
            session_state = self.get_session(session_id)
            if session_state:
                if self.debug:
                    logger.debug("recover session_state")
            else:
                # 新的 session，或者新的 agent，都需要重新开一个 session
                session_state = await self.create_session(
                    session_id,
                    user_id,
                    req.client_id,
                    agent_config=req.agent_config,
                    workspace_dir=req.workspace_dir,
                    log_dir=req.log_dir,
                )
                if self.debug:
                    logger.debug("create new session_state")
            env = self.merge_env(session_state, req)

            resp = await self.working_streaming_response(request_id=request_id, parser=parser, seq_counter=seq_counter)
            yield resp

            # 准备工具列表
            task_model_manager = session_state.task_model_manager
            task_tool_manager = session_state.task_tool_manager
            task_code_manager = session_state.task_code_manager
            history_messages = session_state.history_messages
            thought_messages = session_state.thought_messages

            if req.workspace_dir and req.workspace_dir != task_tool_manager.workspace_dir:
                await task_tool_manager.discover_file_system_tools(req.workspace_dir)
                session_state.developer_level_tools = await task_tool_manager.get_tools()

            # 确认 tools 有哪些
            system_level_tools = session_state.agent_config.get_builtin_tools(req.allowed_subagents)  # core builtin tools: CodeInterpreter, Task
            developer_level_tools = session_state.developer_level_tools  # file system tools + mcp tools + session state tools
            client_level_tools = req.client_tools or []

            allowed_tools = req.allowed_tools or session_state.agent_config.allowed_tools or None
            disallowed_tools = req.disallowed_tools or None
            stop_tools = req.stop_tools or []
            for tool in client_level_tools:
                stop_tools.append(tool.get("function", {}).get("name"))
            if req.structured_output is not None:
                # 如果指定了结构化输出，则添加结构化输出工具
                structured_output_tool = GenerateStructuredOutputTool(req.structured_output)
                system_level_tools.append(structured_output_tool.function_tool_schema)
                stop_tools.append(structured_output_tool.name)
                if allowed_tools is not None and structured_output_tool.name not in allowed_tools:
                    allowed_tools.append(structured_output_tool.name)

            total_tools: list[ToolData] = system_level_tools + developer_level_tools + client_level_tools
            total_tool_names = [tool.get("function", {}).get("name") for tool in total_tools]
            tools = copy.deepcopy(total_tools)  # 深拷贝，避免修改原始工具列表
            if isinstance(allowed_tools, list) and len(allowed_tools) == 0:
                tools = []
            if allowed_tools and "*" not in allowed_tools:
                tools = [tool for tool in tools if tool.get("function", {}).get("name") in allowed_tools]
            if disallowed_tools and len(disallowed_tools) > 0:
                tools = [tool for tool in tools if tool.get("function", {}).get("name") not in disallowed_tools]
            tool_names = [tool.get("function", {}).get("name") for tool in tools]
            allowed_name2tool: dict[str, BaseTool] = {}
            for tool in tools:
                tool_name = tool.get("function", {}).get("name")
                tool_obj = task_tool_manager.get_tool(tool_name)
                if tool_obj:
                    allowed_name2tool[tool_name] = tool_obj
                    continue
                if tool_name == GenerateStructuredOutputTool.NAME:
                    allowed_name2tool[tool_name] = GenerateStructuredOutputTool(req.structured_output)
                    continue
            if len(tools) != len(total_tools):
                # 有一些工具被过滤掉了
                logger.warning(f"allowed tools: [{', '.join(tool_names)}]")
                logger.warning(f"disallowed tools: [{', '.join([tool_name for tool_name in total_tool_names if tool_name not in tool_names])}]")
            else:
                logger.info(f"all tools are allowed: [{', '.join(tool_names)}]")
            resp = await self.counting_event_streaming_response(
                request_id=request_id,
                parser=parser,
                seq_counter=seq_counter,
                event=TaskToolsUpdatedEvent(
                    tools=tools,
                ),
            )
            yield resp

            # 确认推理参数
            inference_args = dict()
            inference_args.update(session_state.agent_config.inference_args)
            if req.inference_args:
                inference_args.update(req.inference_args)
            inference_args["tools"] = tools

            # if self.debug:
            #     logger.debug(f"Session {session_id} inference_args: {json.dumps(inference_args, ensure_ascii=False, indent=2)}")

            # 初始化引用管理器
            reference_manager = ReferenceManager()
            # ? 在历史轮的答案里保留引用会影响效果吗？
            # ? 由于模型看到历史轮里的可引用数据和引用编号，导致模型输出的引用[^1]可能实际引用的是历史轮里的数据而不是当前轮的数据，从而产生冲突
            # ? 因此，多轮情况下，如果保留历史轮的引用，那当前轮的引用编号应该从上一轮最后一个引用编号+1 开始
            # ? 但是，这样复杂度会显著上升。而且模型引用历史轮里的数据有点奇怪，尤其是历史轮里的代码执行结果，可能变量已经被覆盖或者内核已经重置，在当前轮中并不存在
            # ? 所以，应该约束引用的使用范围，确保当前轮的引用只包含当前轮的有效数据。历史轮中的引用和引用编号都丢弃，只保留当前轮的引用。
            # ? 后续可引入动态裁剪工具，将没用的工具输出裁剪掉

            current_step = 0
            if len(thought_messages) > 0:
                current_step = sum([1 for m in thought_messages if m["role"] == "assistant"])

            if len(history_messages) == 0:
                system_content = self.build_system_content(session_id, session_state, env=env)
                history_messages.append({"role": "system", "content": system_content})

            if req.history_messages:
                history_messages.extend(req.history_messages)
            if req.thought_messages:
                thought_messages.extend(req.thought_messages)

            if not req.history_messages and not req.thought_messages:
                thought_messages.clear()
            else:
                logger.warning("接收到指定上下文，不清空思考过程，而是基于指定上下文继续思考")

            # 我们把跟用户对话时效性强相关的内容从 role=system 移动到 role=user 中，避免 system content 的缓存失效
            user_message_content = req.user_message_content
            if user_message_content:
                if isinstance(user_message_content, str):
                    user_message_content = [{"type": "text", "text": user_message_content}]
                is_first_turn = len([m for m in history_messages if m["role"] != "system"]) == 0
                new_user_message_content = await self.wrap_user_message_content(
                    user_message_content,
                    allowed_name2tool,
                    is_first_turn,
                    is_compress=False,
                )

                history_messages.append({"role": "user", "content": new_user_message_content})

            while True:
                current_step += 1
                if self.debug:
                    logger.debug(f"历史消息数量: {len(history_messages)}, 当前推理深度: {current_step}")
                # 调用推理引擎获取回复
                # 只有之前轮里的 think 在 history_messages 里需要去掉，而当前轮的 think 在 thought_messages 里需要保留
                messages = remove_citations_in_messages(remove_thoughts_in_messages(history_messages)) + thought_messages
                if self.debug:
                    logger.debug(messages_to_text([m for m in messages if m["role"] != "system"]))

                reasoning_content: str = ""
                tool_calls: list[ToolCallContentData] = []
                answer_content: str = ""
                # 先考虑把 tool_calls 整理出来。整理完可能是空列表。
                # "tool_calls": [
                #     {
                #         "function": {
                #             "arguments": "{}",
                #             "name": "Search"
                #         },
                #         "id": "call_g16uvNKM2r7L36PcHmgbPAAo",
                #         "type": "function"
                #     }
                # ]
                total_tokens = None

                model_request = await self.streaming_request(
                    request_id=request_id,
                    task_id=task_id,
                    session_id=session_id,
                    user_id=user_id,
                    payload=ModelRequest(
                        messages=messages,
                        inference_args=inference_args,
                    ),
                )
                model_task_obj = None
                on_reasoning = False
                stream = await task_model_manager.on_task_subscribe(model_request)
                async for chunk in stream:
                    if chunk.error:
                        resp = await self.fail_streaming_response(
                            request_id=request_id,
                            parser=parser,
                            seq_counter=seq_counter,
                            error=chunk.error,
                        )
                        yield resp
                        return
                    event = chunk.result
                    if isinstance(event, ObjectEvent):
                        model_task_obj = event.task
                        continue
                    # 只允许 reasoning  直接 yield
                    # tool_call_item 和 message_item 要进一步解析才能 yield
                    if isinstance(event, TaskOutputItemAddedEvent):
                        item = event.item
                        if isinstance(item, ReasoningItem):
                            on_reasoning = True
                    elif isinstance(event, TaskOutputItemDoneEvent):
                        item = event.item
                        if isinstance(item, ReasoningItem):
                            on_reasoning = False
                            resp = await self.counting_event_streaming_response(
                                request_id=request_id,
                                parser=parser,
                                seq_counter=seq_counter,
                                event=event,
                            )
                            yield resp
                    if on_reasoning:
                        resp = await self.counting_event_streaming_response(
                            request_id=request_id,
                            parser=parser,
                            seq_counter=seq_counter,
                            event=event,
                        )
                        yield resp
                if not model_task_obj:
                    error_message = "model task object is None"
                    logger.error(error_message)
                    resp = await self.fail_streaming_response(request_id, parser, seq_counter, error_message)
                    yield resp
                    return
                # 处理模型调用结果
                if model_task_obj.usage and model_task_obj.usage.total_tokens:
                    usage = model_task_obj.usage
                    total_tokens = usage.total_tokens
                    # 处理使用情况
                    # 每多调用一次 LLM 都要累加 token 消耗
                    parser.task.usage.add_usage(usage)
                    session_state.usage.add_usage(usage)
                model_output = model_task_obj.output
                for item in model_output:
                    if isinstance(item, MessageItem):
                        answer_content = content_items_to_text(item.content)
                    elif isinstance(item, ToolCallItem):
                        tool_call_data = ToolCallContentData(
                            id=item.call_id,
                            type="function",
                            function={
                                "name": item.name,
                                "arguments": item.arguments,
                            },
                        )
                        tool_calls.append(tool_call_data)
                    elif isinstance(item, ReasoningItem):
                        reasoning_content = content_items_to_text(item.content)

                assistant_message = {"role": "assistant"}
                assistant_content = []
                if reasoning_content:
                    assistant_content.append({"type": "text", "text": reasoning_content})
                if answer_content:
                    assistant_content.append({"type": "text", "text": answer_content})
                assistant_message["content"] = assistant_content
                if tool_calls:
                    assistant_message["tool_calls"] = tool_calls
                if self.debug:
                    logger.debug(f"{messages_to_text([assistant_message])}")
                rollout = {
                    "session_id": session_id,
                    "task_id": parser.task.id,
                    "request_id": request_id,
                    "rollout_id": str(f"rollout_{uuid.uuid4()}"),
                    "input_messages": copy.deepcopy(messages),
                    "output_messages": copy.deepcopy([assistant_message]),
                    "inference_args": copy.deepcopy(inference_args),
                    "request": req.model_dump(exclude={"structured_output"}),
                    "turn": len([m for m in history_messages if m["role"] == "assistant"]),
                    "is_answer": False if tool_calls else True,
                    "step": current_step if tool_calls else None,
                }

                self.save_rollout(session_state, rollout, req.rollout_save_dir)
                if req.return_rollout:
                    event = TaskRolloutEvent(**rollout)
                    resp = await self.counting_event_streaming_response(
                        request_id=request_id,
                        parser=parser,
                        seq_counter=seq_counter,
                        event=event,
                    )
                    yield resp

                if tool_calls:
                    thought_messages.append(assistant_message)
                    # 上下文压缩分 2 个等级
                    # 1.  0% token usage 触发：直接丢弃历史轮次中 reasoning（保留当前轮的 reasoning）
                    # 2. 90% token usage 触发：将当前上下文提交给总结 agent 进行总结，然后清空历史轮和当前轮，用总结后的上下文继续思考
                    if self.debug:
                        logger.debug(f"Token usage: {total_tokens}/{session_state.agent_config.max_model_length} ({total_tokens / session_state.agent_config.max_model_length:.2%})")
                    if total_tokens is None:
                        logger.error("Total tokens is None, cannot check for context compression.")
                    elif total_tokens > session_state.agent_config.compress_threshold_tokens:
                        # 处理超出最大模型长度的情况
                        resp = await self.counting_event_streaming_response(
                            request_id=request_id,
                            parser=parser,
                            seq_counter=seq_counter,
                            event=TaskContextCompressionCreatedEvent(),
                        )
                        yield resp

                        resp = await self.counting_event_streaming_response(
                            request_id=request_id,
                            parser=parser,
                            seq_counter=seq_counter,
                            event=TaskContextCompressionInProgressEvent(),
                        )
                        yield resp
                        # 将当前上下文提交给总结 agent 进行总结
                        compress_prompt = session_state.agent_config.compress_prompt
                        # 只有之前轮里的 think 在 history_messages 里需要去掉，而当前轮的 think 在 thought_messages 里需要保留
                        messages_to_compress = remove_citations_in_messages(remove_thoughts_in_messages(history_messages)) + thought_messages
                        compress_messages = self.build_compress_messages(compress_prompt, messages_to_compress)
                        compress_inference_args = {
                            "model": session_state.agent_config.compress_model,
                            "OPENAI_API_KEY": inference_args.get("OPENAI_API_KEY", None),
                            "OPENAI_BASE_URL": inference_args.get("OPENAI_BASE_URL", None),
                        }
                        payload = {
                            "messages": compress_messages,
                            "inference_args": compress_inference_args,
                        }
                        compress_request = await self.invoke_request(
                            request_id,
                            task_id=f"compress_{uuid.uuid4().hex}",
                            session_id=session_id,
                            user_id=user_id,
                            payload=payload,
                        )
                        compress_response = await task_model_manager.on_task_invoke(compress_request)
                        if compress_response.error:
                            # 压缩出现错误
                            logger.error(f"Compact request failed: {compress_response.error}")
                            resp = await self.fail_streaming_response(request_id, parser, seq_counter, compress_response.error)
                            yield resp
                            return
                        # 正常压缩上下文
                        compressed_result = compress_response.result
                        if not compressed_result:
                            error_message = "compressed result is empty"
                            logger.error(error_message)
                            resp = await self.fail_streaming_response(request_id, parser, seq_counter, error_message)
                            yield resp
                            return
                        # 处理压缩后的结果
                        compressed_completion: ChatCompletion = compressed_result.metadata
                        if compressed_completion.usage:
                            usage = compressed_completion.usage
                            # 处理使用情况
                            # 每多调用一次 LLM 都要累加 token 消耗
                            parser.task.usage.add_completion_usage(usage)
                            session_state.usage.add_completion_usage(usage)
                        compressed_message = compressed_completion.choices[0].message
                        compressed_reasoning_content = ""
                        if hasattr(compressed_message, "reasoning_content"):
                            compressed_reasoning_content = compressed_message.reasoning_content
                        compressed_content = compressed_message.content
                        if not compressed_content:
                            error_message = "compressed content is empty"
                            logger.error(error_message)
                            resp = await self.fail_streaming_response(request_id, parser, seq_counter, error_message)
                            yield resp
                            return
                        # 保存一下模型调用的输入输出
                        rollout = {
                            "session_id": session_id,
                            "task_id": parser.task.id,
                            "request_id": request_id,
                            "rollout_id": str(f"rollout_{uuid.uuid4()}"),
                            "input_messages": copy.deepcopy(compress_messages),
                            "output_messages": [compressed_message.model_dump()],
                            "inference_args": copy.deepcopy(compress_inference_args),
                            "request": req.model_dump(exclude={"structured_output"}),
                            "is_answer": False,
                            "is_compress": True,
                            "turn": len([m for m in history_messages if m["role"] == "assistant"]),
                            "step": current_step,
                        }
                        self.save_rollout(session_state, rollout, req.rollout_save_dir)
                        if req.return_rollout and req.include_compress_model_rollout:
                            resp = await self.counting_event_streaming_response(
                                request_id=request_id,
                                parser=parser,
                                seq_counter=seq_counter,
                                event=TaskRolloutEvent(**rollout),
                            )
                            yield resp
                        # 将当前用户的 query 改为压缩后的上下文
                        # 需要带上变量、文件路径
                        # TODO: 压缩的上下文里的引用[^1]如何处理？
                        compressed_message_content, compressed_block_list = await self.parse_answer(
                            request_id,
                            session_id,
                            compressed_content,
                            task_code_manager,
                            reference_manager,
                        )
                        prefix_content = []
                        prefix_content.append({"type": "text", "text": "This session is being continued from a previous conversation that ran out of context. The conversation is summarized below:"})
                        prefix_content.append({"type": "text", "text": "\nAnalysis:"})
                        prefix_content.append({"type": "text", "text": compressed_reasoning_content})
                        prefix_content.append({"type": "text", "text": "\nSummary:"})

                        # 处理 system-reminder、nlu、current_time 等边缘信息
                        # 第一轮需要带上 memory
                        is_first_turn = len([m for m in history_messages if m["role"] != "system"]) == 0
                        new_user_message_content = await self.wrap_user_message_content(
                            prefix_content + compressed_message_content,
                            allowed_name2tool,
                            is_first_turn,
                            is_compress=True,
                        )
                        new_user_message = {"role": "user", "content": new_user_message_content}

                        # 清空上下文，替换为总结后的上下文
                        if len(history_messages) > 0 and history_messages[-1]["role"] == "user":
                            history_messages.pop(-1)
                        history_messages.append(new_user_message)
                        thought_messages.clear()

                        resp = await self.counting_event_streaming_response(
                            request_id=request_id,
                            parser=parser,
                            seq_counter=seq_counter,
                            event=TaskContextCompressionCompletedEvent(),
                        )
                        yield resp
                        continue

                    # 1. 开始执行
                    call_id_to_request: dict[str, ToolCallItem] = {}
                    call_id_to_output: dict[str, ToolResultItem] = {}
                    should_stop_tool_calls = False
                    for tool_call in tool_calls:
                        call_id, call_name, call_args = parse_function_call_response(tool_call)
                        # 在这里不做参数校验，而是直接创建 tool call created event
                        # 参数校验放到真正执行 tool 的时候做，如果校验出错，则作为工具结果返回
                        if call_name in stop_tools:
                            should_stop_tool_calls = True
                        tool_call_request = ToolCallItem(
                            status=ItemStatus.IN_PROGRESS,
                            call_id=call_id,
                            name=call_name,
                            arguments="",
                            language="json",
                        )
                        tool_call_output = ToolResultItem(
                            status=ItemStatus.IN_PROGRESS,
                            call_id=call_id,
                            output=[],
                            message_content=[],
                            block_list=[],
                        )
                        call_id_to_request[call_id] = tool_call_request
                        call_id_to_output[call_id] = tool_call_output
                        resp = await self.counting_event_streaming_response(
                            request_id=request_id,
                            parser=parser,
                            seq_counter=seq_counter,
                            event=TaskOutputItemAddedEvent(
                                agent_step=current_step,
                                item=tool_call_request,
                            ),
                        )
                        yield resp
                        # TaskToolCallArgumentsDeltaEvent
                        # TaskToolCallArgumentsDeltaEvent
                        # TaskToolCallArgumentsDoneEvent
                        tool_call_request.arguments = call_args
                        tool_call_request.status = ItemStatus.COMPLETED
                        resp = await self.counting_event_streaming_response(
                            request_id=request_id,
                            parser=parser,
                            seq_counter=seq_counter,
                            event=TaskOutputItemDoneEvent(
                                agent_step=current_step,
                                item=tool_call_request,
                            ),
                        )
                        yield resp
                        resp = await self.counting_event_streaming_response(
                            request_id=request_id,
                            parser=parser,
                            seq_counter=seq_counter,
                            event=TaskOutputItemAddedEvent(
                                agent_step=current_step,
                                item=tool_call_output,
                            ),
                        )
                        yield resp

                    # 2. 执行
                    call_response_streams = []  # 冷流。放进去的流只有定义，还未执行
                    call_id_to_task: dict[str, TaskObject] = {}
                    call_id_to_start_time: dict[str, float] = {}
                    call_id_to_end_time: dict[str, float] = {}
                    for call_id, tool_call_request in call_id_to_request.items():
                        # 2.1. 开始处理工具调用
                        call_id_to_start_time[call_id] = time.time()
                        call_name = tool_call_request.name
                        call_args = tool_call_request.arguments
                        # 2.2. 开始校验参数。校验失败则作为工具结果返回。校验失败的工具调用不允许进入 in_progress 状态，而是直接 completed 掉
                        tool_definition = next((tool for tool in total_tools if tool.get("function", {}).get("name") == call_name), None)
                        if not tool_definition:
                            error_message = f"Tool '{call_name}' not found."
                            logger.error(error_message)
                            call_response_stream = self.tool_result_of_internal_error_stream_generator(
                                request_id=request_id,
                                call_id=call_id,
                                session_id=session_id,
                                user_id=user_id,
                                error_message=error_message,
                            )
                            continue

                        validated_call_args = validate_function_call_arguments_str(tool_definition["function"]["parameters"], call_args)
                        if not validated_call_args:
                            # 获取详细的验证错误信息
                            validation_error = get_validation_error_message_str(tool_definition["function"]["parameters"], call_args)
                            error_message = f"Invalid arguments for tool '{call_name}'.\n\nValidation errors:\n{validation_error}\n\nReceived arguments:\n{call_args}"
                            logger.error(error_message)
                            call_response_stream = self.tool_result_of_internal_error_stream_generator(
                                request_id=request_id,
                                call_id=call_id,
                                session_id=session_id,
                                user_id=user_id,
                                error_message=error_message,
                            )
                            continue
                        # 2.3. 参数校验通过，进入调用状态
                        tool_call_request.arguments = json.dumps(validated_call_args, ensure_ascii=False, separators=(",", ":"))
                        # 参数校验成功才允许 stop_tools 生效
                        if call_name in stop_tools:
                            should_stop_tool_calls = True
                            resp = self.input_required_streaming_response(
                                request_id=request_id,
                                parser=parser,
                                seq_counter=seq_counter,
                                input_required=tool_call_request,
                            )
                            yield resp
                            # TODO 这里要终止工具调用
                            break
                        # 2.4. 开始执行工具调用
                        # 不同的工具调用，走不同的逻辑
                        # builtin tools
                        # 由于 structured_output_tool 在 should_stop_tool_calls 里，这里不需要处理 structured_output_tool 的调用
                        if call_name == "Task":
                            # 3. 启动新的代理来处理复杂的多步骤任务
                            subagent_req = ExecuteSubAgentRequest.model_validate(validated_call_args)
                            name = subagent_req.name
                            description = subagent_req.description
                            prompt = subagent_req.prompt
                            subagent = session_state.get_subagent_by_name(name)
                            if subagent is None:
                                error_message = f"Subagent '{name}' not found while calling Task."
                                logger.error(error_message)

                                call_response_stream = self.tool_result_of_internal_error_stream_generator(
                                    request_id=request_id,
                                    call_id=call_id,
                                    session_id=session_id,
                                    user_id=user_id,
                                    error_message=error_message,
                                )
                                continue
                            subagent_config = session_state.agent_config.model_copy()
                            subagent_config.name = subagent.name
                            subagent_config.description = subagent.description
                            if subagent.model:
                                subagent_config.model = subagent.model  # Optional model name
                            subagent_config.developer_prompt = subagent.developer_prompt
                            subagent_config.code_for_agent = subagent.code_for_agent
                            subagent_config.code_for_interpreter = subagent.code_for_interpreter
                            subagent_config.allowed_tools = subagent.allowed_tools
                            disallowed_tools = req.disallowed_tools or []
                            if "Task" not in disallowed_tools:
                                disallowed_tools.append("Task")  # 子代理不允许调用 Task 工具
                            if "Task" in subagent.allowed_tools:
                                subagent.allowed_tools.remove("Task")  # 从子代理允许的工具中移除 Task

                            subagent_user_prompt = prompt
                            if req.subagent_prompt_template:
                                subagent_user_prompt = req.subagent_prompt_template.replace("{{prompt}}", prompt)

                            task_req = SessionRequest(
                                client_id=req.client_id,
                                user_message_content=[{"type": "text", "text": subagent_user_prompt}],
                                agent_config=subagent_config,
                                allowed_tools=subagent.allowed_tools,  # 子代理允许的工具
                                disallowed_tools=disallowed_tools,  # 子代理不允许的工具
                                allowed_subagents=[],  # 子代理不允许其他子代理
                                stop_tools=[],  # 子代理不需要停止工具
                                client_tools=[],  # 子代理不需要客户端工具
                                history_messages=[],  # 子代理不需要历史消息
                                thought_messages=[],  # 子代理不需要思考过程
                                previous_task_id=None,  # 子代理不需要前置 Response
                                workspace_dir=req.workspace_dir,  # 子代理需要当前工作目录
                                subagent_prompt_template=None,  # 子代理不需要子代理的 prompt template
                                env=env,  # 子代理需要环境变量
                                inference_args=None,  # 子代理不需要额外指定推理参数
                                structured_output=None,  # 子代理不需要结构化输出
                                log_dir=req.log_dir,
                                rollout_save_dir=req.rollout_save_dir,
                                return_rollout=req.return_rollout,
                            )
                            subagent_session_id = f"{session_id}_{name}_{uuid.uuid4().hex}"
                            task_request = TaskStreamingRequest(
                                id=request_id,
                                params=TaskParams(
                                    id=call_id,
                                    session_id=subagent_session_id,  # 子代理使用全新的会话 ID，和当前会话隔离
                                    user_id=user_id,
                                    payload=task_req,
                                ),
                            )
                            call_response_stream = await self.on_task_subscribe(task_request)
                        elif call_name == "Skill":
                            skill_name = validated_call_args.get("skill_name", "")
                            call_response_stream = self._load_skill_stream_generator(
                                state=session_state,
                                skill_name=skill_name,
                                session_id=session_id,
                                request_id=request_id,
                                task_id=call_id,
                                user_id=user_id,
                                env=env,
                                log_dir=req.log_dir,
                            )
                        elif call_name == "CodeInterpreter":
                            code = validated_call_args.get("code", "")
                            kernel_id = await self.lazy_init_kernel(request_id, session_state, task_code_manager, env)

                            # 3. 执行代码
                            code_req = ExecuteCodeRequest(
                                kernel_id=kernel_id,
                                code=code,
                                mode="full",
                                msg_id=call_id,
                            )
                            code_request = TaskStreamingRequest(
                                id=request_id,
                                params=TaskParams(
                                    id=call_id,
                                    session_id=session_id,
                                    user_id=user_id,
                                    payload=code_req,
                                ),
                            )
                            call_response_stream = await task_code_manager.on_task_subscribe(code_request)
                        else:
                            # 3. 执行工具调用
                            tool_req = CallToolRequest(
                                call_name=call_name,
                                call_args=validated_call_args,
                            )
                            tool_request = TaskInvokeRequest(
                                id=request_id,
                                params=TaskParams(
                                    id=call_id,
                                    session_id=session_id,
                                    user_id=user_id,
                                    payload=tool_req,
                                ),
                            )
                            call_response_stream = await task_tool_manager.on_task_subscribe(tool_request)
                        call_response_streams.append(call_response_stream)

                    if should_stop_tool_calls:
                        # 如果遇到 stop_tools，则终止当前会话
                        logger.info(f"Session {session_id} is stopped at tool_call: {stop_tools}")
                        if len(call_response_streams) > 0:
                            logger.warning(f"Session {session_id} has {len(call_response_streams)} tool calls running, but will be stopped.")
                        # 停止时 tool_call 进入 in_progress 状态，但是 status 变为 incomplete
                        # 用户拿到 ResponseToolCallInProgress 自行校验参数
                        # 使用 break，使得 completion response 正常工作
                        break

                    # 4. 处理执行结果
                    call_done = {}
                    async for call_response in merge_streams(*call_response_streams):  # 冷流变“热“：开始正式执行。merge 表示多个流的异步并行合并
                        # if self.debug:
                        #     logger.debug(call_response)
                        # 2. 处理结果，合并到 main agent 的流里
                        yield call_response
                        event = call_response.result
                        if call_response.error:
                            error_message = f"Tool call error: {call_response.error}"
                            logger.error(error_message)
                            if event:
                                if isinstance(event, TaskEvent) and isinstance(event, ObjectEvent):
                                    call_id = event.task_id
                                    call_id_to_task[call_id] = event.task
                                    call_done[call_id] = event.task.is_final()
                            continue
                        call_id = event.task_id
                        # 子 agent 里调用工具时，可能会出现 call_id 不在 call_id_to_request 里的情况
                        if call_id in call_id_to_request:
                            tool_call_request = call_id_to_request[call_id]
                            call_id_to_end_time[call_id] = time.time()
                            if isinstance(event, ObjectEvent):
                                call_id_to_task[call_id] = event.task
                                call_done[call_id] = event.task.is_final()
                        else:
                            # call_id 不在 call_id_to_request 里，说明这是子 agent 里调用工具的结果
                            pass

                        if isinstance(event, TaskRolloutEvent):
                            # logger.debug(f"Received rollout event from tool call ({call_id}): {event}")
                            if req.include_subagent_rollout:
                                self.save_rollout(session_state, event.model_dump(), req.rollout_save_dir)
                                if req.return_rollout:
                                    resp = await self.counting_event_streaming_response(
                                        request_id=request_id,
                                        parser=parser,
                                        seq_counter=seq_counter,
                                        event=event,
                                    )
                                    yield resp

                    # 5. 记录工具调用结果到上下文
                    for call_id, tool_call_task in call_id_to_task.items():
                        # 对状态流协议的设计，我们可以保证每个 call_id 都能收集到 tool_call_task，因此不会遗漏某个工具的输出
                        # 5.1. 工具调用完成
                        tool_call_request = call_id_to_request[call_id]  # for reading
                        tool_call_output = call_id_to_output[call_id]  # for writing. 下面处理工具的输出后写入到 tool_call_output
                        if call_id not in call_done:
                            # 说明工具调用没有正常结束
                            logger.warning(f"Tool call ({call_id}) did not complete normally.")
                            tool_call_request.status = ItemStatus.INCOMPLETE
                        else:
                            tool_call_request.status = ItemStatus.COMPLETED

                        # 5.2. 记录工具调用的使用情况
                        start_time, end_time = call_id_to_start_time.get(call_id), call_id_to_end_time.get(call_id)
                        duration = end_time - start_time if start_time and end_time else None
                        parser.task.usage.add_tool_call(call_id, tool_call_request.name, tool_call_request.arguments, time=duration)
                        session_state.usage.add_tool_call(call_id, tool_call_request.name, tool_call_request.arguments, time=duration)

                        # 5.3. 记录 rollout
                        # if tool_call_task.rollouts:
                        #     for rollout_event in tool_call_task.rollouts:
                        #         self.save_rollout(session_state, rollout_event.model_dump(), req.rollout_save_dir)
                        #         resp = await self.counting_event_streaming_response(
                        #             request_id=request_id,
                        #             task_id=task_id,
                        #             parser=parser,
                        #             seq_counter=seq_counter,
                        #             event=rollout_event,
                        #         )
                        #         # WARNING: 在 4. 处理执行结果 里已经 yield 过一次了
                        #         if req.return_rollout:
                        #             yield resp

                        # 5.4. 处理引用池
                        # 有两种情况：
                        # 1. tool_call == subagent calling
                        # 2. tool_call == function calling
                        # 通过 tool_call_request.name 来判断是哪种情况
                        if tool_call_request.name == "Task":
                            # 1. subagent calling
                            # TODO 子智能体完成，需要立刻销毁 子智能体的 jupyter kernel
                            if not tool_call_task.output or not isinstance(tool_call_task.output[-1], MessageItem):
                                # 无法获得可解析的 MessageItem 时，需要考虑推理出 output。
                                # 比如，考虑如果发生 error，自动将 error 作为 output
                                if tool_call_task.error:
                                    tool_call_task.output = (tool_call_task.output or []) + [
                                        MessageItem(
                                            call_id=call_id,
                                            status=ItemStatus.INCOMPLETE,
                                            content=[],
                                            message_content=[{"type": "text", "text": f"The tool {tool_call_request.name} failed. Error: {tool_call_task.error.message}."}],
                                            block_list=[],
                                        )
                                    ]
                                else:
                                    # 没有 output 也没有 error，说明子 agent 链接断开或其他情况，总之就是没有正常结束
                                    tool_call_task.output = (tool_call_task.output or []) + [
                                        MessageItem(
                                            call_id=call_id,
                                            status=ItemStatus.INCOMPLETE,
                                            content=[],
                                            message_content=[{"type": "text", "text": f"The tool {tool_call_request.name} failed and returned no content."}],
                                            block_list=[],
                                        )
                                    ]
                            item = tool_call_task.output[-1]
                            assert isinstance(item, MessageItem), tool_call_task
                            # 以下正式开始将子 agent 的输出合并进主 agent 的 messages 里，需要考虑子 agent 回答里的引用和变量
                            # 1. 获取子 agent 的引用项，number to tool_result
                            # 2. 获取子 agent 的最后一个 message item 里的引用，过滤出被引用到的 tool_result
                            # 3. 将被引用到的 tool_result 加入主 agent 的引用池，替换 message_content 和 block_list 里的引用编号为在主 agent 引用池中的编号
                            # 4. 替换 message item 里的引用 [^1] 为主 agent 引用池中的编号
                            # 5. 生成 tool_result

                            # 正式开始！
                            # 1. 获取子 agent 的引用项，number to tool_result
                            subagent_output = tool_call_task.output
                            subagent_tool_result = ToolResult(
                                message_content=[],
                                block_list=[],
                            )
                            for item_i in subagent_output:
                                # 可引用的资源一定在 FunctionCallOutputItem 里
                                if isinstance(item_i, ToolResultItem):
                                    subagent_tool_result.extend_message_content(item_i.message_content)
                                    subagent_tool_result.extend_block_list(item_i.block_list)
                            ref_id_to_tool_result = group_by_ref_id(subagent_tool_result.message_content, subagent_tool_result.block_list)

                            # 2. 获取子 agent 的最后一个 message item 里的引用，过滤出被引用到的 tool_result
                            texts = []
                            for c in item.message_content:
                                if c.get("type") == "text":
                                    texts.append(c.get("text", ""))
                            full_text = "\n".join(texts)
                            citations = extract_citations(full_text)
                            cited_tool_result = ToolResult(
                                message_content=[],
                                block_list=[],
                            )
                            for number in citations:
                                # number 可能是 str 也可能是 int
                                tool_result = ref_id_to_tool_result.get(number)
                                if tool_result:
                                    cited_tool_result.extend_result(ToolResult.from_dict(tool_result))
                                    continue
                                if str.isdigit(number):
                                    number_int = int(number)
                                    tool_result = ref_id_to_tool_result.get(number_int)
                                    if tool_result:
                                        cited_tool_result.extend_result(ToolResult.from_dict(tool_result))

                            # 3. 将被引用到的 tool_result 加入主 agent 的引用池，替换 message_content 和 block_list 里的引用编号为在主 agent 引用池中的编号
                            new_cited_tool_result, citations_old2new = reference_manager.process_tool_result(cited_tool_result)

                            # 4. 替换 message item 里的引用 [^1] 为主 agent 引用池中的编号
                            subagent_answer_content = copy.deepcopy(item.content)
                            subagent_answer_message_content = copy.deepcopy(item.message_content) or []
                            subagent_answer_block_list = copy.deepcopy(item.block_list) or []
                            subagent_answer_message_content = replace_citations_in_message_content(subagent_answer_message_content, citations_old2new)
                            subagent_answer_block_list = replace_citations_in_message_content(subagent_answer_block_list, citations_old2new)
                            if isinstance(subagent_answer_content, str):
                                subagent_answer_content = replace_citations(subagent_answer_content, citations_old2new)
                            else:
                                for c in subagent_answer_content:
                                    if isinstance(c, TextContentItem):
                                        c.text = replace_citations(c.text, citations_old2new)

                            # 5. 生成 tool_result
                            # 将被引用数据添加到真正的 subagent 回答前
                            tool_result = ToolResult(
                                message_content=[],
                                block_list=[],
                            )
                            tool_result.extend_result(new_cited_tool_result)
                            tool_result.extend_message_content(subagent_answer_message_content)
                            tool_result.extend_block_list(subagent_answer_block_list)

                            tool_call_output.output = subagent_answer_content
                            tool_call_output.message_content = tool_result.message_content
                            tool_call_output.block_list = tool_result.block_list
                        else:
                            # 2. function calling
                            if not tool_call_task.output:
                                # 仅在没有输出时才处理 error，自动将 error 作为 output
                                if tool_call_task.error:
                                    tool_call_task.output = [
                                        ToolResultItem(
                                            call_id=call_id,
                                            output=[],
                                            message_content=[{"type": "text", "text": f"The tool {tool_call_request.name} failed. Error: {tool_call_task.error.message}."}],
                                            block_list=[],
                                        )
                                    ]
                                else:
                                    tool_call_task.output = [
                                        ToolResultItem(
                                            call_id=call_id,
                                            output=[],
                                            message_content=[{"type": "text", "text": f"The tool {tool_call_request.name} executed successfully but returned no content."}],
                                            block_list=[],
                                        )
                                    ]
                            item = tool_call_task.output[-1]
                            if isinstance(item, ToolResultItem):
                                delta_message_content = item.message_content
                                delta_block_list = item.block_list
                                # 处理引用
                                tool_result = ToolResult(
                                    message_content=delta_message_content,
                                    block_list=delta_block_list,
                                )
                            else:
                                tool_result = ToolResult(
                                    message_content=[{"type": "text", "text": f"The tool {tool_call_request.name} does not return ToolResultItem."}],
                                    block_list=[],
                                )
                            tool_result, _ = reference_manager.process_tool_result(tool_result)
                            if not tool_result.message_content:
                                # 这是内部处理，不要放到 block_list 里
                                tool_result.message_content = [{"type": "text", "text": f"The tool {tool_call_request.name} executed successfully but returned no content."}]
                            tool_call_output.output = item.output
                            tool_call_output.message_content = tool_result.message_content
                            tool_call_output.block_list = tool_result.block_list

                        resp = await self.counting_event_streaming_response(
                            request_id=request_id,
                            parser=parser,
                            seq_counter=seq_counter,
                            event=TaskOutputItemDoneEvent(
                                agent_step=current_step,
                                item=tool_call_output,
                            ),
                        )
                        yield resp

                        # 兼容一下 OpenAI 的 tool result 只能是 text 的情况
                        # 这里的处理和给外部的 event 不一样，这是故意的，我们要暴露一个标准的 event 范式，隐藏非标准的内部处理
                        # 如果需要获取非标准的处理，可以查看 rollouts 里的数据
                        # logger.info(content_to_text(tool_call_output.message_content))
                        is_all_text = is_text_content(tool_call_output.message_content)
                        if is_all_text:
                            thought_messages.append({"role": "tool", "content": tool_call_output.message_content, "tool_call_id": call_id})
                        else:
                            thought_messages.append({"role": "tool", "content": [{"type": "text", "text": f"The execution results of {tool_call_request.name} will be provided by the user as following:"}], "tool_call_id": call_id})

                            suffix_content = [{"type": "text", "text": f"The execution results of {tool_call_request.name} are provided as above."}]
                            if GenerateStructuredOutputTool.NAME in allowed_name2tool:
                                # 如果允许结构化输出，则添加结构化输出的提示
                                structured_output_tool: GenerateStructuredOutputTool = allowed_name2tool[GenerateStructuredOutputTool.NAME]
                                suffix_content.append({"type": "text", "text": f"<system-reminder>\nThe user would like to receive structured output. So you MUST finally use `{GenerateStructuredOutputTool.NAME}` to finish your task.\n</system-reminder>"})
                            thought_messages.append({"role": "user", "content": tool_call_output.message_content + suffix_content})
                else:
                    # 没有调工具就是回答了
                    # 解析变量并注入回答内容
                    answer_message_content, answer_block_list = await self.parse_answer(
                        request_id,
                        session_id,
                        answer_content,
                        task_code_manager,
                        reference_manager,
                    )

                    item = MessageItem(
                        role="assistant",
                        content="",
                        call_id=task_id,
                        agent_id=session_state.agent_config.agent_id,
                        name=session_state.agent_config.name,
                    )
                    resp = await self.counting_event_streaming_response(
                        request_id=request_id,
                        parser=parser,
                        seq_counter=seq_counter,
                        event=TaskOutputItemAddedEvent(
                            agent_step=current_step,
                            item=item,
                        ),
                    )
                    yield resp
                    item.content = answer_content
                    item.message_content = answer_message_content
                    item.block_list = answer_block_list
                    resp = await self.counting_event_streaming_response(
                        request_id=request_id,
                        parser=parser,
                        seq_counter=seq_counter,
                        event=TaskOutputItemDoneEvent(
                            agent_step=current_step,
                            item=item,
                        ),
                    )
                    yield resp

                    # 思维记忆：保留 thought messages 在 history messages 中
                    history_messages.extend(thought_messages)
                    thought_messages.clear()
                    history_messages.append(assistant_message)
                    break

            resp = await self.complete_streaming_response(request_id=request_id, parser=parser, seq_counter=seq_counter)
            yield resp
        except Exception as e:
            logger.error(f"Error: {e}\n{traceback.format_exc()}")
            resp = await self.fail_streaming_response(request_id=request_id, parser=parser, seq_counter=seq_counter, error=str(e))
            yield resp
            return

    async def _load_skill_stream_generator(
        self,
        state: SessionState,
        skill_name: str,  # 技能名称
        session_id: str,
        request_id: str,
        task_id: str,
        user_id: str,
        env: dict[str, Any],  # 环境变量
        log_dir: Optional[str] = None,
    ) -> AsyncIterable[TaskStreamingResponse]:
        # 初始化日志记录
        logger_id = f"{state.main_agent_id}/task_skill_manager"
        LOG_DIR = log_dir or os.getenv("LOG_DIR", "output/logs")
        logger = create_logger(os.path.join(LOG_DIR, "agents"), logger_id)

        initial_task = self.create_task_object(
            task_id=task_id,
            session_id=session_id,
            user_id=user_id,
        )
        initial_task = await self.upsert_task(initial_task)
        parser = StreamableTaskParser(initial_task)
        seq_counter = SequenceCounter()
        resp = await self.created_streaming_response(request_id=request_id, parser=parser, seq_counter=seq_counter)
        yield resp

        # 准备资源
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

        builtin_skills = {skill.name: skill for skill in state.agent_config.builtin_skills}
        if skill_name not in builtin_skills:
            error_message = f"Skill {skill_name} not found"
            logger.error(error_message)
            resp = await self.fail_streaming_response(request_id=request_id, parser=parser, seq_counter=seq_counter, error=error_message)
            yield resp
            return

        skill = builtin_skills[skill_name]
        prompt, _, code_for_interpreter = apply_env(
            env=env or {},
            prompt=skill.prompt,
            code_for_agent=skill.code_for_agent,
            code_for_interpreter=skill.code_for_interpreter,
        )
        code_result = await self.load_code(request_id, session_id, code_for_interpreter, state.task_code_manager, env=env)
        tool_result = ToolResult()
        if code_result:
            message_content=[
                {"type": "text", "text": f"<system-reminder>Loaded skill_name='{skill_name}'</system-reminder>"},
                {"type": "text", "text": prompt},
            ]
            if code_result.message_content:
                message_content.append({"type": "text", "text": "<executed-result>"})
                message_content.extend(code_result.message_content)
                message_content.append({"type": "text", "text": "</executed-result>"})
            tool_result.message_content.extend(message_content)

            block_list=[
                {"type": "text", "text": f"Loaded Skill '{skill_name}'"},
            ]
            tool_result.block_list.extend(block_list)
        else:
            error_message = f"Failed to load skill skill_name='{skill_name}': Failed to load code that required by skill."
            logger.error(error_message)
            tool_result.message_content = [{"type": "text", "text": f"<system-reminder>{error_message}</system-reminder>"}]

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
        output_item.output = content_datas_to_content_items(tool_result.message_content)
        resp = await self.counting_event_streaming_response(
            request_id=request_id,
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

    def save_rollout(self, state: SessionState, rollout: dict, rollout_save_dir: Optional[str] = None):
        if not rollout_save_dir:
            log_dir = os.getenv("LOG_DIR", "output/logs")
            agent_id = state.main_agent_id
            date_str = datetime.datetime.now().strftime("%Y%m%d")
            save_dir = Path(log_dir) / "agents" / agent_id / "rollout" / date_str
            save_dir.mkdir(parents=True, exist_ok=True)
            rollout_save_dir = save_dir
        else:
            rollout_save_dir: Path = Path(rollout_save_dir)
            if not rollout_save_dir.exists():
                rollout_save_dir.mkdir(parents=True, exist_ok=True)
                logger.success(f"Rollout save directory created at {rollout_save_dir}")

        session_id = state.session_id
        messages_filepath = rollout_save_dir / f"{session_id}.rollout.jsonl"
        append_to_json_list([rollout], messages_filepath)
        logger.success(f"Rollout saved to {messages_filepath}")

    def build_compress_messages(self, compress_prompt: str, messages: list[DialogData]):
        system_message = {"role": "system", "content": [{"type": "text", "text": "You are a helpful AI assistant tasked with summarizing conversations."}]}
        compress_messages = [msg for msg in messages if msg["role"] not in ["system", "developer"]]  # = history_messages + thought_messages
        user_message = {"role": "user", "content": [{"type": "text", "text": compress_prompt}]}
        # 如果现在正在尝试进行工具调用，则打断工具调用，转为压缩总结
        last_message = compress_messages[-1] if len(compress_messages) > 0 else None
        if last_message and last_message["role"] == "assistant" and "tool_calls" in last_message:
            interrupt_output = """The user doesn't want to proceed with this tool use. \
The tool use was rejected (eg. if it was a file edit, the new_string was NOT written to the file). \
STOP what you are doing and wait for the user to tell you how to proceed.

[Request interrupted by user for tool use]\
"""
            tool_calls = last_message["tool_calls"]
            for tool_call in tool_calls:
                call_id = tool_call["id"]
                compress_messages.append({"role": "tool", "content": [{"type": "text", "text": interrupt_output}], "tool_call_id": call_id})
        compress_messages = [system_message] + compress_messages + [user_message]
        return compress_messages

    async def wrap_user_message_content(
        self,
        message_content: list[ContentData],
        allowed_name2tool: dict[str, BaseTool],
        is_first_turn: bool,
        is_compress: bool = False,
    ) -> list[ContentData]:
        """Wrap user message content with additional context: memory, todo list, system reminders.

        Args:
            message_content (list[ContentData]): The main content of the user message.
            block_list (list[BlockData]): The list of blocks associated with the message.
            allowed_name2tool (dict[str, ToolData]): The mapping of allowed tool names to their data.
            is_first_turn (bool): Whether this is the first turn of the conversation.
            is_compress (bool, optional): The user message content is just compressed.

        Returns:
            list[ContentData]: The new message content with additional context.
        """
        prefix_content = []
        suffix_content = []
        if is_first_turn:
            # 第一轮
            if MemoryTool.NAME in allowed_name2tool:
                memory_tool: MemoryTool = allowed_name2tool[MemoryTool.NAME]
                memory_tool.provide_system_reminder(prefix_content, suffix_content)

            if TodoWriteTool.NAME in allowed_name2tool:
                todo_write_tool: TodoWriteTool = allowed_name2tool[TodoWriteTool.NAME]
                todo_write_tool.provide_system_reminder(prefix_content, suffix_content)
        if GenerateStructuredOutputTool.NAME in allowed_name2tool:
            suffix_content.append({"type": "text", "text": f"<system-reminder>\nThe user would like to receive structured output. So you MUST finally use `{GenerateStructuredOutputTool.NAME}` to finish your task.\n</system-reminder>"})
        if len(prefix_content) > 0:
            prefix_content.append({"type": "text", "text": f"User Query:\n\n"})

        # if suffix_content:
        #     query = content_to_text(user_message_content)
        #     nlu = self.query_nlu(query)
        #     current_time = datetime.datetime.now()
        #     current_time_str = format_datetime_with_holiday(current_time, language=language)

        #     system_reminders = []
        #     system_reminders.append(f"Current time: {current_time_str}")
        #     if task_tool_manager.workspace_dir:
        #         system_reminders.append(f"Current directory: {task_tool_manager.workspace_dir}")
        #     if nlu:
        #         system_reminders.append(f"NLU: {nlu}")
        #     if system_reminders:
        #         suffix_content.append({"type": "text", "text": f"<system-reminder>\n{'\n'.join(system_reminders)}\n</system-reminder>"})
        new_message_content = prefix_content + message_content + suffix_content
        return new_message_content

    async def parse_answer(
        self,
        request_id: str,
        session_id: str,
        answer: str,
        task_code_manager: TaskCodeManager,
        reference_manager: ReferenceManager,
    ):
        # 处理 apply
        message_content: list[ContentData] = []
        block_list: list[BlockData] = []
        text_blocks = parse_text_with_apply(answer)
        for text_block in text_blocks:
            if text_block["type"] == "text":
                message_content.append(text_block)
                block_list.append(text_block)
            elif text_block["type"] == "apply":
                code = text_block["text"]
                code_result = await self.extract_variable(request_id, session_id, code, task_code_manager)
                if not code_result:
                    # apply 代码块执行失败
                    logger.warning("Code execution failed")
                    continue
                prefix_message_content = [
                    {"type": "text", "text": "<executed-code>"},
                    {"type": "text", "text": code},
                    {"type": "text", "text": "</executed-code>"},
                    {"type": "text", "text": "<code-result>"},
                ]
                suffix_message_content = [
                    {"type": "text", "text": "</code-result>"},
                ]
                tool_result = ToolResult.from_dict(code_result)
                tool_result, _ = reference_manager.process_tool_result(tool_result)
                code_message_content = tool_result.message_content
                code_block_list = tool_result.block_list
                full_message_content = prefix_message_content + code_message_content + suffix_message_content
                full_block_list = prefix_message_content + code_block_list + suffix_message_content
                message_content.extend(full_message_content)
                block_list.extend(full_block_list)
        return message_content, block_list

    def _validate_request(self, request: Union[TaskInvokeRequest, TaskStreamingRequest]):
        task_params: TaskParams = request.params
        try:
            if isinstance(task_params.payload, SessionRequest):
                req: SessionRequest = task_params.payload
            else:
                req: SessionRequest = SessionRequest.model_validate(task_params.payload)
        except Exception as e:
            logger.error(f"Invalid request payload: {e}")
            return InvalidParamsError(message=str(e))
        return req

    async def on_get_task(self, request):
        return await super().on_get_task(request)

    async def on_cancel_task(self, request):
        return await super().on_cancel_task(request)

    async def on_get_task_push_notification(self, request):
        return await super().on_get_task_push_notification(request)

    async def on_resubscribe_to_task(self, request):
        return await super().on_resubscribe_to_task(request)

    async def on_set_task_push_notification(self, request):
        return await super().on_set_task_push_notification(request)
