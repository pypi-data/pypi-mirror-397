import traceback
from typing import Optional, Any, Dict, List, Union
import uuid
import asyncio
from collections import defaultdict

from pydantic import BaseModel, Field
from loguru import logger
from fastapi import APIRouter, HTTPException, Query, Path
import json

from agentlin.environment.server.task_env_manager import TaskEnvManager
from agentlin.environment.core import list_environments_detailed
from agentlin.code_interpreter.types import ToolResponse
from agentlin.core.types import (
    ToolData,
    TaskStreamingResponse,
    TaskInvokeRequest,
    TaskStreamingRequest,
    TaskParams,
)
from agentlin.route.task_manager import _create_response


# ==================== 请求和响应模型 ====================

class CreateEnvRequest(BaseModel):
    """创建环境请求"""
    session_id: Optional[str] = None  # 可选的会话ID，如果不提供则自动生成
    env_id: Optional[str] = None
    user_id: Optional[str] = None
    client_id: str = "default"
    env_vars: Optional[Dict[str, str]] = None
    env_class_path: Optional[str] = None  # 环境类路径，如 "arc-agi-3" 或 "module:Class"
    env_init_kwargs: Optional[Dict[str, Any]] = None  # 环境初始化参数


class CreateEnvResponse(BaseModel):
    """创建环境响应"""
    session_id: str
    env_id: str
    initial_state: Dict[str, Any]  # 初始状态的观察（原 ToolResponse）
    tools: List[ToolData]  # 初始状态可用的工具
    done: bool = False  # 环境是否已结束


class StepRequest(BaseModel):
    """执行步骤请求（工具调用）"""
    session_id: str
    tool_name: str  # 要调用的工具名称
    tool_args: Dict[str, Any] = Field(default_factory=dict)  # 工具参数
    env_vars: Optional[Dict[str, str]] = None  # 环境变量
    stream: bool = False  # 是否流式返回
    request_id: Optional[str] = None
    task_id: Optional[str] = None
    user_id: Optional[str] = None


class StepResponse(BaseModel):
    """执行步骤响应"""
    new_state: Dict[str, Any]  # 新状态的观察（原 ToolResponse）
    tools: List[ToolData]  # 新状态可用的工具
    done: bool = False  # 环境是否已结束
    tool_name: str = ""  # 调用的工具名称
    tool_args: Dict[str, Any] = Field(default_factory=dict)  # 调用的工具参数


class ObservationRequest(BaseModel):
    """获取观察请求"""
    session_id: str


class ObservationResponse(BaseModel):
    """获取观察响应"""
    state: Dict[str, Any]  # 当前状态的观察（原 ToolResponse）
    tools: List[ToolData]  # 当前状态可用的工具
    done: bool = False  # 环境是否已结束


class ResetRequest(BaseModel):
    """重置环境请求"""
    session_id: str
    seed: Optional[int] = None
    options: Optional[Dict[str, Any]] = None


class ResetResponse(BaseModel):
    """重置环境响应"""
    observation: Dict[str, Any]  # 重置后的初始状态（原 ToolResponse）
    tools: List[ToolData]  # 初始状态可用的工具
    done: bool = False  # 环境是否已结束


class CloseRequest(BaseModel):
    """关闭环境请求"""
    session_id: str


class CloseResponse(BaseModel):
    """关闭环境响应"""
    status: str = "closed"
    message: str = "Environment closed successfully"


class SessionInfoResponse(BaseModel):
    """会话信息响应"""
    session_id: str
    user_id: str
    client_id: str
    env_id: str
    env_vars: Dict[str, str]
    is_active: bool
    created_at: float
    last_accessed_at: float


class ListSessionsResponse(BaseModel):
    """列出会话响应"""
    sessions: List[SessionInfoResponse]
    total: int


class EnvironmentInfo(BaseModel):
    """环境信息"""
    name: str
    source: Optional[str] = None
    module: Optional[str] = None
    importable: Optional[Union[str, bool]] = None  # 支持 str 和 bool 类型
    default_params_summary: Optional[str] = None
    origin: Optional[str] = None


class ListEnvironmentsResponse(BaseModel):
    """列出环境响应"""
    environments: List[EnvironmentInfo]
    total: int
    grouped: Dict[str, List[EnvironmentInfo]] = Field(default_factory=dict)


class EnvironmentDetailResponse(BaseModel):
    """环境详细信息响应"""
    name: str
    details: List[EnvironmentInfo]


# ==================== 路由器创建函数 ====================

def create_env_router(task_env_manager: TaskEnvManager) -> APIRouter:
    """创建环境路由器

    Args:
        task_env_manager: 任务环境管理器实例

    Returns:
        APIRouter: FastAPI 路由器
    """
    router = APIRouter(tags=["Environment"])

    # ==================== 核心环境接口 ====================

    @router.post("/create", response_model=CreateEnvResponse)
    async def create_environment(request: CreateEnvRequest):
        """创建新的环境实例"""
        try:
            session_id = request.session_id or f"session-{uuid.uuid4().hex}"
            user_id = request.user_id or f"user-{uuid.uuid4().hex}"

            session = await task_env_manager.create_session(
                session_id=session_id,
                user_id=user_id,
                client_id=request.client_id,
                env_id=request.env_id,
                env_vars=request.env_vars or {},
                env_class_path=request.env_class_path,
                env_init_kwargs=request.env_init_kwargs or {},
            )

            # 获取初始状态和工具
            obs_resp = await task_env_manager.observation(session_id=session_id)

            return CreateEnvResponse(
                session_id=session.session_id,
                env_id=session.env_id,
                initial_state=obs_resp.observation,  # 已经是字典
                tools=obs_resp.tools,
                done=obs_resp.done,
            )
        except Exception as e:
            logger.error(f"Error creating environment: {e}")
            raise HTTPException(status_code=500, detail=str(e))

    @router.post("/step")
    async def step_environment(step_req: StepRequest):
        """在环境中执行工具调用步骤（支持流式和非流式）"""
        try:
            request_id = step_req.request_id if step_req.request_id else str(uuid.uuid4())
            task_id = step_req.task_id if step_req.task_id else str(uuid.uuid4())
            session_id = step_req.session_id
            user_id = step_req.user_id if step_req.user_id else str(uuid.uuid4())

            # 使用 TaskEnvManager.step() 方法
            logger.info(f"Step request: stream={step_req.stream}")

            # 无论哪种模式都需要 await，因为 step() 是 async 函数
            # stream=True: 返回 AsyncGenerator
            # stream=False: 返回 TaskResponse
            response = await task_env_manager.step(
                session_id=session_id,
                tool_name=step_req.tool_name,
                tool_args=step_req.tool_args,
                env_vars=step_req.env_vars,
                request_id=request_id,
                task_id=task_id,
                user_id=user_id,
                stream=step_req.stream,
            )

            logger.info(f"Step response type: {type(response)}")
            return _create_response(response)
        except Exception as e:
            logger.error(f"Error stepping environment: {e}\n{traceback.format_exc()}")
            raise HTTPException(status_code=500, detail=str(e))

    @router.post("/observation", response_model=ObservationResponse)
    async def get_observation(request: ObservationRequest):
        """获取当前环境观察、工具列表和完成状态"""
        try:
            # 一次性获取所有信息
            obs_resp = await task_env_manager.observation(session_id=request.session_id)

            return ObservationResponse(
                state=obs_resp.observation,
                tools=obs_resp.tools,
                done=obs_resp.done,
            )
        except Exception as e:
            logger.error(f"Error getting observation: {e}\n{traceback.format_exc()}")
            raise HTTPException(status_code=500, detail=str(e))

    @router.post("/reset", response_model=ResetResponse)
    async def reset_environment(request: ResetRequest):
        """重置环境到初始状态"""
        try:
            # 执行重置（一次性获取所有信息）
            reset_result = await task_env_manager.reset(
                session_id=request.session_id,
                seed=request.seed,
                options=request.options,
            )

            return ResetResponse(
                observation=reset_result.observation,
                tools=reset_result.tools,
                done=reset_result.done,
            )
        except Exception as e:
            logger.error(f"Error resetting environment: {e}\n{traceback.format_exc()}")
            raise HTTPException(status_code=500, detail=str(e))

    @router.post("/close", response_model=CloseResponse)
    async def close_environment(request: CloseRequest):
        """关闭并清理环境"""
        try:
            session = task_env_manager.get_session(request.session_id)
            if not session:
                raise HTTPException(status_code=404, detail=f"Session not found: {request.session_id}")

            task_env_manager.delete_session(request.session_id)

            return CloseResponse(
                status="closed",
                message=f"Environment session {request.session_id} closed successfully"
            )
        except Exception as e:
            logger.error(f"Error closing environment: {e}\n{traceback.format_exc()}")
            raise HTTPException(status_code=500, detail=str(e))

    # ==================== 管理接口 ====================

    @router.get("/session/{session_id}", response_model=SessionInfoResponse)
    async def get_session_info(session_id: str):
        """获取会话详细信息"""
        try:
            session = task_env_manager.get_session(session_id)
            if not session:
                raise HTTPException(status_code=404, detail=f"Session not found: {session_id}")

            return SessionInfoResponse(
                session_id=session.session_id,
                user_id=session.user_id,
                client_id=session.client_id,
                env_id=session.env_id,
                env_vars=session.env_vars,
                is_active=session.is_active,
                created_at=session.created_at,
                last_accessed_at=session.last_accessed_at,
            )
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error getting session info: {e}")
            raise HTTPException(status_code=500, detail=str(e))

    @router.get("/sessions", response_model=ListSessionsResponse)
    async def list_sessions(user_id: Optional[str] = Query(None, description="Filter by user ID")):
        """列出所有或指定用户的会话"""
        try:
            sessions = task_env_manager.list_sessions(user_id=user_id)

            session_infos = [
                SessionInfoResponse(
                    session_id=s.session_id,
                    user_id=s.user_id,
                    client_id=s.client_id,
                    env_id=s.env_id,
                    env_vars=s.env_vars,
                    is_active=s.is_active,
                    created_at=s.created_at,
                    last_accessed_at=s.last_accessed_at,
                )
                for s in sessions
            ]

            return ListSessionsResponse(
                sessions=session_infos,
                total=len(session_infos),
            )
        except Exception as e:
            logger.error(f"Error listing sessions: {e}")
            raise HTTPException(status_code=500, detail=str(e))

    @router.delete("/session/{session_id}")
    async def delete_session(session_id: str):
        """删除指定会话"""
        try:
            session = task_env_manager.get_session(session_id)
            if not session:
                raise HTTPException(status_code=404, detail=f"Session not found: {session_id}")

            task_env_manager.delete_session(session_id)

            return {"status": "success", "message": f"Session {session_id} deleted successfully"}
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error deleting session: {e}")
            raise HTTPException(status_code=500, detail=str(e))

    @router.post("/sessions/cleanup")
    async def cleanup_inactive_sessions(inactive_seconds: int = Query(3600, description="Inactive threshold in seconds")):
        """清理不活跃的会话"""
        try:
            current_time = asyncio.get_event_loop().time()
            cleaned_sessions = []

            for session_id, session in list(task_env_manager.sessions.items()):
                if current_time - session.last_accessed_at > inactive_seconds:
                    task_env_manager.delete_session(session_id)
                    cleaned_sessions.append(session_id)

            return {
                "status": "success",
                "cleaned_count": len(cleaned_sessions),
                "cleaned_sessions": cleaned_sessions,
            }
        except Exception as e:
            logger.error(f"Error cleaning up sessions: {e}")
            raise HTTPException(status_code=500, detail=str(e))

    @router.get("/health")
    async def health_check():
        """健康检查"""
        return {
            "status": "healthy",
            "active_sessions": len(task_env_manager.sessions),
            "timestamp": asyncio.get_event_loop().time(),
        }

    # ==================== 环境发现接口 ====================

    @router.get("/list", response_model=ListEnvironmentsResponse)
    async def list_environments():
        """列出所有可用的环境"""
        try:
            details = list_environments_detailed()

            # 按名称分组，处理重名情况
            grouped = defaultdict(list)
            all_envs = []

            for d in details:
                env_info = EnvironmentInfo(
                    name=d.get("name"),
                    source=d.get("source"),
                    module=d.get("module"),
                    importable=d.get("importable"),
                    default_params_summary=d.get("default_params_summary"),
                    origin=d.get("origin"),
                )
                all_envs.append(env_info)
                grouped[d.get("name")].append(env_info)

            return ListEnvironmentsResponse(
                environments=all_envs,
                total=len(all_envs),
                grouped=dict(grouped),
            )
        except Exception as e:
            logger.error(f"Error listing environments: {e}")
            raise HTTPException(status_code=500, detail=str(e))

    @router.get("/info/{env_path:path}", response_model=EnvironmentDetailResponse)
    async def get_environment_info(env_path: str = Path(..., description="Environment module path or name")):
        """获取指定环境的详细信息"""
        try:
            details = list_environments_detailed()
            found = [
                EnvironmentInfo(
                    name=d.get("name"),
                    source=d.get("source"),
                    module=d.get("module"),
                    importable=d.get("importable"),
                    default_params_summary=d.get("default_params_summary"),
                    origin=d.get("origin"),
                )
                for d in details
                if d.get("name") == env_path or d.get("module") == env_path
            ]

            if not found:
                raise HTTPException(
                    status_code=404,
                    detail=f"Environment not found: {env_path}"
                )

            return EnvironmentDetailResponse(
                name=env_path,
                details=found,
            )
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error getting environment info: {e}")
            raise HTTPException(status_code=500, detail=str(e))

    return router
