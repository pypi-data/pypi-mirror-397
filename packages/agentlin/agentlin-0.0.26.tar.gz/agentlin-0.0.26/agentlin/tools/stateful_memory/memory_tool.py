

from pydantic import BaseModel
from agentlin.core.types import BaseTool, ToolParams, ToolResult
from agentlin.tools.core import tool_result_of_text


class MemorySessionState(BaseModel):
    memory: str = ""  # 记忆内容


class MemoryTool(BaseTool):
    """
    用于访问和管理 Agent 的记忆的工具。
    """
    NAME = "SaveMemory"

    def __init__(self, session_state: MemorySessionState):
        """
        初始化 Memory 工具

        Args:
            session_state: 会话状态对象，用于存储和检索记忆内容
        """
        self.session_state = session_state

        parameters = {
            "type": "object",
            "properties": {
                "memory": {
                    "type": "string",
                    "description": "要存储的记忆内容。",
                },
            },
            "required": ["memory"],
            "additionalProperties": False,
        }

        super().__init__(
            name=self.NAME,
            title=self.NAME,
            description="""保存特定信息或事实到长期记忆。使用结构化的 markdown 格式，越详细越好。""",
            parameters=parameters,
        )

    def provide_system_reminder(self, prefix_content: list[dict], suffix_content: list[dict]):
        """提供系统提醒，包含当前记忆内容"""
        memory_text = self.session_state.memory
        if len(memory_text.strip()) > 0:
            prefix_content.append({"type": "text", "text": f"<memory>\n{memory_text}\n</memory>"})

    async def execute(self, params: ToolParams) -> ToolResult:
        """执行记忆操作

        Args:
            params: 包含写入记忆所需参数的字典

        Returns:
            ToolResult 对象，包含写入结果
        """
        memory = params.get("memory", "")
        self.session_state.memory = memory
        return tool_result_of_text("记忆已更新")
