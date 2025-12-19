from typing import Any

from agentlin.code_interpreter.display_mime import display
from agentlin.code_interpreter.data_to_visual_json import AiVisual


def display_visual(visual: AiVisual, **extra: Any) -> None:
    """Display a visual in a Jupyter notebook.

    参数:
        visual: 遵循 `AiVisual` 的实例
        **extra: 预留扩展字段（当前未使用，便于未来扩展携带元信息）
    """
    display(visual)
