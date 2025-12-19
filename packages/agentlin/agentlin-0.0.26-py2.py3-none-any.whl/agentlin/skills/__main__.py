import json
import inspect
from pathlib import Path
from typing import Optional, List

import typer
from rich.console import Console
from rich.table import Table
from loguru import logger

from agentlin.core.agent_schema import content_to_text
from agentlin.core.types import ToolResult
from agentlin.skills.core import load_skill, load_skill_config, SkillConfig


app = typer.Typer(
	help="AgentLin 技能管理 CLI - 加载、查看和测试技能 (skill)",
	epilog="""`一个技能（skill） = 特定领域的专业知识（prompt） + 一组可执行的操作（tools）`

技能不是独立包，而是由工具集（toolsets）或环境（environments）插件附带的说明性文件（skill_*.md）。默认根据 allowed_tools 按名称加载工具；仅当 YAML 显式提供 module 路径时，才会从该模块加载工具。

一个 md 文件即可描述一个技能：

```markdown
---
name: skill_name
description: A brief description of the skill.
allowed_tools: ["tool_1", "tool_2"]
---
当情况 X 发生时，使用 tool_1 来执行操作 A。
当情况 Y 发生时，使用 tool_2 来执行操作 B。
当情况 Z 发生时，先使用 tool_1 获得结果 A'，再根据情况使用 tool_2 来执行操作 C。
```
""",
)


def _iter_dirs(root: Path, max_depth: int = 3):
	"""Yield directories up to max_depth from root, skipping heavy/hidden dirs."""
	SKIP_NAMES = {
		".git", "__pycache__", "node_modules", ".mypy_cache", ".pytest_cache",
		".venv", "venv", "env", "build", "dist", ".idea", ".vscode",
		"site-packages", "Library", "Applications"
	}
	def _walk(dir_path: Path, depth: int):
		if depth > max_depth:
			return
		try:
			for entry in dir_path.iterdir():
				if not entry.is_dir():
					continue
				name = entry.name
				if name.startswith('.') or name in SKIP_NAMES:
					continue
				yield entry
				yield from _walk(entry, depth + 1)
		except Exception:
			return
	yield from _walk(root, 1)


def _discover_skills(root: Path):
	"""Find directories containing a skill_*.md and return info dicts.

	Returns entries with the resolved md file path in `path`.
	"""
	skills = []
	# also include root itself if it contains main.md
	candidates = [root] + list(_iter_dirs(root))
	seen = set()
	for d in candidates:
		try:
			key = str(d.resolve())
			if key in seen:
				continue
			seen.add(key)
			# prefer skill_*.md; fallback to none if not found
			md_files = sorted(d.glob("skill_*.md"))
			if not md_files:
				continue
			# pick a best md similar to core logic
			pick = md_files[0]
			if len(md_files) > 1:
				dir_name = d.name.lower()
				for f in md_files:
					suffix = f.stem[6:].lower() if f.stem.startswith("skill_") else f.stem.lower()
					if suffix == dir_name or dir_name.endswith(suffix) or suffix.endswith(dir_name):
						pick = f
						break
			# optional skill module existence
			module_files = list(d.glob("skill_*.py"))

			# parse config (fast, without loading tools). If parsing fails, skip.
			import asyncio
			try:
				cfg = asyncio.run(load_skill_config(pick))
				name = cfg.name
				desc_first = (cfg.description or "").strip().split('\n')[0]
				allowed = cfg.allowed_tools or []
			except Exception:
				# Skip invalid or non-skill markdown files
				continue

			abs_path = pick.resolve()
			skills.append({
				"name": name,
				# show md file path on the right for clarity
				"path": str(abs_path),  # keep absolute for resolution
				"abs_path": str(abs_path),
				"config": str(pick.name),
				"module_files": [str(p.name) for p in module_files],
				"allowed_tools": allowed,
				"description": desc_first,
			})
		except Exception:
			continue
	# sort by name
	skills.sort(key=lambda x: x.get("name", ""))
	return skills


def _prefer_relative(abs_path: Path) -> str:
	"""Return path relative to current working directory when possible, else absolute.

	Display preference: relative to PWD > absolute.
	"""
	try:
		return str(abs_path.relative_to(Path.cwd()))
	except Exception:
		return str(abs_path)


def _compute_default_roots(root_opt: Optional[str]) -> List[Path]:
	"""Build default search roots with proper priority.

	Priority: specified root > ./toolsets > ./environments > agentlin/skills/builtin > .
	"""
	if root_opt:
		root_path = Path(root_opt).resolve()
		if not root_path.exists() or not root_path.is_dir():
			raise FileNotFoundError(f"根目录无效: {root_path}")
		return [root_path]

	roots: List[Path] = []
	default_toolsets = Path("toolsets").resolve()
	if default_toolsets.exists() and default_toolsets.is_dir():
		roots.append(default_toolsets)
	default_envs = Path("environments").resolve()
	if default_envs.exists() and default_envs.is_dir():
		roots.append(default_envs)
	try:
		builtin_dir = (Path(__file__).resolve().parent / "builtin").resolve()
		if builtin_dir.exists() and builtin_dir.is_dir():
			roots.append(builtin_dir)
	except Exception:
		pass
	roots.append(Path(".").resolve())
	return roots


def _resolve_skill_input(skill_input: str, roots: List[Path]) -> Path:
	"""Resolve a user-provided input to a concrete path (dir or md file).

	- If input is an existing path, return it.
	- Else, treat input as a skill name and search discovered skills across roots.
	  Return the md file path when matched by name (case-insensitive).
	"""
	p = Path(skill_input)
	if p.exists():
		return p.resolve()

	name_lc = skill_input.strip().lower()
	for rp in roots:
		try:
			for s in _discover_skills(rp):
				if s.get("name", "").strip().lower() == name_lc:
					return Path(s["path"]).resolve()
		except Exception:
			continue

	raise FileNotFoundError(f"未找到名为 '{skill_input}' 的技能，请先运行 'agent-skill list' 查看可用技能")


@app.command("list")
def list_command(
	root: str = typer.Option(None, "--root", "-r", help="扫描技能根目录；优先级：指定文件夹 > ./toolsets > ./environments > agentlin/skills/builtin > 当前目录"),
	detailed: bool = typer.Option(False, "--detailed", "-d", help="显示详细信息"),
):
	"""列出指定目录下可发现的技能包 (包含 skill_*.md 的目录)"""
	console = Console()
	# 搜索优先级：指定文件夹 -> ./toolsets -> ./environments -> agentlin/skills/builtin -> 当前目录
	try:
		roots = _compute_default_roots(root)
	except FileNotFoundError as e:
		console.print(f"[red]✗ 根目录无效:[/red] {e}")
		raise typer.Exit(1)

	# 合并多个根目录的技能列表，并去重
	seen_paths = set()
	skills = []
	for rp in roots:
		try:
			found = _discover_skills(rp)
			for s in found:
				abs_p = s.get("abs_path") or s.get("path")
				if abs_p and abs_p not in seen_paths:
					seen_paths.add(abs_p)
					skills.append(s)
		except Exception:
			continue
	if not skills:
		console.print("[yellow]未在默认搜索目录下找到任何技能 (包含 skill_*.md 的目录)[/yellow]")
		return

	if detailed:
		table = Table(title="可用技能 (详细)", show_lines=True)
		table.add_column("名称", style="cyan", no_wrap=True)
		table.add_column("配置文件路径", style="magenta", no_wrap=True)
		table.add_column("模块文件", style="yellow")
		table.add_column("允许工具", style="green")
		table.add_column("描述", style="white")

		for s in skills:
			module_files = "\n".join(s["module_files"]) if s["module_files"] else "N/A"
			allowed = ", ".join(s["allowed_tools"]) if s["allowed_tools"] else "*"
			display_path = _prefer_relative(Path(s.get("abs_path") or s["path"]))
			table.add_row(
				s["name"],
				display_path,
				module_files,
				allowed,
				s["description"] or "",
			)
		console.print(table)
		console.print(f"\n找到 [bold]{len(skills)}[/bold] 个技能")
	else:
		header = typer.style("可用技能:", fg=typer.colors.CYAN, bold=True)
		typer.echo(header)
		for s in skills:
			name_styled = typer.style(s["name"], fg=typer.colors.GREEN, bold=True)
			display_path = _prefer_relative(Path(s.get("abs_path") or s["path"]))
			path_dim = typer.style(display_path, fg=typer.colors.WHITE, dim=True)
			meta = []
			if s["module_files"]:
				meta.append("module")
			meta_str = f" [{', '.join(meta)}]" if meta else ""
			typer.echo(f"- {name_styled}{meta_str}  -> {path_dim}")
		typer.echo(f"\n找到 {typer.style(str(len(skills)), fg=typer.colors.CYAN, bold=True)} 个技能")


def _parse_json_option(console: Console, value: Optional[str], label: str) -> dict:
	if not value:
		return {}
	try:
		return json.loads(value)
	except json.JSONDecodeError as e:
		console.print(f"[red bold]✗ {label} 格式错误:[/red bold] {e}")
		console.print("[dim]请提供有效的 JSON 格式，例如: '{\"key\": \"value\"}'[/dim]")
		raise typer.Exit(1)


def _print_skill_basic(console: Console, cfg: SkillConfig):
	console.print("═" * 60)
	console.print(f"[bold cyan]技能信息: {cfg.name}[/bold cyan]")
	console.print("═" * 60)
	console.print()

	console.print("[bold]基本信息[/bold]")
	console.print(f"  [dim]技能ID:[/dim] [yellow]{cfg.skill_id}[/yellow]")
	console.print(f"  [dim]描述:[/dim] {cfg.description or 'N/A'}")
	if cfg.module_path:
		console.print(f"  [dim]模块提示:[/dim] [magenta]{cfg.module_path}[/magenta]")
	console.print()

	if cfg.allowed_tools:
		console.print("[bold]允许的工具[/bold]")
		console.print(f"  {', '.join(cfg.allowed_tools)}")
		console.print()

	if cfg.metadata:
		console.print("[bold]其他元数据[/bold]")
		meta_preview = json.dumps(cfg.metadata, indent=2, ensure_ascii=False)
		# 最多显示前 30 行
		lines = meta_preview.splitlines()
		shown = lines[:30]
		console.print("  " + "\n  ".join(shown))
		if len(lines) > 30:
			console.print(f"  [dim]...(还有 {len(lines) - 30} 行)[/dim]")
		console.print()


@app.command("info")
def info_command(
	skill_path: str = typer.Argument(..., help="技能路径 (目录或 skill_*.md)"),
	tool_init_args: Optional[str] = typer.Option(
		None,
		"--tool-init-args", "--init-args",
		help="工具初始化参数 (JSON格式)，用于实例化技能中工具"
	),
	load_tools_flag: bool = typer.Option(True, "--load-tools/--no-load-tools", help="是否加载并显示工具信息"),
):
	"""显示技能的配置信息，并可选加载工具列表"""
	console = Console()
	spath = Path(skill_path)

	# 先加载配置（不依赖工具）。当传入目录时，选择目录中的一个 skill_*.md。
	import asyncio
	try:
		# 支持按名称自动解析
		if not spath.exists():
			roots = _compute_default_roots(None)
			spath = _resolve_skill_input(skill_path, roots)

		if spath.is_dir():
			md_files = sorted(spath.glob("skill_*.md"))
			if not md_files:
				raise FileNotFoundError(f"目录中未找到 skill_*.md: {spath}")
			pick = md_files[0]
			if len(md_files) > 1:
				dir_name = spath.name.lower()
				for f in md_files:
					suffix = f.stem[6:].lower() if f.stem.startswith("skill_") else f.stem.lower()
					if suffix == dir_name or dir_name.endswith(suffix) or suffix.endswith(dir_name):
						pick = f
						break
			spath_md = pick
		else:
			spath_md = spath
		cfg = asyncio.run(load_skill_config(spath_md))
	except Exception as e:
		console.print(f"[red bold]✗ 读取技能配置失败:[/red bold] {e}")
		raise typer.Exit(1)

	_print_skill_basic(console, cfg)

	if not load_tools_flag:
		return

	# 加载工具
	init_args = _parse_json_option(console, tool_init_args, "初始化参数")
	try:
		cfg_loaded = asyncio.run(load_skill(spath, **init_args))
	except Exception as e:
		console.print(f"[red bold]✗ 加载技能工具失败:[/red bold] {e}")
		raise typer.Exit(1)

	tools = cfg_loaded.tools or []
	console.print("[bold]工具信息[/bold]")
	console.print(f"  [dim]工具数量:[/dim] [blue]{len(tools)}[/blue] 个")
	console.print()
	for i, t in enumerate(tools, 1):
		console.print(f"  [cyan]{i}.[/cyan] [bold green]{t.name}[/bold green]  [dim]({t.__class__.__name__})[/dim]")
		if t.description:
			first = t.description.strip().split('\n')[0]
			if len(first) > 120:
				first = first[:117] + "..."
			console.print(f"     [dim]描述:[/dim] {first}")
	console.print()


@app.command("load")
def load_command(
	skill_path: str = typer.Argument(..., help="技能路径 (目录或 skill_*.md)"),
	show_details: bool = typer.Option(True, "--details/--no-details", help="显示工具详情"),
	tool_init_args: Optional[str] = typer.Option(
		None,
		"--tool-init-args", "--init-args",
		help="工具初始化参数 (JSON格式)"
	),
):
	"""加载技能并显示已发现/实例化的工具"""
	console = Console()
	spath = Path(skill_path)
	init_args = _parse_json_option(console, tool_init_args, "初始化参数")
	import asyncio

	try:
		console.print(f"\n正在加载技能: [cyan bold]{spath}[/cyan bold]...\n")
		cfg = asyncio.run(load_skill(spath, **init_args))
		tools = cfg.tools or []

		console.print("─" * 60)
		console.print(f"[green bold]✓ 成功加载技能[/green bold]  (工具数量: {len(tools)})")
		console.print("─" * 60)
		console.print()

		for i, tool in enumerate(tools, 1):
			console.print(f"[bold cyan]{i}.[/bold cyan] [bold yellow]{tool.__class__.__name__}[/bold yellow]")

			if show_details:
				if tool.name != tool.__class__.__name__:
					console.print(f"   [dim]名称:[/dim] [green]{tool.name}[/green]")

				if tool.description:
					desc = tool.description.strip()
					if len(desc) > 200:
						truncated = desc[:200]
						last_period = truncated.rfind('。')
						if last_period == -1:
							last_period = truncated.rfind('.')
						if last_period > 100:
							desc = truncated[:last_period + 1] + " [dim]...[/dim]"
						else:
							desc = truncated + "[dim]...[/dim]"
					for line in desc.split('\n')[:4]:
						if line.strip():
							console.print(f"        {line}")

				if getattr(tool, "parameters", None):
					properties = tool.parameters.get('properties', {})
					required = tool.parameters.get('required', [])
					param_count = len(properties)
					required_count = len(required)
					if param_count > 0:
						console.print(f"   [dim]参数:[/dim] [blue]{param_count}[/blue] 个参数", end="")
						if required_count > 0:
							console.print(f" ([red]{required_count}[/red] 个必需)", end="")
						console.print()

						shown = list(properties.keys())[:5]
						labels = []
						for p in shown:
							if p in required:
								labels.append(f"[red]{p}*[/red]")
							else:
								labels.append(f"[blue]{p}[/blue]")
						console.print(f"        {', '.join(labels)}", end="")
						if len(properties) > 5:
							console.print(f" [dim]...(+{len(properties) - 5})[/dim]", end="")
						console.print()

				console.print()

	except Exception as e:
		console.print()
		console.print("─" * 60)
		console.print(f"[red bold]✗ 加载失败[/red bold]")
		console.print("─" * 60)
		console.print(f"\n[red]{e}[/red]\n")
		logger.debug(f"详细错误: {e}", exc_info=True)
		raise typer.Exit(1)


def _exec_tool(console: Console, tool, exec_args: dict, detailed: bool):
	try:
		if inspect.iscoroutinefunction(tool.execute):
			import asyncio
			result = asyncio.run(tool.execute(exec_args))
		else:
			result = tool.execute(exec_args)

		console.print(f"[green bold]✓ 执行成功[/green bold]")
		console.print()
		console.print("[bold]执行结果:[/bold]")
		console.print()
		console.print("─" * 60)

		if hasattr(result, 'message_content') and result.message_content:
			text = content_to_text(result.message_content)
			console.print(f"{text}")
		elif isinstance(result, ToolResult):
			console.print(f"{result.model_dump_json(indent=2)}")
		elif isinstance(result, dict):
			console.print(json.dumps(result, indent=2, ensure_ascii=False))
		else:
			console.print(f"{result}")
		console.print("─" * 60)

		if detailed and hasattr(result, 'message_content') and result.message_content:
			console.print()
			console.print(f"[bold]完整执行结果:[/bold]")
			if isinstance(result, ToolResult):
				console.print(f"{result.model_dump_json(indent=2)}")
			else:
				console.print(f"{json.dumps(result, indent=2, ensure_ascii=False)}")
		console.print()
	except Exception as e:
		console.print(f"[red bold]✗ 执行失败:[/red bold] {e}")
		console.print()
		import traceback
		console.print(f"[dim]{traceback.format_exc()}[/dim]")


def _test_exec_shared(
	skill_path: str,
	tool_init_args: Optional[str],
	tool_args: Optional[str],
	tool_name: Optional[str],
	tool_index: Optional[int],
	detailed: bool,
):
	console = Console()

	init_args = _parse_json_option(console, tool_init_args, "初始化参数")
	exec_args = _parse_json_option(console, tool_args, "执行参数")

	import asyncio
	# 解析名称或路径
	spath = Path(skill_path)
	try:
		if not spath.exists():
			roots = _compute_default_roots(None)
			spath = _resolve_skill_input(skill_path, roots)
	except Exception as e:
		console.print(f"[red]✗ 解析技能路径失败:[/red] {e}")
		raise typer.Exit(1)

	cfg = asyncio.run(load_skill(spath, **init_args))
	tools = cfg.tools or []
	if not tools:
		console.print(f"[red bold]✗ 该技能未加载到任何工具[/red bold]")
		raise typer.Exit(1)

	# 选择工具
	target = None
	if tool_name:
		for t in tools:
			if t.name == tool_name or t.__class__.__name__ == tool_name:
				target = t
				break
		if not target:
			console.print(f"[red]✗ 未找到名为 {tool_name} 的工具[/red]")
			console.print("可用工具:")
			for t in tools:
				console.print(f"  - {t.name} ({t.__class__.__name__})")
			raise typer.Exit(1)
	elif tool_index:
		if 1 <= tool_index <= len(tools):
			target = tools[tool_index - 1]
		else:
			console.print(f"[red]✗ 工具序号越界 (1~{len(tools)})[/red]")
			raise typer.Exit(1)
	else:
		target = tools[0]

	console.print()
	console.print("─" * 60)
	console.print(f"[yellow bold]执行工具: {target.name}[/yellow bold]")
	console.print("─" * 60)
	console.print(f"[dim]参数:[/dim] {json.dumps(exec_args, ensure_ascii=False)}")
	console.print()

	_exec_tool(console, target, exec_args, detailed)


@app.command("test")
def test_command(
	skill_path: str = typer.Argument(..., help="技能路径 (目录或 skill_*.md)"),
	tool_init_args: Optional[str] = typer.Option(
		None,
		"--tool-init-args", "--init-args",
		help="工具初始化参数 (JSON格式)"
	),
	tool_args: Optional[str] = typer.Option(
		None,
		"--args",
		help="工具执行参数 (JSON格式)，如果提供则执行工具并显示结果"
	),
	tool_name: Optional[str] = typer.Option(None, "--tool-name", help="指定要执行的工具名称或类名"),
	tool_index: Optional[int] = typer.Option(None, "--tool-index", help="指定要执行的工具序号(从1开始)"),
	detailed: bool = typer.Option(False, "--detailed", "-d", help="显示详细执行结果"),
):
	"""测试加载技能并可执行其中一个工具"""
	_test_exec_shared(skill_path, tool_init_args, tool_args, tool_name, tool_index, detailed)


@app.command("exec")
def exec_command(
	skill_path: str = typer.Argument(..., help="技能路径 (目录或 skill_*.md)"),
	tool_init_args: Optional[str] = typer.Option(
		None,
		"--tool-init-args", "--init-args",
		help="工具初始化参数 (JSON格式)"
	),
	tool_args: Optional[str] = typer.Option(
		None,
		"--args",
		help="工具执行参数 (JSON格式)，如果提供则执行工具并显示结果"
	),
	tool_name: Optional[str] = typer.Option(None, "--tool-name", help="指定要执行的工具名称或类名"),
	tool_index: Optional[int] = typer.Option(None, "--tool-index", help="指定要执行的工具序号(从1开始)"),
	detailed: bool = typer.Option(False, "--detailed", "-d", help="显示详细执行结果"),
):
	"""执行技能中的工具 (test 命令的别名)"""
	_test_exec_shared(skill_path, tool_init_args, tool_args, tool_name, tool_index, detailed)


@app.command("run")
def run_command(
	skill_path: str = typer.Argument(..., help="技能路径 (目录或 skill_*.md)"),
	tool_init_args: Optional[str] = typer.Option(
		None,
		"--tool-init-args", "--init-args",
		help="工具初始化参数 (JSON格式)"
	),
	tool_args: Optional[str] = typer.Option(
		None,
		"--args",
		help="工具执行参数 (JSON格式)，如果提供则执行工具并显示结果"
	),
	tool_name: Optional[str] = typer.Option(None, "--tool-name", help="指定要执行的工具名称或类名"),
	tool_index: Optional[int] = typer.Option(None, "--tool-index", help="指定要执行的工具序号(从1开始)"),
	detailed: bool = typer.Option(False, "--detailed", "-d", help="显示详细执行结果"),
):
	"""运行技能中的工具 (test 命令的别名)"""
	_test_exec_shared(skill_path, tool_init_args, tool_args, tool_name, tool_index, detailed)


if __name__ == "__main__":
	app()

