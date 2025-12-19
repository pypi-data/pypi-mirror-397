import enum
import importlib
from fastmcp import FastMCP


class McpServerModule:
    """MCP 服务器模块的类型注释类"""
    mcp: FastMCP


class MCPServer(enum.Enum):
    bash = "bash"
    file_system = "file_system"
    memory = "memory"
    web = "web"
    todo = "todo"
    aime = "aime"
    wencai = "wencai"

    def __str__(self):
        return self.name


def create_mcp_server(name: str, home: str = None) -> FastMCP:
    server_path = f"agentlin.tools.server.{name}_mcp_server"
    server_module: McpServerModule = importlib.import_module(server_path)
    if name == MCPServer.file_system.value:
        server_module.WORKSPACE_DIR = home
    return server_module.mcp

