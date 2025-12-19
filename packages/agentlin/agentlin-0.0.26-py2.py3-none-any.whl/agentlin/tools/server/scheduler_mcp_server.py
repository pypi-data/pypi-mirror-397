import asyncio
import signal
import threading
from typing import Any, Optional, Annotated, Dict, List
from loguru import logger
import sys
import json
import re
import platform

from fastmcp import FastMCP, Context

from agentlin.core.types import TaskObject as CoreTaskObject
from agentlin.tools.scheduler.task import (
    ScheduleApiTask,
    TaskType,
    ShellCommandApi,
    ApiCallApi,
    AiTaskApi,
    ReminderTaskApi,
)
from agentlin.tools.scheduler.executor import Executor
from agentlin.tools.scheduler.persistence import Database
from agentlin.tools.scheduler.scheduler import Scheduler
from agentlin.tools.scheduler.utils import human_readable_cron

scheduler = None
server = None
scheduler_task = None
mcp = None

def _format_task_response(task: ScheduleApiTask) -> Dict[str, Any]:
    """Format a task for API response."""
    result = {
        "id": task.id,
        "name": task.name,
        "schedule": task.schedule,
        "schedule_human_readable": human_readable_cron(task.schedule),
        "type": task.type.value,
        "description": task.description,
        "enabled": task.enabled,
        "do_only_once": task.do_only_once,
        "status": task.status.value,
        "created_at": task.created_at.isoformat(),
        "updated_at": task.updated_at.isoformat(),
        "last_run": task.last_run.isoformat() if task.last_run else None,
        "next_run": task.next_run.isoformat() if task.next_run else None,
        "api": task.api.dict(),
    }

    # Add type-specific fields
    if isinstance(task.api, ShellCommandApi):
        result["command"] = task.api.command

    elif isinstance(task.api, ApiCallApi):
        result["api_url"] = task.api.url
        result["api_method"] = task.api.method
        result["api_headers"] = task.api.headers
        if task.api.body:
            result["api_body_keys"] = list(task.api.body.keys())

    elif isinstance(task.api, AiTaskApi):
        result["prompt"] = task.api.prompt

    elif isinstance(task.api, ReminderTaskApi):
        result["reminder_title"] = task.api.title
        result["reminder_message"] = task.api.message

    return result


def _format_execution_response(execution: CoreTaskObject) -> Dict[str, Any]:
    metadata = execution.metadata or {}
    return {
        "id": execution.id,
        "status": execution.status.value,
        "start_time": metadata.get("start_time"),
        "end_time": metadata.get("end_time"),
        "task_object": execution.model_dump(),
    }


def run_scheduler_in_thread(scheduler_instance: Scheduler):
    """Run the scheduler in a separate thread."""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    async def scheduler_loop():
        await scheduler_instance.start()
        try:
            while True:
                await asyncio.sleep(1)
        except asyncio.CancelledError:
            await scheduler_instance.stop()

    loop.run_until_complete(scheduler_loop())
    loop.close()


def handle_sigterm(signum, frame):
    """Handle SIGTERM gracefully"""
    logger.info("Received SIGTERM signal. Shutting down...")
    if scheduler:
        try:
            # Create a new event loop for clean shutdown
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(scheduler.stop())
            loop.close()
        except Exception as e:
            logger.error(f"Error during shutdown: {e}")
    sys.exit(0)


def create_mcp_server(db_path: str, agent_server_url: str, execution_timeout: int):
    global scheduler, server, scheduler_task, mcp
    mcp = FastMCP(
        "Scheduler Tool Server",
        version="0.1.0",
        dependencies=[
            "croniter",
            "pydantic",
            "openai",
            "aiohttp",
        ]
    )

    # Register signal handlers
    signal.signal(signal.SIGTERM, handle_sigterm)

    database = Database(db_path)
    executor = Executor(agent_server_url, execution_timeout)
    scheduler = Scheduler(database, executor)

    # Start the scheduler in a separate thread
    scheduler_thread = threading.Thread(
        target=run_scheduler_in_thread,
        args=(scheduler,),
        daemon=True  # Make thread a daemon so it exits when the main thread exits
    )
    scheduler_thread.start()
    logger.info(f"Scheduler started in background thread")


    @mcp.tool()
    async def list_tasks() -> List[Dict[str, Any]]:
        """List all scheduled tasks."""
        tasks = await scheduler.get_all_tasks()
        return [_format_task_response(task) for task in tasks]

    @mcp.tool()
    async def get_task(task_id: str) -> Optional[Dict[str, Any]]:
        """Get details of a specific task.

        Args:
            task_id: ID of the task to retrieve
        """
        task = await scheduler.get_task(task_id)
        if not task:
            return None

        result = _format_task_response(task)

        # Add execution history
        executions = await scheduler.get_task_executions(task_id)
        result["executions"] = [_format_execution_response(exec) for exec in executions]

        return result

    @mcp.tool()
    async def add_command_task(
        name: str,
        schedule: str,
        command: str,
        description: Optional[str] = None,
        enabled: bool = True,
        do_only_once: bool = True,  # New parameter with default True
    ) -> Dict[str, Any]:
        """Add a new shell command task."""
        task = ScheduleApiTask(
            name=name,
            schedule=schedule,
            api=ShellCommandApi(command=command),
            description=description,
            enabled=enabled,
            do_only_once=do_only_once,
        )

        task = await scheduler.add_task(task)
        return _format_task_response(task)

    @mcp.tool()
    async def add_api_task(
        name: str,
        schedule: str,
        api_url: str,
        api_method: str = "GET",
        api_headers: Optional[Dict[str, str]] = None,
        api_body: Optional[Dict[str, Any]] = None,
        description: Optional[str] = None,
        enabled: bool = True,
        do_only_once: bool = True,  # New parameter with default True
    ) -> Dict[str, Any]:
        """Add a new API call task."""
        task = ScheduleApiTask(
            name=name,
            schedule=schedule,
            api=ApiCallApi(
                url=api_url,
                method=api_method,
                headers=api_headers,
                body=api_body,
            ),
            description=description,
            enabled=enabled,
            do_only_once=do_only_once,
        )

        task = await scheduler.add_task(task)
        return _format_task_response(task)

    @mcp.tool()
    async def add_ai_task(
        name: str,
        schedule: str,
        prompt: str,
        description: Optional[str] = None,
        enabled: bool = True,
        do_only_once: bool = True,  # New parameter with default True
    ) -> Dict[str, Any]:
        """Add a new AI task."""
        task = ScheduleApiTask(
            name=name,
            schedule=schedule,
            api=AiTaskApi(prompt=prompt),
            description=description,
            enabled=enabled,
            do_only_once=do_only_once,
        )

        task = await scheduler.add_task(task)
        return _format_task_response(task)

    @mcp.tool()
    async def add_reminder_task(
        name: str,
        schedule: str,
        message: str,
        title: Optional[str] = None,
        description: Optional[str] = None,
        enabled: bool = True,
        do_only_once: bool = True,
    ) -> Dict[str, Any]:
        """Add a new reminder task that shows a popup notification with sound."""
        # Check if we have notification capabilities on this platform
        os_type = platform.system()
        has_notification_support = True

        if os_type == "Linux":
            # Check for notify-send or zenity
            try:
                import shutil
                notify_send_path = shutil.which("notify-send")
                zenity_path = shutil.which("zenity")
                if not notify_send_path and not zenity_path:
                    has_notification_support = False
            except ImportError:
                # Can't check, we'll try anyway
                pass

        if not has_notification_support:
            logger.warning(f"Platform {os_type} may not support notifications")

        task = ScheduleApiTask(
            name=name,
            schedule=schedule,
            api=ReminderTaskApi(title=title or name, message=message),
            description=description,
            enabled=enabled,
            do_only_once=do_only_once,
        )

        task = await scheduler.add_task(task)
        return _format_task_response(task)

    @mcp.tool()
    async def update_task(
        task_id: str,
        name: Optional[str] = None,
        schedule: Optional[str] = None,
        command: Optional[str] = None,
        api_url: Optional[str] = None,
        api_method: Optional[str] = None,
        api_headers: Optional[Dict[str, str]] = None,
        api_body: Optional[Dict[str, Any]] = None,
        prompt: Optional[str] = None,
        description: Optional[str] = None,
        enabled: Optional[bool] = None,
        do_only_once: Optional[bool] = None,  # New parameter
        reminder_title: Optional[str] = None, # New parameter for reminders
        reminder_message: Optional[str] = None, # New parameter for reminders
    ) -> Optional[Dict[str, Any]]:
        """Update an existing task."""
        task = await scheduler.get_task(task_id)
        if not task:
            return None

        update_data: Dict[str, Any] = {}

        if name is not None:
            update_data["name"] = name
        if schedule is not None:
            update_data["schedule"] = schedule
        if description is not None:
            update_data["description"] = description
        if enabled is not None:
            update_data["enabled"] = enabled
        if do_only_once is not None:
            update_data["do_only_once"] = do_only_once

        api_updates: Dict[str, Any] = {}

        if isinstance(task.api, ShellCommandApi):
            if command is not None:
                api_updates["command"] = command

        elif isinstance(task.api, ApiCallApi):
            if api_url is not None:
                api_updates["url"] = api_url
            if api_method is not None:
                api_updates["method"] = api_method
            if api_headers is not None:
                api_updates["headers"] = api_headers
            if api_body is not None:
                api_updates["body"] = api_body

        elif isinstance(task.api, AiTaskApi):
            if prompt is not None:
                api_updates["prompt"] = prompt

        elif isinstance(task.api, ReminderTaskApi):
            if reminder_title is not None:
                api_updates["title"] = reminder_title
            if reminder_message is not None:
                api_updates["message"] = reminder_message

        if api_updates:
            update_data["api"] = task.api.copy(update=api_updates)

        task = await scheduler.update_task(task_id, **update_data)
        if not task:
            return None

        return _format_task_response(task)

    @mcp.tool()
    async def remove_task(task_id: str) -> bool:
        """Remove a task."""
        return await scheduler.delete_task(task_id)

    @mcp.tool()
    async def enable_task(task_id: str) -> Optional[Dict[str, Any]]:
        """Enable a task."""
        task = await scheduler.enable_task(task_id)
        if not task:
            return None

        return _format_task_response(task)

    @mcp.tool()
    async def disable_task(task_id: str) -> Optional[Dict[str, Any]]:
        """Disable a task."""
        task = await scheduler.disable_task(task_id)
        if not task:
            return None

        return _format_task_response(task)

    @mcp.tool()
    async def run_task_now(task_id: str) -> Optional[Dict[str, Any]]:
        """Run a task immediately."""
        execution = await scheduler.run_task_now(task_id)
        if not execution:
            return None

        task = await scheduler.get_task(task_id)
        if not task:
            return None

        result = _format_task_response(task)
        result["execution"] = _format_execution_response(execution)

        return result

    @mcp.tool()
    async def get_task_executions(task_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Get execution history for a task."""
        executions = await scheduler.get_task_executions(task_id, limit)
        return [_format_execution_response(exec) for exec in executions]

    return mcp


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Run MCP SSE-based server")
    parser.add_argument("--host", default="0.0.0.0", help="Host to bind to")
    parser.add_argument("--port", type=int, default=7779, help="Port to listen on")
    parser.add_argument("--agent-server-url", default="http://localhost:7778", help="Agent server URL")
    parser.add_argument("--debug", action="store_true", help="Enable debug mode")
    args = parser.parse_args()

    logger.info("Starting Scheduler MCP Server...")

    mcp = create_mcp_server(
        db_path="scheduler.db",
        agent_server_url=args.agent_server_url,
        execution_timeout=300  # 5 minutes timeout for task execution
    )
    mcp.run("http", host=args.host, port=args.port, log_level="debug" if args.debug else "info")

