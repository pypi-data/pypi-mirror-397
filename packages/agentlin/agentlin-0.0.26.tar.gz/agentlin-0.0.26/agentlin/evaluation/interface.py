from abc import ABC, abstractmethod
import asyncio

from agentlin.evaluation.types import EvaluationResult


class IEvaluator(ABC):
    def evaluate(self, **kwargs) -> EvaluationResult:
        return asyncio.run(self.async_evaluate(**kwargs))

    @abstractmethod
    async def async_evaluate(self, **kwargs) -> EvaluationResult:
        pass
