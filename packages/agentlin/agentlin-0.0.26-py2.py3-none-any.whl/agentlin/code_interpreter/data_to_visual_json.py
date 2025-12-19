from typing import Any, Literal, Optional
from pydantic import BaseModel

from agentlin.code_interpreter.types import MIME_VISUAL, VisualDataV1


class AiVisual(BaseModel):
    # visual-json 的传输对象，包含给 agent 看的和给前端渲染的，共两部分数据，压缩传输
    # 注意，仅当 config 不为空且 image_url 不为空时，前端才能渲染，type 才有效。
    # 渲染发生错误或无法画图时，模型会写 message 字段给出错误信息，此时 type 有值但 config 为空，你应该忽略 type。
    type: Literal["chart", "common"] = "common"
    config: Optional[dict[str, Any]] = None
    image_url: Optional[str] = None
    caption: Optional[str] = None
    message: Optional[str] = None

    def to_visual_data(self) -> VisualDataV1:
        return {
            "type": self.type,
            "config": self.config or {},
            "caption": self.caption,
        }

    def __str__(self) -> str:
        from agentlin.code_interpreter.display_mime import display
        display(self)
        return ""

    def _repr_mimebundle_(self, include=None, exclude=None) -> dict[str, Any]:
        """
        Return MIME bundle for Jupyter display

        Returns:
            Dict containing the custom MIME type and chart JSON data
        """
        return {
            MIME_VISUAL: self.model_dump()
        }



