from typing import Optional, Dict, Any, List
from abc import ABC, abstractmethod
from pydantic import BaseModel, ValidationError
import asyncio

from agentlin.code_interpreter.types import MIME_TOOL_RESPONSE
from agentlin.environment.interface import IEnvironment, IStoppableState
from agentlin.environment.state.text_state import ErrorState, TextState
from agentlin.core.types import BaseTool, ToolData, ToolParams, ToolResult, ContentData, BlockData


class ToolEnvState(IStoppableState):
    """
    工具环境状态基类，包含工具调用相关的状态信息
    """
    message_content: List[dict] = []
    block_list: List[dict] = []
    allowed_tools: List[str] = []

    def check_validity(self) -> bool:
        rules = [
            super().check_validity(),
            isinstance(self.message_content, list),
            isinstance(self.block_list, list),
            isinstance(self.allowed_tools, list),
        ]
        return all(rules)

    def _repr_mimebundle_(self):
        bundle = super()._repr_mimebundle_()
        bundle.update(
            {
                MIME_TOOL_RESPONSE: {
                    "message_content": self.message_content,
                    "block_list": self.block_list,
                }
            }
        )
        return bundle


class ToolCallArguments(BaseModel):
    """工具调用参数基类"""

    name: str
    arguments: Dict[str, Any] = {}


class ToolEnvironment(IEnvironment, ABC):
    """
    使用 BaseTool 和 tool_call 的环境基类
    """

    def __init__(self, info: Optional[Dict[str, str]] = None):
        super().__init__()
        self.tools: List[BaseTool] = []
        self.name2tool: Dict[str, BaseTool] = {}

        self.info = {
            "done": "Task completed successfully!",
            "invalid_state": "The state is invalid.",
            "tool_not_found": "The specified tool was not found.",
            "tool_execution_error": "Error occurred during tool execution.",
            "invalid_arguments": "Invalid tool arguments provided.",
            "help": """You should provide tool_name and tool_arguments.

<example-code>
state = env.provide_initial_state()
next_state = env(state, tool_name='tool_name', tool_arguments={'param': 'value'})
next_state
</example-code>""",
        }
        if info:
            self.info.update(info)

        # 注册工具
        self._register_tools()

    @abstractmethod
    def _register_tools(self):
        """注册环境所需的工具，子类必须实现此方法"""
        pass

    def add_tool(self, tool: BaseTool):
        """添加工具到环境中"""
        self.tools.append(tool)
        self.name2tool[tool.name] = tool

    def list_tools(self) -> List[ToolData]:
        """列出所有可用工具"""
        return [tool.function_tool_schema for tool in self.tools]

    def get_available_tool_names(self) -> List[str]:
        """获取所有可用工具名称"""
        return list(self.name2tool.keys())

    async def execute_tool(self, tool_name: str, tool_arguments: Dict[str, Any]) -> ToolResult:
        """执行指定工具"""
        tool = self.name2tool.get(tool_name)
        if not tool:
            error_message = f"Tool '{tool_name}' not found. Available tools: {self.get_available_tool_names()}"
            return ToolResult(
                message_content=[{"type": "text", "text": error_message}],
                block_list=[{"type": "text", "text": error_message}],
            )
        try:
            result = await tool.execute(tool_arguments)
            return result
        except Exception as e:
            error_message = f"Tool execution failed: {str(e)}"
            return ToolResult(
                message_content=[{"type": "text", "text": error_message}],
                block_list=[{"type": "text", "text": error_message}],
            )

    def forward(self, s: ToolEnvState, **kwargs) -> ToolEnvState:
        """环境状态转移函数"""
        if s.done:
            return self._create_done_state()

        if not s.check_validity():
            return self._create_error_state(self.info["invalid_state"])

        try:
            args = ToolCallArguments.model_validate(kwargs)
            return self._handle_tool_call(s, args.name, args.arguments)
        except ValidationError as e:
            return self._create_error_state(f"Invalid arguments: {e}\n\n{self.info['help']}")
        except Exception as e:
            return self._create_error_state(f"Unknown error: {e}\n\n{self.info['help']}")

    @abstractmethod
    def _handle_tool_call(self, state: ToolEnvState, tool_name: str, tool_arguments: Dict[str, Any]) -> ToolEnvState:
        """处理工具调用，子类必须实现此方法"""
        pass

    def _create_done_state(self) -> ToolEnvState:
        """创建完成状态"""
        message = self.info["done"]
        return ToolEnvState(
            message_content=[{"type": "text", "text": message}],
            block_list=[{"type": "text", "text": message}],
            allowed_tools=self.get_available_tool_names(),
            done=True,
        )

    def _create_error_state(self, message: str) -> ToolEnvState:
        """创建错误状态"""
        return ToolEnvState(
            message_content=[{"type": "text", "text": f"Error: {message}"}],
            block_list=[{"type": "text", "text": f"Error: {message}"}],
            allowed_tools=self.get_available_tool_names(),
            done=False,
        )

    def _create_text_state(self, text: str, allowed_tools: List[str] = None, session_data: Dict[str, Any] = None, done: bool = False) -> ToolEnvState:
        """创建文本状态"""
        return ToolEnvState(
            message_content=[{"type": "text", "text": text}],
            block_list=[{"type": "text", "text": text}],
            allowed_tools=allowed_tools or self.get_available_tool_names(),
            done=done,
        )

    def provide_initial_state(self) -> ToolEnvState:
        """提供初始状态，子类可以重写此方法"""
        message = f"Environment initialized. Available tools: {self.get_available_tool_names()}\n\n{self.info['help']}"
        return ToolEnvState(
            message_content=[{"type": "text", "text": message}],
            block_list=[{"type": "text", "text": message}],
            allowed_tools=self.get_available_tool_names(),
            done=False,
        )


class AsyncToolEnvironment(ToolEnvironment):
    """
    异步工具环境基类，支持异步工具调用
    """

    @abstractmethod
    async def _ahandle_tool_call(self, state: ToolEnvState, tool_name: str, tool_arguments: Dict[str, Any]) -> ToolEnvState:
        """异步处理工具调用，子类必须实现此方法"""
        pass

    def _handle_tool_call(self, state: ToolEnvState, tool_name: str, tool_arguments: Dict[str, Any]) -> ToolEnvState:
        """同步版本的工具调用处理，默认抛出异常提示使用异步版本"""
        loop = asyncio.get_event_loop()
        if loop.is_running():
            task = loop.create_task(self._ahandle_tool_call(state, tool_name, tool_arguments))
            return task.result()
        return loop.run_until_complete(self._ahandle_tool_call(state, tool_name, tool_arguments))

    async def aforward(self, s: ToolEnvState, **kwargs) -> ToolEnvState:
        """异步环境状态转移函数"""
        if s.done:
            return self._create_done_state()

        if not s.check_validity():
            return self._create_error_state(self.info["invalid_state"])

        try:
            args = ToolCallArguments.model_validate(kwargs)
            return await self._ahandle_tool_call(s, args.name, args.arguments)
        except ValidationError as e:
            return self._create_error_state(f"Invalid arguments: {e}\n\n{self.info['help']}")
        except Exception as e:
            return self._create_error_state(f"Unknown error: {e}\n\n{self.info['help']}")
