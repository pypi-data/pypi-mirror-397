import json
import subprocess
import traceback
import importlib
from importlib import util as import_util
import inspect
from typing import Any, Dict, List, Optional, Union, Set, Type

from fastmcp import Client as McpClient
from fastmcp.tools.tool import ToolResult as McpToolResult, Tool as BaseMcpTool
from mcp.types import Tool as McpTool
from mcp.types import ContentBlock, TextContent, ImageContent, AudioContent, ResourceLink, EmbeddedResource
from loguru import logger
from pydantic import BaseModel, PrivateAttr

from agentlin.code_interpreter.types import ToolResponse
from agentlin.core.types import (
    ContentData,
    AudioContentItem,
    ImageContentItem,
    TextContentItem,
    FileContentItem,
    ContentItem,
    BaseTool,
    FunctionDefinition,
    FunctionParameters,
    ToolParams,
    ToolResult,
    sanitize_parameters,
)

def tool_result_of_text(text: str) -> ToolResult:
    message_content = [{"type": "text", "text": text}]
    block_list = [{"type": "text", "text": text}]
    return ToolResult(
        message_content=message_content,
        block_list=block_list,
    )

def tool_result_of_internal_error(text: str) -> ToolResult:
    message_content = [{"type": "text", "text": text}]
    block_list = []
    return ToolResult(
        message_content=message_content,
        block_list=block_list,
    )

def tool_response_of_text(text: str) -> ToolResponse:
    return ToolResponse(
        message_content=[{"type": "text", "text": text}],
        block_list=[{"type": "text", "text": text}],
    )

def tool_response_of_internal_error(text: str) -> ToolResponse:
    return ToolResponse(
        message_content=[{"type": "text", "text": text}],
        block_list=[],
    )


def message_content_to_mcp_content(message_content: List[ContentData]) -> List[ContentBlock]:
    mcp_content: List[ContentBlock] = []
    for c in message_content:
        if c["type"] == "text":
            mcp_content.append(TextContent(type="text", text=c["text"]))
        elif c["type"] == "image_url":
            mcp_content.append(ImageContent(type="image", mimeType="image/png", data=c["image_url"]["url"]))
        elif c["type"] == "input_audio":
            mcp_content.append(AudioContent(type="audio", mimeType="audio/wav", data=c["input_audio"]["data"]))
        # TODO 暂不支持
        # elif c["type"] == "link":
        #     mcp_content.append(ResourceLink(url=c["url"], title=c.get("title", "")))
        # elif c["type"] == "embed":
        #     mcp_content.append(EmbeddedResource(url=c["url"], title=c.get("title", "")))
    return mcp_content


class TransformedMcpTool(BaseMcpTool):
    # Use PrivateAttr to prevent Pydantic from generating schema for arbitrary type BaseTool
    _base_tool: BaseTool = PrivateAttr()

    def __init__(self, base_tool: BaseTool):
        super().__init__(
            name=base_tool.name,
            title=base_tool.title,
            description=base_tool.description,
            parameters=base_tool.parameters,
        )
        # Assign after BaseModel init per Pydantic best practices for PrivateAttr
        self._base_tool = base_tool

    async def run(self, arguments: dict[str, Any]) -> McpToolResult:
        result = await self._base_tool.execute(arguments)
        mcp_content = []
        structured_content = {}
        if result.message_content:
            mcp_content = message_content_to_mcp_content(result.message_content)
        if result.block_list:
            structured_content["block_list"] = result.block_list
        if result.data:
            structured_content["data"] = result.data
        return McpToolResult(
            content=mcp_content,
            structured_content=structured_content,
        )


class GenerateStructuredOutputTool(BaseTool):
    NAME = "GenerateStructuredOutput"

    def __init__(self, structured_output: BaseModel):
        parameters = structured_output.model_json_schema()
        if "additionalProperties" not in parameters:
            parameters["additionalProperties"] = False
        super().__init__(
            name=self.NAME,
            title=self.NAME,
            description="Generate structured output according to the specified schema. You should call this tool to submit the final structured result.",
            parameters=parameters,
            strict=True,
        )
        self.structured_output = structured_output

    async def execute(self, params: ToolParams) -> ToolResult:
        # this should never be executed.
        try:
            output_instance = self.structured_output.model_validate(params)
            output_dict = output_instance.model_dump()
            content = json.dumps(output_dict, ensure_ascii=False, indent=2)
            return tool_result_of_text(content)
        except Exception as e:
            error_message = f"Failed to validate structured output: {e}"
            logger.error(error_message)
            return tool_result_of_text(error_message)


class DiscoveredMcpTool(BaseTool):
    def __init__(self, client: McpClient, tool: McpTool):
        self.client = client
        self.tool = tool
        parameters = tool.inputSchema
        if "additionalProperties" not in parameters:
            parameters["additionalProperties"] = False
        super().__init__(
            name=tool.name,
            title=tool.title,
            description=tool.description,
            parameters=parameters,
            strict=True,
        )

    async def execute(self, params: ToolParams) -> ToolResult:
        async with self.client:
            result = await self.client.call_tool(
                name=self.tool.name,
                arguments=params,
            )
        content = result.content
        structured_content = result.structured_content
        # logger.debug(json.dumps(content, indent=2, ensure_ascii=False))
        # logger.debug(json.dumps(structured_content, indent=2, ensure_ascii=False))

        message_content: list[ContentData] = []
        for c in content:
            if isinstance(c, TextContent):
                message_content.append({"type": "text", "text": c.text})
            elif isinstance(c, ImageContent):
                message_content.append({"type": "image_url", "image_url": {"url": f"data:{c.mimeType};base64,{c.data}"}})
            elif isinstance(c, AudioContent):
                message_content.append({"type": "input_audio", "input_audio": {"data": f"data:{c.mimeType};base64,{c.data}"}})
            # TODO 暂不支持
            # elif isinstance(c, ResourceLink):
            #     message_content.append({"type": "link", "url": c.url, "title": c.title})
            # elif isinstance(c, EmbeddedResource):
            #     message_content.append({"type": "embed", "url": c.url, "title": c.title})

        block_list = []
        if structured_content:
            if "message_content" in structured_content:
                message_content = structured_content.pop("message_content", [])
            block_list = structured_content.pop("block_list", [])
        if not block_list:
            block_list = message_content
        return ToolResult(
            message_content=message_content,
            block_list=block_list,
        )


def _format_default(param: inspect.Parameter) -> str:
    """Format parameter with default value for display."""
    if param.default is inspect._empty:  # type: ignore[attr-defined]
        return f"{param.name}=<required>"
    dv = param.default
    if isinstance(dv, str):
        return f"{param.name}='{dv}'"
    return f"{param.name}={dv}"


def _resolve_module_and_class(tool_path: str) -> tuple[str, Optional[str]]:
    """
    Resolve module path and optional class name from tool_path.

    Supported forms:
    - "bash" -> module: agentlin.tools.builtin.file_system_tools + class by name
    - "bash-tool" -> module: agentlin.tools.tool_bash
    - "file_system_tools:bash" -> module: agentlin.tools.builtin.file_system_tools + class by name
    - "file_system_tools:BashTool" -> module: agentlin.tools.builtin.file_system_tools + class
    - "agentlin.tools.tool_bash" -> module: agentlin.tools.tool_bash
    - "agentlin.tools.tool_bash:BashTool" -> module + class
    """
    module_part = tool_path
    class_part: Optional[str] = None

    if ":" in tool_path:
        module_part, class_part = tool_path.split(":", 1)

    # normalize hyphens to underscores for module import
    module_part = module_part.replace("-", "_")

    # If it's not a fully qualified path, try unprefixed first, then fallback to agentlin.tools
    if not module_part.startswith("agentlin."):
        # 优先尝试 builtin 子包（不带 tool_ 前缀）
        # 因为 builtin 包中的模块没有 tool_ 前缀
        base_name_without_prefix = module_part.replace("tool_", "")
        base_name_with_prefix = f"tool_{base_name_without_prefix}" if not module_part.startswith("tool_") else module_part

        fallbacks = [
            # 首先尝试 builtin 包，不带 tool_ 前缀
            f"agentlin.tools.builtin.{base_name_without_prefix}",
            # 然后尝试顶层 tools 包，带 tool_ 前缀
            f"agentlin.tools.{base_name_with_prefix}",
            # 最后尝试全局可导入，带 tool_ 前缀
            base_name_with_prefix,
        ]

        for fallback in fallbacks:
            # If fallback exists, use it; otherwise still return fallback and let caller raise a clear error
            try:
                if import_util.find_spec(fallback) is not None:
                    return fallback, class_part
            except Exception:
                continue
        # 如果都找不到，返回第一个 fallback 让调用者报错
        return fallbacks[0], class_part

    return module_part, class_part


def _search_tool_by_name(tool_name: str) -> Optional[tuple[str, str]]:
    """
    Search for a tool by its tool.name across all available modules.

    Args:
        tool_name: The tool name to search for (case-insensitive)

    Returns:
        Tuple of (tool_prefer_name, class_name) if found, None otherwise
        The tool_prefer_name is the simplified name from list_tools_detailed that can be used for loading
    """
    tool_name_lower = tool_name.lower()
    details = list_tools_detailed()

    for tool_info in details:
        module_path = tool_info.get("module")
        prefer_name = tool_info.get("prefer") or tool_info.get("name")
        if not module_path or not prefer_name:
            continue

        try:
            mod = importlib.import_module(module_path)
            for _, obj in inspect.getmembers(mod, inspect.isclass):
                try:
                    if issubclass(obj, BaseTool) and obj is not BaseTool:
                        # Try to instantiate and check name
                        temp_instance = obj()
                        if hasattr(temp_instance, 'name') and temp_instance.name.lower() == tool_name_lower:
                            logger.debug(f"Found tool '{tool_name}' in module '{module_path}' as class '{obj.__name__}'")
                            return prefer_name, obj.__name__
                except Exception:
                    continue
        except Exception:
            continue

    return None


def _try_load_local_tool(tool_path: str) -> Optional[str]:
    """
    尝试从指定路径加载本地工具。

    支持的路径格式：
    - 相对路径：tools/custom, ./tools/bash, toolsets/arxiv
    - 绝对路径：/path/to/tool_dir

    如果路径指向一个有效的工具目录：
    1. 将工具目录添加到 sys.path
    2. 返回可导入的模块名（tool_* 格式）

    返回 None 表示不是本地路径或找不到有效工具。
    """
    import sys
    import os
    from pathlib import Path

    # 提取路径（去除可能的类名后缀）
    base_path = tool_path.split(":")[0] if ":" in tool_path else tool_path

    # 判断是否看起来像一个路径（包含 / 或 \ 或以 . 开头）
    if not ("/" in base_path or "\\" in base_path or base_path.startswith(".")):
        return None

    try:
        # 尝试多个路径解析策略
        candidate_paths = []

        # 1. 相对于当前工作目录
        cwd_path = Path(base_path).resolve()
        candidate_paths.append(cwd_path)

        # 2. 如果是相对路径，也尝试相对于项目根目录
        if not Path(base_path).is_absolute():
            # 查找项目根目录（包含 pyproject.toml 或 .git 的目录）
            current = Path.cwd()
            for _ in range(10):  # 最多向上查找10层
                if (current / "pyproject.toml").exists() or (current / ".git").exists():
                    project_root_path = (current / base_path).resolve()
                    if project_root_path != cwd_path:
                        candidate_paths.append(project_root_path)
                    break
                parent = current.parent
                if parent == current:  # 已到文件系统根目录
                    break
                current = parent

        # 尝试每个候选路径
        tool_dir = None
        for candidate in candidate_paths:
            if candidate.exists() and candidate.is_dir():
                tool_dir = candidate
                logger.debug(f"Found valid directory at {tool_dir}")
                break
            else:
                logger.debug(f"Path {candidate} does not exist or is not a directory")

        if not tool_dir:
            return None

        # 查找 tool_* 模块
        tool_module_name = None
        for item in tool_dir.iterdir():
            # 查找 tool_*.py 文件
            if item.is_file() and item.suffix == ".py" and item.stem.startswith("tool_"):
                tool_module_name = item.stem
                break
            # 查找 tool_*/ 包
            if item.is_dir() and item.name.startswith("tool_") and (item / "__init__.py").exists():
                tool_module_name = item.name
                break

        if not tool_module_name:
            logger.debug(f"Directory {tool_dir} found, but no tool_* module found (files: {[f.name for f in tool_dir.iterdir()]})")
            return None

        # 将工具目录添加到 sys.path（如果尚未添加）
        tool_dir_str = str(tool_dir)
        if tool_dir_str not in sys.path:
            sys.path.insert(0, tool_dir_str)
            logger.debug(f"Added {tool_dir_str} to sys.path")

        logger.info(f"Found local tool module: {tool_module_name} in {tool_dir}")
        return tool_module_name

    except Exception as e:
        logger.debug(f"Error while trying to load local tool from path {base_path}: {e}")
        return None


def _pick_tool_class(module, class_name: Optional[str]) -> Union[Type[BaseTool], List[Type[BaseTool]]]:
    """
    Pick the appropriate tool class(es) from module.

    Supports multiple ways to specify a tool:
    1. By class name: "BashTool" - returns single class
    2. By tool.name (case-insensitive): "bash", "Bash" - returns single class
    3. Auto-selection if no name provided - returns all tool classes
    """
    candidates = []
    for _, obj in inspect.getmembers(module, inspect.isclass):
        try:
            if issubclass(obj, BaseTool) and obj is not BaseTool:
                candidates.append(obj)
        except TypeError:
            continue

    if class_name:
        # Try exact class name match first
        for c in candidates:
            if c.__name__ == class_name:
                return c

        # Try to instantiate candidates and match by tool.name (case-insensitive)
        class_name_lower = class_name.lower()
        for c in candidates:
            try:
                # Instantiate with no args to check the tool name
                temp_instance = c()
                if hasattr(temp_instance, 'name') and temp_instance.name.lower() == class_name_lower:
                    logger.debug(f"Found tool class {c.__name__} by tool.name '{temp_instance.name}' matching '{class_name}'")
                    return c
            except Exception as e:
                # If instantiation fails, skip this candidate
                logger.debug(f"Could not instantiate {c.__name__} for name matching: {e}")
                continue

        raise AttributeError(
            f"Class or tool name '{class_name}' not found in module '{module.__name__}'. "
            f"Available classes: {[c.__name__ for c in candidates]}"
        )

    if not candidates:
        raise AttributeError(f"No BaseTool subclass found in module '{module.__name__}'. Provide a load_tools() function or specify a class via '<module>:<ClassName>'.")

    # If no class_name specified, return all candidates
    return candidates


def load_tools(tool_path: str, **tool_args) -> List[BaseTool]:
    """
    动态加载工具模块并实例化工具对象。

    优先策略：
    1) 若 tool_path 是路径（包含 / 或 \），则从该路径加载本地工具
    2) 若模块定义了 load_tools(**kwargs) -> List[BaseTool]，则调用并返回结果
    3) 否则在模块中查找 BaseTool 的子类并尝试用 **kwargs 实例化（可通过 '<module>:<Class>' 指定类）

    参数示例：
    - "bash" 或 "bash-tool" (工具名)
    - "agentlin.tools.tool_bash" (完整模块路径)
    - "bash:BashTool" 或 "agentlin.tools.tool_bash:BashTool" (指定类)
    - "tools/custom" (本地路径 - 相对路径)
    - "./tools/bash" (本地路径 - 相对路径)
    - "/absolute/path/to/tool_dir" (本地路径 - 绝对路径)
    - "tools/custom:CustomTool" (本地路径 + 指定类)

    返回：
        工具实例列表。如果模块只有一个工具类，返回单个实例的列表。
    """
    logger.info(f"Loading tools from {tool_path}")

    # Try to load from local path first (if tool_path looks like a path)
    local_tool_module = _try_load_local_tool(tool_path)
    if local_tool_module:
        module_name = local_tool_module
        class_name = None
        if ":" in tool_path:
            _, class_name = tool_path.split(":", 1)
        logger.info(f"Loading from local path: {module_name}")
    else:
        module_name, class_name = _resolve_module_and_class(tool_path)
        logger.info(f"Tool module name {module_name}")

    if class_name:
        logger.info(f"Requested tool class {class_name}")

    if tool_args:
        logger.info(f"Tool args provided ({len(tool_args)} total): {tool_args}")
    else:
        logger.info("No tool args provided, using defaults")

    try:
        module = importlib.import_module(module_name)

        # Path A: explicit module-level load_tools (only if no specific class requested)
        if not class_name and hasattr(module, "load_tools") and inspect.isfunction(module.load_tools):  # type: ignore[attr-defined]
            tool_load_func = module.load_tools  # type: ignore[attr-defined]
            try:
                sig = inspect.signature(tool_load_func)
                defaults_info = [_format_default(param) for param in sig.parameters.values()]
                if defaults_info:
                    logger.debug("Tool defaults: " + ", ".join(defaults_info))

                if tool_args:
                    provided_params = set(tool_args.keys())
                    all_params = set(sig.parameters.keys())
                    default_params = all_params - provided_params
                    default_values = []
                    for name in default_params:
                        p = sig.parameters[name]
                        if p.default is not inspect._empty:  # type: ignore[attr-defined]
                            default_values.append(_format_default(p))
                    if default_values:
                        logger.info("Using defaults for: " + ", ".join(default_values))
                elif sig.parameters:
                    logger.info("All parameters will use their default values")
            except Exception as e:  # pragma: no cover - best effort logging
                logger.debug(f"Could not inspect tool load function signature: {e}")

            logger.debug(f"Calling {module_name}.load_tools with {len(tool_args)} arguments")
            tools = tool_load_func(**tool_args)
            if not isinstance(tools, list):
                tools = [tools]
            for tool in tools:
                if not isinstance(tool, BaseTool):
                    logger.warning(f"Object returned by {module_name}.load_tools is not a BaseTool; got {type(tool).__name__}")
            logger.info(f"Successfully loaded {len(tools)} tool(s) from {tool_path}")
            return tools

        # Path B: find a subclass of BaseTool and instantiate directly
        tool_class_result = _pick_tool_class(module, class_name)

        # Handle both single class and list of classes
        tool_classes = tool_class_result if isinstance(tool_class_result, list) else [tool_class_result]

        loaded_tools = []
        for tool_class in tool_classes:
            try:
                sig = inspect.signature(tool_class)
                defaults_info = [_format_default(param) for param in list(sig.parameters.values())[1:]]  # skip 'self'
                if defaults_info:
                    logger.debug(f"Constructor defaults for {tool_class.__name__}: " + ", ".join(defaults_info))
            except Exception as e:  # pragma: no cover - best effort logging
                logger.debug(f"Could not inspect constructor signature: {e}")

            # Validate required parameters
            missing_required = []
            try:
                sig = inspect.signature(tool_class)
                for name, p in list(sig.parameters.items())[1:]:  # skip 'self'
                    if p.default is inspect._empty and name not in tool_args:
                        missing_required.append(name)
            except Exception:
                # If we cannot inspect, attempt best-effort construction
                pass

            if missing_required:
                logger.warning(f"Skipping {tool_class.__name__}: missing required init params: {', '.join(missing_required)}")
                continue

            try:
                tool_instance = tool_class(**tool_args)
                loaded_tools.append(tool_instance)
                logger.info(f"Successfully loaded tool {tool_instance.__class__.__name__}")
            except Exception as e:
                logger.warning(f"Failed to instantiate {tool_class.__name__}: {e}")
                continue

        if not loaded_tools:
            raise RuntimeError(f"Failed to load any tools from {tool_path}")

        logger.info(f"Successfully loaded {len(loaded_tools)} tool(s) from {tool_path}")
        return loaded_tools

    except (ImportError, AttributeError) as e:
        # If import fails or no class found, and no ":" in original path, try searching by tool name
        if ":" not in tool_path and "/" not in tool_path and "\\" not in tool_path:
            logger.debug(f"Failed to load directly, trying to search by tool name: {tool_path}")
            search_result = _search_tool_by_name(tool_path)
            if search_result:
                found_tool_name, found_class = search_result
                logger.info(f"Found tool '{tool_path}' as '{found_tool_name}:{found_class}'")
                # Retry loading with the found tool name and class
                return load_tools(f"{found_tool_name}:{found_class}", **tool_args)

        # If it's an ImportError, provide import-specific message
        if isinstance(e, ImportError):
            error_message = f"Could not import '{tool_path}' tool. Ensure the package/module '{module_name}' is importable.\n{e}"
        else:
            error_message = f"Failed to load tool '{tool_path}': {str(e)}"

        logger.error(error_message)
        raise ValueError(error_message) from e
    except Exception as e:
        error_message = f"Failed to load tool {tool_path} with args {tool_args}: {str(e)}"
        logger.error(error_message)
        raise RuntimeError(error_message) from e


def list_tools() -> list[str]:
    """
    列出可用的工具名称。

    搜索范围与约定：
    - 内置模块包：agentlin.tools 以及 agentlin.tools.builtin 下的模块
      满足以下任一条件即视为工具模块：
        1) 模块中存在函数 load_tools
        2) 模块中定义了 BaseTool 的子类
    - 系统可导入的顶层模块名形如 tool_*（例如 tool_bash、tool_chart）
      会转换为友好名称（将前缀 tool_ 去掉，下划线转连字符），如 bash、chart。
    - 工作区本地目录 tools/*（如果存在），若子目录内含有以 tool_ 开头的包或 .py 文件，
      则将该子目录名加入列表（用于提示本地可安装的工具）。

    返回：
        工具名称的去重列表，已按字母排序。
    """
    details = list_tools_detailed()
    names = sorted({d["name"] for d in details})
    return names


def list_tools_detailed() -> list[dict[str, Optional[str]]]:
    """
    返回包含详细信息的工具列表，用于 UI/CLI 展示与去重判断。

    字段：
    - name: 友好名称（如 'bash', 'chart'）
    - module: 完整模块路径（如 'agentlin.tools.tool_bash' 或 'tool_chart'），本地目录则可能为 None
    - origin: 'builtin' | 'external' | 'local'
    - source: 内部源标识（如 'package:agentlin.tools', 'package:agentlin.tools.builtin', 'import:tool_*', 'local:tools/<dir>'）
    - importable: bool 是否可被 importlib 正常导入
    - classes: BaseTool 子类名列表
    - has_factory: 是否存在模块级 load_tools
    - default_params_summary: 从类构造器或工厂函数推断的默认参数摘要（简要字符串）
    - prefer: 推荐加载标识（通常与 name 相同，可作为 load_tools 的参数）
    """
    import pkgutil
    from pathlib import Path

    results: list[dict] = []

    EXCLUDE_BUILTIN_NAMES = {
        "__main__",
        "__init__",
        "core",  # 核心功能，不是具体工具
        "validate",
        "scheduler",
        "rag",
        "stateful_browser",
        "stateful_document",
        "stateful_memory",
        "server",
    }

    def _inspect_module(module_name: str, require_tool_class: bool = False) -> tuple[bool, list[str], bool, str]:
        """返回 (has_tool, class_names, has_factory, default_params_summary)。

        Args:
            module_name: 模块名
            require_tool_class: 如果为 True，只有存在 BaseTool 子类时才认为是有效工具
        """
        try:
            mod = importlib.import_module(module_name)
        except Exception as e:
            logger.error(e)
            return False, [], False, ""

        has_factory = hasattr(mod, "load_tools") and inspect.isfunction(getattr(mod, "load_tools", None))
        class_names: list[str] = []
        for _, obj in inspect.getmembers(mod, inspect.isclass):
            try:
                if inspect.isabstract(obj):
                    continue
                if issubclass(obj, BaseTool) and obj is not BaseTool:
                    class_names.append(obj.__name__)
            except Exception:
                continue

        default_summary = ""
        # 优先展示工厂函数参数，其次展示首个类构造参数
        if has_factory:
            try:
                sig = inspect.signature(getattr(mod, "load_tools"))
                parts = [_format_default(p) for p in sig.parameters.values()]
                default_summary = ", ".join(parts)
            except Exception:
                pass
        elif class_names:
            try:
                cls = getattr(mod, class_names[0])
                sig = inspect.signature(cls)
                parts = [_format_default(p) for p in list(sig.parameters.values())[1:]]  # 跳过 self
                default_summary = ", ".join(parts)
            except Exception:
                pass

        # 如果要求必须有工具类，则只在有类时才返回 True
        if require_tool_class:
            has_tool = len(class_names) > 0
        else:
            has_tool = len(class_names) > 0 or has_factory
        return has_tool, class_names, has_factory, default_summary

    # 1) builtin: agentlin.tools
    # 注意：这里大多数 tool_*.py 是函数库而非工具类，所以不需要列出
    # 只列出那些确实包含 BaseTool 子类的模块
    try:
        import agentlin.tools as _tools_pkg  # type: ignore
        for mod_info in pkgutil.iter_modules(_tools_pkg.__path__):  # type: ignore[attr-defined]
            base = mod_info.name
            if base in EXCLUDE_BUILTIN_NAMES:
                continue
            # Skip tool_ prefix for display name
            display_name = base[len("tool_"):] if base.startswith("tool_") else base
            full = f"{_tools_pkg.__name__}.{base}"
            # 对于顶层 tools 包，要求必须有工具类才列出
            has_tool, class_names, has_factory, default_summary = _inspect_module(full, require_tool_class=True)
            if has_tool:
                results.append({
                    "name": display_name,
                    "module": full,
                    "origin": "builtin",
                    "source": "package:agentlin.tools",
                    "importable": import_util.find_spec(full) is not None,
                    "classes": class_names,
                    "has_factory": has_factory,
                    "default_params_summary": default_summary,
                    "prefer": display_name,
                })
    except Exception:
        pass

    # 1b) builtin: agentlin.tools.builtin
    try:
        import agentlin.tools.builtin as _builtin_pkg  # type: ignore
        for mod_info in pkgutil.iter_modules(_builtin_pkg.__path__):  # type: ignore[attr-defined]
            base = mod_info.name
            if base in EXCLUDE_BUILTIN_NAMES:
                continue
            display_name = base[len("tool_"):] if base.startswith("tool_") else base
            full = f"{_builtin_pkg.__name__}.{base}"
            has_tool, class_names, has_factory, default_summary = _inspect_module(full)
            if class_names:
                results.append({
                    "name": display_name,
                    "module": full,
                    "origin": "builtin",
                    "source": "package:agentlin.tools.builtin",
                    "importable": import_util.find_spec(full) is not None,
                    "classes": class_names,
                    "has_factory": has_factory,
                    "default_params_summary": default_summary,
                    "prefer": display_name,
                })
    except Exception:
        pass

    # 2) external: 顶层 tool_* 包
    try:
        for _finder, name, _ispkg in pkgutil.iter_modules():
            if not name.startswith("tool_"):
                continue
            full = name
            has_tool, class_names, has_factory, default_summary = _inspect_module(full)
            if has_tool:
                friendly = name[len("tool_"):].replace("_", "-")
                results.append({
                    "name": friendly,
                    "module": full,
                    "origin": "external",
                    "source": "import:tool_*",
                    "importable": import_util.find_spec(full) is not None,
                    "classes": class_names,
                    "has_factory": has_factory,
                    "default_params_summary": default_summary,
                    "prefer": friendly,
                })
    except Exception:
        pass

    # 3) local: 工作区 tools 目录
    try:
        current_file = Path(__file__).resolve()
        repo_root = current_file
        for _ in range(5):
            if (repo_root / "pyproject.toml").exists() or (repo_root / ".git").exists():
                break
            repo_root = repo_root.parent

        local_tools_dir = repo_root / "tools"
        if local_tools_dir.exists() and local_tools_dir.is_dir():
            for child in local_tools_dir.iterdir():
                if not child.is_dir():
                    continue
                # 查找 tool_*
                has_tool_file = False
                tool_entry = None
                for p in child.iterdir():
                    if p.is_file() and p.suffix == ".py" and p.stem.startswith("tool_"):
                        has_tool_file = True
                        tool_entry = p.name
                        break
                    if p.is_dir() and p.name.startswith("tool_") and (p / "__init__.py").exists():
                        has_tool_file = True
                        tool_entry = p.name
                        break
                if has_tool_file:
                    results.append({
                        "name": child.name,
                        "module": None,
                        "origin": "local",
                        "source": f"local:tools/{child.name}",
                        "importable": False,
                        "classes": [],
                        "has_factory": False,
                        "default_params_summary": "",
                        "prefer": child.name,
                    })
    except Exception:
        pass

    # 去除明显的伪项
    results = [r for r in results if r.get("name") not in {"__main__", "__init__"}]

    # 排序：按 name, origin
    results.sort(key=lambda r: (r.get("name", ""), r.get("origin", "")))
    return results
