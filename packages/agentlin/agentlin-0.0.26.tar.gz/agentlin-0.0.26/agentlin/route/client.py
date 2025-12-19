import asyncio
from contextlib import AsyncExitStack, asynccontextmanager
import anyio
from fastmcp import Client
from loguru import logger
from typing_extensions import Any, AsyncIterable, Optional
import json
import traceback
import random
import uuid

import httpx
from httpx_sse import connect_sse
from fastmcp.client.transports import ClientTransportT
from fastmcp.client.elicitation import ElicitRequestParams, ElicitResult, RequestContext, ClientSession, LifespanContextT

from agentlin.core.types import *
from agentlin.core.agent_message_queue import AgentMessageQueue
from agentlin.core.swam import Swarm
from agentlin.route.agent_config import AgentConfig


class AgentClient(AgentMessageQueue):
    def __init__(
        self,
        client_id: str,
        backend_url: str,
        *,
        mcp_config: Optional[ClientTransportT] = None,
        rabbitmq_host: str = "localhost",
        rabbitmq_port: int = 5672,
        rabbitmq_user: str = "guest",
        rabbitmq_password: str = "guest",
        auto_ack: bool = False,
        reconnect_initial_delay: float = 5.0,
        reconnect_max_delay: float = 60.0,
        message_timeout: float = 30.0,
        rpc_timeout: float = 30.0,
        log_dir: Optional[str] = None,
    ):
        AgentMessageQueue.__init__(
            self,
            name=client_id,
            rabbitmq_host=rabbitmq_host,
            rabbitmq_port=rabbitmq_port,
            rabbitmq_user=rabbitmq_user,
            rabbitmq_password=rabbitmq_password,
            auto_ack=auto_ack,
            reconnect_initial_delay=reconnect_initial_delay,
            reconnect_max_delay=reconnect_max_delay,
            message_timeout=message_timeout,
            rpc_timeout=rpc_timeout,
            log_dir=log_dir,
        )
        self.client_id = client_id
        self.backend_url = backend_url
        self.register_rpc_method("elicitation", self.on_elicitation)
        self.mcp_config = mcp_config
        self.client: Optional[Client] = None
        self.client_tools: Optional[list[ToolData]] = None
        if mcp_config:
            self.client = Client(mcp_config=mcp_config)

        # session context management
        self._session: AgentClientSession | None = None
        self._exit_stack: AsyncExitStack | None = None
        self._nesting_counter: int = 0
        self._context_lock = anyio.Lock()
        self._session_task: asyncio.Task | None = None
        self._ready_event = anyio.Event()
        self._stop_event = anyio.Event()

    async def initialize(self):
        if self.client:
            async with self.client:
                tools = await self.client.list_tools()
                tools = [{"type": "function", "function": tool.model_dump()} for tool in tools]
                self.client_tools = tools
        return await super().initialize()

    async def on_elicitation(
        self,
        message: str,
        response_type: type,
        params: ElicitRequestParams,
        context: RequestContext[ClientSession, LifespanContextT],
    ):
        # Present the message to the user and collect input
        print(f"{message}")
        print("===Params===")
        print(params)
        print("===Context===")
        print(context)
        user_input = input(f"{message}\n Please input (y/N): ")
        if user_input.strip().lower() in ["y", "yes"]:
            action = "accept"
        else:
            action = "reject"
        return ElicitResult(action=action)

    async def _handle_regular_message(self, message):
        self.logger.debug(f"Received regular message: {message}")

    def is_connected(self) -> bool:
        """Check if the client is currently connected."""
        return self._session is not None

    @asynccontextmanager
    async def _context_manager(self):
        async with AgentClientSession(self) as session:
            self._session = session
            # Initialize the session
            try:
                yield
            except anyio.ClosedResourceError:
                raise RuntimeError("Server session was closed unexpectedly")
            except TimeoutError:
                raise RuntimeError("Failed to initialize server session")
            finally:
                self._session = None

    async def __aenter__(self):
        await self._connect()

        # Check if session task failed and raise error immediately
        if self._session_task is not None and self._session_task.done() and not self._session_task.cancelled():
            exception = self._session_task.exception()
            if isinstance(exception, httpx.HTTPStatusError):
                raise exception
            elif exception is not None:
                raise RuntimeError(f"Client failed to connect: {exception}") from exception

        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self._disconnect()

    async def _connect(self):
        # ensure only one session is running at a time to avoid race conditions
        async with self._context_lock:
            need_to_start = self._session_task is None or self._session_task.done()
            if need_to_start:
                self._stop_event = anyio.Event()
                self._ready_event = anyio.Event()
                self._session_task = asyncio.create_task(self._session_runner())
            await self._ready_event.wait()
            self._nesting_counter += 1
        return self

    async def _disconnect(self, force: bool = False):
        # ensure only one session is running at a time to avoid race conditions
        async with self._context_lock:
            # if we are forcing a disconnect, reset the nesting counter
            if force:
                self._nesting_counter = 0

            # otherwise decrement to check if we are done nesting
            else:
                self._nesting_counter = max(0, self._nesting_counter - 1)

            # if we are still nested, return
            if self._nesting_counter > 0:
                return

            # stop the active seesion
            if self._session_task is None:
                return
            self._stop_event.set()
            runner_task = self._session_task
            self._session_task = None

        # wait for the session to finish
        if runner_task:
            await runner_task

        # Reset for future reconnects
        self._stop_event = anyio.Event()
        self._ready_event = anyio.Event()
        self._session = None
        self._initialize_result = None

    async def _session_runner(self):
        try:
            async with AsyncExitStack() as stack:
                try:
                    await stack.enter_async_context(self._context_manager())
                    # Session/context is now ready
                    self._ready_event.set()
                    # Wait until disconnect/stop is requested
                    await self._stop_event.wait()
                finally:
                    # On exit, ensure ready event is set (idempotent)
                    self._ready_event.set()
        except Exception:
            # Ensure ready event is set even if context manager entry fails
            self._ready_event.set()
            raise

    async def chat(
        self,
        user_message_content: list[ContentData],
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
        env: Optional[dict[str, str]] = None,
        rollout_save_dir: Optional[str] = None,
        return_rollout: bool = False,
    ) -> AsyncIterable[TaskStreamingResponse]:
        """
        发起对话聊天请求

        Args:
            user_message_content: 用户消息内容
            client_id: 前端 ID，默认为 "aime"
            task_id: 任务 ID，如果为 None 则自动生成
            agent_config: 主机代理配置
            allowed_tools: 允许的工具列表. None 为允许所有，[] 为不允许任何
            disallowed_tools: 不允许的工具列表. None 和 [] 不进行处理
            allowed_subagents: 允许的子代理列表. None 为允许所有，[] 为不允许任何
            stop_tools: 遇到 stop_tools 时终止. None 和 [] 不进行处理
            client_tools: 客户端的工具定义，遇到客户端工具时一定终止
            history_messages: 历史消息列表，用于 completion 模式
            thought_messages: 思考消息列表，用于 completion 模式
            inference_args: 推理参数，如 max_tokens, temperature 等
            workspace_dir: 当前工作目录，用于 file_system_mcp 和代码解释器
            env: 环境变量字典
            rollout_save_dir: rollout 保存目录
            return_rollout: 是否在响应中返回 rollout 结果

        Returns:
            AsyncIterable[TaskStreamingResponse]: 流式响应

        Raises:
            ValueError: 当必需参数缺失或无效时
            httpx.HTTPStatusError: 当HTTP请求失败时
        """
        # 参数验证
        if not user_message_content:
            raise ValueError("user_message_content cannot be empty")

        # 生成默认值，使用更安全的 UUID 生成
        if task_id is None:
            task_id = uuid.uuid4().hex
        if user_id is None:
            user_id = uuid.uuid4().hex

        # 合并客户端工具
        all_client_tools = []
        if self.client_tools:
            all_client_tools.extend(self.client_tools)
        if client_tools:
            all_client_tools.extend(client_tools)

        # 构建完整的请求payload，对应 SessionRequest 的字段
        payload = {
            "user_id": user_id,
            "client_id": self._session.client.client_id,
            "user_message_content": user_message_content,
            "agent_config": agent_config,
            "allowed_tools": allowed_tools,
            "disallowed_tools": disallowed_tools,
            "allowed_subagents": allowed_subagents,
            "stop_tools": stop_tools,
            "client_tools": all_client_tools if all_client_tools else None,
            "history_messages": history_messages or [],
            "thought_messages": thought_messages or [],
            "inference_args": inference_args or {},
            "workspace_dir": workspace_dir,
            "env": env,
            "rollout_save_dir": rollout_save_dir,
            "return_rollout": return_rollout,
        }

        # 构建任务参数
        task_params = TaskParams(
            id=task_id,
            session_id=self._session.get_session_id(),
            payload=payload,
        )

        # 发送流式请求并返回结果
        stream = self._session.task_streaming(task_params)
        return stream

    async def chat_text(self, message: str, **kwargs) -> AsyncIterable[TaskStreamingResponse]:
        """
        便捷方法：使用纯文本消息发起对话

        Args:
            message: 文本消息内容
            **kwargs: 其他传递给 chat 方法的参数

        Returns:
            AsyncIterable[TaskStreamingResponse]: 流式响应
        """
        user_message_content = [{"type": "text", "text": message}]
        return await self.chat(user_message_content=user_message_content, **kwargs)

    async def show_streaming_response(self, stream: AsyncIterable[TaskStreamingResponse]):
        """Process the streaming response from the task manager."""
        try:
            async for item in stream:
                if not isinstance(item, TaskStreamingResponse):
                    self.logger.debug(f"Received unexpected item: {item}")
                    continue
                if item.error:
                    self.logger.error(f"Error in request {item.id}: {item.error}")
                    continue
                event = item.result
                self.logger.debug(event.model_dump_json(indent=2))
        except KeyboardInterrupt:
            self.logger.info("Streaming interrupted by user.")
        except Exception as e:
            self.logger.error(f"Error during streaming: {e}\n{traceback.format_exc()}")


class AgentClientSession:
    """
    会话管理器，用于管理单个对话会话的状态和历史
    """

    def __init__(
        self,
        client: AgentClient,
        session_id: Optional[str] = None,
        **default_kwargs,
    ):
        self.client = client
        self.client_id = client.client_id
        self.session_id = session_id or uuid.uuid4().hex
        self.default_kwargs = default_kwargs

    async def __aenter__(self):
        await self.initialize()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        body = {
            "session_id": self.session_id,
        }
        async with httpx.AsyncClient() as client:
            response = await client.post(self.client.backend_url + "/stop", json=body, timeout=60)
            response.raise_for_status()
            resp = response.json()
            logger.debug(f"Closed session {self.session_id}:\n{resp}")

    async def initialize(self):
        pass

    def get_session_id(self) -> str:
        """获取会话ID"""
        return self.session_id

    def reset_session(self) -> str:
        """重置会话，生成新的会话ID"""
        self.session_id = uuid.uuid4().hex
        return self.session_id

    async def task_streaming(self, payload: TaskParams) -> AsyncIterable[TaskStreamingResponse]:
        request = TaskStreamingRequest(params=payload)
        with httpx.Client(timeout=None) as client:
            with connect_sse(client, "POST", self.client.backend_url, json=request.model_dump()) as event_source:
                for sse in event_source.iter_sse():
                    yield TaskStreamingResponse(**json.loads(sse.data))

    async def _send_request(self, request: JSONRPCRequest) -> dict[str, Any]:
        async with httpx.AsyncClient() as client:
            response = await client.post(self.client.backend_url, json=request.model_dump(), timeout=60)
            response.raise_for_status()
            return response.json()

    async def on_task(self, payload: dict[str, Any]) -> TaskResponse:
        payload = TaskParams(**payload)
        request = TaskInvokeRequest(params=payload)
        return TaskResponse(**await self._send_request(request))

    async def get_task(self, payload: dict[str, Any]) -> GetTaskResponse:
        request = GetTaskRequest(params=payload)
        return GetTaskResponse(**await self._send_request(request))

    async def cancel_task(self, payload: dict[str, Any]) -> CancelTaskResponse:
        request = CancelTaskRequest(params=payload)
        return CancelTaskResponse(**await self._send_request(request))

    async def set_task_callback(self, payload: dict[str, Any]) -> SetTaskPushNotificationResponse:
        request = SetTaskPushNotificationRequest(params=payload)
        return SetTaskPushNotificationResponse(**await self._send_request(request))

    async def get_task_callback(self, payload: dict[str, Any]) -> GetTaskPushNotificationResponse:
        request = GetTaskPushNotificationRequest(params=payload)
        return GetTaskPushNotificationResponse(**await self._send_request(request))


async def main():
    client = AgentClient(
        client_id="iWencai",
        backend_url="http://localhost:9999/v1/agent",
    )
    # async with Swarm([client]):  # 启动基于消息队列的群组环境
    async with client:  # client 开始说话
        while user_input := input("请输入消息内容（输入exit退出）："):
            if user_input.lower() == "exit":
                break
            stream = await client.chat_text(user_input)
            # async for chunk in stream:
            #     print(chunk)
            await client.show_streaming_response(stream)


if __name__ == "__main__":
    asyncio.run(main())
