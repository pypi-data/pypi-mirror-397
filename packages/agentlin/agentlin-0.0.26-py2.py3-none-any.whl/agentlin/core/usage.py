
from typing import Optional
from pydantic import BaseModel, Field
from openai.types.completion_usage import CompletionUsage
from openai.types.responses.response_usage import ResponseUsage


class TokenDetails(BaseModel):
    """Token 详情"""
    cached_tokens: int = 0

class OutputTokenDetails(BaseModel):
    """输出 Token 详情"""
    reasoning_tokens: int = 0

class ToolCallDetail(BaseModel):
    """工具调用详情"""
    name: str
    arguments: str
    time: float = 0   # 调用时长(ms)

class Usage(BaseModel):
    """使用统计信息"""
    input_tokens: int = 0
    input_tokens_details: TokenDetails = Field(default_factory=TokenDetails)
    output_tokens: int = 0
    output_tokens_details: OutputTokenDetails = Field(default_factory=OutputTokenDetails)
    total_tokens: int = 0

    # 工具调用统计
    tool_calls: int = 0  # 总工具调用次数
    tool_calls_details: dict[str, ToolCallDetail] = Field(default_factory=dict)  # 按工具名称分类的调用详情

    def add_tool_call(self, call_id: str, tool_name: str, tool_args: str, time: int = 0):
        """添加工具调用记录"""
        self.tool_calls += 1
        if call_id not in self.tool_calls_details:
            self.tool_calls_details[call_id] = ToolCallDetail(name=tool_name, arguments=tool_args)

        detail = self.tool_calls_details[call_id]
        if time:
            detail.time += time

    def add_completion_usage(self, usage: CompletionUsage):
        self.input_tokens += usage.prompt_tokens
        if usage.prompt_tokens_details:
            self.input_tokens_details.cached_tokens += usage.prompt_tokens_details.cached_tokens
        self.output_tokens += usage.completion_tokens
        if usage.completion_tokens_details:
            self.output_tokens_details.reasoning_tokens += usage.completion_tokens_details.reasoning_tokens
        self.total_tokens += usage.total_tokens

    def add_respose_usage(self, usage: ResponseUsage):
        self.input_tokens += usage.input_tokens
        if usage.input_tokens_details:
            self.input_tokens_details.cached_tokens += usage.input_tokens_details.cached_tokens
        self.output_tokens += usage.output_tokens
        if usage.output_tokens_details:
            self.output_tokens_details.reasoning_tokens += usage.output_tokens_details.reasoning_tokens
        self.total_tokens += usage.total_tokens

    def add_usage(self, other: 'Usage') -> 'Usage':
        """合并两个 Usage 对象"""
        merged = Usage(
            input_tokens=self.input_tokens + other.input_tokens,
            output_tokens=self.output_tokens + other.output_tokens,
            total_tokens=self.total_tokens + other.total_tokens,
            tool_calls=self.tool_calls + other.tool_calls,
        )

        # 合并 token 详情
        merged.input_tokens_details.cached_tokens = (
            self.input_tokens_details.cached_tokens + other.input_tokens_details.cached_tokens
        )
        merged.output_tokens_details.reasoning_tokens = (
            self.output_tokens_details.reasoning_tokens + other.output_tokens_details.reasoning_tokens
        )

        # 合并工具调用详情
        all_call_ids = set(self.tool_calls_details.keys()) | set(other.tool_calls_details.keys())
        for call_id in all_call_ids:
            other_detail = other.tool_calls_details.get(call_id)
            self_detail = self.tool_calls_details.get(call_id)
            if other_detail is None:
                merged.tool_calls_details[call_id] = self_detail
                continue
            if self_detail is None:
                merged.tool_calls_details[call_id] = other_detail
                continue
            merged.tool_calls_details[call_id].time = self_detail.time + other_detail.time

        return merged
