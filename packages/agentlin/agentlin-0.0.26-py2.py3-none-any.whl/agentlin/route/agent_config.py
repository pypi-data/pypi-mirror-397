import copy
import os
import re
from pydantic import BaseModel
from typing_extensions import Any, Union, Optional
from pathlib import Path

from loguru import logger
from xlin import ls, load_text, xmap_async, load_text

from agentlin.core.types import ToolData
from agentlin.core.config import parse_config_from_markdown
from agentlin.skills.core import SkillConfig, is_skill_md_file, load_skill



class CodeInterpreterConfig(BaseModel):
    jupyter_host: str  # Jupyter host URL
    jupyter_port: str  # Jupyter port
    jupyter_token: str  # Jupyter token
    jupyter_timeout: int  # Jupyter timeout
    jupyter_username: str  # Jupyter username


class BuiltInSubAgentConfig(BaseModel):
    subagents: list[str]


class FileSystemConfig(BaseModel):
    workspace_dir: str


class BuiltInToolConfig(BaseModel):
    CodeInterpreter: Optional[CodeInterpreterConfig] = None
    Task: Optional[BuiltInSubAgentConfig] = None
    FileSystem: Optional[FileSystemConfig] = None


class SubAgentConfig(BaseModel):
    """
    Configuration for a sub-agent.
    """

    id: str
    name: str
    description: str
    model: Optional[str] = None  # Optional model name
    developer_prompt: str
    code_for_agent: Optional[str] = None
    code_for_interpreter: Optional[str] = None
    allowed_tools: list[str] = ["*"]
    env: dict[str, Any] = {}


BUILTIN_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "CodeInterpreter",
            "description": "在受限、安全的沙盒环境中执行 Python 3 代码的解释器，可用于数据处理、科学计算、自动化脚本、可视化等任务，支持大多数标准库及常见第三方科学计算库。",
            "parameters": {
                "type": "object",
                "required": ["code"],
                "properties": {
                    "code": {
                        "type": "string",
                        "description": "要执行的 Python 代码",
                    }
                },
                "additionalProperties": False,
            },
            "strict": True,
        },
    },
    {
        "type": "function",
        "function": {
            "name": "Task",
            "description": """\
Launch a new task to handle complex, multi-step tasks autonomously.

## Available Agent Types
Available agent types and the tools they have access to:
{{subagents}}

## Alert
When using the Task tool, you must specify a 'name' parameter to select which agent to use.

When to use the Task tool:
- For complex, multi-step tasks that require autonomous handling.

Usage notes:
1. Launch multiple agents concurrently whenever possible to maximize performance.
2. The agent will return a single message back to you.
3. Each agent invocation is stateless.
4. Your prompt should contain a highly detailed task description.
5. Clearly tell the agent whether you expect it to write code or do research.""",
            "parameters": {
                "type": "object",
                "required": ["name", "description", "prompt"],
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "The type of specialized agent to use for this task",
                    },
                    "description": {
                        "type": "string",
                        "description": "A short (3-5 word) description of the task",
                    },
                    "prompt": {
                        "type": "string",
                        "description": "The task for the agent to perform",
                    },
                },
                "additionalProperties": False,
            },
            "strict": True,
        },
    },
    {
        "type": "function",
        "function": {
            "name": "Skill",
            "description": """\
Launch specific skill to handle specific task. Check if any of the available skills below can help complete the task more effectively.

## Available Skills
{{skills}}

## Alert
When loading skill, you must specify the 'skill_name' parameter to select the skill.
The skill's prompt will expand and provide detailed instructions.

When to load skill:
- You have thought to solve the task, and the task cannot be solved without the skill.
- In most situations, you load skill for domain-specific, detailed task.""",
            "parameters": {
                "type": "object",
                "required": ["skill_name"],
                "properties": {
                    "skill_name": {
                        "type": "string",
                        "description": "The name of specialized skill to load",
                    },
                },
                "additionalProperties": False,
            },
            "strict": True,
        },
    }
]

COMPACT_PROMPT = """\
Your task is to create a detailed summary of the conversation so far, paying close attention to the user's explicit requests and your previous actions.
This summary should be thorough in capturing technical details, code patterns, and architectural decisions that would be essential for continuing development work without losing context.

Before providing your final summary, wrap your analysis in <analysis> tags to organize your thoughts and ensure you've covered all necessary points. In your analysis process:

1. Chronologically analyze each message and section of the conversation. For each section thoroughly identify:
   - The user's explicit requests and intents
   - Your approach to addressing the user's requests
   - Key decisions, technical concepts and code patterns
   - Specific details like:
     - file names
     - full code snippets
     - function signatures
     - file edits

- Errors that you ran into and how you fixed them
- Pay special attention to specific user feedback that you received, especially if the user told you to do something differently.

2. Double-check for technical accuracy and completeness, addressing each required element thoroughly.

Your summary should include the following sections:

1. Primary Request and Intent: Capture all of the user's explicit requests and intents in detail
2. Key Technical Concepts: List all important technical concepts, technologies, and frameworks discussed.
3. Files and Code Sections: Enumerate specific files and code sections examined, modified, or created. Pay special attention to the most recent messages and include full code snippets where applicable and include a summary of why this file read or edit is important.
4. Errors and fixes: List all errors that you ran into, and how you fixed them. Pay special attention to specific user feedback that you received, especially if the user told you to do something differently.
5. Problem Solving: Document problems solved and any ongoing troubleshooting efforts.
6. All user messages: List ALL user messages that are not tool results. These are critical for understanding the users' feedback and changing intent.
7. Pending Tasks: Outline any pending tasks that you have explicitly been asked to work on.
8. Current Work: Describe in detail precisely what was being worked on immediately before this summary request, paying special attention to the most recent messages from both user and assistant. Include file names and code snippets where applicable.
9. Optional Next Step: List the next step that you will take that is related to the most recent work you were doing. IMPORTANT: ensure that this step is DIRECTLY in line with the user's explicit requests, and the task you were working on immediately before this summary request. If your last task was concluded, then only list next steps if they are explicitly in line with the users request. Do not start on tangential requests without confirming with the user first.
   If there is a next step, include direct quotes from the most recent conversation showing exactly what task you were working on and where you left off. This should be verbatim to ensure there's no drift in task interpretation.

Here's an example of how your output should be structured:

<example>
<analysis>
[Your thought process, ensuring all points are covered thoroughly and accurately]
</analysis>

<summary>
1. Primary Request and Intent:
   [Detailed description]

2. Key Technical Concepts:

   - [Concept 1]
   - [Concept 2]
   - [...]

3. Files and Code Sections:

   - [File Name 1]
     - [Summary of why this file is important]
     - [Summary of the changes made to this file, if any]
     - [Important Code Snippet]
   - [File Name 2]
     - [Important Code Snippet]
   - [...]

4. Errors and fixes:

   - [Detailed description of error 1]:
     - [How you fixed the error]
     - [User feedback on the error if any]
   - [...]

5. Problem Solving:
   [Description of solved problems and ongoing troubleshooting]

6. All user messages:

   - [Detailed non tool use user message]
   - [...]

7. Pending Tasks:

   - [Task 1]
   - [Task 2]
   - [...]

8. Current Work:
   [Precise description of current work]

9. Optional Next Step:
   [Optional Next step to take]

</summary>
</example>

Please provide your summary based on the conversation so far, following this structure and ensuring precision and thoroughness in your response.

There may be additional summarization instructions provided in the included context. If so, remember to follow these instructions when creating the above summary. Examples of instructions include:
<example>

## Compact Instructions

When summarizing the conversation focus on typescript code changes and also remember the mistakes you made and how you fixed them.
</example>

<example>
# Summary instructions
When you are using compact - please focus on test output and code changes. Include file reads verbatim.
</example>\
"""


async def load_subagent(path: str) -> Optional[SubAgentConfig]:
    """
    Load a sub-agent configuration from a markdown file.

    Expected format:
    ---
    name: agent-name
    description: Agent description
    model: model-name (optional)
    allowed_tools: ["tool1", "tool2"] (optional, defaults to ["*"])
    ---

    Agent prompt content here...

    ## Code for Agent (optional)
    ```python
    # Code specific for agent
    ```

    ## Code for Interpreter (optional)
    ```python
    # Code specific for interpreter
    ```
    """
    try:
        text = load_text(path)
        if not text:
            return None

        base_dir = Path(path).parent

        config, developer_prompt, code_for_agent, code_for_interpreter = parse_config_from_markdown(base_dir, text)

        # Extract required fields
        name = config.get("name")
        description = config.get("description")
        model = config.get("model")  # Optional model name

        if not name or not description:
            print(f"Missing required fields (name, description) in {path}")
            return None

        # Generate ID from file path
        file_path = Path(path)
        agent_id = file_path.stem

        return SubAgentConfig(
            id=agent_id,
            name=name,
            description=description,
            model=model,
            developer_prompt=developer_prompt,
            code_for_agent=code_for_agent,
            code_for_interpreter=code_for_interpreter,
            allowed_tools=config.get("allowed_tools", ["*"]),
            env=config.get("env", {}),
        )

    except ValueError as e:
        print(f"Error parsing config from {path}: {e}")
        return None
    except Exception as e:
        print(f"Error loading subagent from {path}: {e}")
        return None


async def load_subagents(dir_path: Union[str, list[str]]) -> list[SubAgentConfig]:
    """Load sub-agent configurations from a directory.

    Args:
        dir_path (Union[str, list[str]]): Directory path or list of directory paths containing sub-agent markdown files.

    Returns:
        list[SubAgentConfig]: List of loaded sub-agent configurations.
    """
    paths = ls(dir_path, filter=lambda f: f.name.endswith(".md"))
    if not paths:
        return []
    results = await xmap_async(paths, load_subagent, is_async_work_func=True, desc="Loading subagents")
    subagents: list[SubAgentConfig] = []
    for subagent in results:
        if subagent and isinstance(subagent, SubAgentConfig):
            subagents.append(subagent)
        else:
            logger.warning(f"Invalid subagent: {subagent}")
    return subagents


async def load_skills(dir_path: Union[str, list[str]]) -> list[SkillConfig]:
    """Load skill configuration from a markdown file.

    Args:
        dir_path (Union[str, list[str]]): Directory path or list of directory paths containing skill markdown files.

    Returns:
        list[SkillConfig]: List of loaded skill configurations.
    """
    paths = ls(dir_path, filter=lambda f: is_skill_md_file(f))
    if not paths:
        return []
    results = await xmap_async(paths, load_skill, is_async_work_func=True, desc="Loading skills")
    skills: list[SkillConfig] = []
    for skill in results:
        if skill and isinstance(skill, SkillConfig):
            skills.append(skill)
        else:
            logger.warning(f"Invalid skill: {skill}")
    return skills


class AgentConfig(BaseModel):
    agent_id: str
    name: str
    description: str
    developer_prompt: str
    code_for_agent: str
    code_for_interpreter: str
    allowed_tools: list[str] = ["*"]
    env: dict[str, Any] = {}
    tool_mcp_config: dict[str, Any] = {
        "mcpServers": {
            "aime_sse_server": {"url": "http://localhost:7778/tool_mcp"},
        }
    }

    model: str
    max_model_length: int
    max_response_length: int

    compress_prompt: str
    compress_model: str
    compress_threshold_token_ratio: float = 0.9  # 压缩上下文的触发比例

    inference_args: dict[str, Any] = {}

    # 内置工具列表
    builtin_tools: list[ToolData] = copy.deepcopy(BUILTIN_TOOLS)
    code_interpreter_config: CodeInterpreterConfig
    builtin_subagents: list[SubAgentConfig] = []
    builtin_skills: list[SkillConfig] = []

    @property
    def compress_threshold_tokens(self) -> int:
        """计算压缩上下文的触发 token 数量"""
        return int(self.compress_threshold_token_ratio * self.max_model_length)

    def get_builtin_tools(
        self,
        allowed_subagents: Optional[list[str]] = None,
        allowed_skills: Optional[list[str]] = None,
    ) -> list[ToolData]:
        """获取内置工具列表"""
        for tool in self.builtin_tools:
            if tool["function"]["name"] == "Task":
                # 如果内置工具中已经有 Task 工具，则更新 description
                subagents_texts = []
                subagent_names = []
                for subagent in self.builtin_subagents:
                    if allowed_subagents is not None and subagent.name not in allowed_subagents:
                        continue
                    # 只添加允许的子智能体
                    subagent_names.append(subagent.name)
                    subagents_texts.append(f"### {subagent.name}\nTools: {', '.join(subagent.allowed_tools)}\nDescription: {subagent.description}\n")
                subagents_text = "\n".join(subagents_texts)
                tool["function"]["description"] = tool["function"]["description"].replace("{{subagents}}", subagents_text)
                # print(tool)
                tool["function"]["parameters"]["properties"]["name"]["enum"] = subagent_names
                # "enum": ["A", "B"]
            elif tool["function"]["name"] == "Skill":
                # 如果内置工具中已经有 Skill 工具，则更新 description
                skills_texts = []
                skill_names = []
                for skill in self.builtin_skills:
                    if allowed_skills is not None and skill.name not in allowed_skills:
                        continue
                    # 只添加允许的技能
                    skill_names.append(skill.name)
                    skills_texts.append(f"### {skill.name}\nDescription: {skill.description}\n")
                skills_text = "\n".join(skills_texts)
                tool["function"]["description"] = tool["function"]["description"].replace("{{skills}}", skills_text)
                tool["function"]["parameters"]["properties"]["skill_name"]["enum"] = skill_names
                # "enum": ["A", "B"]
        return self.builtin_tools


def resolve_dir(base_dir: Path, builtin_dir: list[str]) -> Optional[Path]:
    resolved_dir = []
    if builtin_dir:
        if isinstance(builtin_dir, list):
            for subdir in builtin_dir:
                path = Path(subdir)
                if path.exists():
                    resolved_dir.append(path)
                elif (base_dir / path).exists():
                    resolved_dir.append(base_dir / path)
        elif isinstance(builtin_dir, str):
            path = Path(builtin_dir)
            if path.exists():
                resolved_dir.append(path)
            elif (base_dir / path).exists():
                resolved_dir.append(base_dir / path)
    return resolved_dir


async def load_agent_config(agent_path: Union[str, Path]) -> AgentConfig:
    """Load agent configuration from a path (file or directory).

    Layout (when a directory is provided):
    - [agent_path]/
      - subagents/           # optional, can be overridden by `builtin_subagents` in YAML
      - main.md              # required unless `agent_path` itself is a file path to this
      - compress_prompt.md    # optional, overrides default COMPACT_PROMPT

    Behavior:
    - If ``agent_path`` is a file, it's treated as the main agent config (``main.md``),
      and the working directory becomes its parent directory.
    - If ``agent_path`` is a directory, the loader expects ``main.md`` in that directory.
    - Merges environment variables from YAML key ``env`` with the function argument ``env``
      (function arg wins), then performs ``{{VAR}}`` substitution in code sections.
    - Loads builtin subagents from paths specified by YAML key ``builtin_subagents``
      (string or list). If a path isn't absolute, it's resolved relative to the working
      directory. Each subagent is a ``.md`` file parsed by ``load_subagents``.
    - Code Interpreter settings default from process env when not provided in YAML:
      JUPYTER_HOST, JUPYTER_PORT, JUPYTER_TOKEN, JUPYTER_TIMEOUT, JUPYTER_USERNAME.
    - Compact prompt is read from ``compress_prompt.md`` if present; otherwise uses
      ``COMPACT_PROMPT``.

    Args:
        agent_path (Union[str, Path]): Directory containing agent files or a direct path
            to ``main.md``.

    Raises:
        FileNotFoundError: If the main agent config file (``main.md``) cannot be found.

    Returns:
        AgentConfig: Fully populated agent configuration object.
    """
    agent_path = Path(agent_path)
    if agent_path.is_file():
        main_agent_config = agent_path
        base_dir = agent_path.parent
    else:
        base_dir = agent_path
        main_agent_config = base_dir / "main.md"
    if not main_agent_config.exists():
        raise FileNotFoundError(f"Main agent config not found: {main_agent_config}")

    text = load_text(main_agent_config)
    config, developer_prompt, code_for_agent, code_for_interpreter = parse_config_from_markdown(base_dir, text)

    # 内建工具的配置
    builtin_tools = BUILTIN_TOOLS
    # 内建子智能体的配置
    builtin_subagents_dir = config.get("builtin_subagents", ["agents"])
    builtin_subagents_dirpath = resolve_dir(base_dir, builtin_subagents_dir)
    builtin_subagents = await load_subagents(builtin_subagents_dirpath)
    # 加载技能配置
    builtin_skills_dir = config.get("builtin_skills", ["skills"])
    builtin_skills_dirpath = resolve_dir(base_dir, builtin_skills_dir)
    builtin_skills = await load_skills(builtin_skills_dirpath)

    # 代码解释器的配置
    code_interpreter_config: dict = config.get("code_interpreter_config", {})
    if "jupyter_host" not in code_interpreter_config or not code_interpreter_config["jupyter_host"]:
        code_interpreter_config["jupyter_host"] = os.getenv("JUPYTER_HOST", "localhost")
    if "jupyter_port" not in code_interpreter_config or not code_interpreter_config["jupyter_port"]:
        code_interpreter_config["jupyter_port"] = os.getenv("JUPYTER_PORT", "8888")
    if "jupyter_token" not in code_interpreter_config or not code_interpreter_config["jupyter_token"]:
        code_interpreter_config["jupyter_token"] = os.getenv("JUPYTER_TOKEN", "")
    if "jupyter_timeout" not in code_interpreter_config or not code_interpreter_config["jupyter_timeout"]:
        code_interpreter_config["jupyter_timeout"] = os.getenv("JUPYTER_TIMEOUT", 60)
    if "jupyter_username" not in code_interpreter_config or not code_interpreter_config["jupyter_username"]:
        code_interpreter_config["jupyter_username"] = os.getenv("JUPYTER_USERNAME", "user")
    code_interpreter_config = CodeInterpreterConfig.model_validate(code_interpreter_config)

    # 压缩上下文的配置
    compress_prompt_filepath = base_dir / "compress_prompt.md"
    if compress_prompt_filepath.exists():
        compress_prompt = load_text(compress_prompt_filepath)
    else:
        compress_prompt = COMPACT_PROMPT

    return AgentConfig(
        agent_id=base_dir.name,
        name=config.get("name", "unknown"),
        description=config.get("description", ""),
        developer_prompt=developer_prompt,
        code_for_agent=code_for_agent or "",
        code_for_interpreter=code_for_interpreter or "",
        compress_prompt=compress_prompt,
        compress_model=config.get("compress_model", "gpt-4o"),
        compress_threshold_token_ratio=config.get("compress_threshold_token_ratio", 0.9),
        allowed_tools=config.get("allowed_tools", ["*"]),
        model=config.get("model"),
        max_model_length=config.get("max_model_length", 128000),
        max_response_length=config.get("max_response_length", 8*1024),
        tool_mcp_config=config.get("tool_mcp_config", {}),
        code_interpreter_config=code_interpreter_config,
        inference_args=config.get("inference_args", {}),
        builtin_tools=builtin_tools,
        builtin_subagents=builtin_subagents,
        builtin_skills=builtin_skills,
        env=config.get("env", {}),
    )


async def get_agent_id(client_id: str) -> str:
    frontend_to_agent_map = {
        "AInvest": "aime",
        "AIME": "aime",
        "iWencai": "wencai",
        "ARC-AGI": "agi",
    }
    return frontend_to_agent_map.get(client_id, "aime")


async def get_agent_config(agent_id: str) -> AgentConfig:
    """获取指定agent的配置"""
    home_path = Path(__file__).parent.parent.parent
    # 映射agent_id到对应的配置路径
    path = home_path / "assets" / agent_id
    return await load_agent_config(path)
