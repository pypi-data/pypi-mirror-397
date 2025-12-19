from collections import defaultdict
import os
import json
import asyncio
from datetime import datetime
import traceback
from typing import Any, AsyncIterable, AsyncIterator, Literal, Optional, Union
import uuid

from fastapi import APIRouter, FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse, FileResponse, Response
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, TypeAdapter, ValidationError
from dotenv import load_dotenv
from loguru import logger
from sse_starlette.sse import EventSourceResponse

from agentlin.core.types import (
    ContentData,
    BlockData,
    DialogData,
    JSONRPCResponse,
    ListTasksParams,
    ListTasksRequest,
    TaskInvokeRequest,
    TaskStreamingRequest,
    TaskStreamingResponse,
    TaskParams,
    ToolData,
    GetTaskRequest,
    TaskQueryParams,
    CancelTaskRequest,
    TaskResubscriptionRequest,
    UnsupportedOperationError,
)
from agentlin.route.agent_config import AgentConfig
from agentlin.route.task_agent_manager import SessionRequest, TaskAgentManager, get_structured_output
from agentlin.route.task_manager import _create_response, _process_request


class CreateTask(BaseModel):
    user_message_content: list[ContentData]
    stream: bool
    structured_output: Optional[dict[str, Any]] = None
    client_id: Optional[str] = None
    request_id: Optional[str] = None
    session_id: Optional[str] = None
    task_id: Optional[str] = None
    user_id: Optional[str] = None
    agent_config: Optional[AgentConfig] = None
    allowed_tools: Optional[list[str]] = None
    disallowed_tools: Optional[list[str]] = None
    allowed_subagents: Optional[list[str]] = None
    stop_tools: Optional[list[str]] = None
    client_tools: Optional[list[ToolData]] = None
    history_messages: Optional[list[DialogData]] = None
    thought_messages: Optional[list[DialogData]] = None
    inference_args: Optional[dict[str, Any]] = None
    workspace_dir: Optional[str] = None
    env: Optional[dict[str, str]] = None
    log_dir: Optional[str] = None
    rollout_save_dir: Optional[str] = None
    return_rollout: bool = False
    include_compress_model_rollout: bool = False  # 是否包含 compress model 的 rollout 结果
    include_subagent_rollout: bool = False  # 是否包含子 agent 的 rollout 结果


def create_task_router(task_manager: TaskAgentManager) -> APIRouter:
    app = APIRouter()

    @app.post("/tasks")
    async def tasks(request: Request, create_req: CreateTask):
        # 注意：避免变量遮蔽，后续会创建同名的 JSON-RPC request 对象，这里先缓存原始 CreateResponse
        request_id = create_req.request_id if create_req.request_id else str(uuid.uuid4())  # 用于将所有复杂的链路串起来，复杂的 api 调用都共享同一个 request_id
        task_id = create_req.task_id if create_req.task_id else str(uuid.uuid4())  # 作为 task_id，会用于区分 main agent task 和 subagent task 的结果
        session_id = create_req.session_id if create_req.session_id else str(uuid.uuid4())  # 用于绑定上下文缓存，用在继续交互的场景，同一个会话包含多轮人机交互，共享同一个上下文
        user_id = create_req.user_id if create_req.user_id else str(uuid.uuid4())
        client_id = create_req.client_id if create_req.client_id else "AIME"
        history_messages = create_req.history_messages if create_req.history_messages is not None else []
        thought_messages = create_req.thought_messages if create_req.thought_messages is not None else []

        req = SessionRequest(
            client_id=client_id,
            user_message_content=create_req.user_message_content,
            agent_config=create_req.agent_config,
            allowed_tools=create_req.allowed_tools,
            disallowed_tools=create_req.disallowed_tools,
            allowed_subagents=create_req.allowed_subagents,
            stop_tools=create_req.stop_tools,
            client_tools=create_req.client_tools,
            history_messages=history_messages,
            thought_messages=thought_messages,
            inference_args=create_req.inference_args,
            workspace_dir=create_req.workspace_dir,
            env=create_req.env,
            structured_output=create_req.structured_output,
            log_dir=create_req.log_dir,
            rollout_save_dir=create_req.rollout_save_dir,
            return_rollout=create_req.return_rollout,
            include_compress_model_rollout=create_req.include_compress_model_rollout,
            include_subagent_rollout=create_req.include_subagent_rollout,
        )
        if create_req.stream:
            if create_req.structured_output is not None:
                logger.warning("stream=True and structured_output is not None, structured_output will be ignored in streaming mode.")
                raise ValueError("stream=True and structured_output is not None, structured_output will be ignored in streaming mode.")
            task_stream_req = TaskStreamingRequest(
                id=request_id,
                params=TaskParams(
                    id=task_id,
                    session_id=session_id,
                    user_id=user_id,
                    payload=req,
                ),
            )
            response = await task_manager.on_task_subscribe(task_stream_req)
        else:
            task_req = TaskInvokeRequest(
                id=request_id,
                params=TaskParams(
                    id=task_id,
                    session_id=session_id,
                    user_id=user_id,
                    payload=req,
                ),
            )
            response = await task_manager.on_task_invoke(task_req)
            if create_req.structured_output is not None:
                response = get_structured_output(response, create_req.structured_output)
        return _create_response(response)

    @app.get("/tasks")
    async def list_tasks(request: Request):
        """
        List all tasks.

        - Returns a JSON-RPC ListTasksResponse envelope.
        """
        request_id = request.headers.get("X-Request-ID", f"req-{str(uuid.uuid4())}")
        user_id = request.headers.get("X-User-ID")
        if not user_id:
            raise HTTPException(status_code=400, detail="X-User-ID header is required")
        req = ListTasksRequest(
            id=request_id,
            params=ListTasksParams(
                user_id=user_id,
            ),
        )
        result = await task_manager.on_list_tasks(req)
        return _create_response(result)


    @app.get("/tasks/{task_id}")
    async def get_task(
        request: Request,
        task_id: str,
    ):
        """
        Retrieve a task by ID.

        - When stream=true, attempts to resubscribe to task events if supported; otherwise returns JSON-RPC error.
        - Non-streaming returns a JSON-RPC GetTaskResponse envelope.
        """
        request_id = request.headers.get("X-Request-ID", f"req-{str(uuid.uuid4())}")
        # Non-streaming fetch
        req = GetTaskRequest(
            id=request_id,
            params=TaskQueryParams(id=task_id),
        )
        result = await task_manager.on_get_task(req)
        return _create_response(result)

    @app.delete("/tasks/{task_id}")
    async def delete_task(request: Request, task_id: str):
        """
        Delete/cancel a task by ID. Maps to CancelTask.
        """
        request_id = request.headers.get("X-Request-ID", f"req-{str(uuid.uuid4())}")
        req = CancelTaskRequest(
            id=request_id,
            params=TaskQueryParams(id=task_id),
        )
        result = await task_manager.on_cancel_task(req)
        return _create_response(result)

    @app.post("/tasks/{task_id}/cancel")
    async def cancel_task(request: Request, task_id: str):
        """
        Cancel a task by ID. Same behavior as DELETE /tasks/{id}.
        """
        # retrieve request_id from header
        request_id = request.headers.get("X-Request-ID", f"req-{str(uuid.uuid4())}")
        req = CancelTaskRequest(
            id=request_id,
            params=TaskQueryParams(id=task_id),
        )
        result = await task_manager.on_cancel_task(req)
        return _create_response(result)

    @app.post("/tasks/{task_id}/pause")
    async def pause_task(request: Request, task_id: str):
        """
        Pause a task by ID.
        """
        raise UnsupportedOperationError("Pause task operation is not supported yet.")

    @app.post("/tasks/{task_id}/resume")
    async def resume_task(request: Request, task_id: str):
        """
        Resume a paused task by ID.
        """
        raise UnsupportedOperationError("Resume task operation is not supported yet.")

    @app.post("/agent")
    async def agent(request: Request):
        """
        Endpoint to process session requests.
        """
        return await _process_request(task_manager, request)


    @app.post("/agent/stop")
    async def stop(request: Request):
        """
        Endpoint to stop an agent.
        """
        try:
            data = await request.json()
            session_id = data.get("session_id")
            if not session_id:
                raise HTTPException(status_code=400, detail="Session ID is required")

            task_manager.delete_session(session_id)
            return {"status": "success", "message": f"Session {session_id} stopped successfully"}
        except Exception as e:
            logger.error(f"Error stopping agent: {e}")
            raise HTTPException(status_code=500, detail=str(e))


    return app
