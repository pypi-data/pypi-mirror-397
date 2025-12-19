import traceback
from typing_extensions import Union, AsyncIterable
import asyncio
import time
import os
import json
import uuid
import websockets

from agentlin.core.agent_schema import content_datas_to_content_items, create_logger
from agentlin.route.task_manager import InMemoryTaskManager, SequenceCounter, StreamableTaskParser
from agentlin.core.types import *
from agentlin.store.task_store import InMemoryTaskStore
from agentlin.tools.tool_code_interpreter import iopub_msg_to_tool_response, parse_msg_list_to_tool_response
from agentlin.code_interpreter.client import JupyterClient


TASK_CODE_MANAGER = "task_code_manager"


class ExecuteCodeRequest(BaseModel):
    kernel_id: str
    code: str  # Code to execute in Jupyter kernel
    mode: Literal["simple", "full", "debug"] = "full"  # Mode to return blocks, default is "full"

    # Optional parameters for Jupyter connection
    # If not provided, will use environment variables or default values
    jupyter_host: Optional[str] = None  # Jupyter host, default is None
    jupyter_port: Optional[str] = None  # Jupyter port, default is None
    jupyter_token: Optional[str] = None  # Jupyter token, default is None
    jupyter_timeout: int = 60  # seconds, default is 1 minutes
    jupyter_username: Optional[str] = "user"  # Username for Jupyter connection, default is "user"
    session_id: Optional[str] = None  # Optional session ID, if not provided a new one will be generated
    msg_id: Optional[str] = None  # Optional message ID, if not provided a new one will be generated


class TaskCodeManager(InMemoryTaskManager):
    def __init__(
        self,
        agent_id: str,
        jupyter_host: str = os.getenv("JUPYTER_HOST", "localhost"),
        jupyter_port: int = os.getenv("JUPYTER_PORT", 8888),
        jupyter_token: str = os.getenv("JUPYTER_TOKEN", "jupyter_server_token"),
        jupyter_timeout: int = os.getenv("JUPYTER_TIMEOUT", 60),
        jupyter_username: str = os.getenv("JUPYTER_USERNAME", "user"),
        log_dir: Optional[str] = None,
        task_store: Optional[InMemoryTaskStore] = None,
    ):
        super().__init__(task_store=task_store)
        self.jupyter_host = jupyter_host
        self.jupyter_port = jupyter_port
        self.jupyter_token = jupyter_token
        self.jupyter_timeout = jupyter_timeout
        self.jupyter_username = jupyter_username
        self.client = JupyterClient(
            jupyter_host=jupyter_host,
            jupyter_port=jupyter_port,
            jupyter_token=jupyter_token,
        )

        # 初始化日志记录
        logger_id = f"{agent_id}/{TASK_CODE_MANAGER}"
        self.LOG_DIR = log_dir or os.getenv("LOG_DIR", "output/logs")
        self.logger = create_logger(os.path.join(self.LOG_DIR, "agents"), logger_id)
        self.logger.info(f"初始化 {logger_id}: Jupyter host={jupyter_host}, port={jupyter_port}, token={jupyter_token}, timeout={jupyter_timeout}, username={jupyter_username}")

    def create_kernel(self) -> str:
        return self.client.create_kernel().get("id")

    def delete_kernel(self, kernel_id: str):
        return self.client.delete_kernel(kernel_id)

    def _validate_request(self, request: Union[TaskInvokeRequest, TaskStreamingRequest]):
        task_params: TaskParams = request.params
        try:
            req = ExecuteCodeRequest.model_validate(task_params.payload)
        except Exception as e:
            self.logger.error(f"Invalid request payload: {e}")
            return InvalidParamsError(message=str(e))
        return req

    async def on_task_subscribe(self, request: TaskStreamingRequest) -> AsyncIterable[TaskStreamingResponse]:
        await self.upsert_task(request.params)
        task_params: TaskParams = request.params
        request_id = request.id
        task_id = task_params.id
        session_id = task_params.session_id
        user_id = task_params.user_id
        req = self._validate_request(request)
        if isinstance(req, JSONRPCError):
            self.logger.error(f"Error in tool task: {req}")
            return self._stream_error(request_id=request_id, error=req)
        return self._stream_generator(req, session_id, request_id, task_id, user_id)

    async def _stream_generator(
        self,
        req: ExecuteCodeRequest,
        session_id: str,
        request_id: str,
        task_id: str,
        user_id: str,
    ) -> AsyncIterable[TaskStreamingResponse]:
        initial_task = self.create_task_object(
            task_id=task_id,
            session_id=session_id,
            user_id=user_id,
        )
        initial_task = await self.upsert_task(initial_task)
        parser = StreamableTaskParser(initial_task)
        seq_counter = SequenceCounter()
        resp = await self.created_streaming_response(request_id=request_id, parser=parser, seq_counter=seq_counter)
        yield resp

        # 准备资源
        resp = await self.working_streaming_response(request_id=request_id, parser=parser, seq_counter=seq_counter)
        yield resp

        current_step = 0
        output_item = ToolResultItem(
            call_id=task_id,
            output=[],
            message_content=[],
            block_list=[],
        )
        resp = await self.counting_event_streaming_response(
            request_id=request_id,
            parser=parser,
            seq_counter=seq_counter,
            event=TaskOutputItemAddedEvent(
                agent_step=current_step,
                item=output_item,
            ),
        )
        yield resp

        if not req.kernel_id:
            error_message = "kernel_id is required, but it is not provided or created failed"
            self.logger.error(error_message)
            resp = await self.fail_streaming_response(request_id=request_id, parser=parser, seq_counter=seq_counter, error=error_message)
            yield resp
            return

        # 设置默认参数
        req.jupyter_host = req.jupyter_host or self.jupyter_host
        req.jupyter_port = req.jupyter_port or self.jupyter_port
        req.jupyter_token = req.jupyter_token or self.jupyter_token
        req.jupyter_timeout = req.jupyter_timeout or self.jupyter_timeout
        req.jupyter_username = req.jupyter_username or self.jupyter_username
        req.session_id = req.session_id or session_id
        req.msg_id = req.msg_id or str(uuid.uuid4())

        if not all([req.jupyter_host, req.jupyter_port, req.jupyter_token]):
            error_message = "Missing Jupyter connection config"
            self.logger.error(error_message)
            resp = await self.fail_streaming_response(request_id=request_id, parser=parser, seq_counter=seq_counter, error=error_message)
            yield resp
            return

        url = f"ws://{req.jupyter_host}:{req.jupyter_port}/api/kernels/{req.kernel_id}/channels?token={req.jupyter_token}"

        # 构造 execute_request 消息
        request_msg = {
            "header": {
                "msg_id": req.msg_id,
                "username": req.jupyter_username,
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
        start_time = time.time()
        self.logger.debug(f"Executing code in kernel {req.kernel_id} with timeout {req.jupyter_timeout} seconds")
        tool_result = ToolResult()

        try:
            async with websockets.connect(url, ping_interval=None, max_size=5 * (2**20), write_limit=5 * (2**20)) as ws:
                self.logger.debug(f"Connected to Jupyter kernel {req.kernel_id} at {url}")
                # 发送执行请求
                await ws.send(json.dumps(request_msg, ensure_ascii=False, separators=(",", ":")))

                # 接收执行结果
                while True:
                    try:
                        msg_raw = await asyncio.wait_for(ws.recv(), timeout=1)
                    except asyncio.TimeoutError:
                        # 判断是否超时
                        if time.time() - start_time > req.jupyter_timeout:
                            error_message = f"Execution timeout after {req.jupyter_timeout} seconds. Starting at {start_time}, current time is {time.time()}"
                            self.logger.error(error_message)
                            resp = await self.fail_streaming_response(request_id=request_id, task_id=task_id, error=error_message)
                            yield resp
                            return
                        continue

                    iopub_msg: dict = json.loads(msg_raw)
                    self.logger.debug(f"Received message: \n{json.dumps(iopub_msg, indent=2, ensure_ascii=False)}")

                    # 只收集当前执行的消息
                    if iopub_msg.get("parent_header", {}).get("msg_id") != req.msg_id:
                        continue

                    # 处理 iopub 消息
                    res = iopub_msg_to_tool_response(iopub_msg, req.mode)
                    if res:
                        self.logger.debug(res)
                        tool_result.extend_result(ToolResult.from_dict(res))
                        self.logger.debug(tool_result)
                        resp = await self.counting_event_streaming_response(
                            request_id=request_id,
                            parser=parser,
                            seq_counter=seq_counter,
                            event=TaskToolResultDeltaEvent(
                                item_id=output_item.id,
                                call_id=output_item.call_id,
                                agent_step=current_step,
                                delta_message_content=res.get("message_content", []),
                                delta_block_list=res.get("block_list", []),
                            ),
                        )
                        yield resp

                    self.logger.debug(f"Collected message: {req.msg_id}")

                    if iopub_msg["msg_type"] == "status" and iopub_msg["content"].get("execution_state") == "idle":
                        self.logger.debug(f"Msg {req.msg_id} Execution completed, kernel is idle")
                        break
        except Exception as e:
            self.logger.error(f"WebSocket error: {str(e)}\nurl: {url}\n{traceback.format_exc()}")
            error_message = f"WebSocket error: {str(e)}\nIt means the CodeInterpreter tool is not working properly. Do not use the CodeInterpreter tool any more."
            tool_result.message_content.append({"type": "text", "text": f"<system-reminder>{error_message}</system-reminder>"})

        if not tool_result.message_content:
            error_message = "No output received from Jupyter kernel"
            tool_result.message_content = [{"type": "text", "text": f"<system-reminder>{error_message}</system-reminder>"}]
        resp = await self.counting_event_streaming_response(
            request_id=request_id,
            parser=parser,
            seq_counter=seq_counter,
            event=TaskToolResultDoneEvent(
                item_id=output_item.id,
                call_id=output_item.call_id,
                agent_step=current_step,
                message_content=tool_result.message_content,
                block_list=tool_result.block_list,
            ),
        )
        yield resp
        output_item.message_content = tool_result.message_content
        output_item.block_list = tool_result.block_list
        output_item.output = content_datas_to_content_items(tool_result.message_content)
        resp = await self.counting_event_streaming_response(
            request_id=request_id,
            parser=parser,
            seq_counter=seq_counter,
            event=TaskOutputItemDoneEvent(
                agent_step=current_step,
                item=output_item,
            ),
        )
        yield resp

        resp = await self.complete_streaming_response(request_id=request_id, parser=parser, seq_counter=seq_counter)
        yield resp
