
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from fastmcp import FastMCP
from loguru import logger

from agentlin.app.route_chatkit import AgentChatKitServer, InMemoryStore, create_chatkit_app, create_chatkit_router
from agentlin.app.route_task import create_task_router


def create_server(mcp_name2server: dict[str, FastMCP]={}) -> FastAPI:
    app = FastAPI(
        title="Agent Server",
        description="A service for managing agent tasks and sessions",
        version="1.0.0",
        openapi_tags=[
            {
                "name": "Agent Server",
                "description": "Endpoints for managing agent tasks and sessions",
            },
            {
                "name": "Agent Chat",
                "description": "Endpoints for Agent Chat Kit functionalities",
            },
            {
                "name": "Environment",
                "description": "Endpoints for Environment interactions",
            },
        ],
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    store = InMemoryStore()
    server = AgentChatKitServer(
        store,
        debug=True,
        use_message_queue=False,
    )
    app.mount("/app", create_chatkit_app(), name="Agent Chat")
    app.include_router(create_chatkit_router(server), tags=["Agent Chat"])
    app.include_router(create_task_router(server.task_agent_manager), prefix="/v1", tags=["Agent Server"])
    from agentlin.app.weather.main import app as weather_app
    app.mount("/weather", weather_app)
    if mcp_name2server:
        for mcp_name, mcp_server in mcp_name2server.items():
            app.mount(f"/{mcp_name}-mcp", mcp_server.http_app())
    from agentlin.tools.server.code_interpreter_server import app as code_interpreter_app
    app.mount("/code-interpreter", code_interpreter_app)
    from agentlin.environment.server.route_env import create_env_router
    from agentlin.environment.server.task_env_manager import TaskEnvManager
    task_env_manager = TaskEnvManager()
    app.include_router(create_env_router(task_env_manager), prefix="/v1/env", tags=["Environment"])


    @app.get("/readiness")
    def readiness():
        """
        Readiness endpoint to check if the service is ready.
        """
        return {"readiness": "ok"}


    @app.get("/liveness")
    def liveness():
        """
        Liveness endpoint to check if the service is alive.
        """
        return {"liveness": "ok"}


    @app.get("/health")
    def health():
        """
        Health check endpoint to verify the service is operational.
        """
        return {"status": "healthy"}


    @app.get("/version")
    def version():
        """
        Version endpoint to return the service version.
        """
        return {
            "version": "1.0.0",
            "description": "Agent Server for managing agent tasks and sessions",
        }
    return app


if __name__ == "__main__":
    import argparse
    import uvicorn

    parser = argparse.ArgumentParser(description="Run the FastAPI app")
    parser.add_argument("--host", type=str, default="0.0.0.0", help="Host to bind")
    parser.add_argument("--port", type=int, default=9999, help="Port to bind")
    parser.add_argument("--debug", action="store_true", help="Enable debug mode")
    parser.add_argument("--env-file", type=str, default=".env", help="Path to the .env file")
    args = parser.parse_args()

    logger.info(f"Loading environment variables from {args.env_file}")
    load_dotenv(args.env_file)

    logger.info(f"Starting Agent Server on {args.host}:{args.port}")

    app = create_server()
    if args.debug:
        logger.info("Debug mode is enabled.")
        app.debug = True
        app.logger.setLevel("DEBUG")

    uvicorn.run(app, host=args.host, port=args.port)
