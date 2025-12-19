"""Task model implementation for MCP Scheduler."""
from __future__ import annotations

import uuid
import re
from datetime import datetime
from enum import Enum
from typing import Literal, Optional, Dict, Any, Union

from pydantic import BaseModel, Field, validator
from agentlin.core.types import TaskStatus


class TaskType(str, Enum):
    """Type of a scheduled task."""
    SHELL_COMMAND = "shell_command"
    API_CALL = "api_call"
    AI = "ai"
    REMINDER = "reminder"  # New task type for reminders


def sanitize_ascii(text: str) -> str:
    """Strips non-ASCII characters from a string."""
    if not text:
        return text
    return re.sub(r'[^\x00-\x7F]+', '', text)


def _sanitize_dict_values(data: Optional[Dict[str, str]]) -> Optional[Dict[str, str]]:
    """Sanitize dictionary keys and values to ASCII-only strings."""
    if data is None:
        return None
    return {sanitize_ascii(str(k)): sanitize_ascii(str(v)) for k, v in data.items()}


def _ascii_only(cls, v):
    if isinstance(v, str):
        return sanitize_ascii(v)
    return v


class ApiTaskBase(BaseModel):
    """Base class for all API payload definitions."""

    kind: TaskType

    def to_flat_dict(self) -> Dict[str, Any]:
        """Flatten API payload into legacy column names for storage."""
        raise NotImplementedError


class ShellCommandApi(ApiTaskBase):
    """API payload for shell command tasks."""

    kind: Literal[TaskType.SHELL_COMMAND] = TaskType.SHELL_COMMAND
    command: str

    _normalize_strings = validator("command", pre=True, allow_reuse=True)(_ascii_only)

    @validator("command")
    def ensure_command(cls, v: str) -> str:
        if not v:
            raise ValueError("Command is required for shell_command tasks")
        return v

    def to_flat_dict(self) -> Dict[str, Any]:
        return {"command": self.command}


class ApiCallApi(ApiTaskBase):
    """API payload for generic HTTP call tasks."""

    kind: Literal[TaskType.API_CALL] = TaskType.API_CALL
    url: str
    method: str = "GET"
    headers: Optional[Dict[str, str]] = None
    body: Optional[Dict[str, Any]] = None

    _normalize_strings = validator("url", "method", pre=True, allow_reuse=True)(_ascii_only)

    @validator("headers", pre=True)
    def sanitize_headers(cls, v):
        return _sanitize_dict_values(v)

    @validator("url")
    def ensure_url(cls, v: str) -> str:
        if not v:
            raise ValueError("API URL is required for api_call tasks")
        return v

    def to_flat_dict(self) -> Dict[str, Any]:
        return {
            "api_url": self.url,
            "api_method": self.method,
            "api_headers": self.headers,
            "api_body": self.body,
        }


class AiTaskApi(ApiTaskBase):
    """API payload for AI completion tasks."""

    kind: Literal[TaskType.AI] = TaskType.AI
    prompt: str

    _normalize_strings = validator("prompt", pre=True, allow_reuse=True)(_ascii_only)

    @validator("prompt")
    def ensure_prompt(cls, v: str) -> str:
        if not v:
            raise ValueError("Prompt is required for AI tasks")
        return v

    def to_flat_dict(self) -> Dict[str, Any]:
        return {"prompt": self.prompt}


class ReminderTaskApi(ApiTaskBase):
    """API payload for reminder notification tasks."""

    kind: Literal[TaskType.REMINDER] = TaskType.REMINDER
    title: Optional[str] = None
    message: str

    _normalize_strings = validator("title", "message", pre=True, allow_reuse=True)(_ascii_only)

    @validator("message")
    def ensure_message(cls, v: str) -> str:
        if not v:
            raise ValueError("Message is required for reminder tasks")
        return v

    def to_flat_dict(self) -> Dict[str, Any]:
        return {
            "reminder_title": self.title,
            "reminder_message": self.message,
        }


ApiTask = Union[ShellCommandApi, ApiCallApi, AiTaskApi, ReminderTaskApi]


class ScheduleApiTask(BaseModel):
    """Model representing a scheduled API task."""

    id: str = Field(default_factory=lambda: f"task_{uuid.uuid4().hex[:12]}")
    name: str
    schedule: str
    api: ApiTask
    description: Optional[str] = None
    enabled: bool = True
    do_only_once: bool = True
    last_run: Optional[datetime] = None
    next_run: Optional[datetime] = None
    status: TaskStatus = TaskStatus.QUEUED
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    _normalize_strings = validator("name", "schedule", "description", pre=True, allow_reuse=True)(_ascii_only)

    @property
    def type(self) -> TaskType:
        """Expose task type derived from the API payload."""
        return self.api.kind

    def to_dict(self) -> Dict[str, Any]:
        """Convert the task to a dictionary for serialization."""
        return {
            "id": self.id,
            "name": self.name,
            "schedule": self.schedule,
            "type": self.type.value,
            "description": self.description,
            "enabled": self.enabled,
            "do_only_once": self.do_only_once,
            "last_run": self.last_run.isoformat() if self.last_run else None,
            "next_run": self.next_run.isoformat() if self.next_run else None,
            "status": self.status.value,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "api": self.api.dict(),
        }


def build_api_from_flat_fields(task_type: TaskType, data: Dict[str, Any]) -> ApiTask:
    """Construct an ApiTask from legacy flat field data."""
    if task_type == TaskType.SHELL_COMMAND:
        return ShellCommandApi(command=data.get("command"))
    if task_type == TaskType.API_CALL:
        return ApiCallApi(
            url=data.get("api_url"),
            method=data.get("api_method") or "GET",
            headers=data.get("api_headers"),
            body=data.get("api_body"),
        )
    if task_type == TaskType.AI:
        return AiTaskApi(prompt=data.get("prompt"))
    if task_type == TaskType.REMINDER:
        return ReminderTaskApi(
            title=data.get("reminder_title"),
            message=data.get("reminder_message"),
        )
    raise ValueError(f"Unsupported task type: {task_type}")

