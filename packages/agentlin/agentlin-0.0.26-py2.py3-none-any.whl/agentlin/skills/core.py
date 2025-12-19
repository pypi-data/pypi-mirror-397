"""
Skill loading utilities.

This module provides a configuration loader for Skills, mirroring the
agent configuration loader in `agentlin.route.agent_config.load_agent_config`,
and dynamic tool loading patterns similar to `agentlin.tools.core.load_tools`.

Updated design:
- Skill is no longer a standalone Python package. It is a descriptive markdown
  file (skill_*.md) that typically ships with a toolset plugin or an
  environment plugin.
- Default behavior loads tools by names from `allowed_tools` via
  `agentlin.tools.core.load_tools`.
- We DO NOT auto-discover or import `skill_*.py` modules in the same folder
  anymore. If the YAML explicitly provides `skill_module/module/tools_module`
  ("module_path"), we will import that module and attempt to load tools from it.

Expected skill layout now:

        any_folder/
        └── skill_<name>.md   # required: YAML front matter + skill prompt

`load_skill_config()` parses skill_*.md and returns a SkillConfig with prompt
and metadata. `load_skill()` loads tools from the explicitly-specified module
(if provided), otherwise falls back to loading by names from `allowed_tools`.
"""

from __future__ import annotations

import importlib
import importlib.util
import inspect
import os
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple, Type, Union

import yaml
from loguru import logger
from pydantic import BaseModel, Field, ConfigDict
from xlin import load_text

# Reuse BaseTool from core types and tool loader from tools.core
from agentlin.core.config import apply_env, parse_config_from_markdown
from agentlin.core.types import BaseTool
from agentlin.tools.core import load_tools as load_tools_by_name


class SkillConfig(BaseModel):
    """Configuration object representing a Skill.

    Fields
    - skill_id: Derived from the directory (package) name.
    - name: Human-friendly name from YAML front matter.
    - description: Short description from YAML front matter.
    - prompt: The prompt content (markdown) after YAML front matter.
    - allowed_tools: Optional hint list from YAML for which tool names are allowed (informational).
    - tools: Loaded tool instances (BaseTool) discovered from the skill module.
    - metadata: Additional arbitrary fields in YAML front matter are preserved here.
    - module_path: Optional import path or file path to the skill module (if discovered).
    """

    model_config = ConfigDict(arbitrary_types_allowed=True)

    skill_id: str
    name: str
    description: str = ""
    prompt: str
    code_for_agent: Optional[str] = None
    code_for_interpreter: Optional[str] = None
    allowed_tools: List[str] = Field(default_factory=lambda: ["*"])
    env: dict[str, Any] = Field(default_factory=dict)
    tools: List[BaseTool] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    module_path: Optional[str] = None


def _pick_skill_md(base_dir: Path) -> Path:
    """Pick a skill_*.md file in base_dir with reasonable heuristics.

    Preference order:
    - Exact match with directory name: skill_<dir>.md (case-insensitive)
    - Otherwise, first file in sorted order.
    """
    md_files = sorted(base_dir.glob("skill_*.md"))
    if not md_files:
        raise FileNotFoundError(f"No skill_*.md found in {base_dir}")
    if len(md_files) == 1:
        return md_files[0]
    dir_name = base_dir.name.lower()
    for f in md_files:
        suffix = f.stem[6:].lower() if f.stem.startswith("skill_") else f.stem.lower()
        if suffix == dir_name or dir_name.endswith(suffix) or suffix.endswith(dir_name):
            return f
    return md_files[0]


async def load_skill_config(skill_path: Union[str, Path]) -> Optional[SkillConfig]:
    """Load a SkillConfig from a skill_*.md file (directories are not accepted).

    Behavior:
    - `skill_path` MUST be a `skill_*.md` file. Directories are not allowed.
    - YAML front matter provides fields like name, description, allowed_tools, etc.
    - The rest of the markdown becomes `prompt`.
    """
    path = Path(skill_path)
    try:
        text = load_text(path)
        if not text:
            return None

        base_dir = path.parent

        config, prompt, code_for_agent, code_for_interpreter = parse_config_from_markdown(base_dir, text)

        # Extract required fields
        name = config.get("name")
        description = config.get("description")
        if not name or not description:
            print(f"Missing required fields (name, description) in {path}")
            return None

        # Derive id/name
        skill_id = str(path.resolve())
        allowed_tools = config.get("allowed_tools", ["*"])
        metadata = {k: v for k, v in config.items() if k not in {"name", "description", "allowed_tools", "env", "file_prompt"}}

        # Optional module hint for tool loading
        module_path_hint = config.get("skill_module") or config.get("module") or config.get("tools_module")

        return SkillConfig(
            skill_id=skill_id,
            name=name,
            description=description,
            prompt=prompt,
            code_for_agent=code_for_agent,
            code_for_interpreter=code_for_interpreter,
            allowed_tools=allowed_tools if isinstance(allowed_tools, list) else ["*"],
            env=config.get("env", {}),
            tools=[],
            metadata=metadata,
            module_path=module_path_hint,
        )
    except ValueError as e:
        print(f"Error parsing config from {path}: {e}")
        return None
    except Exception as e:
        print(f"Error loading subagent from {path}: {e}")
        return None


def _discover_skill_module(base_dir: Path, module_hint: Optional[str]) -> Optional[Tuple[str, Path]]:
    """Discover the skill module within `base_dir`.

    Returns (module_name, file_path) if found.

    Resolution order:
    1) If `module_hint` is provided:
       - If it's an import path, try importing directly.
       - If it's a file path, ensure it exists and use it.
    2) Search for a Python file named `skill_*.py` in base_dir.
       - If multiple exist, prefer one that matches the skill directory name suffix.
       - Otherwise pick the first in sorted order.
    """
    # 1) Honor explicit hint
    if module_hint:
        hint_path = Path(module_hint)
        if hint_path.suffix == ".py" and hint_path.exists():
            return (hint_path.stem, hint_path.resolve())
        # Try relative to base_dir
        if not hint_path.is_absolute() and (base_dir / hint_path).with_suffix(".py").exists():
            p = (base_dir / hint_path).with_suffix(".py").resolve()
            return (p.stem, p)
        # Otherwise assume it's an importable module path
        try:
            spec = importlib.util.find_spec(module_hint)
            if spec and spec.origin:
                return (module_hint.split(".")[-1], Path(spec.origin))
        except Exception:
            pass

    # 2) Search for skill_*.py in base_dir
    candidates = sorted(base_dir.glob("skill_*.py"))
    if not candidates:
        return None

    # prefer matching suffix with dir name
    dir_name = base_dir.name.lower()
    for c in candidates:
        if dir_name.endswith(c.stem.replace("skill_", "").lower()):
            return (c.stem, c.resolve())
    return (candidates[0].stem, candidates[0].resolve())


def _import_module_from_path(module_name: str, file_path: Path):
    """Import a module from a specific file path without installation."""
    spec = importlib.util.spec_from_file_location(module_name, str(file_path))
    if not spec or not spec.loader:
        raise ImportError(f"Cannot load spec for module {module_name} from {file_path}")
    mod = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = mod
    spec.loader.exec_module(mod)  # type: ignore[attr-defined]
    return mod


def _instantiate_tool_classes(classes: Sequence[Type[BaseTool]], tool_kwargs: Dict[str, Any]) -> List[BaseTool]:
    tools: List[BaseTool] = []
    for cls in classes:
        try:
            sig = inspect.signature(cls)
            params = sig.parameters
            if any(p.kind in (p.VAR_KEYWORD,) or p.name in tool_kwargs for p in params.values()):
                tool = cls(**tool_kwargs)
            else:
                tool = cls()
            tools.append(tool)
        except Exception as e:
            logger.warning(f"Failed to instantiate tool class {cls.__name__}: {e}")
    return tools


def _collect_base_tool_classes(mod) -> List[Type[BaseTool]]:
    classes: List[Type[BaseTool]] = []
    for _, obj in inspect.getmembers(mod, inspect.isclass):
        try:
            if issubclass(obj, BaseTool) and obj is not BaseTool:
                classes.append(obj)
        except TypeError:
            continue
    return classes


async def _load_tools_from_skill_module(mod, tool_kwargs: Dict[str, Any]) -> List[BaseTool]:
    """Load tools from a skill module.

    Priority:
    1) module.load_tools(**kwargs) -> List[BaseTool]
    2) module.get_tools(**kwargs) -> List[BaseTool]
    3) module.TOOLS or module.tools (iterable of BaseTool or classes)
    4) Discover BaseTool subclasses and instantiate
    """
    # 1) Factory functions
    for fname in ("load_tools", "get_tools"):
        if hasattr(mod, fname) and inspect.isfunction(getattr(mod, fname)):
            try:
                res = getattr(mod, fname)(**tool_kwargs)
                if inspect.isawaitable(res):
                    res = await res
                if isinstance(res, list):
                    # Already a list of tools
                    tools: List[BaseTool] = []
                    for t in res:
                        if isinstance(t, BaseTool):
                            tools.append(t)
                        elif inspect.isclass(t) and issubclass(t, BaseTool):
                            tools.extend(_instantiate_tool_classes([t], tool_kwargs))
                        else:
                            logger.warning(f"Ignoring non-BaseTool entry from {fname}: {t}")
                    if tools:
                        return tools
            except Exception as e:
                logger.warning(f"Error calling {fname} in {mod.__name__}: {e}")

    # 2) Module-level constants
    for var_name in ("TOOLS", "tools"):
        if hasattr(mod, var_name):
            raw = getattr(mod, var_name)
            collected: List[BaseTool] = []
            if isinstance(raw, (list, tuple, set)):
                for item in raw:
                    if isinstance(item, BaseTool):
                        collected.append(item)
                    elif inspect.isclass(item) and issubclass(item, BaseTool):
                        collected.extend(_instantiate_tool_classes([item], tool_kwargs))
            if collected:
                return collected

    # 3) Discover classes
    classes = _collect_base_tool_classes(mod)
    if classes:
        return _instantiate_tool_classes(classes, tool_kwargs)

    return []


def is_skill_md_file(path: Union[str, Path]) -> bool:
    """Check if the given path is a skill_*.md file."""
    path = Path(path)
    return path.is_file() and path.suffix == ".md" and path.name.startswith("skill_")


async def load_skill(skill_dir: Union[str, Path], **tool_kwargs) -> SkillConfig:
    """Load a full Skill including tools.

    Steps:
    - Load SkillConfig from skill_*.md using `load_skill_config`.
    - If YAML provides a module path (`skill_module`/`module`/`tools_module`),
      import it and load tools from it using common patterns.
    - Otherwise DO NOT auto-discover modules in the directory; instead, fall back
      to `allowed_tools` names via `agentlin.tools.core.load_tools`.
    """
    skill_dir = Path(skill_dir)
    # Accept either a skill md file or a directory. If directory is provided,
    # pick a skill_*.md and then delegate to load_skill_config(md_file).
    if skill_dir.is_file():
        md_file = skill_dir
        base_dir = md_file.parent
    else:
        base_dir = skill_dir
        md_file = _pick_skill_md(base_dir)

    if not is_skill_md_file(md_file):
        raise FileNotFoundError(f"load_skill_config expects a skill_*.md file, got: {md_file}")

    cfg = await load_skill_config(md_file)

    # Only discover/import module when module_path is explicitly provided by YAML
    discovered = None
    if cfg.module_path:
        discovered = _discover_skill_module(base_dir, cfg.module_path)
    tools: List[BaseTool] = []

    if discovered:
        module_name, file_path = discovered
        try:
            mod = _import_module_from_path(module_name, file_path)
            tools = await _load_tools_from_skill_module(mod, tool_kwargs)
        except Exception as e:
            logger.warning(f"Failed to load tools from skill module {file_path}: {e}")

    # Fallback: try allowed tool names if module yielded nothing
    if not tools and cfg.allowed_tools:
        collected: List[BaseTool] = []
        for name in cfg.allowed_tools:
            if name == "*":
                continue
            try:
                loaded = load_tools_by_name(name, **tool_kwargs)
                collected.extend(loaded)
            except Exception as e:
                logger.debug(f"Skipping tool '{name}': {e}")
        tools = collected

    cfg.tools = tools
    return cfg


__all__ = [
    "SkillConfig",
    "load_skill_config",
    "load_skill",
]
