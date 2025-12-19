"""
环境基类

如何构建一个足够通用的环境接口，以便于后续扩展不同类型的环境

首先思考：环境的基本要素有哪些？教科书上一般会提到状态、动作、奖励、转移函数等
实际上，在物理环境中，不存在动作和奖励，所谓的动作和奖励是人通过语言描述出来的；也不存在转移函数，那是隐含在状态的变化中的。
所以，唯一真实存在的只有可观测的状态。
所以，基类Env只需要包含状态，且状态的转移函数应该隐藏起来无法被观测。

其次，考虑到我们要支持多种类型的环境，比如文本环境、图像环境、模拟环境等，这些环境可能有不同的特性和需求
注意到，不同环境可能有不同的状态表示方式（文本、图像、数值等），动作空间（离散、连续等），奖励机制（即时奖励、延迟奖励等），转移函数（确定性、随机性等）
我们需要一个通用的【环境表示】，能表示所有的状态、动作、奖励、转移函数。
这个通用表示是【代码】。因为：所有的状态都需要通过代码实现，用代码进行执行和操作，代码的执行导致的环境发生变化。
【代码的执行导致的环境发生变化】是一个通用描述，就算是物理环境，机器人的动作也是通过代码控制的，代码的执行导致机器人的动作，机器人的动作导致环境的变化。
所以，动作就是代码的执行。我们无需预先定义动作空间，agent 应该自己挖掘动作空间，写代码对环境进行操作。
这样，奖励需要由 agent 自己挖掘，环境不需要预先定义奖励机制。反正，奖励也由代码表示，作为环境状态的一部分。

因此，Env 的基类只需要定义一个转移函数接口，接受输入，返回 self。
这让我想起了 PyTorch 的 nn.Module。所以干脆就继承 nn.Module。从而这个函数就叫 forward。
forward 函数既是转移函数的实现，也是环境与 agent 之间的唯一交互接口。
这样甚至能够利用 PyTorch 的一些特性，比如参数管理、计算图、序列化、计算资源调度、并行计算、检查点等。

所以，我们的设计要点：
1. 环境包含初始状态（provide_initial_state 函数）和转移函数（forward 函数）
2. 动作和奖励都是代码，agent 需要生成代码来操作环境，挖掘奖励。

环境对象完全交给 agent 自己写代码管理。

let it hack!

agent 写的代码应该类似如下：

env = EnvSubclass(...)  # 创建环境对象
state_0 = env.provide_initial_state()  # 获取初始状态
display(state_0)  # 显示环境状态
state_1 = env(state_0, ...)  # env 接受一个状态和动作，返回下一个状态
display(state_1)  # 显示环境状态
state_2 = env(state_1, ...)  # agent 决定使用任意状态和任意动作。使用任意状态意味着 agent 可以针对同一个状态对不同的动作进行探索，提高探索效率；也可以设计对应的状态来验证某个动作的效果。
display(state_2)  # 显示环境状态
...

训练阶段，agent 可以对同一个 state 使用不同的 action 进行探索，提升探索效率。也可以设计对应的状态来验证某个动作的效果。
测试阶段，agent 只能选择最优 action，迭代 state 直到终止。
"""
from abc import ABC, abstractmethod
from typing import TypeVar, Generic, Dict, Any, List, Optional
from pydantic import BaseModel

from agentlin.code_interpreter.types import MIME_TOOL_RESPONSE, MIME_ENV_EVENT, ToolResponse
from agentlin.core.types import BaseTool, ToolData


class IState(BaseModel, ABC):
    def check_validity(self) -> bool:
        # check if the state is valid
        return True

    @abstractmethod
    def display(self) -> ToolResponse:
        # return {
        #     "message_content": [],
        #     "block_list": [],
        #     "data": {},
        # }
        pass

    def _repr_mimebundle_(self):
        # for jupyter notebook rich display
        resp = self.display()
        return {MIME_TOOL_RESPONSE: resp}


T = TypeVar("T", bound=IState)

class IEnvironment(ABC, Generic[T]):
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description

    def __call__(self, s: T, **kwargs):
        return self.forward(s, **kwargs)

    def forward(self, s: T, **kwargs) -> T:
        # 接受一个状态，返回下一个状态
        # 实现子类时，应该对 kwargs 进行参数校验
        raise NotImplementedError("Env is an abstract class, cannot be instantiated directly.")

    @abstractmethod
    def provide_initial_state(self) -> T:
        raise NotImplementedError("Env is an abstract class, cannot be instantiated directly.")

    def _repr_mimebundle_(self):
        s = self.provide_initial_state()
        if hasattr(s, "_repr_mimebundle_"):
            return s._repr_mimebundle_()
        return {"text/plain": self.__repr__()}


class IToolEnvironment(IEnvironment[T], Generic[T]):
    """
    介于 IEnvironment 和具体环境实现之间，专为支持工具型环境抽象。
    约定：
    - 必须实现 provide_tools, list_tools, list_available_name2tool
    - 工具相关环境应继承本类
    - 环境的状态转移完全委托给工具完成. 工具可在内部使用环境的唯一 state
    - 不同状态下可用的工具不同
    - 环境的forward会调用工具完成状态转移,如果状态合法,则不会复制状态而是直接返回已有状态(该状态已经被工具inplace修改,无需复制)
    """

    @abstractmethod
    def provide_tools(self, state: T) -> list[BaseTool]:
        """返回与当前状态相关联的工具列表"""
        pass

    def list_tools(self, state: T) -> list[ToolData]:
        tools = self.provide_tools(state)
        return [tool.function_tool_schema for tool in tools]

    def list_available_name2tool(self, state: T) -> dict[str, BaseTool]:
        tools = self.provide_tools(state)
        return {tool.name: tool for tool in tools}


class IStoppableState(IState):
    done: bool = False

    def check_validity(self) -> bool:
        return isinstance(self.done, bool)

    def display(self) -> ToolResponse:
        message = f"State done: {self.done}"
        return ToolResponse(
            message_content=[{"type": "text", "text": message}],
            block_list=[{"type": "text", "text": message}],
            data={"done": self.done},
        )


class ICount2StopState(IStoppableState):
    count: int = 0
    max_count: int = 0

    def check_validity(self) -> bool:
        rules = [
            super().check_validity(),
            isinstance(self.count, int),
            isinstance(self.max_count, int),
            0 <= self.count <= self.max_count,
        ]
        return all(rules)

    def display(self) -> ToolResponse:
        if not self.check_validity():
            message = "Invalid state"
        elif self.done:
            message = f"Progress: {self.count}/{self.max_count}. Done: {self.done}."
        else:
            message = f"Progress: {self.count}/{self.max_count}. {self.max_count-self.count} steps remain. Done: {self.done}."
        return ToolResponse(
            message_content=[{"type": "text", "text": message}],
            block_list=[{"type": "text", "text": message}],
            data={"done": self.done},
        )
