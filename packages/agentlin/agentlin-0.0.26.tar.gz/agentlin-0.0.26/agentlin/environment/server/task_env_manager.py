import asyncio
import uuid
import json
import traceback
from typing import Any, AsyncIterable, Optional, Union, TypedDict, Dict
from loguru import logger
from pydantic import BaseModel, Field

from agentlin.core.types import (
    JSONRPCError,
    TaskInvokeRequest,
    TaskStreamingRequest,
    TaskResponse,
    TaskStreamingResponse,
    TaskParams,
    BaseTool,
    ToolData,
    ToolResultItem,
    TaskOutputItemAddedEvent,
    TaskOutputItemDoneEvent,
    TaskToolResultDeltaEvent,
    TaskToolResultDoneEvent,
)
from agentlin.route.task_manager import InMemoryTaskManager
from agentlin.store.task_store import InMemoryTaskStore
from agentlin.environment.interface import IToolEnvironment, IEnvironment, IState
from agentlin.environment.core import load_environment
from agentlin.code_interpreter.types import ToolResponse
from agentlin.tools.core import tool_response_of_internal_error


# ==================== 动作类型定义 ====================

class ActionDict(TypedDict, total=False):
    """工具调用动作格式"""
    tool_name: str
    name: str  # tool_name 的别名
    tool_args: dict[str, Any]
    arguments: dict[str, Any]  # tool_args 的别名


# 动作可以是工具调用字典或其他自定义类型
Action = Union[ActionDict, dict[str, Any], str, int, float, list, None]


class EnvSessionState(BaseModel):
    """环境会话状态"""
    session_id: str
    user_id: str
    client_id: str
    env_id: str  # 环境 ID

    # 环境配置
    env_vars: dict[str, str] = Field(default_factory=dict)
    env_class_path: Optional[str] = None  # 环境类路径，如 "arc-agi-3" 或 "module:Class"
    env_init_kwargs: dict[str, Any] = Field(default_factory=dict)  # 环境初始化参数

    # 环境状态
    is_active: bool = True
    created_at: float = Field(default_factory=lambda: asyncio.get_event_loop().time())
    last_accessed_at: float = Field(default_factory=lambda: asyncio.get_event_loop().time())

    # 运行时属性（不参与序列化）
    model_config = {"arbitrary_types_allowed": True, "extra": "allow"}

    def __init__(self, **data):
        # 提取运行时属性
        env_instance = data.pop("env_instance", None)
        current_state = data.pop("current_state", None)

        super().__init__(**data)

        # 设置运行时属性
        self.env_instance: Optional[IEnvironment] = env_instance
        self.current_state: Optional[IState] = current_state

    async def init(self):
        """初始化环境"""
        logger.info(f"Initializing environment session {self.session_id}")

        # 如果提供了环境类路径，加载环境实例
        if self.env_class_path and not self.env_instance:
            try:
                self.env_instance = load_environment(self.env_class_path, **self.env_init_kwargs)
                self.current_state = self.env_instance.provide_initial_state()
                logger.info(f"Loaded environment: {self.env_class_path}")
            except Exception as e:
                logger.error(f"Failed to load environment {self.env_class_path}: {e}")
                raise

    async def start(self):
        """启动环境"""
        logger.info(f"Starting environment session {self.session_id}")
        self.is_active = True
        # 在这里可以启动环境相关的后台任务
        pass

    def stop(self):
        """停止环境"""
        logger.info(f"Stopping environment session {self.session_id}")
        self.is_active = False
        # 在这里可以清理环境资源
        pass

    def update_last_accessed(self):
        """更新最后访问时间"""
        self.last_accessed_at = asyncio.get_event_loop().time()

    def get_tools(self) -> list[ToolData]:
        """获取当前状态可用的工具列表"""
        if not self.env_instance or not self.current_state:
            return []

        if isinstance(self.env_instance, IToolEnvironment):
            return self.env_instance.list_tools(self.current_state)
        return []

    def get_tool_by_name(self, tool_name: str) -> Optional[BaseTool]:
        """根据名称获取工具"""
        if not self.env_instance or not self.current_state:
            return None

        if isinstance(self.env_instance, IToolEnvironment):
            name2tool = self.env_instance.list_available_name2tool(self.current_state)
            return name2tool.get(tool_name)
        return None


class EnvSessionRequest(BaseModel):
    """环境会话请求 - 用于工具调用"""
    client_id: str
    env_id: Optional[str] = None
    env_vars: Optional[dict[str, str]] = None

    # 工具调用参数
    tool_name: str
    tool_args: dict[str, Any] = Field(default_factory=dict)


# ==================== 响应类型定义 ====================

class SessionInfoResponse(BaseModel):
    """会话信息响应"""
    session_id: str
    env_id: str
    env_vars: dict[str, str] = Field(default_factory=dict)
    is_active: bool
    created_at: float
    last_accessed_at: float


class StatusResponse(BaseModel):
    """状态响应"""
    status: str
    message: str


class StepResponse(BaseModel):
    """步骤响应（强化学习风格）"""
    observation: ToolResponse  # 使用 ToolResponse 作为观察类型
    reward: float = 0.0
    done: bool = False
    info: dict[str, Any] = Field(default_factory=dict)
    truncated: bool = False


class ObservationResponse(BaseModel):
    """观察响应"""
    observation: dict[str, Any]  # 使用 Dict 避免严格的 Pydantic 验证
    tools: list[ToolData] = Field(default_factory=list)  # 可用工具列表
    done: bool = False  # 环境是否已结束


class ToolsResponse(BaseModel):
    """工具列表响应"""
    tools: list[ToolData]  # 使用 ToolData 类型
    count: int


class ToolCallResponse(BaseModel):
    """工具调用响应"""
    observation: ToolResponse  # 使用 ToolResponse 作为观察类型
    tool_name: str
    tool_args: dict[str, Any] = Field(default_factory=dict)


class ExecuteResponse(BaseModel):
    """执行响应"""
    status: str
    message: str
    payload: dict[str, Any] = Field(default_factory=dict)


class TaskEnvManager(InMemoryTaskManager):
    """任务环境管理器

    负责管理环境会话，包括创建、获取、删除等操作。
    每个会话对应一个独立的环境实例。
    """

    def __init__(
        self,
        debug: bool = False,
        task_store: Optional[InMemoryTaskStore] = None,
        session_timeout: float = 3600.0,  # 会话超时时间（秒），默认1小时
    ):
        """初始化任务环境管理器

        Args:
            debug: 是否启用调试模式
            task_store: 任务存储
            session_timeout: 会话超时时间（秒）
        """
        super().__init__(task_store=task_store)
        self.sessions: dict[str, EnvSessionState] = {}
        self.debug = debug
        self.session_timeout = session_timeout

        # 启动会话清理任务
        self._cleanup_task: Optional[asyncio.Task] = None

    async def start(self):
        """启动管理器"""
        logger.info("Starting TaskEnvManager")
        # 启动会话清理任务
        self._cleanup_task = asyncio.create_task(self._cleanup_expired_sessions())

    def stop(self):
        """停止管理器"""
        logger.info("Stopping TaskEnvManager")
        # 停止所有会话
        for session_id in list(self.sessions.keys()):
            self.delete_session(session_id)

        # 取消清理任务
        if self._cleanup_task:
            self._cleanup_task.cancel()

    async def _cleanup_expired_sessions(self):
        """清理过期会话（后台任务）"""
        while True:
            try:
                await asyncio.sleep(300)  # 每5分钟检查一次
                current_time = asyncio.get_event_loop().time()
                expired_sessions = []

                for session_id, session in self.sessions.items():
                    if current_time - session.last_accessed_at > self.session_timeout:
                        expired_sessions.append(session_id)

                for session_id in expired_sessions:
                    logger.info(f"Cleaning up expired session: {session_id}")
                    self.delete_session(session_id)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in cleanup task: {e}")

    async def create_session(
        self,
        session_id: str,
        user_id: str,
        client_id: str,
        env_id: Optional[str] = None,
        env_vars: Optional[dict[str, str]] = None,
        env_class_path: Optional[str] = None,
        env_init_kwargs: Optional[dict[str, Any]] = None,
    ) -> EnvSessionState:
        """创建环境会话

        Args:
            session_id: 会话 ID
            user_id: 用户 ID
            client_id: 客户端 ID
            env_id: 环境 ID
            env_vars: 环境变量
            env_class_path: 环境类路径（如 "arc-agi-3" 或 "module:Class"）
            env_init_kwargs: 环境初始化参数

        Returns:
            EnvSessionState: 创建的会话状态
        """
        if env_id is None:
            env_id = f"env-{uuid.uuid4().hex}"

        if env_vars is None:
            env_vars = {}

        if env_init_kwargs is None:
            env_init_kwargs = {}

        state = EnvSessionState(
            session_id=session_id,
            user_id=user_id,
            client_id=client_id,
            env_id=env_id,
            env_vars=env_vars,
            env_class_path=env_class_path,
            env_init_kwargs=env_init_kwargs,
        )

        await state.init()
        await state.start()

        self.sessions[session_id] = state
        logger.info(f"Created environment session: {session_id} with env_id: {env_id}")

        return state

    def get_session(self, session_id: str) -> Optional[EnvSessionState]:
        """获取环境会话

        Args:
            session_id: 会话 ID

        Returns:
            Optional[EnvSessionState]: 会话状态，如果不存在则返回 None
        """
        session = self.sessions.get(session_id, None)
        if session:
            session.update_last_accessed()
        return session

    def delete_session(self, session_id: str):
        """删除环境会话

        Args:
            session_id: 会话 ID
        """
        if session_id in self.sessions:
            session = self.sessions[session_id]
            session.stop()
            del self.sessions[session_id]
            logger.info(f"Deleted environment session: {session_id}")

    def list_sessions(self, user_id: Optional[str] = None) -> list[EnvSessionState]:
        """列出会话

        Args:
            user_id: 可选的用户 ID，用于过滤

        Returns:
            list[EnvSessionState]: 会话列表
        """
        if user_id:
            return [s for s in self.sessions.values() if s.user_id == user_id]
        return list(self.sessions.values())

    async def __call__(
        self,
        request: EnvSessionRequest,
        request_id: Optional[str] = None,
        session_id: Optional[str] = None,
        task_id: Optional[str] = None,
        user_id: Optional[str] = None,
        stream: bool = False,
    ):
        """执行环境任务

        Args:
            request: 环境会话请求
            request_id: 请求 ID
            session_id: 会话 ID
            task_id: 任务 ID
            user_id: 用户 ID
            stream: 是否流式返回

        Returns:
            TaskResponse 或 AsyncIterable[TaskStreamingResponse]: 任务响应
        """
        request_id = request_id if request_id else uuid.uuid4().hex
        task_id = task_id if task_id else uuid.uuid4().hex
        session_id = session_id if session_id else uuid.uuid4().hex
        user_id = user_id if user_id else uuid.uuid4().hex

        # 构造任务请求
        if stream:
            task_request = TaskStreamingRequest(
                id=request_id,
                params=TaskParams(
                    id=task_id,
                    session_id=session_id,
                    user_id=user_id,
                    payload=request,
                )
            )
            return self.on_task_subscribe(task_request)
        else:
            task_request = TaskInvokeRequest(
                id=request_id,
                params=TaskParams(
                    id=task_id,
                    session_id=session_id,
                    user_id=user_id,
                    payload=request,
                )
            )
            return await self.on_task_invoke(task_request)

    # ==================== 便捷调用方法 ====================

    async def step(
        self,
        session_id: str,
        tool_name: str,
        tool_args: dict[str, Any] = {},
        env_vars: Optional[dict[str, str]] = None,
        request_id: Optional[str] = None,
        task_id: Optional[str] = None,
        user_id: Optional[str] = None,
        stream: bool = False,
    ):
        """执行环境步骤（工具调用）

        Args:
            session_id: 会话 ID
            tool_name: 工具名称
            tool_args: 工具参数
            env_vars: 环境变量
            request_id: 请求 ID
            task_id: 任务 ID
            user_id: 用户 ID
            stream: 是否流式返回

        Returns:
            TaskResponse 或 AsyncIterable[TaskStreamingResponse]: 任务响应

        Raises:
            ValueError: 当 session 不存在时
        """
        session = self.get_session(session_id)
        if not session:
            raise ValueError(f"Session not found: {session_id}")

        # 构造请求
        request = EnvSessionRequest(
            client_id=session.client_id,
            env_id=session.env_id,
            env_vars=env_vars,
            tool_name=tool_name,
            tool_args=tool_args,
        )

        request_id = request_id if request_id else uuid.uuid4().hex
        task_id = task_id if task_id else uuid.uuid4().hex
        user_id = user_id if user_id else session.user_id

        # 根据 stream 参数选择调用方式
        logger.info(f"TaskEnvManager.step: stream={stream}")
        if stream:
            task_request = TaskStreamingRequest(
                id=request_id,
                params=TaskParams(
                    id=task_id,
                    session_id=session_id,
                    user_id=user_id,
                    payload=request,
                )
            )
            # on_task_subscribe 是 async 函数（不是 async generator），返回 async generator 对象
            # 需要 await 来获取它返回的 async generator
            result = await self.on_task_subscribe(task_request)
            logger.info(f"Stream mode, returning: {type(result)}")
            return result
        else:
            task_request = TaskInvokeRequest(
                id=request_id,
                params=TaskParams(
                    id=task_id,
                    session_id=session_id,
                    user_id=user_id,
                    payload=request,
                )
            )
            result = await self.on_task_invoke(task_request)
            logger.info(f"Non-stream mode, returning: {type(result)}")
            return result

    async def observation(self, session_id: str, info: Optional[dict[str, Any]] = None) -> ObservationResponse:
        """获取当前观察

        Args:
            session_id: 会话 ID
            info: 额外信息

        Returns:
            ObservationResponse: 观察响应

        Raises:
            ValueError: 当 session 不存在时
        """
        session = self.get_session(session_id)
        if not session:
            raise ValueError(f"Session not found: {session_id}")

        obs = await self._get_observation(session)
        # 转换 ToolResponse 为字典以避免 Pydantic 严格验证
        obs_dict = obs.model_dump() if hasattr(obs, 'model_dump') else obs

        # 获取可用工具
        tools = session.get_tools()

        # 获取完成状态
        done = session.current_state.done if session.current_state else False

        return ObservationResponse(
            observation=obs_dict,
            tools=tools,
            done=done,
        )

    async def reset(
        self,
        session_id: str,
        seed: Optional[int] = None,
        options: Optional[dict[str, Any]] = None,
    ) -> ObservationResponse:
        """重置环境

        Args:
            session_id: 会话 ID
            seed: 随机种子
            options: 重置选项
            info: 额外信息

        Returns:
            ObservationResponse: 重置后的观察响应

        Raises:
            ValueError: 当 session 不存在时
        """
        session = self.get_session(session_id)
        if not session:
            raise ValueError(f"Session not found: {session_id}")

        obs = await self._reset_environment(session, seed, options or {})
        # 转换 ToolResponse 为字典以避免 Pydantic 严格验证
        obs_dict = obs.model_dump() if hasattr(obs, 'model_dump') else obs

        # 获取可用工具
        tools = session.get_tools()

        # 获取完成状态
        done = session.current_state.done if session.current_state else False

        return ObservationResponse(
            observation=obs_dict,
            tools=tools,
            done=done,
        )

    async def list_tools(self, session_id: str) -> ToolsResponse:
        """获取工具列表

        Args:
            session_id: 会话 ID

        Returns:
            ToolsResponse: 工具列表响应

        Raises:
            ValueError: 当 session 不存在时
        """
        session = self.get_session(session_id)
        if not session:
            raise ValueError(f"Session not found: {session_id}")

        tools = session.get_tools()  # 已经返回 list[ToolData]
        return ToolsResponse(tools=tools, count=len(tools))

    async def call_tool(
        self,
        session_id: str,
        tool_name: str,
        tool_args: dict[str, Any] = {},
    ) -> ToolResponse:
        """调用工具

        Args:
            session_id: 会话 ID
            tool_name: 工具名称
            tool_args: 工具参数

        Returns:
            ToolCallResponse: 工具调用响应

        Raises:
            ValueError: 当 session 不存在或 tool_name 为空时
        """
        session = self.get_session(session_id)
        if not session:
            return tool_response_of_internal_error(f"Session not found: {session_id}")

        observation = await self._call_environment_tool(session, tool_name, tool_args)
        return observation

    # ==================== 环境交互核心方法 ====================

    async def _execute_action(self, session: EnvSessionState, action: Action) -> ToolResponse:
        """执行动作并返回观察结果

        Args:
            session: 会话状态
            action: 动作（可以是字典格式的工具调用或其他格式）

        Returns:
            ToolResponse: 观察结果
        """
        if not session.env_instance or not session.current_state:
            logger.warning("No environment instance or state")
            error_msg = f"No environment instance or state for action: {action}"
            return ToolResponse(
                message_content=[{"type": "text", "text": error_msg}],
                block_list=[{"type": "text", "text": error_msg}],
                data={"action": action, "session_id": session.session_id},
            )

        # 检查是否为工具调用格式
        if isinstance(action, dict):
            tool_name = action.get("tool_name") or action.get("name")
            if tool_name:
                tool_args = action.get("tool_args") or action.get("arguments") or {}
                return await self._call_environment_tool(session, tool_name, tool_args)

        # 默认动作处理
        logger.warning(f"Unhandled action type: {type(action)}")
        warning_msg = f"Unhandled action type: {type(action).__name__}"
        return ToolResponse(
            message_content=[{"type": "text", "text": warning_msg}],
            block_list=[{"type": "text", "text": warning_msg}],
            data={"action": action, "session_id": session.session_id},
        )

    async def _call_environment_tool(self, session: EnvSessionState, tool_name: str, tool_args: dict[str, Any]) -> ToolResponse:
        """调用环境工具

        Args:
            session: 会话状态
            tool_name: 工具名称
            tool_args: 工具参数

        Returns:
            ToolResponse: 工具调用结果的观察
        """
        if not isinstance(session.env_instance, IToolEnvironment):
            error_msg = f"Environment does not support tool calling: {type(session.env_instance).__name__}"
            logger.error(error_msg)
            return ToolResponse(
                message_content=[{"type": "text", "text": error_msg}],
                block_list=[{"type": "text", "text": error_msg}],
                data={"error": error_msg, "tool_name": tool_name},
            )

        if not session.current_state:
            error_msg = "No current state for tool calling"
            logger.error(error_msg)
            return ToolResponse(
                message_content=[{"type": "text", "text": error_msg}],
                block_list=[{"type": "text", "text": error_msg}],
                data={"error": error_msg, "tool_name": tool_name},
            )

        try:
            new_state = session.env_instance(
                session.current_state,
                tool_name=tool_name,
                tool_args=tool_args,
            )
            session.current_state = new_state
            return new_state.display()  # IState.display() 返回 ToolResponse
        except Exception as e:
            error_msg = f"Error calling tool {tool_name}: {e}"
            logger.error(error_msg)
            return ToolResponse(
                message_content=[{"type": "text", "text": error_msg}],
                block_list=[{"type": "text", "text": error_msg}],
                data={"error": str(e), "tool_name": tool_name},
            )

    async def _get_observation(self, session: EnvSessionState) -> ToolResponse:
        """获取当前状态的观察

        Args:
            session: 会话状态

        Returns:
            ToolResponse: 当前观察
        """
        if not session.current_state:
            warning_msg = "No current state for observation"
            logger.warning(warning_msg)
            return ToolResponse(
                message_content=[{"type": "text", "text": warning_msg}],
                block_list=[{"type": "text", "text": warning_msg}],
                data={
                    "session_id": session.session_id,
                    "env_id": session.env_id,
                    "is_active": session.is_active,
                },
            )

        try:
            return session.current_state.display()  # IState.display() 返回 ToolResponse
        except Exception as e:
            error_msg = f"Error getting state display: {e}"
            logger.error(error_msg)
            return ToolResponse(
                message_content=[{"type": "text", "text": error_msg}],
                block_list=[{"type": "text", "text": error_msg}],
                data={"error": str(e)},
            )

    async def _reset_environment(self, session: EnvSessionState, seed: Optional[int], options: dict[str, Any]) -> ToolResponse:
        """重置环境到初始状态

        Args:
            session: 会话状态
            seed: 随机种子
            options: 重置选项

        Returns:
            ToolResponse: 初始观察
        """
        if not session.env_instance:
            warning_msg = "No environment instance for reset"
            logger.warning(warning_msg)
            return ToolResponse(
                message_content=[{"type": "text", "text": warning_msg}],
                block_list=[{"type": "text", "text": warning_msg}],
                data={
                    "session_id": session.session_id,
                    "env_id": session.env_id,
                    "seed": seed,
                    "options": options,
                },
            )

        try:
            session.current_state = session.env_instance.provide_initial_state()
            return session.current_state.display()  # IState.display() 返回 ToolResponse
        except Exception as e:
            error_msg = f"Error resetting environment: {e}"
            logger.error(error_msg)
            return ToolResponse(
                message_content=[{"type": "text", "text": error_msg}],
                block_list=[{"type": "text", "text": error_msg}],
                data={"error": str(e)},
            )

    def _validate_request(self, request: Union[TaskInvokeRequest, TaskStreamingRequest]):
        """验证请求参数"""
        task_params: TaskParams = request.params
        try:
            if isinstance(task_params.payload, EnvSessionRequest):
                req = task_params.payload
            else:
                req = EnvSessionRequest.model_validate(task_params.payload)
        except Exception as e:
            logger.error(f"Invalid request payload: {e}")
            from agentlin.core.types import InvalidParamsError
            return InvalidParamsError(message=str(e))
        return req

    async def on_task_subscribe(
        self,
        request: TaskStreamingRequest,
    ) -> AsyncIterable[TaskStreamingResponse]:
        """处理任务订阅请求（流式）

        Args:
            request: 任务流式请求

        Yields:
            TaskStreamingResponse: 任务流式响应
        """
        task_params: TaskParams = request.params
        request_id = request.id
        task_id = task_params.id
        session_id = task_params.session_id
        user_id = task_params.user_id

        req = self._validate_request(request)
        if isinstance(req, JSONRPCError):
            logger.error(f"Error in tool task: {req}")
            return self._stream_error(request_id, req)
        return self._stream_generator(req, request_id, task_id, session_id, user_id)

    async def _stream_generator(
        self,
        req: EnvSessionRequest,
        request_id: str,
        task_id: str,
        session_id: str,
        user_id: str,
    ) -> AsyncIterable[TaskStreamingResponse]:
        """流式生成器

        Args:
            req: 环境会话请求
            request_id: 请求 ID
            task_id: 任务 ID
            session_id: 会话 ID
            user_id: 用户 ID

        Yields:
            TaskStreamingResponse: 任务流式响应
        """
        from agentlin.route.task_manager import SequenceCounter, StreamableTaskParser
        from agentlin.core.agent_schema import content_datas_to_content_items

        # 创建任务
        logger.debug(f"Environment Tool Call\ntool_name: {req.tool_name}\ntool_args: {req.tool_args}")
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

        # 准备资源（获取或创建会话）
        resp = await self.working_streaming_response(request_id=request_id, parser=parser, seq_counter=seq_counter)
        yield resp

        # 获取或创建会话
        session = self.get_session(session_id)
        if not session:
            try:
                session = await self.create_session(
                    session_id=session_id,
                    user_id=user_id,
                    client_id=req.client_id,
                    env_id=req.env_id,
                    env_vars=req.env_vars,
                )
            except Exception as e:
                error_message = f"Failed to create session: {e}"
                logger.error(error_message)
                resp = await self.fail_streaming_response(
                    request_id=request_id,
                    parser=parser,
                    seq_counter=seq_counter,
                    error=error_message,
                )
                yield resp
                return

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

        # 执行工具调用
        try:
            # 直接使用请求中的 tool_name 和 tool_args
            tool_name = req.tool_name
            tool_args = req.tool_args

            # 调用环境工具
            observation = await self._call_environment_tool(session, tool_name, tool_args)

            # 将观察结果转换为消息内容
            message_content = observation.get("message_content", [])
            block_list = observation.get("block_list", [])

        except Exception as e:
            error_message = f"Error while executing tool call: {e}"
            logger.error(f"{error_message}\n{traceback.format_exc()}")
            message_content = [{"type": "text", "text": error_message}]
            block_list = message_content

        resp = await self.counting_event_streaming_response(
            request_id=request_id,
            parser=parser,
            seq_counter=seq_counter,
            event=TaskToolResultDeltaEvent(
                item_id=output_item.id,
                call_id=output_item.call_id,
                agent_step=current_step,
                delta_message_content=message_content,
                delta_block_list=block_list,
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
                message_content=message_content,
                block_list=block_list,
            ),
        )
        yield resp

        output_item.message_content = message_content
        output_item.block_list = block_list
        output_item.output = content_datas_to_content_items(message_content)

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
