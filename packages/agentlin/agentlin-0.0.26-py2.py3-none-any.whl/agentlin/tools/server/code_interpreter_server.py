import asyncio
import sys
from typing_extensions import Literal, Optional
import json
import uuid
import traceback

from pydantic import BaseModel
import websockets
import httpx
import os
import time
import datetime

from pydantic import BaseModel
from fastapi import FastAPI, Request, Response
from fastapi.responses import JSONResponse, StreamingResponse
from fastapi.middleware.gzip import GZipMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from loguru import logger

from agentlin.code_interpreter.jupyter_parse import iopub_msg_to_tool_response, parse_msg_list_to_tool_response


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # 记录请求开始时间
        start_time = time.time()

        # 获取客户端IP
        client_ip = request.client.host if request.client else "unknown"

        # 获取用户代理
        user_agent = request.headers.get("user-agent", "unknown")

        # 记录请求信息
        logger.info(f"REQUEST: {request.method} {request.url} from {client_ip} - User-Agent: {user_agent}")

        try:
            # 处理请求
            response = await call_next(request)

            # 计算处理时间
            process_time = time.time() - start_time

            # 记录响应信息
            logger.info(f"RESPONSE: {request.method} {request.url.path} - Status: {response.status_code} - Time: {process_time:.3f}s - Size: {response.headers.get('content-length', 'unknown')} bytes")

            return response

        except Exception as e:
            # 记录异常
            process_time = time.time() - start_time
            logger.error(f"REQUEST FAILED: {request.method} {request.url.path} - Time: {process_time:.3f}s - Error: {str(e)}")
            raise


def create_error_response(status_code: int, status_msg: str, traceback_info: str = None):
    """
    创建统一的错误响应格式
    """
    response_content = {
        "status_code": status_code,
        "status_msg": status_msg,
        "traceback": traceback_info,
        "data": None
    }
    return JSONResponse(content=response_content, status_code=200)


app = FastAPI()

# 添加请求日志中间件
app.add_middleware(RequestLoggingMiddleware)


class ExecuteRequest(BaseModel):
    kernel_id: str  # Kernel ID to connect to Jupyter kernel
    code: str  # Code to execute in Jupyter kernel
    mode: Literal["simple", "full", "debug"] = "full"  # Mode to return blocks, default is "full"

    # Optional parameters for Jupyter connection
    # If not provided, will use environment variables or default values
    timeout: int = 60  # seconds, default is 1 minutes
    jupyter_host: Optional[str] = None  # Jupyter host, default is None
    jupyter_port: Optional[str] = None  # Jupyter port, default is None
    jupyter_token: Optional[str] = None  # Jupyter token, default is None
    session_id: Optional[str] = None  # Optional session ID, if not provided a new one will be generated
    call_id: Optional[str] = None  # Optional call ID, if not provided a new one will be generated
    msg_id: Optional[str] = None  # Optional message ID, if not provided a new one will be generated
    username: Optional[str] = "user"  # Username for Jupyter connection, default is "user"


async def interactive_coding(req: ExecuteRequest):
    if not req.kernel_id:
        logger.error("kernel_id is required")
        error_response = create_error_response(400, "kernel_id is required")
        yield f"data: {json.dumps(error_response, ensure_ascii=False)}\n\n"
        return

    # 设置默认参数
    req.jupyter_host = req.jupyter_host or os.getenv("JUPYTER_HOST", "localhost")
    req.jupyter_port = req.jupyter_port or os.getenv("JUPYTER_PORT", "8888")
    req.jupyter_token = req.jupyter_token or os.getenv("JUPYTER_TOKEN", None)
    req.timeout = req.timeout or os.getenv("JUPYTER_TIMEOUT", 60)
    req.username = req.username or os.getenv("JUPYTER_USERNAME", "user")
    req.session_id = req.session_id or str(uuid.uuid4())
    req.msg_id = req.msg_id or str(uuid.uuid4())

    if not all([req.jupyter_host, req.jupyter_port, req.jupyter_token]):
        logger.error("Missing Jupyter connection config")
        error_response = create_error_response(400, "Missing Jupyter connection config")
        yield f"data: {json.dumps(error_response, ensure_ascii=False)}\n\n"
        return

    url = f"ws://{req.jupyter_host}:{req.jupyter_port}/api/kernels/{req.kernel_id}/channels?token={req.jupyter_token}"

    # 构造 execute_request 消息
    request_msg = {
        "header": {
            "msg_id": req.msg_id,
            "username": req.username,
            "session": req.session_id,
            "msg_type": "execute_request",
            "version": "5.3",
        },
        "parent_header": {},
        "metadata": {},
        "content": {
            "code": req.code,
            "silent": False,
            "store_history": True,
            "user_expressions": {},
            "allow_stdin": False,
            "stop_on_error": True,
        },
    }

    # 保存结果
    results = []
    message_content = []
    block_list = []

    start_time = time.time()
    logger.debug(f"Executing code in kernel {req.kernel_id} (Config: timeout {req.timeout} seconds)")

    try:
        async with websockets.connect(url, ping_interval=None, max_size=5 * (2**20), write_limit=5 * (2**20)) as ws:
            logger.debug(f"Connected to Jupyter kernel {req.kernel_id} at {url}")
            # 发送执行请求
            await ws.send(json.dumps(request_msg, ensure_ascii=False, separators=(",", ":")))

            while True:
                try:
                    msg_raw = await asyncio.wait_for(ws.recv(), timeout=1)
                except asyncio.TimeoutError:
                    # 判断是否超时
                    if time.time() - start_time > req.timeout:
                        error_response = {"status_code": 408, "status_msg": "Execution timeout", "traceback": None, "data": None}
                        yield f"data: {json.dumps(error_response, ensure_ascii=False)}\n\n"
                        return
                    continue

                iopub_msg: dict = json.loads(msg_raw)
                logger.debug(f"Received message: \n{json.dumps(iopub_msg, indent=2, ensure_ascii=False)}")

                # 只收集当前执行的消息
                if iopub_msg.get("parent_header", {}).get("msg_id") != req.msg_id:
                    continue

                # 处理 iopub 消息
                response = iopub_msg_to_tool_response(iopub_msg, req.mode)
                if response:
                    if req.call_id:
                        response["call_id"] = req.call_id
                    yield f"data: {json.dumps(response, ensure_ascii=False)}\n\n"
                    await asyncio.sleep(0.1)  # 确保流式传输的间隔
                    content = response.get("message_content", [])
                    block = response.get("block_list", [])
                    message_content.extend(content)
                    block_list.extend(block)

                logger.debug(f"Collected message: {req.msg_id}")

                if iopub_msg["msg_type"] == "status" and iopub_msg["content"].get("execution_state") == "idle":
                    logger.debug(f"Msg {req.msg_id} Execution completed, kernel is idle")
                    break

    except Exception as e:
        logger.error(f"WebSocket error: {str(e)}\nurl: {url}\n{traceback.format_exc()}")
        error_response = {"status_code": 500, "status_msg": f"WebSocket error. Exception: {e}", "traceback": f"url: {url}\n{traceback.format_exc()}", "data": None}
        yield f"data: {json.dumps(error_response, ensure_ascii=False)}\n\n"
        return


@app.post("/api/v2/streaming_execute", response_class=StreamingResponse)
async def api_v2_streaming_execute(req: ExecuteRequest):
    stream = interactive_coding(req)
    return StreamingResponse(
        stream,
        media_type="text/event-stream",
    )


async def execute(req: ExecuteRequest):
    if not req.kernel_id:
        logger.error("kernel_id is required")
        return create_error_response(400, "kernel_id is required")

    # 设置默认参数
    req.jupyter_host = req.jupyter_host or os.getenv("JUPYTER_HOST", "localhost")
    req.jupyter_port = req.jupyter_port or os.getenv("JUPYTER_PORT", "8888")
    req.jupyter_token = req.jupyter_token or os.getenv("JUPYTER_TOKEN", None)
    req.timeout = req.timeout or os.getenv("JUPYTER_TIMEOUT", 60)
    req.username = req.username or os.getenv("JUPYTER_USERNAME", "user")
    req.session_id = req.session_id or str(uuid.uuid4())
    req.msg_id = req.msg_id or str(uuid.uuid4())

    if not all([req.jupyter_host, req.jupyter_port, req.jupyter_token]):
        logger.error("Missing Jupyter connection config")
        return create_error_response(400, "Missing Jupyter connection config")

    url = f"ws://{req.jupyter_host}:{req.jupyter_port}/api/kernels/{req.kernel_id}/channels?token={req.jupyter_token}"

    # 构造 execute_request 消息
    request_msg = {
        "header": {
            "msg_id": req.msg_id,
            "username": req.username,
            "session": req.session_id,
            "msg_type": "execute_request",
            "version": "5.3",
        },
        "parent_header": {},
        "metadata": {},
        "content": {
            "code": req.code,
            "silent": False,
            "store_history": True,
            "user_expressions": {},
            "allow_stdin": False,
            "stop_on_error": True,
        },
    }

    # 保存结果
    results = []

    start_time = time.time()
    logger.debug(f"Executing code in kernel {req.kernel_id} (Config: timeout {req.timeout} seconds)")

    try:
        async with websockets.connect(url, ping_interval=None, max_size=5 * (2**20), write_limit=5 * (2**20)) as ws:
            logger.debug(f"Connected to Jupyter kernel {req.kernel_id} at {url}")
            # 发送执行请求
            await ws.send(json.dumps(request_msg, ensure_ascii=False, separators=(",", ":")))

            while True:
                try:
                    msg_raw = await asyncio.wait_for(ws.recv(), timeout=1)
                except asyncio.TimeoutError:
                    # 判断是否超时
                    if time.time() - start_time > req.timeout:
                        logger.error("Execution timeout")
                        return create_error_response(408, "Execution timeout")
                    continue

                msg = json.loads(msg_raw)
                logger.debug(f"Received message: {json.dumps(msg, indent=2, ensure_ascii=False)}")

                # 只收集当前执行的消息
                if msg.get("parent_header", {}).get("msg_id") != req.msg_id:
                    continue

                results.append(msg)
                logger.debug(f"Collected message: {req.msg_id}")

                if msg["msg_type"] == "status" and msg["content"].get("execution_state") == "idle":
                    logger.debug(f"Msg {req.msg_id} Execution completed, kernel is idle")
                    break

    except Exception as e:
        logger.error(f"WebSocket error. Exception: {e}\nurl: {url}\n{traceback.format_exc()}")
        return create_error_response(500, f"WebSocket error. Exception: {e}", f"url: {url}\n{traceback.format_exc()}")

    try:
        logger.debug(f"Parsing {len(results)} execution results")
        response = parse_msg_list_to_tool_response(results, req.mode)
        message_content = response["message_content"]
        block_list = response["block_list"]
    except Exception as e:
        logger.error(f"Error parsing execution results: {str(e)}\n\nresults = {json.dumps(results, indent=2, ensure_ascii=False)}\n{traceback.format_exc()}")
        return create_error_response(500, f"Error parsing execution results. Exception: {e}", f"results = {json.dumps(results, indent=2, ensure_ascii=False)}\n{traceback.format_exc()}")

    data = {
        "message_content": message_content,
        "block_list": block_list,
        "execution_time": time.time() - start_time,
    }
    if req.call_id:
        data["call_id"] = req.call_id
    return {
        "status_code": 200,
        "status_msg": "",
        "data": data,
    }


@app.post("/api/v3/execute")
async def api_v3_execute(req: ExecuteRequest):
    response = await execute(req)
    return response


@app.post("/api/v2/execute")
async def api_v2_execute(req: ExecuteRequest):
    response = await execute(req)
    if isinstance(response, dict) and response.get("status_code") == 200 and response.get("data"):
        return response.get("data")
    return response


@app.get("/jupyter/get")
async def jupyter_get(req: Request):
    """
    代理GET请求到Jupyter服务
    """
    try:
        body = await req.json()
    except Exception as e:
        logger.error(f"Invalid JSON body. Exception: {e}\n{traceback.format_exc()}")
        return create_error_response(400, f"Invalid JSON body. Exception: {e}", traceback.format_exc())

    jupyter_protocol = body.get("jupyter_protocol", "http")
    jupyter_host = body.get("jupyter_host", "localhost")
    jupyter_port = body.get("jupyter_port", "8888")
    jupyter_path = body.get("jupyter_path", "/")
    jupyter_token = body.get("jupyter_token", None)
    jupyter_params = body.get("jupyter_params", None)
    timeout = body.get("timeout", 30)  # 默认超时30秒

    # 验证必要参数
    if not jupyter_host or not jupyter_port:
        logger.error("Missing jupyter_host or jupyter_port")
        return create_error_response(400, "Missing jupyter_host or jupyter_port")

    if not jupyter_path:
        logger.error("Missing jupyter_path")
        return create_error_response(400, "Missing jupyter_path")
    if not isinstance(jupyter_path, str):
        logger.error("jupyter_path must be a string")
        return create_error_response(400, "jupyter_path must be a string")
    if not jupyter_path.startswith("/"):
        logger.error("jupyter_path must start with '/'")
        return create_error_response(400, "jupyter_path must start with '/'")

    # 构建目标URL
    target_url = f"{jupyter_protocol}://{jupyter_host}:{jupyter_port}{jupyter_path}"

    try:
        # 转发请求到Jupyter服务
        async with httpx.AsyncClient() as client:
            headers = dict(req.headers)
            headers.pop("host", None)
            headers.pop("content-length", None)
            if jupyter_token:
                headers["Authorization"] = f"token {jupyter_token}"

            logger.debug(f"Forwarding GET request to {target_url} with params {jupyter_params} and headers {headers}")
            resp = await client.get(
                target_url,
                headers=headers,
                timeout=timeout,  # 设置请求超时时间
                params=jupyter_params,  # 添加查询参数
            )
            logger.debug(f"Response from Jupyter GET request: {resp.status_code} {resp.text}")

            response_content = {
                "status_code": resp.status_code,
                "status_msg": "ok",
                "data": resp.json() if resp.headers.get("content-type") == "application/json" else resp.content.decode(),
                "headers": dict(resp.headers),
            }
            return JSONResponse(content=response_content, status_code=200)
    except httpx.TimeoutException:
        logger.error(f"Request timed out after {timeout} seconds")
        return create_error_response(504, f"Request timed out after {timeout} seconds")
    except Exception as e:
        logger.error(f"Exception: {str(e)}\n{traceback.format_exc()}")
        return create_error_response(500, str(e), traceback.format_exc())


@app.post("/jupyter/post")
async def jupyter_post(req: Request):
    """
    代理POST请求到Jupyter服务
    """
    try:
        body = await req.json()
    except Exception as e:
        logger.error(f"Invalid JSON body. Exception: {e}\n{traceback.format_exc()}")
        return create_error_response(400, f"Invalid JSON body. Exception: {e}", traceback.format_exc())

    jupyter_protocol = body.get("jupyter_protocol", "http")
    jupyter_host = body.get("jupyter_host", "localhost")
    jupyter_port = body.get("jupyter_port", "8888")
    jupyter_path = body.get("jupyter_path", "/")
    jupyter_token = body.get("jupyter_token", None)
    jupyter_params = body.get("jupyter_params", None)
    timeout = body.get("timeout", 30)  # 默认超时30秒

    # 验证必要参数
    if not jupyter_host or not jupyter_port:
        logger.error("Missing jupyter_host or jupyter_port")
        return create_error_response(400, "Missing jupyter_host or jupyter_port")

    if not jupyter_path:
        logger.error("Missing jupyter_path")
        return create_error_response(400, "Missing jupyter_path")
    if not isinstance(jupyter_path, str):
        logger.error("jupyter_path must be a string")
        return create_error_response(400, "jupyter_path must be a string")
    if not jupyter_path.startswith("/"):
        logger.error("jupyter_path must start with '/'")
        return create_error_response(400, "jupyter_path must start with '/'")

    # 构建目标URL
    target_url = f"{jupyter_protocol}://{jupyter_host}:{jupyter_port}{jupyter_path}"

    try:
        # 转发请求到Jupyter服务
        async with httpx.AsyncClient() as client:
            headers = dict(req.headers)
            headers.pop("host", None)
            headers.pop("content-length", None)
            if jupyter_token:
                headers["Authorization"] = f"token {jupyter_token}"

            logger.debug(f"Forwarding POST request to {target_url} with params {jupyter_params} and headers {headers}")
            resp = await client.post(
                target_url,
                headers=headers,
                timeout=timeout,  # 设置请求超时时间
                params=jupyter_params,  # 添加查询参数
            )
            logger.debug(f"Response from Jupyter POST request: {resp.status_code} {resp.text}")


            response_content = {
                "status_code": resp.status_code,
                "status_msg": "ok",
                "data": resp.json() if resp.headers.get("content-type") == "application/json" else resp.content.decode(),
                "headers": dict(resp.headers),
            }
            return JSONResponse(content=response_content, status_code=200)
    except httpx.TimeoutException:
        logger.error(f"Request timed out after {timeout} seconds")
        return create_error_response(504, f"Request timed out after {timeout} seconds")
    except Exception as e:
        logger.error(f"Exception: {str(e)}\n{traceback.format_exc()}")
        return create_error_response(500, str(e), traceback.format_exc())


@app.post("/jupyter/patch")
async def jupyter_patch(req: Request):
    """
    代理PATCH请求到Jupyter服务
    """
    try:
        body = await req.json()
    except Exception as e:
        logger.error(f"Invalid JSON body. Exception: {e}\n{traceback.format_exc()}")
        return create_error_response(400, f"Invalid JSON body. Exception: {e}", traceback.format_exc())

    jupyter_protocol = body.get("jupyter_protocol", "http")
    jupyter_host = body.get("jupyter_host", "localhost")
    jupyter_port = body.get("jupyter_port", "8888")
    jupyter_path = body.get("jupyter_path", "/")
    jupyter_token = body.get("jupyter_token", None)
    jupyter_params = body.get("jupyter_params", None)
    timeout = body.get("timeout", 30)  # 默认超时30秒

    # 验证必要参数
    if not jupyter_host or not jupyter_port:
        logger.error("Missing jupyter_host or jupyter_port")
        return create_error_response(400, "Missing jupyter_host or jupyter_port")

    if not jupyter_path:
        logger.error("Missing jupyter_path")
        return create_error_response(400, "Missing jupyter_path")
    if not isinstance(jupyter_path, str):
        logger.error("jupyter_path must be a string")
        return create_error_response(400, "jupyter_path must be a string")
    if not jupyter_path.startswith("/"):
        logger.error("jupyter_path must start with '/'")
        return create_error_response(400, "jupyter_path must start with '/'")

    # 构建目标URL
    target_url = f"{jupyter_protocol}://{jupyter_host}:{jupyter_port}{jupyter_path}"

    try:
        # 转发请求到Jupyter服务
        async with httpx.AsyncClient() as client:
            headers = dict(req.headers)
            headers.pop("host", None)
            headers.pop("content-length", None)
            if jupyter_token:
                headers["Authorization"] = f"token {jupyter_token}"

            logger.debug(f"Forwarding PATCH request to {target_url} with params {jupyter_params} and headers {headers}")
            resp = await client.patch(
                target_url,
                headers=headers,
                timeout=timeout,  # 设置请求超时时间
                params=jupyter_params,  # 添加查询参数
            )
            logger.debug(f"Response from Jupyter PATCH request: {resp.status_code} {resp.text}")


            response_content = {
                "status_code": resp.status_code,
                "status_msg": "ok",
                "data": resp.json() if resp.headers.get("content-type") == "application/json" else resp.content.decode(),
                "headers": dict(resp.headers),
            }
            return JSONResponse(content=response_content, status_code=200)
    except httpx.TimeoutException:
        logger.error(f"Request timed out after {timeout} seconds")
        return create_error_response(504, f"Request timed out after {timeout} seconds")
    except Exception as e:
        logger.error(f"Exception: {str(e)}\n{traceback.format_exc()}")
        return create_error_response(500, str(e), traceback.format_exc())


@app.post("/jupyter/put")
async def jupyter_put(req: Request):
    """
    代理PUT请求到Jupyter服务
    """
    try:
        body = await req.json()
    except Exception as e:
        logger.error(f"Invalid JSON body. Exception: {e}\n{traceback.format_exc()}")
        return create_error_response(400, f"Invalid JSON body. Exception: {e}", traceback.format_exc())

    jupyter_protocol = body.get("jupyter_protocol", "http")
    jupyter_host = body.get("jupyter_host", "localhost")
    jupyter_port = body.get("jupyter_port", "8888")
    jupyter_path = body.get("jupyter_path", "/")
    jupyter_token = body.get("jupyter_token", None)
    jupyter_params = body.get("jupyter_params", None)
    timeout = body.get("timeout", 30)  # 默认超时30秒

    # 验证必要参数
    if not jupyter_host or not jupyter_port:
        logger.error("Missing jupyter_host or jupyter_port")
        return create_error_response(400, "Missing jupyter_host or jupyter_port")

    if not jupyter_path:
        logger.error("Missing jupyter_path")
        return create_error_response(400, "Missing jupyter_path")
    if not isinstance(jupyter_path, str):
        logger.error("jupyter_path must be a string")
        return create_error_response(400, "jupyter_path must be a string")
    if not jupyter_path.startswith("/"):
        logger.error("jupyter_path must start with '/'")
        return create_error_response(400, "jupyter_path must start with '/'")

    # 构建目标URL
    target_url = f"{jupyter_protocol}://{jupyter_host}:{jupyter_port}{jupyter_path}"

    try:
        # 转发请求到Jupyter服务
        async with httpx.AsyncClient() as client:
            headers = dict(req.headers)
            headers.pop("host", None)
            headers.pop("content-length", None)
            if jupyter_token:
                headers["Authorization"] = f"token {jupyter_token}"

            logger.debug(f"Forwarding PUT request to {target_url} with params {jupyter_params} and headers {headers}")
            resp = await client.put(
                target_url,
                headers=headers,
                timeout=timeout,  # 设置请求超时时间
                params=jupyter_params,  # 添加查询参数
            )
            logger.debug(f"Response from Jupyter PUT request: {resp.status_code} {resp.text}")


            response_content = {
                "status_code": resp.status_code,
                "status_msg": "ok",
                "data": resp.json() if resp.headers.get("content-type") == "application/json" else resp.content.decode(),
                "headers": dict(resp.headers),
            }
            return JSONResponse(content=response_content, status_code=200)

    except httpx.TimeoutException:
        logger.error(f"Request timed out after {timeout} seconds")
        return create_error_response(504, f"Request timed out after {timeout} seconds")
    except Exception as e:
        logger.error(f"Exception: {str(e)}\n{traceback.format_exc()}")
        return create_error_response(500, str(e), traceback.format_exc())


@app.post("/jupyter/delete")
async def jupyter_delete(req: Request):
    """
    代理DELETE请求到Jupyter服务
    """
    try:
        body = await req.json()
    except Exception as e:
        logger.error(f"Invalid JSON body. Exception: {e}\n{traceback.format_exc()}")
        return create_error_response(400, f"Invalid JSON body. Exception: {e}", traceback.format_exc())

    jupyter_protocol = body.get("jupyter_protocol", "http")
    jupyter_host = body.get("jupyter_host", "localhost")
    jupyter_port = body.get("jupyter_port", "8888")
    jupyter_path = body.get("jupyter_path", "/")
    jupyter_token = body.get("jupyter_token", None)
    jupyter_params = body.get("jupyter_params", None)
    timeout = body.get("timeout", 30)  # 默认超时30秒

    # 验证必要参数
    if not jupyter_host or not jupyter_port:
        logger.error("Missing jupyter_host or jupyter_port")
        return create_error_response(400, "Missing jupyter_host or jupyter_port")

    if not jupyter_path:
        logger.error("Missing jupyter_path")
        return create_error_response(400, "Missing jupyter_path")
    if not isinstance(jupyter_path, str):
        logger.error("jupyter_path must be a string")
        return create_error_response(400, "jupyter_path must be a string")
    if not jupyter_path.startswith("/"):
        logger.error("jupyter_path must start with '/'")
        return create_error_response(400, "jupyter_path must start with '/'")

    # 构建目标URL
    target_url = f"{jupyter_protocol}://{jupyter_host}:{jupyter_port}{jupyter_path}"

    try:
        # 转发请求到Jupyter服务
        async with httpx.AsyncClient() as client:
            headers = dict(req.headers)
            headers.pop("host", None)
            headers.pop("content-length", None)
            if jupyter_token:
                headers["Authorization"] = f"token {jupyter_token}"

            logger.debug(f"Forwarding DELETE request to {target_url} with params {jupyter_params} and headers {headers}")
            resp = await client.delete(
                target_url,
                headers=headers,
                timeout=timeout,  # 设置请求超时时间
                params=jupyter_params,  # 添加查询参数
            )
            logger.debug(f"Response from Jupyter DELETE request: {resp.status_code} {resp.text}")

            response_content = {
                "status_code": resp.status_code,
                "status_msg": "ok",
                "data": resp.json() if resp.headers.get("content-type") == "application/json" else resp.content.decode(),
                "headers": dict(resp.headers),
            }
            return JSONResponse(content=response_content, status_code=200)
    except httpx.TimeoutException:
        logger.error(f"Request timed out after {timeout} seconds")
        return create_error_response(504, f"Request timed out after {timeout} seconds")
    except Exception as e:
        logger.error(f"Exception: {str(e)}\n{traceback.format_exc()}")
        return create_error_response(500, str(e), traceback.format_exc())


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


@app.get("/")
def root():
    """
    Root endpoint to check if the service is running.
    """
    return {"message": "Code Interpreter Service is running."}


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
    return {"version": "1.0.0", "description": "Code Interpreter Service for Jupyter Kernels"}


app.add_middleware(GZipMiddleware, minimum_size=4000)  # 仅压缩大于4KB的数据


def init_server(app: FastAPI, log_dir: str, debug: bool):
    os.makedirs(log_dir, exist_ok=True)  # 确保日志目录存在
    logger.remove()  # 移除现有的日志处理器，包括默认的控制台日志处理器
    if debug:
        # 在debug模式下，将日志级别调整为DEBUG
        logger.add(
            log_dir + "/code_interpreter_{time:YYYY-MM-DD}.log",
            rotation="1 day",
            retention="30 days",
            compression="zip",
            format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
            level="DEBUG",
            enqueue=True,  # 🔥 异步错误日志
            backtrace=True,
            diagnose=True,
            catch=True,  # 捕获日志记录本身的异常
        )
        app.debug = True
        logger.info("Debug mode is enabled.")
    else:
        logger.add(
            log_dir + "/code_interpreter_{time:YYYY-MM-DD}.log",
            rotation="1 day",
            retention="30 days",
            compression="zip",
            format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
            level="INFO",
            enqueue=True,  # 🔥 异步错误日志
            backtrace=True,
            diagnose=True,
            catch=True,  # 捕获日志记录本身的异常
        )
    logger.add(
        sys.stderr,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        level="INFO",
        enqueue=False,  # 控制台输出保持同步，便于实时查看
    )


if __name__ == "__main__":
    import argparse
    import uvicorn

    parser = argparse.ArgumentParser(description="Run the FastAPI app")
    parser.add_argument("--host", type=str, default="0.0.0.0", help="Host to bind")
    parser.add_argument("--port", type=int, default=8889, help="Port to bind")
    parser.add_argument("--debug", action="store_true", help="Enable debug mode")
    parser.add_argument("--workers", type=int, default=1, help="Number of worker processes")
    parser.add_argument("--log-dir", type=str, default="logs/code_interpreter", help="Directory to store logs")
    args = parser.parse_args()

    # 配置日志
    # date_str = datetime.datetime.now().strftime("%Y-%m-%d")
    init_server(app, args.log_dir, args.debug)

    logger.info(f"Starting Code Interpreter Service on {args.host}:{args.port}")
    # 当使用 workers > 1 时，需要使用导入字符串而不是应用对象
    if args.workers > 1:
        uvicorn.run("code_interpreter:app", host=args.host, port=args.port, workers=args.workers)
    else:
        uvicorn.run(app, host=args.host, port=args.port)
    # python code_interpreter.py --host $HOST --port $PORT
