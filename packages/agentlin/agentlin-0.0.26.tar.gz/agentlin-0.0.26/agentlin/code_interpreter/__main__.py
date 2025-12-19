import os
from pathlib import Path
import traceback
from typing import Annotated, Optional

from tqdm import tqdm
import typer
import asyncio
from loguru import logger
from dotenv import load_dotenv

from agentlin.code_interpreter.client import JupyterClient

app = typer.Typer()


@app.command()
def clean_kernel(
    host: Annotated[str, typer.Option(help="The Jupyter server host", envvar="JUPYTER_HOST")] = "localhost",
    port: Annotated[int, typer.Option(help="The Jupyter server port", envvar="JUPYTER_PORT")] = 8888,
    path: Annotated[str, typer.Option(help="The Jupyter server path", envvar="JUPYTER_PATH")] = "",
    token: Annotated[str, typer.Option(help="The Jupyter server token", envvar="JUPYTER_TOKEN")] = "jupyter_server_token",
):
    load_dotenv()

    client = JupyterClient(
        jupyter_host=host,
        jupyter_port=f"{port}{path}",
        jupyter_token=token,
    )
    kernels = client.list_kernels()
    if not kernels:
        logger.info("No kernels to clean.")
        return
    for kernel in tqdm(kernels):
        kernel_id = kernel.get("id")
        client.delete_kernel(kernel_id)
        logger.info(f"Deleted kernel {kernel_id}")
    logger.info(f"Cleaned {len(kernels)} kernels.")
    client.close()

if __name__ == "__main__":
    app()