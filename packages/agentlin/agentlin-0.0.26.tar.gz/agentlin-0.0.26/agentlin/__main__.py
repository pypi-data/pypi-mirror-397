"""
Entry point for running agentlin modules as executables.

Usage:
    ```sh
    python -m agentlin.tools.server.bash_mcp_server --port 9999
    agentlin mcp-server --name bash --port 9999
    agentlin code-interpreter-server --port 8889 --debug
    agentlin agent-server --port 8000
    agentlin task-server --port 8001
    agentlin sgl-server --port 8002
    agentlin env-as-mcp-server --env environments/arc-agi-3/env_arc_agi_3 --port 7779 --env-args '{"game_id": "your_game_id", "card_id": "your_card_id"}'
    agentlin env-as-mcp-server --env arc-agi-3

    # subcommands
    agentlin run --agent path/to/agent_config.yaml --instruction "Your instruction here" --workspace ./workspace --rollout-dir ./rollouts --verbose
    agentlin evaluate --name gsm8k --agent ./path/to/agent/main.md --eval-args '{"split": "test"}' --rollout-n 2 --rollout-dir ./eval_rollouts --max-workers 4 --verbose
    agentlin env list
    agentlin env info arc-agi-3
    agentlin env play --env environments/arc-agi-3 --max-steps 10 --rollout-dir ./play_rollouts --verbose
    agentlin env play --env qa_env --env-args '{"question": "2+2?", "answer": "4"}' --max-steps 5 --verbose
    ```
"""

from typing import Dict, Any
import os
import sys
import enum
import importlib

import typer
import uvicorn
from fastmcp import FastMCP
from dotenv import load_dotenv
from loguru import logger

from agentlin.evaluation.__main__ import app as eval_app
from agentlin.route.__main__ import app as run_app
from agentlin.code_interpreter.__main__ import app as ci_app
from agentlin.environment.__main__ import app as env_app
from agentlin.tools.__main__ import app as tool_app
from agentlin.skills.__main__ import app as skill_app
from agentlin.tools.server.__main__ import MCPServer, create_mcp_server
from agentlin.tools.server.env_mcp_server import mcp_server_from_env_path


app = typer.Typer()
app.add_typer(eval_app, name="evaluate", help="Run Evaluations", invoke_without_command=True)
app.add_typer(run_app, name="run", help="Run Agents", invoke_without_command=True)
app.add_typer(env_app, name="env", help="Manage, serve, and interact with environments", invoke_without_command=True)
app.add_typer(tool_app, name="tool", help="Manage and run tools", invoke_without_command=True)
app.add_typer(skill_app, name="skill", help="Manage and run skills", invoke_without_command=True)
app.add_typer(ci_app, name="code-interpreter", help="Run Code Interpreter", invoke_without_command=True)


# region MCP Servers and other servers
example_usage = "\n\n".join([f"agentlin mcp_server --name {mcp_server.name} --port 7779 --debug" for mcp_server in MCPServer])


@app.command(
    help=f"""Run the specified MCP server.\n\nExamples:\n\n{example_usage}""",
)
def mcp_server(
    name: MCPServer = typer.Option(
        MCPServer.bash,
        "--name",
        help="The name of the MCP server to run.",
        case_sensitive=False,
    ),
    host: str = typer.Option("0.0.0.0", help="The host to bind the server to"),
    port: int = typer.Option(7779, help="The port to run the server on"),
    path: str = typer.Option("/mcp", help="The path for the MCP server"),
    home: str = typer.Option(None, help="The target directory for file operations (if applicable)"),
    debug: bool = typer.Option(False, help="Enable debug mode"),
):
    """
    Launch an MCP server.
    """
    selected_server = name
    server_name = selected_server.name
    mcp = create_mcp_server(server_name, home)

    typer.echo(f"Starting {server_name} MCP server on {host}:{port} at path {path} with debug={debug}")
    # Run the selected MCP server
    mcp.run("http", host=host, port=port, path=path, log_level="debug" if debug else "info")

@app.command(
    help=f"""Run the environment as MCP server.\n\nExamples:\n\nagentlin env-as-mcp-server --env environments/arc-agi-3/env_arc_agi_3 --port 7779 --env-args '{{"game_id": "your_game_id", "card_id": "your_card_id"}}'\nagentlin env-as-mcp-server --env arc-agi-3""",
)
def env_as_mcp_server(
    env: str = typer.Option(
        ...,
        "-e",
        "--env",
        help="The environment name of the MCP server to run.",
        case_sensitive=False,
    ),
    host: str = typer.Option("0.0.0.0", help="The host to bind the server to"),
    port: int = typer.Option(7779, help="The port to run the server on"),
    path: str = typer.Option("/mcp", help="The path for the MCP server"),
    debug: bool = typer.Option(False, help="Enable debug mode"),
    env_args: str = typer.Option("{}", help="JSON string of environment arguments"),
    env_file: str = typer.Option(".env", help="Path to the .env file for environment variables"),
):
    """
    Launch an MCP server.
    """
    if env_file:
        load_dotenv(env_file)
        logger.info(f"Loading environment variables from {env_file}")
    mcp = mcp_server_from_env_path(env, env_args)
    typer.echo(f"Starting {env} MCP server with env_args={env_args} on {host}:{port} at path {path} with debug={debug}")
    mcp.run("http", host=host, port=port, path=path, log_level="debug" if debug else "info")


@app.command(
    help="Run the code interpreter server",
)
def code_interpreter_server(
    host: str = typer.Option("0.0.0.0", help="The host to bind the code interpreter server to"),
    port: int = typer.Option(8889, help="The port to run the code interpreter server on"),
    debug: bool = typer.Option(False, help="Enable debug mode for the code interpreter server"),
    env_file: str = typer.Option(".env", help="Path to the .env file for environment variables"),
    log_dir: str = typer.Option("logs/code_interpreter", help="Directory to store logs"),
):
    """
    Run the code interpreter server with the specified host and port.
    """
    typer.echo(f"Starting code interpreter server on {host}:{port}")
    if env_file:
        load_dotenv(env_file)
        logger.info(f"Loading environment variables from {env_file}")

    from agentlin.tools.server.code_interpreter_server import app, init_server

    init_server(app, log_dir, debug)

    typer.echo(f"Running Code Interpreter Server at http://{host}:{port}")
    uvicorn.run(app, host=host, port=port, log_level="info" if not debug else "debug")


@app.command(
    help="Run the agent server",
)
def agent_server(
    host: str = typer.Option("0.0.0.0", help="The host to bind the agent server to"),
    port: int = typer.Option(9999, help="The port to run the agent server on"),
    debug: bool = typer.Option(False, help="Enable debug mode for the agent server"),
    env_file: str = typer.Option(".env", help="Path to the .env file for environment variables"),
    mcp_servers: str = typer.Option("", help="Comma-separated list of MCP servers to mount (e.g., 'aime,wencai,web')"),
    home: str = typer.Option("", help="The target directory for file operations (if applicable)"),
):
    """
    Run the agent server with the specified host and port.
    """
    typer.echo(f"Starting agent server on {host}:{port}")
    if env_file:
        load_dotenv(env_file)
        logger.info(f"Loading environment variables from {env_file}")

    from agentlin.app.server import create_server

    mcp_name_list = [s.strip() for s in mcp_servers.split(",")] if mcp_servers else []
    mcp_name2server = {}
    if mcp_name_list:
        logger.info(f"Mounting MCP servers: {mcp_name_list}")
        if MCPServer.file_system.value in mcp_name_list:
            if not home:
                home = os.getcwd()
                logger.warning("For file_system server, please specify --home to set the target directory.")
                logger.warning(f"Defaulting to current working directory: {home}")
        for mcp_name in mcp_name_list:
            logger.info(f"Mounting MCP server: {mcp_name}")
            mcp_name2server[mcp_name] = create_mcp_server(mcp_name, home)

    app = create_server(mcp_name2server)

    if debug:
        logger.info("Debug mode is enabled.")
        app.debug = True

    typer.echo(f"Running Agent Server at http://{host}:{port}")
    uvicorn.run(app, host=host, port=port, log_level="info" if not debug else "debug")


@app.command(
    help="Run the task server",
)
def task_server(
    host: str = typer.Option("0.0.0.0", help="The host to bind the task server to"),
    port: int = typer.Option(9999, help="The port to run the task server on"),
    debug: bool = typer.Option(False, help="Enable debug mode for the task server"),
    env_file: str = typer.Option(".env", help="Path to the .env file for environment variables"),
):
    """
    Run the task server with the specified host and port.
    """
    typer.echo(f"Starting task server on {host}:{port}")
    if env_file:
        logger.info(f"Loading environment variables from {env_file}")

    from agentlin.rollout.task_server import app
    import multiprocessing
    multiprocessing.set_start_method(method="fork", force=True)

    if debug:
        logger.info("Debug mode is enabled.")
        app.debug = True

    typer.echo(f"Running Agent Server at http://{host}:{port}")
    uvicorn.run(app, host=host, port=port, log_level="info" if not debug else "debug")


@app.command(
    help="Run the sgl server",
)
def sgl_server(
    host: str = typer.Option("0.0.0.0", help="The host to bind the sgl server to"),
    port: int = typer.Option(9999, help="The port to run the sgl server on"),
    env_file: str = typer.Option(".env", help="Path to the .env file for environment variables"),
):
    """
    Run the sgl server with the specified host and port.
    """
    typer.echo(f"Starting sgl server on {host}:{port}")
    if env_file:
        logger.info(f"Loading environment variables from {env_file}")


    from agentlin.rollout.sgl_server import app

    from sglang.srt.utils import kill_process_tree
    from sglang.srt.server_args import prepare_server_args
    from sglang.srt.entrypoints.http_server import launch_server
    server_args = prepare_server_args(sys.argv[1:])

    try:
        typer.echo(f"Running SGL Server at http://{host}:{port}")
        launch_server(server_args)
    finally:
        kill_process_tree(os.getpid(), include_parent=False)
# endregion


if __name__ == "__main__":
    app()
