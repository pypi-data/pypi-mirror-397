"""Task store implementations."""

from __future__ import annotations

import asyncio
from typing import Dict, List, Optional

from agentlin.core.types import ListTasksParams, TaskObject, TaskStatus


class InMemoryTaskStore:
    """Simple asyncio-aware in-memory task store."""

    def __init__(self) -> None:
        self._tasks: Dict[str, TaskObject] = {}
        self._lock = asyncio.Lock()

    async def upsert(self, task: TaskObject) -> TaskObject:
        async with self._lock:
            self._tasks[task.id] = task
            return task

    async def get(self, task_id: str) -> Optional[TaskObject]:
        async with self._lock:
            return self._tasks.get(task_id)

    async def list(self, params: Optional[ListTasksParams] = None) -> List[TaskObject]:
        async with self._lock:
            tasks = list(self._tasks.values())

        if not params:
            return tasks

        filtered = tasks
        if params.session_id:
            filtered = [task for task in filtered if task.session_id == params.session_id]
        if params.user_id:
            filtered = [task for task in filtered if task.user_id == params.user_id]
        if params.status:
            allowed_status: set[TaskStatus] = set(params.status)
            filtered = [task for task in filtered if task.status in allowed_status]

        offset = params.offset or 0
        limit = params.limit or 10
        end = offset + limit if limit > 0 else None
        return filtered[offset:end]

    async def delete(self, task_id: str) -> Optional[TaskObject]:
        async with self._lock:
            return self._tasks.pop(task_id, None)

    async def clear(self) -> None:
        async with self._lock:
            self._tasks.clear()
