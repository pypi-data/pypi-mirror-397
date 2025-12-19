import os
from typing import Optional, Union

import openai
from dotenv import load_dotenv


def init_agentops(AGENTOPS_API_KEY: Optional[str] = None, tags: list[str] = ["AgentLin"], **kwargs):
    """
    https://app.agentops.ai/get-started

    Initialize AgentOps with the API key from environment variables.
    Raises ValueError if AGENTOPS_API_KEY is not set.
    """
    load_dotenv()
    if not AGENTOPS_API_KEY:
        AGENTOPS_API_KEY = os.getenv("AGENTOPS_API_KEY")
    if not AGENTOPS_API_KEY:
        raise ValueError("AGENTOPS_API_KEY is not set. Please set it in your environment variables.")
    import agentops

    agentops.init(
        api_key=AGENTOPS_API_KEY,
        default_tags=tags,
        **kwargs,
    )


def init_swanlab(client: Union[openai.OpenAI, openai.AsyncOpenAI], experiment_name: str = "trajectory"):
    load_dotenv()
    from swanlab.integration.integration_utils.autologging import AutologAPI
    from swanlab.integration.openai.resolver import OpenAIRequestResponseResolver, OpenAIClientResponseResolver
    from swanlab.integration.openai.openai import version

    autolog = AutologAPI(
        name="OpenAI",
        symbols=(
            "chat.completions.create",
            "completions.create",
            # "Asynccompletions.create",
            # "chat.completions.acreate",
            # "Edit.acreate",
            # "Edit.create",
        ),
        resolver=OpenAIClientResponseResolver(),
        client=client,
        lib_version=version,
    )

    autolog.enable(init=dict(experiment_name=experiment_name))
    # export SWANLAB_RESUME=allow
    # export SWANLAB_RUN_ID=<exp_id>
    return client


def init_agentscope(
    AGENTSCOPE_URL: Optional[str] = None,
    project: Optional[str] = None,
    name: Optional[str] = None,
):
    """
    https://doc.agentscope.io/tutorial/task_studio.html#studio

    Initialize AgentScope with the URL from environment variables.
    Raises ValueError if AGENTSCOPE_URL is not set.
    """
    load_dotenv()
    if not AGENTSCOPE_URL:
        AGENTSCOPE_URL = os.getenv("AGENTSCOPE_URL", "http://localhost:3000")
    if not AGENTSCOPE_URL:
        raise ValueError("AGENTSCOPE_URL is not set. Please set it in your environment variables.")
    import agentscope

    agentscope.init(
        project=project,
        name=name,
        studio_url=AGENTSCOPE_URL,
    )

def init_opik():
    from opik import configure, track
    from opik.evaluation import evaluate

    configure()