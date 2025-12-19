import sys
from pathlib import Path
from typing import Optional, List

import typer
from rich.console import Console
from rich.table import Table
from loguru import logger

from agentlin.core.agent_schema import content_to_text
from agentlin.core.types import ToolResult
from agentlin.tools.core import load_tools, list_tools, list_tools_detailed


app = typer.Typer(
    help="AgentLin 工具管理 CLI - 管理工具和工具集 (toolset)",
    epilog="加载优先级: 具体工具 > 工具集"
)


@app.command("list")
def list_command(
    detailed: bool = typer.Option(False, "--detailed", "-d", help="显示详细信息"),
    origin: Optional[str] = typer.Option(None, "--origin", "-o", help="按来源筛选 (builtin/external/local)"),
):
    """列出所有可用的工具集和工具"""
    console = Console()
    tools = list_tools_detailed()

    # 筛选
    if origin:
        tools = [t for t in tools if t["origin"] == origin]

    if not tools:
        console.print("[yellow]未找到工具[/yellow]")
        return

    if detailed:
        # 详细的表格视图
        table = Table(title="可用工具 (详细)", show_lines=True)
        table.add_column("名称", style="cyan", no_wrap=True)
        table.add_column("模块/来源", style="magenta")
        table.add_column("工具数量", style="blue", justify="center")
        table.add_column("工具名称列表", style="yellow")

        for tool in tools:
            # 合并模块和来源为一列，换行显示
            module_info = tool["module"] or "N/A"
            source_info = tool["source"] or tool["origin"]
            combined_module_source = f"{module_info}\n{source_info}"

            # 获取工具名称（而非类名）
            tool_names_list = []
            if tool["classes"] and tool["module"]:
                try:
                    import importlib
                    mod = importlib.import_module(tool["module"])
                    for cls_name in tool["classes"]:
                        try:
                            cls = getattr(mod, cls_name, None)
                            if cls:
                                instance = cls()
                                if hasattr(instance, 'name'):
                                    tool_names_list.append(instance.name)
                                else:
                                    tool_names_list.append(cls_name)
                        except Exception:
                            tool_names_list.append(cls_name)
                except Exception:
                    tool_names_list = tool["classes"]
            else:
                tool_names_list = tool["classes"]

            # 工具名称列表换行显示
            tool_names_str = "\n".join(tool_names_list) if tool_names_list else "N/A"

            table.add_row(
                tool["name"],
                combined_module_source,
                str(len(tool["classes"])),
                tool_names_str,
            )

        console.print(table)
        console.print(f"\n找到 [bold]{len(tools)}[/bold] 个工具")
    else:
        # 树形结构视图
        header = typer.style("可用工具:", fg=typer.colors.CYAN, bold=True)
        typer.echo(header)

        for tool in tools:
            name = tool["name"]
            classes = tool["classes"]
            module = tool["module"] or "<local>"
            source = tool.get("source") or tool.get("origin")
            defaults = tool.get("default_params_summary") or ""

            # 高亮主工具名
            name_styled = typer.style(name, fg=typer.colors.GREEN, bold=True)

            # 构建元信息
            parts = []
            if isinstance(source, str) and source.startswith("local:"):
                prefix = "local:"
                label = typer.style(f"source={prefix}", fg=typer.colors.WHITE, dim=True)
                path_part = source[len(prefix):]
                value = typer.style(path_part, fg=typer.colors.YELLOW, bold=True)
                parts.append(label + value)
            else:
                parts.append(typer.style(f"source={source}", fg=typer.colors.WHITE, dim=True))

            parts.append(typer.style(f"module={module}", fg=typer.colors.WHITE, dim=True))

            sep = typer.style(" | ", fg=typer.colors.WHITE, dim=True)
            meta_composed = sep.join(parts)

            # 显示主工具名和元信息
            typer.echo(f"- {name_styled}  {meta_composed}")

            # 显示树形结构：所有 BaseTool 子类
            if classes:
                # 需要实例化类来获取 tool.name
                import importlib
                tool_names_cache = {}

                # 尝试获取每个类的 tool.name
                if module != "<local>":
                    try:
                        mod = importlib.import_module(module)
                        for cls_name in classes:
                            try:
                                cls = getattr(mod, cls_name, None)
                                if cls:
                                    instance = cls()
                                    if hasattr(instance, 'name'):
                                        tool_names_cache[cls_name] = instance.name
                            except Exception:
                                pass
                    except Exception:
                        pass

                for i, cls_name in enumerate(classes):
                    is_last = (i == len(classes) - 1)
                    tree_char = "└─" if is_last else "├─"

                    # 构建可直接使用的加载路径（高亮显示）
                    load_paths = []

                    # 主路径：module:ClassName
                    main_path = f"{name}:{cls_name}"
                    load_paths.append(("class", main_path))

                    # 如果有 tool.name，添加更多路径选项
                    tool_name = tool_names_cache.get(cls_name)
                    if tool_name:
                        tool_name_lower = tool_name.lower()
                        # module:toolname
                        load_paths.append(("name", f"{name}:{tool_name_lower}"))
                        # toolname (direct)
                        load_paths.append(("short", tool_name_lower))

                    # 类名使用普通颜色
                    cls_styled = typer.style(cls_name, fg=typer.colors.CYAN)

                    # 将所有路径组合在一行显示
                    all_paths_str = " or ".join([typer.style(path, fg=typer.colors.YELLOW, bold=True) for _, path in load_paths])
                    typer.echo(f"  {tree_char} {cls_styled} → [load as: {all_paths_str}]")
            elif tool.get("has_factory"):
                # 如果有工厂函数但没有列出类
                factory_info = typer.style("(via factory function)", fg=typer.colors.MAGENTA, dim=True)
                typer.echo(f"  └─ {factory_info}")
            else:
                # 没有类也没有工厂函数
                no_tools = typer.style("(no BaseTool classes found)", fg=typer.colors.RED, dim=True)
                typer.echo(f"  └─ {no_tools}")

        typer.echo(f"\n找到 {typer.style(str(len(tools)), fg=typer.colors.CYAN, bold=True)} 个工具集")

        # 添加使用提示
        tip = typer.style("\n💡 提示:", fg=typer.colors.BLUE, bold=True)
        typer.echo(tip)
        typer.echo("  • 复制黄色高亮的路径，使用 'agentlin tool load <path>' 来加载工具")
        typer.echo("  • 加载优先级: 具体工具 (如 bash) > 工具集 (如 file_system_tools)")
        typer.echo("  • 支持多种路径格式：")
        typer.echo("    - 完整路径: file_system_tools:BashTool")
        typer.echo("    - 使用小写名: file_system_tools:bash 或 bash")
        typer.echo("  • 使用 'agentlin tool info <name>' 查看工具集详情")
        typer.echo("  • 使用 'agentlin tool info <name> --tool-init-args {...}' 查看工具实例详情")


@app.command("load")
def load_command(
    tool_path: str = typer.Argument(..., help="工具路径 (优先级: 具体工具 > 工具集)，例如: bash, file_system_tools"),
    tool_class: Optional[str] = typer.Option(None, "--class", "-c", help="指定要加载的工具类"),
    show_details: bool = typer.Option(True, "--details/--no-details", help="显示工具详情"),
    tool_init_args: Optional[str] = typer.Option(
        None,
        "--tool-init-args", "--init-args",
        help="工具初始化参数 (JSON格式)"
    ),
):
    """加载指定的工具或工具集"""
    console = Console()

    # 解析初始化参数
    init_args = {}
    if tool_init_args:
        import json
        try:
            init_args = json.loads(tool_init_args)
        except json.JSONDecodeError as e:
            console.print(f"[red bold]✗ 初始化参数格式错误:[/red bold] {e}")
            console.print("[dim]请提供有效的 JSON 格式，例如: '{\"key\": \"value\"}'[/dim]")
            raise typer.Exit(1)

    try:
        # 构建完整路径
        full_path = f"{tool_path}:{tool_class}" if tool_class else tool_path

        console.print(f"\n正在加载工具: [cyan bold]{full_path}[/cyan bold]...\n")
        tools = load_tools(full_path, **init_args)

        # 成功标题
        console.print("─" * 60)
        console.print(f"[green bold]✓ 成功加载 {len(tools)} 个工具[/green bold]")
        console.print("─" * 60)
        console.print()

        for i, tool in enumerate(tools, 1):
            # 工具序号和类名
            console.print(f"[bold cyan]{i}.[/bold cyan] [bold yellow]{tool.__class__.__name__}[/bold yellow]")

            if show_details:
                # 工具名称（如果与类名不同则显示）
                if tool.name != tool.__class__.__name__:
                    console.print(f"   [dim]名称:[/dim] [green]{tool.name}[/green]")

                # 描述（智能截断和格式化）
                if tool.description:
                    desc = tool.description.strip()
                    # 如果描述太长，截断并保留完整句子
                    if len(desc) > 200:
                        # 尝试在句号处截断
                        truncated = desc[:200]
                        last_period = truncated.rfind('。')
                        if last_period == -1:
                            last_period = truncated.rfind('.')
                        if last_period > 100:
                            desc = truncated[:last_period + 1] + " [dim]...[/dim]"
                        else:
                            desc = truncated + "[dim]...[/dim]"

                    # 多行描述的缩进处理
                    desc_lines = desc.split('\n')
                    console.print(f"   [dim]描述:[/dim] {desc_lines[0]}")
                    for line in desc_lines[1:4]:  # 最多显示前4行
                        if line.strip():
                            console.print(f"        {line}")
                    if len(desc_lines) > 4:
                        console.print(f"        [dim]...(还有 {len(desc_lines) - 4} 行)[/dim]")

                # 参数信息
                if hasattr(tool, "parameters") and tool.parameters:
                    properties = tool.parameters.get('properties', {})
                    required = tool.parameters.get('required', [])
                    param_count = len(properties)
                    required_count = len(required)

                    if param_count > 0:
                        console.print(f"   [dim]参数:[/dim] [blue]{param_count}[/blue] 个参数", end="")
                        if required_count > 0:
                            console.print(f" ([red]{required_count}[/red] 个必需)", end="")
                        console.print()

                        # 显示参数列表（最多显示5个）
                        param_list = []
                        for param_name in list(properties.keys())[:5]:
                            is_required = param_name in required
                            if is_required:
                                param_list.append(f"[red]{param_name}*[/red]")
                            else:
                                param_list.append(f"[blue]{param_name}[/blue]")

                        console.print(f"        {', '.join(param_list)}", end="")
                        if len(properties) > 5:
                            console.print(f" [dim]...(+{len(properties) - 5})[/dim]", end="")
                        console.print()

                console.print()  # 工具之间的空行

    except Exception as e:
        console.print()
        console.print("─" * 60)
        console.print(f"[red bold]✗ 加载失败[/red bold]")
        console.print("─" * 60)

        # 提取错误的核心信息
        error_msg = str(e)
        if "Could not import" in error_msg or "No module named" in error_msg:
            # 导入错误：只显示第一行主要错误信息
            lines = error_msg.split('\n')
            main_error = lines[0] if lines else error_msg
            console.print(f"\n[red]{main_error}[/red]")

            # 提示可用工具
            available_tools = list_tools()
            if available_tools:
                console.print(f"\n[dim]可用的工具:[/dim]")
                console.print(f"[dim]{', '.join(available_tools[:10])}[/dim]")
                if len(available_tools) > 10:
                    console.print(f"[dim]...(还有 {len(available_tools) - 10} 个)[/dim]")
        else:
            # 其他错误：显示完整信息
            console.print(f"\n[red]{error_msg}[/red]")

        console.print()

        # 详细错误记录到日志，但不打印到控制台
        logger.debug(f"详细错误: {e}", exc_info=True)
        raise typer.Exit(1)


@app.command("info")
def info_command(
    tool_name: str = typer.Argument(..., help="工具名称或工具集名称"),
    tool_init_args: Optional[str] = typer.Option(
        None,
        "--tool-init-args", "--init-args",
        help="工具初始化参数 (JSON格式)"
    ),
):
    """显示工具或工具集的详细信息"""
    console = Console()
    import json

    # 解析初始化参数
    init_args = {}
    if tool_init_args:
        try:
            init_args = json.loads(tool_init_args)
        except json.JSONDecodeError as e:
            console.print(f"[red bold]✗ 初始化参数格式错误:[/red bold] {e}")
            console.print("[dim]请提供有效的 JSON 格式，例如: '{\"key\": \"value\"}'[/dim]")
            raise typer.Exit(1)

    # 尝试直接加载工具实例（优先级：具体工具 > 工具集）
    try:
        if tool_init_args:
            console.print(f"\n正在加载工具: [cyan bold]{tool_name}[/cyan bold] (使用初始化参数)...\n")
        else:
            console.print(f"\n正在加载工具: [cyan bold]{tool_name}[/cyan bold]...\n")

        tools_instances = load_tools(tool_name, **init_args)

        if not tools_instances:
            console.print("[red bold]✗ 加载失败:[/red bold] 未找到工具")
            raise typer.Exit(1)

        # 如果加载到多个工具，说明是工具集，显示工具集信息
        if len(tools_instances) > 1:
            # 这是工具集，显示工具集的详细信息
            console.print("═" * 60)
            console.print(f"[bold cyan]工具集信息: {tool_name}[/bold cyan]")
            console.print("═" * 60)
            console.print()

            console.print("[bold]基本信息[/bold]")
            console.print(f"  [dim]工具数量:[/dim] [blue]{len(tools_instances)}[/blue] 个")
            console.print()

            console.print(f"[bold]包含的工具 ({len(tools_instances)} 个)[/bold]")
            for i, tool_instance in enumerate(tools_instances, 1):
                console.print(f"  [cyan]{i}.[/cyan] [bold green]{tool_instance.name}[/bold green]")
                console.print(f"     [dim]类名:[/dim] [yellow]{tool_instance.__class__.__name__}[/yellow]")
                if tool_instance.description:
                    # 只显示第一行描述
                    first_line = tool_instance.description.strip().split('\n')[0]
                    if len(first_line) > 80:
                        first_line = first_line[:77] + "..."
                    console.print(f"     [dim]描述:[/dim] {first_line}")
                console.print()

            # 初始化参数
            if init_args:
                console.print("[bold]使用的初始化参数[/bold]")
                console.print(f"  [dim]{json.dumps(init_args, indent=2, ensure_ascii=False)}[/dim]")
                console.print()

            console.print("[dim]提示: 使用 'agentlin tool info <tool_name>:<ClassName>' 查看单个工具的详细信息[/dim]")
            console.print("─" * 60)
            console.print()
            return
        else:
            # 只有一个工具，显示工具实例详细信息
            tool_instance = tools_instances[0]

            # 显示工具实例的详细信息
            console.print("═" * 60)
            console.print(f"[bold cyan]工具详细信息: {tool_instance.name}[/bold cyan]")
            console.print("═" * 60)
            console.print()

            # 基本信息
            console.print("[bold]基本信息[/bold]")
            console.print(f"  [dim]类名:[/dim] [yellow]{tool_instance.__class__.__name__}[/yellow]")
            console.print(f"  [dim]工具名:[/dim] [green bold]{tool_instance.name}[/green bold]")
            console.print()

            # 描述（完整显示，不折叠）
            if tool_instance.description:
                console.print("[bold]描述[/bold]")
                desc_lines = tool_instance.description.strip().split('\n')
                for line in desc_lines:  # 显示所有行
                    console.print(f"  {line}")
                console.print()

            # 参数（完整显示）
            if hasattr(tool_instance, "parameters") and tool_instance.parameters:
                console.print("[bold]参数定义[/bold]")
                properties = tool_instance.parameters.get('properties', {})
                required = tool_instance.parameters.get('required', [])

                if properties:
                    console.print(f"  [dim]参数总数:[/dim] [blue]{len(properties)}[/blue] 个")
                    console.print(f"  [dim]必需参数:[/dim] [red]{len(required)}[/red] 个")
                    console.print()

                    # 显示每个参数（完整显示）
                    for i, (param_name, param_info) in enumerate(properties.items(), 1):
                        is_required = param_name in required
                        required_mark = "[red]*[/red]" if is_required else ""

                        console.print(f"  [cyan]{i}.[/cyan] [bold]{param_name}[/bold]{required_mark}")

                        # 类型
                        param_type = param_info.get('type', 'any')
                        console.print(f"     [dim]类型:[/dim] [magenta]{param_type}[/magenta]")

                        # 描述（完整显示）
                        if 'description' in param_info:
                            desc = param_info['description']
                            console.print(f"     [dim]说明:[/dim] {desc}")

                        # 默认值
                        if 'default' in param_info:
                            console.print(f"     [dim]默认值:[/dim] [yellow]{param_info['default']}[/yellow]")

                        console.print()
                else:
                    console.print("  [dim]无参数[/dim]")
                    console.print()

            # 初始化参数
            if init_args:
                console.print("[bold]使用的初始化参数[/bold]")
                console.print(f"  [dim]{json.dumps(init_args, indent=2, ensure_ascii=False)}[/dim]")
                console.print()

            console.print("─" * 60)
            console.print()
            return

    except Exception as e:
        # 加载失败，可能是工具集名称，尝试显示工具集信息
        pass

    # 显示工具集信息
    tools = list_tools_detailed()

    # 查找匹配的工具（支持模块名和工具名）
    tool = None

    # 先按模块名精确匹配
    for t in tools:
        if t["name"] == tool_name:
            tool = t
            break

    # 如果没找到，尝试按工具类名匹配
    if not tool:
        for t in tools:
            for cls_name in t.get("classes", []):
                # 检查类名（不区分大小写）
                # 例如：bash 可以匹配 BashTool
                if cls_name.lower() == tool_name.lower() or cls_name.lower() == tool_name.lower() + "tool":
                    tool = t
                    break
            if tool:
                break

    if not tool:
        console.print()
        console.print(f"[red bold]✗ 未找到工具或工具集:[/red bold] [yellow]{tool_name}[/yellow]")
        console.print()
        console.print("[dim]可用的工具集:[/dim]")
        available_tools = [f"[cyan]{t['name']}[/cyan]" for t in tools]
        # 每行显示5个
        for i in range(0, len(available_tools), 5):
            console.print("  " + ", ".join(available_tools[i:i+5]))
        console.print()
        raise typer.Exit(1)

    # 标题
    console.print()
    console.print("═" * 60)
    console.print(f"[bold cyan]工具集信息: {tool['name']}[/bold cyan]")
    console.print("═" * 60)
    console.print()

    # 基本信息
    console.print("[bold]基本信息[/bold]")
    console.print(f"  [dim]模块路径:[/dim] [magenta]{tool['module'] or 'N/A'}[/magenta]")
    console.print(f"  [dim]来源:[/dim] [green]{tool['origin']}[/green] [dim]({tool['source']})[/dim]")

    # 状态标识
    status_items = []
    if tool['importable']:
        status_items.append("[green]✓ 可导入[/green]")
    else:
        status_items.append("[red]✗ 不可导入[/red]")

    if tool['has_factory']:
        status_items.append("[blue]✓ 有工厂函数[/blue]")

    console.print(f"  [dim]状态:[/dim] {' '.join(status_items)}")
    console.print()

    # 加载方式
    console.print("[bold]加载方式[/bold]")
    console.print(f"  [yellow]agentlin tool load {tool['prefer']}[/yellow]")
    console.print()

    # 包含的工具类
    if tool['classes']:
        console.print(f"[bold]包含的工具类 ({len(tool['classes'])} 个)[/bold]")

        # 尝试获取每个类的工具名称
        if tool['module']:
            try:
                import importlib
                mod = importlib.import_module(tool['module'])
                for i, cls_name in enumerate(tool['classes'], 1):
                    try:
                        cls = getattr(mod, cls_name, None)
                        if cls:
                            instance = cls()
                            tool_display_name = instance.name if hasattr(instance, 'name') else cls_name
                            console.print(f"  [cyan]{i}.[/cyan] [bold]{cls_name}[/bold]", end="")
                            if tool_display_name != cls_name:
                                console.print(f" [dim]→ {tool_display_name}[/dim]", end="")
                            console.print()

                            # 显示加载命令
                            console.print(f"     [dim]加载:[/dim] [yellow]{tool['prefer']}:{cls_name}[/yellow]", end="")
                            if tool_display_name != cls_name:
                                console.print(f" [dim]或[/dim] [yellow]{tool_display_name.lower()}[/yellow]", end="")
                            console.print()
                    except Exception:
                        console.print(f"  [cyan]{i}.[/cyan] [bold]{cls_name}[/bold]")
                        console.print(f"     [dim]加载:[/dim] [yellow]{tool['prefer']}:{cls_name}[/yellow]")
            except Exception:
                # 如果无法导入，只显示类名
                for i, cls_name in enumerate(tool['classes'], 1):
                    console.print(f"  [cyan]{i}.[/cyan] [bold]{cls_name}[/bold]")
        else:
            # 本地工具，只显示类名
            for i, cls_name in enumerate(tool['classes'], 1):
                console.print(f"  [cyan]{i}.[/cyan] [bold]{cls_name}[/bold]")
        console.print()

    # 默认参数
    if tool['default_params_summary']:
        console.print("[bold]默认参数[/bold]")
        console.print(f"  [dim]{tool['default_params_summary']}[/dim]")
        console.print()

    console.print("─" * 60)
    console.print()


def _test_exec_impl(
    tool_path: str,
    tool_init_args: Optional[str],
    tool_args: Optional[str],
    detailed: bool,
):
    """测试/执行工具的共享实现"""
    console = Console()
    import json

    # 解析初始化参数
    init_args = {}
    if tool_init_args:
        try:
            init_args = json.loads(tool_init_args)
        except json.JSONDecodeError as e:
            console.print(f"[red bold]✗ 初始化参数格式错误:[/red bold] {e}")
            console.print("[dim]请提供有效的 JSON 格式，例如: '{\"key\": \"value\"}'[/dim]")
            raise typer.Exit(1)

    # 解析执行参数
    exec_args = {}
    if tool_args:
        try:
            exec_args = json.loads(tool_args)
        except json.JSONDecodeError as e:
            console.print(f"[red bold]✗ 执行参数格式错误:[/red bold] {e}")
            console.print("[dim]请提供有效的 JSON 格式，例如: '{\"command\": \"ls\"}'[/dim]")
            raise typer.Exit(1)

    try:
        console.print(f"测试加载工具: [cyan]{tool_path}[/cyan]...")
        tools = load_tools(tool_path, **init_args)
        console.print(f"[green]✓[/green] 加载成功! 找到 {len(tools)} 个工具")

        for tool in tools:
            console.print(f"  - {tool.__class__.__name__}: {tool.name}")

        # 如果提供了执行参数，执行第一个工具
        if tool_args and tools:
            console.print()
            console.print("─" * 60)
            console.print(f"[yellow bold]执行工具: {tools[0].name}[/yellow bold]")
            console.print("─" * 60)
            console.print(f"[dim]参数:[/dim] {json.dumps(exec_args, ensure_ascii=False)}")
            console.print()

            try:
                # 调用工具的 execute 方法（可能是异步的）
                import asyncio
                import inspect

                if inspect.iscoroutinefunction(tools[0].execute):
                    # 异步执行
                    result = asyncio.run(tools[0].execute(exec_args))
                else:
                    # 同步执行
                    result = tools[0].execute(exec_args)

                console.print(f"[green bold]✓ 执行成功[/green bold]")
                console.print()
                console.print("[bold]执行结果:[/bold]")
                console.print()
                console.print("─" * 60)

                # 处理 ToolResult 对象
                if hasattr(result, 'message_content') and result.message_content:
                    # 显示内容
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

    except Exception as e:
        console.print(f"[red]✗[/red] 加载失败: {e}")
        raise typer.Exit(1)


@app.command("test")
def test_command(
    tool_path: str = typer.Argument(..., help="工具路径 (支持工具名或工具集名)"),
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
    detailed: bool = typer.Option(False, "--detailed", "-d", help="显示工具详情"),
):
    """测试加载工具或工具集是否成功"""
    _test_exec_impl(tool_path, tool_init_args, tool_args, detailed)


@app.command("exec")
def exec_command(
    tool_path: str = typer.Argument(..., help="工具路径 (支持工具名或工具集名)"),
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
    detailed: bool = typer.Option(False, "--detailed", "-d", help="显示工具详情"),
):
    """执行工具 (test 命令的别名)"""
    _test_exec_impl(tool_path, tool_init_args, tool_args, detailed)


@app.command("run")
def run_command(
    tool_path: str = typer.Argument(..., help="工具路径 (支持工具名或工具集名)"),
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
    detailed: bool = typer.Option(False, "--detailed", "-d", help="显示工具详情"),
):
    """运行工具 (test 命令的别名)"""
    _test_exec_impl(tool_path, tool_init_args, tool_args, detailed)


if __name__ == "__main__":
    app()
