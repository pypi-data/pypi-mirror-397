from typing import Any, Generic, Literal, Optional, Type, get_args, get_origin, TypeVar
from loguru import logger
import uuid

from pydantic import BaseModel, Field

from agentlin.route.agent import Agent
from agentlin.route.agent_config import AgentConfig, load_agent_config


class ConvertConfig(BaseModel):
    name: str
    args: Any = None


TName = TypeVar("TName", bound=str)
TInput = TypeVar("TInput", bound=BaseModel)
TOutput = TypeVar("TOutput", bound=BaseModel)


class Convert(BaseModel, Generic[TName, TInput]):
    name: TName = Field(default=TName, frozen=True)  # pyright: ignore
    args: TInput

    @classmethod
    def create(cls, args: TInput, **kwargs) -> ConvertConfig:
        name_type: Any = None
        anno = cls.model_fields["name"].annotation
        if get_origin(anno) is Literal:
            lits = get_args(anno)
            if len(lits) == 1 and isinstance(lits[0], str):
                name_type = lits[0]

        if name_type is None:
            raise TypeError("Cannot infer 'name' for this Convert[...]. Do not call create() on generic Convert.")

        return ConvertConfig(name=name_type, args=args, **kwargs)


class Converted(BaseModel, Generic[TName, TInput, TOutput]):
    input: Convert[TName, TInput]
    output: TOutput


class DataframeInput(BaseModel):
    columns: list[dict[str, Any]]
    datas: list[dict[str, Any]]
    query: Optional[str] = None
    text: Optional[str] = None
    metadata: Optional[dict[str, Any]] = None

class DataframeOutput(BaseModel):
    columns: list[dict[str, Any]]
    datas: list[dict[str, Any]]
    query: Optional[str] = None
    text: Optional[str] = None
    metadata: Optional[dict[str, Any]] = None

class ChartOutput(BaseModel):
    message_content: list[dict[str, Any]] = []
    block_list: list[dict[str, Any]] = []
    json_data: Optional[dict[str, Any]] = None
    caption: Optional[str] = None
    error_message: Optional[str] = None

ConvertDataframeToChart = Convert[Literal["dataframe_to_chart"], DataframeInput]

async def convert(
    instruction: str,
    name: TName,
    input_model: TInput,
    output_type: Type[TOutput],
    agent: str | AgentConfig | None = None,
    debug: bool = False,
    **kwargs,
) -> TOutput:
    if isinstance(agent, str):
        agent_config = await load_agent_config(agent)
    elif isinstance(agent, AgentConfig):
        agent_config = agent
    else:
        agent_path = name
        agent_config = await load_agent_config(agent_path)
    agent: Agent = Agent(debug=debug)
    session_id = str(uuid.uuid4().hex)
    user_message_content = []
    user_message_content.append({"type": "text", "text": instruction})
    user_message_content.append({"type": "text", "text": input_model.model_dump_json()})
    output = await agent(
        user_message_content=user_message_content,
        structured_output=output_type,
        stream=False,
        session_id=session_id,
        agent_config=agent_config,
        **kwargs,
    )
    agent.delete_session(session_id)
    return output


async def convert_by_convertor(
    instruction: str,
    convertor: Convert[TName, TInput],
    output_type: Type[TOutput],
    agent: str | AgentConfig | None = None,
    debug: bool = False,
    **kwargs,
) -> TOutput:
    """Convert input_model following the instruction and parse the result into output_model.

    Args:
        instruction: The instruction to be followed.
        input_model: A Convert subclass instance containing the input data.
        output_model: A Pydantic model class to parse the converted data.
        agent: The path to the agent configuration file or an AgentConfig instance.
        debug: Whether to enable debug mode for the agent (default False).
        **kwargs: Additional keyword arguments to pass to the agent call.

    Returns:
        An instance of output_model containing the converted data.
    """
    return await convert(
        instruction=instruction,
        name=convertor.name,
        input_model=convertor.args,
        output_type=output_type,
        agent=agent,
        debug=debug,
        **kwargs,
    )