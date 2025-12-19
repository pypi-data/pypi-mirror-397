import json
from typing import List
from pydantic import BaseModel

from agentlin.core.types import BaseTool, ToolParams, ToolResult
from agentlin.tools.tool_todo import TodoItem, text_result_of_todo_read, todo_write, validate_todos


class TodoSessionState(BaseModel):
    todos: str = ""  # 待办事项列表


class TodoWriteTool(BaseTool):
    """
    创建和管理结构化任务列表的工具。
    """

    NAME = "TodoWrite"

    def __init__(self, session_state: TodoSessionState):
        """
        初始化 Todo 写入工具

        Args:
            session_state: 会话状态对象，用于存储和检索待办事项列表
        """
        self.session_state = session_state

        parameters = {
            "type": "object",
            "properties": {
                "todos": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "id": {
                                "type": "string",
                                "description": "任务的唯一标识符",
                            },
                            "content": {
                                "type": "string",
                                "description": "任务描述",
                            },
                            "status": {
                                "type": "string",
                                "enum": ["pending", "in_progress", "completed"],
                                "description": "任务状态：'pending'、'in_progress' 或 'completed'",
                            },
                            "priority": {
                                "type": "string",
                                "enum": ["high", "medium", "low"],
                                "description": "任务优先级：'high'、'medium' 或 'low'",
                            },
                        },
                        "required": ["id", "content", "status", "priority"],
                        "additionalProperties": False,
                    },
                    "description": "todo 项目列表，包含任务内容、状态和优先级",
                },
            },
            "required": ["todos"],
            "additionalProperties": False,
        }

        super().__init__(
            name="TodoWrite",
            title="TodoWrite",
            description="""使用此工具为当前编码会话创建和管理结构化任务列表。这有助于您跟踪进度、组织复杂任务，并向用户展示彻底性。
它还帮助用户了解任务进度和其请求的总体进度。

## 何时使用此工具
在以下场景中主动使用此工具：

1. 复杂的多步骤任务 - 当任务需要 3 个或更多不同的步骤或操作时
2. 非平凡和复杂的任务 - 需要仔细规划或多种操作的任务
3. 用户明确请求 todo 列表 - 当用户直接要求您使用 todo 列表时
4. 用户提供多个任务 - 当用户提供要完成的事项列表（编号或逗号分隔）时
5. 收到新指令后 - 立即将用户要求作为 todo 捕获
6. 当您开始处理任务时 - 在开始工作前将其标记为 in_progress。理想情况下，您应该一次只有一个 todo 为 in_progress
7. 完成任务后 - 将其标记为已完成，并添加在实施过程中发现的任何新后续任务

## 何时不使用此工具

在以下情况下跳过使用此工具：
1. 只有一个简单直接的任务
2. 任务很简单，跟踪它不会带来组织上的好处
3. 任务可以在少于 3 个简单步骤中完成
4. 任务纯粹是对话或信息性的

注意：如果只有一个简单任务要做，您不应该使用此工具。在这种情况下，最好直接执行任务。

## 任务状态和管理

1. **任务状态**：使用这些状态跟踪进度：
   - pending：任务尚未开始
   - in_progress：当前正在处理（一次限制为一个任务）
   - completed：任务成功完成

2. **任务管理**：
   - 在工作时实时更新任务状态
   - 完成后立即将任务标记为完成（不要批量完成）
   - 在任何时间只有一个任务为 in_progress
   - 在开始新任务之前完成当前任务
   - 从列表中完全删除不再相关的任务

3. **任务完成要求**：
   - 只有在您完全完成任务时才将其标记为已完成
   - 如果遇到错误、阻塞或无法完成，请保持任务为 in_progress
   - 当被阻塞时，创建一个新任务描述需要解决的问题
   - 如果出现以下情况，永远不要将任务标记为已完成：
     - 测试失败
     - 实施不完整
     - 遇到未解决的错误
     - 无法找到必要的文件或依赖项

4. **任务分解**：
   - 创建具体、可操作的项目
   - 将复杂任务分解为更小、可管理的步骤
   - 使用清晰、描述性的任务名称

有疑问时，使用此工具。主动进行任务管理展示了专注性，并确保您成功完成所有要求。""",
            parameters=parameters,
        )

    def save_todos(self, todos: List[TodoItem]):
        """保存待办事项列表到会话状态"""
        self.session_state.todos = json.dumps([todo.model_dump() for todo in todos], ensure_ascii=False, separators=(",", ":"))

    def read_todos(self) -> str:
        """从会话状态读取待办事项列表"""
        return text_result_of_todo_read(self.session_state.todos)

    def provide_system_reminder(self, prefix_content: List[dict], suffix_content: List[dict]):
        """提供系统提醒，包含当前待办事项列表"""
        todo_result_str = self.read_todos()
        suffix_content.append({"type": "text", "text": f"<system-reminder>\n{todo_result_str}\n</system-reminder>"})

    async def execute(self, params: ToolParams) -> ToolResult:
        """执行 todo 写入操作

        Args:
            params: 包含写入 todo 所需参数的字典

        Returns:
            ToolResult 对象，包含更新的 todo 列表
        """
        todos = params.get("todos", [])
        result = await todo_write(
            save_todos=lambda todo_items: self.save_todos(todo_items),
            todos=todos,
        )
        return result
