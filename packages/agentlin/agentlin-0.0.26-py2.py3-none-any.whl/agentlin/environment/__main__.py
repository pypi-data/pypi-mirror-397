"""
CLI: Play with an environment

Usage examples:
  agentlin play --env qa_env --env-args '{"question": "2+2?", "answer": "4"}'
  agentlin play --env agentlin.environment.qa_env:QAEnv --env-args '{"question": "2+2?", "answer": "4"}'
  agentlin play --env arc-agi-3 --env-args '{"game_id": "...", "card_id": "..."}' --agent ./assets/agi/agent/main.md

行为约定：
- 若提供 --agent，则加载 Agent 与环境进行交互（自动工具调用、产生 rollout）；
- 否则进入命令行交互界面，用户逐步输入动作参数与环境交互；
- 无论哪种方式，都会生成 rollout，并在末尾执行一次简单奖励统计（如果可用）。
"""

import asyncio
import json
from pathlib import Path
from typing import Annotated, Optional
from collections import defaultdict

import typer
from dotenv import load_dotenv
from loguru import logger

from agentlin.environment.core import load_environment
from agentlin.environment.interface import IEnvironment, IState, IStoppableState
from agentlin.rollout.trajectory import Trajectory, Step
from agentlin.route.agent import Agent
from agentlin.route.agent_config import load_agent_config
from agentlin.core.agent_schema import content_items_to_text, content_to_text


app = typer.Typer(help="Interactively play with an environment or via an Agent")


@app.command(
    name="list",
    help="List available environments",
)
def list_envs():
    from agentlin.environment.core import list_environments_detailed

    details = list_environments_detailed()
    if not details:
        typer.echo("No environments found.")
        raise typer.Exit(code=1)

    # 按名称分组，处理重名情况
    grouped = defaultdict(list)
    for d in details:
        grouped[d.get("name")].append(d)

    header = typer.style("Available environments:", fg=typer.colors.CYAN, bold=True)
    typer.echo(header)
    for name in sorted(grouped.keys()):
        items = grouped[name]
        name_styled = typer.style(name, fg=typer.colors.GREEN, bold=True)
        if len(items) == 1:
            info = items[0]
            source = info.get("source") or info.get("origin")
            module = info.get("module") or "<local>"
            importable = info.get("importable")
            defaults = info.get("default_params_summary") or ""

            # Build meta with dim style, but highlight local source path
            parts = []
            if isinstance(source, str) and source.startswith("local:"):
                prefix = "local:"
                label = typer.style(f"source={prefix}", fg=typer.colors.WHITE, dim=True)
                # highlight only the path after 'local:'
                path_part = source[len(prefix):]
                value = typer.style(path_part, fg=typer.colors.YELLOW, bold=True)
                parts.append(label + value)
            else:
                parts.append(typer.style(f"source={source}", fg=typer.colors.WHITE, dim=True))

            parts.append(typer.style(f"module={module}", fg=typer.colors.WHITE, dim=True))
            parts.append(typer.style(f"importable={importable}", fg=typer.colors.WHITE, dim=True))
            if defaults:
                parts.append(typer.style(f"defaults=({defaults})", fg=typer.colors.WHITE, dim=True))

            sep = typer.style(" | ", fg=typer.colors.WHITE, dim=True)
            meta_composed = sep.join(parts)
            typer.echo(f"- {name_styled}  {meta_composed}")
        else:
            typer.echo(f"- {name_styled}")
            for info in items:
                source = info.get("source") or info.get("origin")
                module = info.get("module") or "<local>"
                importable = info.get("importable")
                defaults = info.get("default_params_summary") or ""
                # Build per-source line with highlighted local path
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
                parts.append(typer.style(f"importable={importable}", fg=typer.colors.WHITE, dim=True))
                if defaults:
                    parts.append(typer.style(f"defaults=({defaults})", fg=typer.colors.WHITE, dim=True))

                sep = typer.style(" | ", fg=typer.colors.WHITE, dim=True)
                meta_composed = sep.join(parts)
                typer.echo(f"    • {meta_composed}")


@app.command(
    name="info",
    help="Show detailed info for a specific environment",
)
def env_info(
	env_path: str = typer.Argument(..., help="Environment module path or '<module>:<Class>'. You can use `agentlin env list` to see available environments."),
):
    """显示指定环境的详细信息。"""
    from agentlin.environment.core import list_environments_detailed
    details = list_environments_detailed()
    found = [d for d in details if d.get("name") == env_path or d.get("module") == env_path]
    if not found:
        typer.echo(typer.style(f"未找到环境: {env_path}", fg=typer.colors.RED, bold=True))
        raise typer.Exit(code=1)
    for info in found:
        typer.echo(typer.style(f"环境: {info.get('name')}", fg=typer.colors.GREEN, bold=True))
        for k, v in info.items():
            if k == "name":
                continue
            typer.echo(f"  {k}: {v}")
        typer.echo("-")


# @app.callback(invoke_without_command=True)
@app.command(
    name="play",
    help="Play with an environment, optionally via an Agent",
)
def play(
    env: Annotated[str, typer.Option("--env", "-e", help="Environment module path or '<module>:<Class>'")],
    env_args: Annotated[Optional[str], typer.Option("--env-args", help="JSON string for environment init params")] = None,
    agent: Annotated[Optional[str], typer.Option("--agent", "-a", help="Path to agent config directory or file")] = None,
    rollout_dir: Annotated[Optional[str], typer.Option("--rollout-dir", help="Directory to save rollout trajectory")] = None,
    max_steps: Annotated[int, typer.Option("--max-steps", help="Max interaction steps in interactive mode")] = 20,
    verbose: Annotated[bool, typer.Option("--verbose/--no-verbose", help="Verbose logs")] = True,
):
    """与指定环境进行交互。若指定 --agent，则由 Agent 与环境交互，否则提供交互式命令行界面。"""
    load_dotenv()

    env_kwargs = {}
    if env_args:
        try:
            env_kwargs = json.loads(env_args)
        except Exception as e:
            raise typer.BadParameter(f"Invalid --env-args JSON: {e}")

    logger.info(f"Loading environment: {env} with args: {env_kwargs}")
    environment: IEnvironment = load_environment(env, **env_kwargs)
    trajectory = Trajectory()

    if agent:
        asyncio.run(_play_with_agent(environment, agent, rollout_dir, verbose))
    else:
        _play_interactively(environment, trajectory, rollout_dir, max_steps, verbose)


def _play_interactively(
    env_obj: IEnvironment,
    traj: Trajectory,
    rollout_dir: Optional[str],
    max_steps: int,
    verbose: bool,
):
    state = env_obj.provide_initial_state()
    _print_state(state)

    step_count = 0
    while True:
        if isinstance(state, IStoppableState) and state.done:
            typer.echo("[done] 环境已终止")
            break
        if step_count >= max_steps:
            typer.echo(f"[stop] 达到最大步数: {max_steps}")
            break

        user_input = typer.prompt('请输入动作参数(JSON，如 {"answer": "4"} 或 {"name":"Tool", "arguments":{...}})，输入 q 退出')
        if user_input.strip().lower() in {"q", "quit", "exit"}:
            break
        try:
            kwargs = json.loads(user_input)
            if not isinstance(kwargs, dict):
                raise ValueError("必须是 JSON 对象")
        except Exception as e:
            typer.echo(f"参数解析失败: {e}")
            continue

        prev = state
        try:
            state = env_obj(prev, **kwargs)  # forward
        except TypeError as e:
            typer.echo(f"调用失败: {e}")
            continue

        # 展示新状态
        _print_state(state)

        # 记录步骤（此处无 agent rollout，可将环境展示作为一条输出）
        traj.append(Step(old_state=prev, new_state=state, rollouts=[{"user_input": user_input}]))
        step_count += 1

    _finalize_rollout(traj, rollout_dir, verbose)


async def _play_with_agent(env_obj: IEnvironment, agent_path: str, rollout_dir: Optional[str], verbose: bool):
    # 让 Agent 与环境互动的最简桥接：
    # 思路：将环境初始状态 display() 的文本作为用户指令，交给 Agent；Agent 在内部会进行工具调用并产生 rollout。
    # 若环境暴露了工具，可在 agent 的工具发现阶段被使用。
    agent_config = await load_agent_config(agent_path)
    agent = Agent(debug=verbose)
    from agentlin.core.types import (
        TaskRolloutEvent,
        TaskStreamingResponse,
        AgentTaskEventType,
        TaskCompletedEvent,
    )
    import uuid

    session_id = uuid.uuid4().hex
    init_state = env_obj.provide_initial_state()
    init_resp = init_state.display()
    env_message_content = init_resp.get("message_content", [])
    instruction = "Please Interact with the environment."

    stream = await agent(
        session_id=session_id,
        user_message_content=env_message_content + [{"type": "text", "text": instruction}],
        stream=True,
        agent_config=agent_config,
        rollout_save_dir=rollout_dir,
        return_rollout=True,
    )

    try:
        async for chunk in stream:
            if isinstance(chunk, TaskStreamingResponse):
                event = chunk.result
                # 打印回答片段
                if isinstance(event, TaskCompletedEvent):
                    task = event.task
                    typer.echo(content_items_to_text(task.output))
    except Exception as e:
        logger.error(f"Agent play failed: {e}")
        agent.delete_session(session_id)


def _print_state(state: IState):
    try:
        resp = state.display()
    except Exception:
        # graceful fallback
        resp = {"message_content": [{"type": "text", "text": str(state)}]}
    message_content = resp.get("message_content") or []
    if message_content:
        # 展示文本内容
        text = content_to_text(message_content)
        typer.echo(text)
    else:
        typer.echo(str(state))


def _ensure_rollout_dir(path: Optional[str]) -> Optional[Path]:
    if not path:
        return None
    p = Path(path)
    p.mkdir(parents=True, exist_ok=True)
    return p


def _finalize_rollout(traj: Trajectory, rollout_dir: Optional[str], verbose: bool):
    # 保存与粗略评分（按完成标志计分）
    if rollout_dir:
        out_dir = _ensure_rollout_dir(rollout_dir)
        if out_dir:
            outfile = out_dir / "trajectory.jsonl"
            traj.save_to_jsonl(str(outfile))
            logger.success(f"Trajectory saved to {outfile}")

    # 简单奖励：统计 done 次数/步数
    total = len(traj.steps)
    done_cnt = 0
    for s in traj.steps:
        ns = s.new_state
        if isinstance(ns, IStoppableState) and ns.done:
            done_cnt += 1
    reward = (done_cnt / total) if total > 0 else 0.0
    typer.echo(f"Reward (done ratio): {reward:.3f}")


if __name__ == "__main__":
    app()
