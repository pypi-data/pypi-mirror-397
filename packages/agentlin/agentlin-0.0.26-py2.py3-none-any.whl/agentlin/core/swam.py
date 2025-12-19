import asyncio

import httpx
from loguru import logger

from agentlin.core.agent_message_queue import AgentMessageQueue


class Swarm:
    def __init__(self, agent_message_queues: list[AgentMessageQueue]):
        self.agent_message_queues = agent_message_queues
        self.running_tasks: list[asyncio.Task] = []

    async def __aenter__(self):
        """进入异步上下文管理器"""
        logger.info("Initializing agent message queues...")
        for mq_entrypoint in self.agent_message_queues:
            await mq_entrypoint.initialize()
        for mq_entrypoint in self.agent_message_queues:
            self.running_tasks.append(asyncio.create_task(mq_entrypoint.run()))
        logger.info("All agent message queues initialized.")
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """退出异步上下文管理器"""
        # 在这里进行清理工作
        logger.info("Stopping agent message queues...")
        for mq_entrypoint in self.agent_message_queues:
            mq_entrypoint.stop()
        logger.info("Waiting for running tasks to complete...")
        for task in self.running_tasks:
            # Check if session task failed and raise error immediately
            if task is not None and task.done() and not task.cancelled():
                exception = task.exception()
                if isinstance(exception, httpx.HTTPStatusError):
                    raise exception
                elif exception is not None:
                    raise RuntimeError(f"Client failed to connect: {exception}") from exception

        await asyncio.gather(*self.running_tasks)
        logger.info("All agent message queues stopped.")
