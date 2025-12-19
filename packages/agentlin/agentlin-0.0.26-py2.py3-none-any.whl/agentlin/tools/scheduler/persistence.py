"""
SQLite persistence layer for MCP Scheduler.
"""
import json
import sqlite3
from datetime import datetime
from typing import List, Optional, Dict, Any

from loguru import logger

from agentlin.core.types import TaskObject as CoreTaskObject, TaskStatus, JSONRPCError, ToolResultItem
from agentlin.tools.scheduler.task import (
    ScheduleApiTask,
    TaskType,
    build_api_from_flat_fields,
)


LEGACY_TASK_STATUS_MAP = {
    "pending": TaskStatus.QUEUED,
    "running": TaskStatus.WORKING,
    "completed": TaskStatus.COMPLETED,
    "failed": TaskStatus.FAILED,
    "disabled": TaskStatus.PAUSED,
}



class Database:
    """SQLite database for task persistence."""

    def __init__(self, db_path="scheduler.db"):
        """Initialize the database connection."""
        self.db_path = db_path
        self._create_tables()

    def _create_tables(self):
        """Create the necessary tables if they don't exist."""
        with sqlite3.connect(self.db_path) as conn:
            # Check if we need to add reminder columns
            try:
                cursor = conn.execute("SELECT reminder_title, reminder_message FROM tasks LIMIT 1")
                has_reminder_columns = True
            except sqlite3.OperationalError:
                has_reminder_columns = False

            # Create tasks table if it doesn't exist
            conn.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                schedule TEXT NOT NULL,
                type TEXT NOT NULL,
                command TEXT,
                api_url TEXT,
                api_method TEXT,
                api_headers TEXT,
                api_body TEXT,
                prompt TEXT,
                description TEXT,
                enabled INTEGER NOT NULL,
                do_only_once INTEGER NOT NULL,
                last_run TEXT,
                next_run TEXT,
                status TEXT NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
            """)

            # Add reminder columns if they don't exist
            if not has_reminder_columns:
                try:
                    conn.execute("ALTER TABLE tasks ADD COLUMN reminder_title TEXT")
                    conn.execute("ALTER TABLE tasks ADD COLUMN reminder_message TEXT")
                    logger.info("Added reminder columns to tasks table")
                except sqlite3.OperationalError as e:
                    logger.error(f"Error adding reminder columns: {e}")

            conn.execute("""
            CREATE TABLE IF NOT EXISTS executions (
                id TEXT PRIMARY KEY,
                task_id TEXT NOT NULL,
                start_time TEXT NOT NULL,
                end_time TEXT,
                status TEXT NOT NULL,
                output TEXT,
                error TEXT,
                task_object TEXT,
                FOREIGN KEY (task_id) REFERENCES tasks (id)
            )
            """)

            # Ensure task_object column exists for legacy databases
            try:
                cursor = conn.execute("PRAGMA table_info(executions)")
                column_names = {row[1] for row in cursor.fetchall()}
                if "task_object" not in column_names:
                    conn.execute("ALTER TABLE executions ADD COLUMN task_object TEXT")
                    logger.info("Added task_object column to executions table")
            except sqlite3.OperationalError as e:
                logger.error(f"Error ensuring task_object column: {e}")

            conn.commit()

    def save_task(self, task: ScheduleApiTask) -> None:
        """Save a task to the database."""
        with sqlite3.connect(self.db_path) as conn:
            api_fields = task.api.to_flat_dict()
            command = api_fields.get("command")
            api_url = api_fields.get("api_url")
            api_method = api_fields.get("api_method")
            api_headers = api_fields.get("api_headers")
            api_body = api_fields.get("api_body")
            prompt = api_fields.get("prompt")
            reminder_title = api_fields.get("reminder_title")
            reminder_message = api_fields.get("reminder_message")

            api_headers_json = json.dumps(api_headers) if api_headers is not None else None
            api_body_json = json.dumps(api_body) if api_body is not None else None

            # Check if reminder columns exist
            try:
                conn.execute(
                    """
                    INSERT OR REPLACE INTO tasks
                    (id, name, schedule, type, command, api_url, api_method, api_headers,
                     api_body, prompt, description, enabled, do_only_once, last_run, next_run,
                     status, created_at, updated_at, reminder_title, reminder_message)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        task.id,
                        task.name,
                        task.schedule,
                        task.type.value,
                        command,
                        api_url,
                        api_method,
                        api_headers_json,
                        api_body_json,
                        prompt,
                        task.description,
                        1 if task.enabled else 0,
                        1 if task.do_only_once else 0,
                        task.last_run.isoformat() if task.last_run else None,
                        task.next_run.isoformat() if task.next_run else None,
                        task.status.value,
                        task.created_at.isoformat(),
                        task.updated_at.isoformat(),
                        reminder_title,
                        reminder_message
                    )
                )
            except sqlite3.OperationalError:
                # Fallback for databases without reminder columns
                conn.execute(
                    """
                    INSERT OR REPLACE INTO tasks
                    (id, name, schedule, type, command, api_url, api_method, api_headers,
                     api_body, prompt, description, enabled, do_only_once, last_run, next_run,
                     status, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        task.id,
                        task.name,
                        task.schedule,
                        task.type.value,
                        command,
                        api_url,
                        api_method,
                        api_headers_json,
                        api_body_json,
                        prompt,
                        task.description,
                        1 if task.enabled else 0,
                        1 if task.do_only_once else 0,
                        task.last_run.isoformat() if task.last_run else None,
                        task.next_run.isoformat() if task.next_run else None,
                        task.status.value,
                        task.created_at.isoformat(),
                        task.updated_at.isoformat()
                    )
                )

                # Log warning about missing reminder columns
                logger.warning("Database missing reminder columns - task reminder data not saved")

            conn.commit()

    def get_task(self, task_id: str) -> Optional[ScheduleApiTask]:
        """Get a task by ID."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("SELECT * FROM tasks WHERE id = ?", (task_id,))
            row = cursor.fetchone()

            if not row:
                return None

            return self._row_to_task(row)

    def get_all_tasks(self) -> List[ScheduleApiTask]:
        """Get all tasks."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("SELECT * FROM tasks")
            rows = cursor.fetchall()

            return [self._row_to_task(row) for row in rows]

    def delete_task(self, task_id: str) -> bool:
        """Delete a task by ID."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
            conn.commit()

            return cursor.rowcount > 0

    def save_execution(self, execution: CoreTaskObject) -> None:
        """Save a task execution to the database."""
        with sqlite3.connect(self.db_path) as conn:
            metadata = execution.metadata or {}
            task_id = metadata.get("scheduler_task_id") or metadata.get("task_id")
            if not task_id:
                logger.error("Execution metadata missing scheduler_task_id; skipping save")
                return

            start_time = metadata.get("start_time") or datetime.utcnow().isoformat()
            end_time = metadata.get("end_time")
            output_summary = self._extract_output_summary(execution)
            error_message = execution.error.message if execution.error else metadata.get("raw_error")

            conn.execute(
                """
                INSERT OR REPLACE INTO executions
                (id, task_id, start_time, end_time, status, output, error, task_object)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    execution.id,
                    task_id,
                    start_time,
                    end_time,
                    execution.status.value,
                    output_summary,
                    error_message,
                    json.dumps(execution.model_dump()),
                )
            )
            conn.commit()

    def get_executions(self, task_id: str, limit: int = 10) -> List[CoreTaskObject]:
        """Get executions for a task."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(
                "SELECT * FROM executions WHERE task_id = ? ORDER BY start_time DESC LIMIT ?",
                (task_id, limit)
            )
            rows = cursor.fetchall()

            return [self._row_to_execution(row) for row in rows]

    def _row_to_task(self, row: sqlite3.Row) -> ScheduleApiTask:
        """Convert a database row to a Task object."""
        # Check for reminder fields in the row
        has_reminder_fields = "reminder_title" in row.keys() and "reminder_message" in row.keys()

        headers = json.loads(row["api_headers"]) if row["api_headers"] else None
        body = json.loads(row["api_body"]) if row["api_body"] else None
        reminder_title = row["reminder_title"] if has_reminder_fields else None
        reminder_message = row["reminder_message"] if has_reminder_fields else None

        api_payload = build_api_from_flat_fields(
            TaskType(row["type"]),
            {
                "command": row["command"],
                "api_url": row["api_url"],
                "api_method": row["api_method"],
                "api_headers": headers,
                "api_body": body,
                "prompt": row["prompt"],
                "reminder_title": reminder_title,
                "reminder_message": reminder_message,
            },
        )

        return ScheduleApiTask(
            id=row["id"],
            name=row["name"],
            schedule=row["schedule"],
            api=api_payload,
            description=row["description"],
            enabled=bool(row["enabled"]),
            do_only_once=bool(row["do_only_once"]),
            last_run=datetime.fromisoformat(row["last_run"]) if row["last_run"] else None,
            next_run=datetime.fromisoformat(row["next_run"]) if row["next_run"] else None,
            status=self._normalize_task_status(row["status"]),
            created_at=datetime.fromisoformat(row["created_at"]),
            updated_at=datetime.fromisoformat(row["updated_at"]),
        )

    def _row_to_execution(self, row: sqlite3.Row) -> CoreTaskObject:
        """Convert a database row to a TaskObject execution."""
        if isinstance(row, dict):
            task_object_blob = row.get("task_object")
        else:
            task_object_blob = row["task_object"] if "task_object" in row.keys() else None

        if task_object_blob:
            try:
                return CoreTaskObject.model_validate_json(task_object_blob)
            except Exception as exc:
                logger.error(f"Failed to parse stored task_object for execution {row['id']}: {exc}")

        # Legacy fallback
        metadata = {
            "scheduler_task_id": row["task_id"],
            "start_time": row["start_time"],
            "end_time": row["end_time"],
        }
        if row["output"]:
            metadata["raw_output"] = row["output"]
        if row["error"]:
            metadata["raw_error"] = row["error"]

        status_value = row["status"]
        status = self._map_legacy_status(status_value)

        execution = CoreTaskObject(
            id=row["id"],
            output=[],
            metadata=metadata,
            status=status,
            error=JSONRPCError(code=500, message=row["error"], data=None) if row["error"] else None,
        )

        if row["output"]:
            execution.output = [
                ToolResultItem(
                    call_id=row["task_id"],
                    output=row["output"],
                    message_content=[{"type": "text", "text": row["output"]}],
                    block_list=[],
                )
            ]

        return execution

    def _extract_output_summary(self, execution: CoreTaskObject) -> Optional[str]:
        if not execution.output:
            return None
        first = execution.output[0]

        content = getattr(first, "output", None)
        if isinstance(content, str):
            return content
        if isinstance(content, list):
            return json.dumps(content)
        if hasattr(first, "content"):
            return json.dumps(first.content)
        return None

    def _normalize_task_status(self, value: Optional[str]) -> TaskStatus:
        if not value:
            return TaskStatus.FAILED
        try:
            return TaskStatus(value)
        except ValueError:
            return LEGACY_TASK_STATUS_MAP.get(value.lower(), TaskStatus.FAILED)

    def _map_legacy_status(self, value: str) -> TaskStatus:
        try:
            return TaskStatus(value)
        except ValueError:
            return LEGACY_TASK_STATUS_MAP.get(value.lower(), TaskStatus.FAILED)