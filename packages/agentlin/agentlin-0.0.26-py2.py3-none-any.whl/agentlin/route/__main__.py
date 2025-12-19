import os
from pathlib import Path
import traceback
from typing import Annotated, Optional
import uuid

import typer
import asyncio
from loguru import logger
from dotenv import load_dotenv

from agentlin.core.types import AgentTaskEvent, AgentTaskEventType, TaskCompletedEvent, TaskStreamingResponse
from agentlin.route.agent import Agent
from agentlin.route.agent_config import load_agent_config

app = typer.Typer()


@app.callback(invoke_without_command=True)
def run(
    agent: Annotated[str, typer.Option(..., "--agent", "-a", help="Path to the agent config directory or file")],
    instruction: Annotated[str, typer.Option(..., "--instruction", "-i", help="Instruction to guide the agent")],
    allowed_tools: Annotated[Optional[str], typer.Option(..., "--allowed-tools", help="Comma-separated list of allowed tools")] = None,
    rollout_dir: Annotated[Optional[str], typer.Option(..., "--rollout-dir", help="Directory to save rollouts")] = None,
    workspace_path: Annotated[Optional[str], typer.Option(..., "--workspace", "-w", help="Path to the workspace directory")] = None,
    debug: Annotated[bool, typer.Option(..., "--debug", "-d", help="Whether to print progress bars and logs")] = True,
    env_file: Annotated[Optional[str], typer.Option(..., "--env-file", help="Path to the .env file")] = None,
):
    """Run an agent.

    Examples:

    $ agent-run --agent ./path/to/agent/main.md -i "Tell me a joke"
    """
    if env_file is not None:
        ok = load_dotenv(env_file)
        if ok:
            logger.info(f"Loaded env file: {env_file}")
    else:
        env_files = [
            os.path.join(os.getcwd(), ".env"),
        ]
        for env_file in env_files:
            ok = load_dotenv(env_file)
            if ok:
                logger.info(f"Loaded env file: {env_file}")
    workspace_path: Path = Path.cwd() if workspace_path is None else Path(workspace_path)
    if not workspace_path.exists():
        workspace_path.mkdir(parents=True, exist_ok=True)
    allowed_tools_list = None
    if allowed_tools is not None:
        allowed_tools_list = [tool.strip() for tool in allowed_tools.split(",")]
        logger.info(f"Using allowed tools: {allowed_tools_list}")

    asyncio.run(
        run_async(
            agent_path=agent,
            instruction=instruction,
            allowed_tools=allowed_tools_list,
            rollout_dir=rollout_dir,
            workspace_path=workspace_path,
            debug=debug,
        )
    )


async def run_async(
    agent_path: str,
    instruction: str,
    allowed_tools: Optional[list[str]],
    rollout_dir: Optional[str],
    workspace_path: Path,
    debug: bool,
):
    # Prepare agent config
    agent_config = await load_agent_config(agent_path)
    logger.success(f"Loaded agent config from {agent_path}")
    agent = Agent(debug=debug)
    task_id = f"task_{uuid.uuid4().hex}"
    session_id = str(uuid.uuid4().hex)
    stream = await agent(
        user_message_content=[{"type": "text", "text": instruction}],
        stream=True,
        session_id=session_id,
        task_id=task_id,
        agent_config=agent_config,
        allowed_tools=allowed_tools,
        workspace_dir=str(workspace_path),
        rollout_save_dir=rollout_dir,
        return_rollout=True,
    )
    from xlin import append_to_json_list
    try:
        async for chunk in stream:
            event = chunk.result
            # logger.info(event)
            append_to_json_list([event.model_dump()], f"output/stream/event_{task_id}.jsonl")
            if isinstance(event, TaskCompletedEvent):
                task = event.task
    except Exception as e:
        logger.error(f"Failed: {e}\n{traceback.format_exc()}")
    finally:
        agent.delete_session(session_id)



if __name__ == "__main__":
    app()
