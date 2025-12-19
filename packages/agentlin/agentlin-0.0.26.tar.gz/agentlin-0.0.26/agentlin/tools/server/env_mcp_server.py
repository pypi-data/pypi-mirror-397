import json
import os
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from dataclasses import dataclass, field
from typing import Any, Union, Optional

from fastmcp import FastMCP
from loguru import logger

from agentlin.environment.core import load_environment
from agentlin.environment.interface import IEnvironment, IToolEnvironment
from agentlin.tools.core import TransformedMcpTool


@dataclass
class AppContext:
    session2env: dict[str, IEnvironment] = field(default_factory=dict)

    def create_or_get_environment(self, session_id: str, **env_args) -> Optional[IEnvironment]:
        if session_id not in self.session2env:
            self.session2env[session_id] = load_environment(**env_args)
        return self.session2env.get(session_id)

    def remove_environment(self, session_id: str):
        self.session2env.pop(session_id, None)


@asynccontextmanager
async def app_lifespan(_server: FastMCP) -> AsyncIterator[AppContext]:
    yield AppContext()


def mcp_server_from_env(env: IToolEnvironment, name: str) -> FastMCP:
    server = FastMCP(
        name=name,
    )
    state = env.provide_initial_state()
    tools = env.provide_tools(state)
    for tool in tools:
        logger.info(f"Loaded tool: {tool.name} - {tool.description}")
        mcp_tool = TransformedMcpTool(tool)
        server.add_tool(mcp_tool)
    return server


def mcp_server_from_env_path(env_path: str, env_args: dict[str, Any]) -> FastMCP:
    env = load_environment(env_path, **json.loads(env_args))
    if not isinstance(env, IToolEnvironment):
        raise ValueError(f"Environment from path {env_path} is not an IToolEnvironment.")
    mcp = mcp_server_from_env(env, env_path)
    return mcp


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Run MCP SSE-based server")
    parser.add_argument("--host", default="0.0.0.0", help="Host to bind to")
    parser.add_argument("--port", type=int, default=7781, help="Port to listen on")
    parser.add_argument("--debug", action="store_true", help="Enable debug mode")
    parser.add_argument("--env-args", type=str, default="{}", help="JSON string of environment arguments")
    parser.add_argument("--env-path", type=str, default="arc-agi-3", help="Path to the environment module or '<module>:<ClassName>'")
    args = parser.parse_args()

    logger.info("Starting MCP Server...")

    env = load_environment(**json.loads(args.env_args))
    if not isinstance(env, IToolEnvironment):
        raise ValueError(f"Environment from path {args.env_path} is not an IToolEnvironment.")
    mcp = mcp_server_from_env(env, args.env_path)
    mcp.run("http", host=args.host, port=args.port, log_level="debug" if args.debug else "info")
