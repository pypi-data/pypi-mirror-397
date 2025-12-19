import copy
import datetime
import time
import uuid
import json
from pathlib import Path
from typing_extensions import Optional, TypedDict

import streamlit as st
from streamlit.delta_generator import DeltaGenerator
from streamlit.runtime.uploaded_file_manager import UploadedFile
from streamlit.elements.lib.column_types import ColumnConfig
from streamlit_markdown import st_markdown
from loguru import logger
from PIL import Image
from plotly import graph_objects as go
from plotly import io as pio

from agentlin.code_interpreter.jupyter_saver import save_jupyter_notebook
from agentlin.core.agent_schema import exist_apply, extract_action, extract_answer, extract_code, extract_code_block, extract_thought, parse_text_with_apply, remove_thoughts
from agentlin.core.multimodal import image_content
from agentlin.core.types import DialogData


def multimodal_content(text: str, files: list[UploadedFile], workspace: Optional[str] = None) -> list[dict]:
    content = []
    content.append({"type": "text", "text": text})
    if files:
        workspace_path = Path(workspace) if workspace else Path("output/code/images")
        workspace_path.mkdir(parents=True, exist_ok=True)
        for file in files:
            image_id = file.file_id
            image_file_path = workspace_path / f"{image_id}.png"
            if not image_file_path.exists():
                with open(image_file_path, "wb") as f:
                    f.write(file.getvalue())
            image = Image.open(file)
            content.extend(image_content(image, image_id))
    return content


def access_variable(agent: AgentCore, variable_name: str):
    access_code = f"""{variable_name}"""
    content_to_agent, _ = agent.simulator.execute(access_code)
    if len(content_to_agent) == 0:
        return None
    msg = content_to_agent[-1]
    logger.debug(f"Access variable {variable_name} content: {msg}")
    if "json" in msg:
        return msg["json"]
    if "plotly_json" in msg:
        return msg["plotly_json"]
    if "text" in msg:
        txt = msg["text"]
        try:
            variable_value = json.loads(txt)
            return variable_value
        except json.JSONDecodeError:
            logger.error(f"无法解析 JSON 字符串: {txt}")
            return None
    return None


def render_content(content: list[dict] | str, key=None):
    if isinstance(content, list):
        for part in content:
            if part["type"] == "text" or part["type"] == "function_call_output":
                if part["type"] == "function_call_output":
                    text = part["output"]
                elif part["type"] == "text":
                    text = part["text"]
                else:
                    text = ""
                if "code-interpreter" in part and not part["code-interpreter"]:
                    st.write(text)
                else:
                    code_block = extract_code_block(remove_thoughts(text))
                    if code_block:
                        code = extract_code(code_block)
                        for i, split in enumerate(text.split(code_block)):
                            st.write(split)
                            if i < len(text.split(code_block)) - 1:
                                # st.write("<code-interpreter>")
                                # st.divider()
                                st.code(code, language="python")
                                # st.divider()
                                # st.write("</code-interpreter>")
                    elif "code-interpreter" in part and part["code-interpreter"]:
                        code = text
                        st.code(code, language="python")
                    else:
                        thought = extract_thought(text)
                        if thought:
                            # st.write("<think>")
                            st.divider()
                            st.write(thought)
                            st.divider()
                            # st.write("</think>")
                            text = remove_thoughts(text)
                        if "<answer>" in text:
                            answer = extract_answer(text)
                            if exist_apply(answer):
                                text_blocks = parse_text_with_apply(answer)
                                for block in text_blocks:
                                    if block["type"] == "text":
                                        st_markdown(block["text"], key=str(uuid.uuid4()))
                                    elif block["type"] == "apply":
                                        st.code(block["apply"], language="python")
                                        if st.button("应用到客户端", key=f"{block['apply']}_{key}"):
                                            print("hello?")
                                            new_config = access_variable(agent, block["apply"])
                                            if new_config:
                                                st.session_state["figure_config"] = new_config
                                                logger.info(f"已更新配置: {new_config}")
                                                st.rerun()
                                            else:
                                                st.error(f"无法访问变量 {block['apply']}，请检查代码是否正确。")
                            else:
                                st_markdown(answer, key=str(uuid.uuid4()))
                        elif "<action>" in text:
                            action = extract_action(text)
                            st.code(action, language="python")
                        else:
                            st.write(text)
            elif part["type"] == "image_url":
                image_url = part["image_url"]
                if isinstance(image_url, dict):
                    image_url = image_url["url"]
                image = base64_to_image(image_url)
                origin_image = image
                image = scale_to_fit_and_add_scale_bar(image)  # 缩放图片到目标大小，并添加比例尺
                left_img, right_image = st.columns([1, 1])
                with left_img:
                    width, height = image.size
                    st.image(image, caption=f"模型看到的图片尺寸: {width}x{height}", width=512)
                with right_image:
                    width, height = origin_image.size
                    st.image(origin_image, caption=f"原始图片 {width}x{height}", width=512)
                if "plotly_json" in part:
                    fig_json = part["plotly_json"]

                    if isinstance(fig_json, dict):
                        fig = go.Figure(fig_json)
                    else:
                        fig = pio.from_json(fig_json)
                    st.plotly_chart(fig, use_container_width=True, key=f"thoughts_plot_{key}")
                    if st.button("应用到客户端图表", key=f"apply_plot_{key}"):
                        st.session_state["figure_config"] = fig.to_plotly_json()
                        st.rerun()
    else:
        st.write(content)


def think_and_answer(
    container: DeltaGenerator,
    agent: AimeAgent,
    dialogs: list[DialogTurn],
    history_messages: list[DialogData],
    thought_messages: list[DialogData],
    key,
    **inference_args,
):
    # history_messages 里定义了任务以及足够的上下文
    # 本函数是在 history_messages 的基础上进行深度推理，继续获取更多信息，做出最后的决策
    # thought_messages 是额外的信息，可能是从外部数据源获取的. 可以注入 thought_messages 来提供更多上下文信息。
    # history_messages 和 thought_messages 都是对话消息列表，每个消息是一个字典，包含 "role" 和 "content" 字段。
    # history_messages + thought_messages 生成 response，如果response 不是 decision，将 response 拼回 thought_messages 中，继续推理。
    # 直到 response 是决策性消息，才将其拼回 history_messages 中。此时 thought_messages 是 history_messages 最后一轮对话的中间结果。
    # inference_args 是推理引擎的参数
    logger.debug("think begin")
    debug = inference_args.get("debug", False)
    current_step = 0
    if len(thought_messages) > 0:
        for i in range(0, len(thought_messages), 2):
            current_step += 1
            step_status = container.status(f"思考 {current_step}", expanded=True, state="running")
            user_msg = thought_messages[i]
            assistant_msg = thought_messages[i + 1] if i + 1 < len(thought_messages) else None
            with step_status:
                render_content(user_msg["content"], f"{key}_user_msg_{i // 2}")
                if assistant_msg:
                    render_content(assistant_msg["content"], f"{key}_assistant_msg_{i // 2}")
    while True:
        current_step += 1
        if debug:
            logger.debug(f"当前推理深度: {current_step}, 历史消息数量: {len(history_messages)}")
        # 调用推理引擎获取回复
        messages = history_messages + thought_messages
        response = agent.inference(messages, **inference_args)
        if debug:
            logger.debug(f"🤖【assistant】: {response}")
        if isinstance(response, dict):
            # function call response
            call_id = response.get("id")
            call_name = response.get("function").get("name")
            call_args = response.get("function").get("arguments", "{}")
            if isinstance(call_args, str) and len(call_args) == 0:
                call_args = "{}"
            kwargs = json.loads(call_args) if isinstance(call_args, str) else call_args
            function_response = agent.call_function(call_name, **kwargs)
            thought_messages.append({"role": "assistant", "content": "", "tool_calls": response})
            thought_messages.append({"role": "tool", "content": function_response, "tool_call_id": call_id})
            # "tool_calls": [
            #     {
            #         "function": {
            #         "arguments": "{}",
            #         "name": "Search"
            #         },
            #         "id": "call_g16uvNKM2r7L36PcHmgbPAAo",
            #         "type": "function"
            #     }
            # ]
        elif isinstance(response, list):
            thought_messages.append({"role": "assistant", "content": "", "tool_calls": response})
            for tool_call in response:
                # function call response
                call_id = tool_call.get("id")
                call_name = tool_call.get("function").get("name")
                call_args = tool_call.get("function").get("arguments", "{}")
                if isinstance(call_args, str) and len(call_args) == 0:
                    call_args = "{}"
                kwargs = json.loads(call_args) if isinstance(call_args, str) else call_args
                function_response = agent.call_function(call_name, **kwargs)
                thought_messages.append({"role": "tool", "content": function_response, "tool_call_id": call_id})
        else:
            response_content = [{"type": "text", "text": response}]

            # 判断是否有代码解释器标记
            code = extract_code(remove_thoughts(response))
            step_status = container.status(f"思考 {current_step}", expanded=True, state="running")
            if code and len(code.strip()) > 0:
                with step_status:
                    render_content(response_content, f"{key}_assistant_msg_{current_step}")
                # 如果有代码解释器标记，为规划阶段，执行代码
                content_to_gpt, _ = agent.simulator.execute(code)
                # logger.info(json.dumps(content_to_gpt, ensure_ascii=False, indent=2))
                if len(content_to_gpt) == 0:
                    content_to_gpt = [{"type": "text", "text": "ok"}]
                with step_status:
                    render_content(content_to_gpt, f"{key}_user_msg_{current_step}")
                thought_messages.append({"role": "assistant", "content": response_content})
                thought_messages.append({"role": "user", "content": content_to_gpt})
            else:
                # 没有代码解释器标记时，为回答阶段，添加到历史记录并返回
                with step_status:
                    thought = extract_thought(response)
                    if thought:
                        # st.write("<think>")
                        st.divider()
                        st.write(thought)
                        st.divider()
                        # st.write("</think>")
                        response = remove_thoughts(response)
                st.write(response)
                history_messages.append({"role": "assistant", "content": response_content})
                break
    logger.debug("think end")
    dialog = {
        "role": "assistant",
        "content": [{"type": "text", "text": response}],
        "thoughts": copy.deepcopy(thought_messages),
    }
    dialogs[-1].update(dialog)

    time_str = datetime.datetime.now().strftime("%Y年%m月%d日%H时%M分%S秒")
    save_messages_json(dialogs, history_messages, thought_messages, f"output/code/dumps/{time_str}.json")
    save_jupyter_notebook(history_messages, thought_messages, f"output/code/dumps/{time_str}.ipynb")


def render_message(chat_container: DeltaGenerator, message: DialogTurn, key=None):
    with chat_container:
        with st.chat_message(message["role"]):
            content = message["content"]
            if message["role"] == "assistant" and len(message["thoughts"]) <= 2 and (not message["content"] or len(message["content"]) == 0):  # 前两个 thought 用于环境感知
                with st.empty():
                    think_and_answer(
                        st.container(),
                        st.session_state.agent,
                        st.session_state.dialogs,
                        st.session_state.history,
                        st.session_state.thoughts,
                        debug=True,
                        multi_modal=False,
                        max_tokens=10 * 1024,
                        key=f"content_{message['role']}_{key}",
                        functions=functions,
                        tools=tools,
                    )
                time.sleep(3)
                st.rerun()
            else:
                if "thoughts" in message and message["thoughts"] and len(message["thoughts"]) > 0:
                    with st.expander("思考过程"):
                        for i, thought in enumerate(message["thoughts"]):
                            if "role" in thought and thought["role"] == "assistant" and "tool_calls" in thought:
                                tool_calls = thought["tool_calls"]
                                strs = []
                                for tool_call in tool_calls:
                                    function_str = tool_call.get("function", {})
                                    function_str = json.dumps(function_str, ensure_ascii=False, separators=(",", ": "))
                                    function_str = f"```json\n{function_str}\n```"
                                    strs.append(function_str)
                                st_markdown(strs, key=f"content_{message['role']}_{key}_thought_{i}")
                            else:
                                render_content(thought["content"], f"content_{message['role']}_{key}_thought_{i}")
                        if message["role"] == "assistant" and len(content) == 1:
                            content = copy.deepcopy(content)
                            response = content[0]["text"]
                            thought = extract_thought(response)
                            if thought:
                                # st.write("<think>")
                                st.divider()
                                st.write(thought)
                                # st.write("</think>")
                                st.divider()
                            response = remove_thoughts(response)
                            content[0]["text"] = response
                render_content(content, f"content_{message['role']}_{key}")
