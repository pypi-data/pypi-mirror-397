import asyncio
import json
import os
import traceback
from typing import AsyncIterable
from typing_extensions import Any, AsyncGenerator
import uuid

from fastmcp import Client
from fastmcp.client.transports import ClientTransportT
from fastmcp.client.elicitation import ElicitRequestParams, ElicitResult, RequestContext, ClientSession, LifespanContextT

from loguru import logger

from agentlin.core.agent_message_queue import AgentMessageQueue
from agentlin.core.agent_schema import apply_environment_variables, content_data_to_content_item, content_datas_to_content_items, extract_variables
from agentlin.environment.interface import IToolEnvironment
from agentlin.route.task_manager import InMemoryTaskManager, SequenceCounter, StreamableTaskParser
from agentlin.core.types import *
from agentlin.store.task_store import InMemoryTaskStore
from agentlin.tools.builtin.file_system_tools import (
    ListDirectoryTool,
    ReadFileTool,
    WriteFileTool,
    GlobTool,
    GrepTool,
    ReplaceInFileTool,
    BashTool,
)
from agentlin.tools.builtin.web_tools import (
    WebSearchTool,
    WebFetchTool,
)
from agentlin.tools.core import DiscoveredMcpTool, tool_result_of_internal_error
from agentlin.tools.stateful_memory.memory_tool import MemoryTool
from agentlin.tools.stateful_memory.todo_tool import TodoWriteTool


TASK_TOOL_MANAGER = "task_tool_manager"


class CallToolRequest(BaseModel):
    call_name: str
    call_args: dict[str, Any]


class TaskToolManager(InMemoryTaskManager, AgentMessageQueue):
    def __init__(
        self,
        client_id: str,
        agent_id: str,
        mcp_config: Optional[ClientTransportT] = None,
        workspace_dir: Optional[str] = None,
        *,
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
        builtin_tools: list[BaseTool] = [],
        task_store: Optional[InMemoryTaskStore] = None,
    ):
        InMemoryTaskManager.__init__(self, task_store=task_store)
        AgentMessageQueue.__init__(
            self,
            name=f"{agent_id}/{TASK_TOOL_MANAGER}",
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
        self.mcp_config = mcp_config
        if mcp_config:
            if isinstance(mcp_config, dict):
                for item in mcp_config:
                    if isinstance(mcp_config[item], dict):
                        if "url" in mcp_config[item]:
                            mcp_url = mcp_config[item]["url"]
                            if not isinstance(mcp_url, str):
                                continue
                            mcp_url = apply_environment_variables(mcp_url)
                            mcp_config[item]["url"] = mcp_url
            self.client = Client(
                mcp_config,
                elicitation_handler=self.on_elicitation,
            )
        self.workspace_dir = workspace_dir
        self.name2tool: dict[str, BaseTool] = {}
        self.register_rpc_method("call_tool", self.call_tool)
        self.builtin_tools = builtin_tools

    async def on_elicitation(
        self,
        message: str,
        response_type: type,
        params: ElicitRequestParams,
        context: RequestContext[ClientSession, LifespanContextT],
    ):
        # Present the message to the user and collect input
        # user_input = input(f"{message}: ")
        print(f"{message}")
        print("===Params===")
        print(params)
        print("===Context===")
        print(context)
        data = {
            "params": params.model_dump(),
        }
        result = await self.call_rpc(self.client_id, "elicitation", message, response_type, data, context)
        if not result:
            logger.error(f"Failed to send elicitation message to {self.client_id}")
            return ElicitResult(action="reject")

        return ElicitResult(action="accept", content=result)

    def get_function_declarations(self) -> List[FunctionDefinition]:
        return [tool.schema for tool in self.name2tool.values()]

    def get_all_tools(self) -> List[BaseTool]:
        return list(self.name2tool.values())

    def get_tool(self, name: str) -> Optional[BaseTool]:
        return self.name2tool.get(name)

    def register_tool(self, tool: BaseTool):
        if tool.name in self.name2tool:
            logger.warning(f'Warning: Tool "{tool.name}" already registered. Overwriting.')
        self.name2tool[tool.name] = tool

    async def discover_tools(self, session_state):
        tasks = [
            self.discover_builtin_tools(),
            # self.discover_environment_tools(session_state.environments),
            self.discover_session_tools(session_state),
            self.discover_mcp_tools(),
            self.discover_file_system_tools(self.workspace_dir),
        ]
        await asyncio.gather(*tasks)

    async def discover_builtin_tools(self):
        if not self.builtin_tools:
            return
        for tool in self.builtin_tools:
            self.register_tool(tool)

    async def discover_environment_tools(self, environments: list[IToolEnvironment]):
        if not environments:
            return
        for environment in environments:
            state = environment.provide_initial_state()
            env_tools = environment.provide_tools(state)
            for tool in env_tools:
                self.register_tool(tool)

    async def discover_mcp_tools(self):
        if not self.mcp_config:
            return
        async with self.client:
            tools = await self.client.list_tools()
            for tool in tools:
                self.register_tool(DiscoveredMcpTool(self.client, tool))

    async def discover_file_system_tools(self, workspace_dir: Optional[str] = None):
        workspace_dir = workspace_dir if workspace_dir else os.getcwd()
        if not workspace_dir or not os.path.isdir(workspace_dir):
            return
        if self.workspace_dir != workspace_dir:
            self.workspace_dir = workspace_dir
        tools = [
            ListDirectoryTool(workspace_dir=workspace_dir),
            ReadFileTool(workspace_dir=workspace_dir),
            WriteFileTool(workspace_dir=workspace_dir),
            GlobTool(workspace_dir=workspace_dir),
            GrepTool(workspace_dir=workspace_dir),
            ReplaceInFileTool(workspace_dir=workspace_dir),
            BashTool(workspace_dir=workspace_dir),
        ]
        for tool in tools:
            self.register_tool(tool)

    async def discover_session_tools(self, session_state):
        tools = [
            TodoWriteTool(session_state=session_state.todo_state),
            MemoryTool(session_state=session_state.memory_state),
            # WebFetchTool(),
            # WebSearchTool(engine="duckduckgo"),
        ]
        for tool in tools:
            self.register_tool(tool)

    async def get_tools(self, allowed_tools: Optional[list[str]] = None) -> list[ToolData]:
        results = []
        for name, tool in self.name2tool.items():
            if allowed_tools is None:
                results.append(tool.function_tool_schema)
                continue
            # 如果指定了 allowed_tools，则只返回这些工具
            if name in allowed_tools:
                results.append(tool.function_tool_schema)
        return results

    async def _handle_regular_message(self, msg: dict[str, Any]):
        """
        Handle regular (non-time) messages from other agents.

        Must be implemented by concrete agent classes to define
        agent-specific message handling behavior.

        Args:
            msg: The decoded message dictionary.
        """
        self.logger.info(msg)

    async def call_tool(
        self,
        request_id: str,
        call_id: str,
        session_id: str,
        user_id: str,
        call_name: str,
        call_args: dict[str, Any],
    ):
        tool_request = await self.invoke_request(
            request_id=request_id,
            task_id=call_id,
            session_id=session_id,
            user_id=user_id,
            payload=CallToolRequest(
                call_name=call_name,
                call_args=call_args,
            ),
        )
        resp = await self.on_task_invoke(tool_request)
        return resp

    def _validate_request(self, request: Union[TaskInvokeRequest, TaskStreamingRequest]):
        task_params: TaskParams = request.params
        try:
            if isinstance(task_params.payload, CallToolRequest):
                req = task_params.payload
            else:
                req = CallToolRequest.model_validate(task_params.payload)
        except Exception as e:
            self.logger.error(f"Invalid request payload: {e}")
            return InvalidParamsError(message=str(e))
        return req

    async def on_task_subscribe(self, request: TaskStreamingRequest) -> AsyncIterable[TaskStreamingResponse]:
        task_params: TaskParams = request.params
        request_id = request.id
        task_id = task_params.id
        session_id = task_params.session_id
        user_id = task_params.user_id
        req = self._validate_request(request)
        if isinstance(req, JSONRPCError):
            self.logger.error(f"Error in tool task: {req}")
            return self._stream_error(request_id=request_id, error=req)
        return self._stream_generator(req, request_id, task_id, session_id, user_id)

    async def _stream_generator(
        self,
        req: CallToolRequest,
        request_id: str,
        task_id: str,
        session_id: str,
        user_id: str,
    ) -> AsyncIterable[TaskStreamingResponse]:
        # 创建任务
        self.logger.debug(f"Tool Call\n{req.call_name}\n{req.call_args}")
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

        # 调用工具
        # ! 无论如何，即使工具调用失败，都需要返回一个错误信息
        try:
            tool = self.get_tool(req.call_name)
            if tool:
                tool_result = await tool.execute(req.call_args)
            else:
                error_message = f"Tool not found: {req.call_name}"
                self.logger.error(error_message)
                tool_result = tool_result_of_internal_error(error_message)
        except Exception as e:
            error_message = f"Error while calling {req.call_name}: {e}"
            self.logger.error(f"{error_message}\n{traceback.format_exc()}")
            tool_result = tool_result_of_internal_error(error_message)

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

