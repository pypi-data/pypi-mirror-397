"""ChatKit server integration for the boilerplate backend."""

from __future__ import annotations

import inspect
import json
import logging
from datetime import datetime
from typing import Annotated, Any, AsyncIterator, Final, Literal, Callable, get_args, get_origin
from uuid import uuid4

# Removed function_tool-related imports after refactor to plain functions
from chatkit.agents import (
    AgentContext,
    ClientToolCall,
    ThreadItemConverter,
    # stream_agent_response,
)
from chatkit.server import ChatKitServer, ThreadItemDoneEvent
from chatkit.types import (
    Attachment,
    ClientToolCallItem,
    HiddenContextItem,
    ThreadItem,
    ThreadMetadata,
    ThreadStreamEvent,
    UserMessageItem,
)
from loguru import logger
from openai.types.responses import ResponseInputContentParam
from pydantic import ConfigDict, Field

from agentlin.app.weather.trans import stream_agent_response
from agentlin.core.types import BaseTool, ToolParams, ToolResult
from agentlin.route.agent_config import load_agent_config
from agentlin.route.task_agent_manager import TaskAgentManager

from .constants import INSTRUCTIONS, MODEL
from .facts import Fact, fact_store
from .memory_store import MemoryStore
from .sample_widget import render_weather_widget, weather_widget_copy_text
from .weather import (
    WeatherLookupError,
    retrieve_weather,
)
from .weather import (
    normalize_unit as normalize_temperature_unit,
)

# If you want to check what's going on under the hood, set this to DEBUG
logging.basicConfig(level=logging.INFO)

SUPPORTED_COLOR_SCHEMES: Final[frozenset[str]] = frozenset({"light", "dark"})
CLIENT_THEME_TOOL_NAME: Final[str] = "switch_theme"


def _normalize_color_scheme(value: str) -> str:
    normalized = str(value).strip().lower()
    if normalized in SUPPORTED_COLOR_SCHEMES:
        return normalized
    if "dark" in normalized:
        return "dark"
    if "light" in normalized:
        return "light"
    raise ValueError("Theme must be either 'light' or 'dark'.")


def _gen_id(prefix: str) -> str:
    return f"{prefix}_{uuid4().hex[:8]}"


def _is_tool_completion_item(item: Any) -> bool:
    return isinstance(item, ClientToolCallItem)


class FactAgentContext(AgentContext):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    store: Annotated[MemoryStore, Field(exclude=True)]
    request_context: dict[str, Any]


async def _stream_saved_hidden(context: FactAgentContext, fact: Fact) -> None:
    await context.stream(
        ThreadItemDoneEvent(
            item=HiddenContextItem(
                id=_gen_id("msg"),
                thread_id=context.thread.id,
                created_at=datetime.now(),
                content=(
                    f'<FACT_SAVED id="{fact.id}" threadId="{context.thread.id}">{fact.text}</FACT_SAVED>'
                ),
            ),
        )
    )


async def save_fact(
    context: FactAgentContext,
    fact: str,
) -> dict[str, str] | None:
    try:
        saved = await fact_store.create(text=fact)
        confirmed = await fact_store.mark_saved(saved.id)
        if confirmed is None:
            raise ValueError("Failed to save fact")
        await _stream_saved_hidden(context, confirmed)
        context.client_tool_call = ClientToolCall(
            name="record_fact",
            arguments={"fact_id": confirmed.id, "fact_text": confirmed.text},
        )
        print(f"FACT SAVED: {confirmed}")
        return {"fact_id": confirmed.id, "status": "saved"}
    except Exception:
        logging.exception("Failed to save fact")
        return None


async def switch_theme(
    context: FactAgentContext,
    theme: str,
) -> dict[str, str] | None:
    logging.debug(f"Switching theme to {theme}")
    try:
        requested = _normalize_color_scheme(theme)
        context.client_tool_call = ClientToolCall(
            name=CLIENT_THEME_TOOL_NAME,
            arguments={"theme": requested},
        )
        return {"theme": requested}
    except Exception:
        logging.exception("Failed to switch theme")
        return None


async def get_weather(
    context: FactAgentContext,
    location: str,
    unit: Literal["celsius", "fahrenheit"] | str | None = None,
) -> dict[str, str | None]:
    print("[WeatherTool] tool invoked", {"location": location, "unit": unit})
    try:
        normalized_unit = normalize_temperature_unit(unit)
    except WeatherLookupError as exc:
        print("[WeatherTool] invalid unit", {"error": str(exc)})
        raise ValueError(str(exc)) from exc

    try:
        data = await retrieve_weather(location, normalized_unit)
    except WeatherLookupError as exc:
        print("[WeatherTool] lookup failed", {"error": str(exc)})
        raise ValueError(str(exc)) from exc

    print(
        "[WeatherTool] lookup succeeded",
        {
            "location": data.location,
            "temperature": data.temperature,
            "unit": data.temperature_unit,
        },
    )
    try:
        widget = render_weather_widget(data)
        copy_text = weather_widget_copy_text(data)
        payload: Any
        try:
            payload = widget.model_dump()
        except AttributeError:
            payload = widget
        print("[WeatherTool] widget payload", payload)
    except Exception as exc:  # noqa: BLE001
        print("[WeatherTool] widget build failed", {"error": str(exc)})
        raise ValueError("Weather data is currently unavailable for that location.") from exc

    print("[WeatherTool] streaming widget")
    try:
        await context.stream_widget(widget, copy_text=copy_text)
    except Exception as exc:  # noqa: BLE001
        print("[WeatherTool] widget stream failed", {"error": str(exc)})
        raise ValueError("Weather data is currently unavailable for that location.") from exc

    print("[WeatherTool] widget streamed")

    observed = data.observation_time.isoformat() if data.observation_time else None

    return {
        "location": data.location,
        "unit": normalized_unit,
        "observed_at": observed,
    }


class DiscoveredFunctionTool(BaseTool):
    """Wrap a plain async function into a BaseTool by introspecting its signature."""

    def __init__(self, ctx: AgentContext, func: Callable[..., Any]):
        self.ctx = ctx
        self.func = func

        name = getattr(func, "__name__", "tool")
        description = (func.__doc__ or "").strip() or name
        parameters = self._build_params_json_schema(func)

        super().__init__(
            name=name,
            title=name,
            description=description,
            parameters=parameters,
            strict=True,
        )

    def _annotation_to_schema(self, annotation: Any) -> dict[str, Any]:
        origin = get_origin(annotation)
        args = get_args(annotation)

        # Handle Literal
        if origin is Literal and args:
            # Infer type from enum members
            enum_values = list(args)
            type_name = None
            if all(isinstance(v, str) for v in enum_values):
                type_name = "string"
            elif all(isinstance(v, bool) for v in enum_values):
                type_name = "boolean"
            elif all(isinstance(v, int) for v in enum_values):
                type_name = "integer"
            elif all(isinstance(v, (int, float)) for v in enum_values):
                type_name = "number"
            return {k: v for k, v in {"type": type_name, "enum": enum_values}.items() if v is not None}

        # Basic builtins
        mapping = {
            str: "string",
            int: "integer",
            float: "number",
            bool: "boolean",
        }
        if annotation in mapping:
            return {"type": mapping[annotation]}

        # Fallback
        return {"type": "string"}

    def _build_params_json_schema(self, func: Callable[..., Any]) -> dict[str, Any]:
        sig = inspect.signature(func)
        properties: dict[str, Any] = {}
        required: list[str] = []
        for i, (name, param) in enumerate(sig.parameters.items()):
            # skip first param which should be the context
            if i == 0:
                continue
            schema = self._annotation_to_schema(param.annotation)
            if param.default is inspect._empty:
                required.append(name)
            properties[name] = schema

        schema: dict[str, Any] = {
            "type": "object",
            "properties": properties,
            "additionalProperties": False,
        }
        if required:
            schema["required"] = required
        return schema

    async def execute(self, params: ToolParams) -> ToolResult:
        result = self.func(self.ctx, **params)
        if inspect.isawaitable(result):
            result = await result

        try:
            text = json.dumps(result, ensure_ascii=False, default=str)
        except Exception:
            text = str(result)

        message_content: list[dict] = [{"text": text, "type": "text"}]
        block_list = []
        if not block_list:
            block_list = message_content
        return ToolResult(
            message_content=message_content,
            block_list=block_list,
        )


def _user_message_text(item: UserMessageItem) -> str:
    parts: list[str] = []
    for part in item.content:
        text = getattr(part, "text", None)
        if text:
            parts.append(text)
    return " ".join(parts).strip()


class FactAssistantServer(ChatKitServer[dict[str, Any]]):
    """ChatKit server wired up with the fact-recording tool."""

    def __init__(self) -> None:
        self.store: MemoryStore = MemoryStore()
        super().__init__(self.store)
        self.agent = "assets/simple"
        self.agent_config = None
        self.tools = [save_fact, switch_theme, get_weather]
        self.session_task_manager = TaskAgentManager(debug=True, use_message_queue=False)
        self._thread_item_converter = self._init_thread_item_converter()

    async def respond(
        self,
        thread: ThreadMetadata,
        item: UserMessageItem | None,
        context: dict[str, Any],
    ) -> AsyncIterator[ThreadStreamEvent]:
        agent_context = FactAgentContext(
            thread=thread,
            store=self.store,
            request_context=context,
        )

        target_item: ThreadItem | None = item
        if target_item is None:
            target_item = await self._latest_thread_item(thread, context)

        if target_item is None or _is_tool_completion_item(target_item):
            return

        agent_input = await self._to_agent_input(thread, target_item)
        if agent_input is None:
            return

        session_id = thread.id
        task_id = thread.id
        logger.debug(agent_input)
        message_content = agent_input

        if not self.agent_config:
            self.agent_config = await load_agent_config(self.agent)
            logger.info(f"Loaded agent config from {self.agent}")
        logger.info(f"Starting session for thread {thread.id} with agent {self.agent}")
        self.agent_config.developer_prompt = INSTRUCTIONS
        tools = [DiscoveredFunctionTool(agent_context, func) for func in self.tools]
        self.session_task_manager.builtin_tools = tools
        stream = await self.session_task_manager(
            request_id=session_id,
            session_id=session_id,
            task_id=task_id,
            user_id=session_id,
            user_message_content=message_content,
            stream=True,
            agent_config=self.agent_config,
            return_rollout=False,
        )

        # result = Runner.run_streamed(
        #     self.assistant,
        #     agent_input,
        #     context=agent_context,
        # )

        async for event in stream_agent_response(agent_context, stream):
            logger.info(event)
            yield event
        return

    async def to_message_content(self, _input: Attachment) -> ResponseInputContentParam:
        raise RuntimeError("File attachments are not supported in this demo.")

    def _init_thread_item_converter(self) -> Any | None:
        converter_cls = ThreadItemConverter
        if converter_cls is None or not callable(converter_cls):
            return None

        attempts: tuple[dict[str, Any], ...] = (
            {"to_message_content": self.to_message_content},
            {"message_content_converter": self.to_message_content},
            {},
        )

        for kwargs in attempts:
            try:
                return converter_cls(**kwargs)
            except TypeError:
                continue
        return None

    async def _latest_thread_item(
        self, thread: ThreadMetadata, context: dict[str, Any]
    ) -> ThreadItem | None:
        try:
            items = await self.store.load_thread_items(thread.id, None, 1, "desc", context)
        except Exception:  # pragma: no cover - defensive
            return None

        return items.data[0] if getattr(items, "data", None) else None

    async def _to_agent_input(
        self,
        thread: ThreadMetadata,
        item: ThreadItem,
    ) -> Any | None:
        if _is_tool_completion_item(item):
            return None

        converter = getattr(self, "_thread_item_converter", None)
        if converter is not None:
            for attr in (
                "to_input_item",
                "convert",
                "convert_item",
                "convert_thread_item",
            ):
                method = getattr(converter, attr, None)
                if method is None:
                    continue
                call_args: list[Any] = [item]
                call_kwargs: dict[str, Any] = {}
                try:
                    signature = inspect.signature(method)
                except (TypeError, ValueError):
                    signature = None

                if signature is not None:
                    params = [
                        parameter
                        for parameter in signature.parameters.values()
                        if parameter.kind
                        not in (
                            inspect.Parameter.VAR_POSITIONAL,
                            inspect.Parameter.VAR_KEYWORD,
                        )
                    ]
                    if len(params) >= 2:
                        next_param = params[1]
                        if next_param.kind in (
                            inspect.Parameter.POSITIONAL_ONLY,
                            inspect.Parameter.POSITIONAL_OR_KEYWORD,
                        ):
                            call_args.append(thread)
                        else:
                            call_kwargs[next_param.name] = thread

                result = method(*call_args, **call_kwargs)
                if inspect.isawaitable(result):
                    return await result
                return result

        if isinstance(item, UserMessageItem):
            return _user_message_text(item)

        return None

    async def _add_hidden_item(
        self,
        thread: ThreadMetadata,
        context: dict[str, Any],
        content: str,
    ) -> None:
        await self.store.add_thread_item(
            thread.id,
            HiddenContextItem(
                id=_gen_id("msg"),
                thread_id=thread.id,
                created_at=datetime.now(),
                content=content,
            ),
            context,
        )


def create_chatkit_server() -> FactAssistantServer | None:
    """Return a configured ChatKit server instance if dependencies are available."""
    return FactAssistantServer()
