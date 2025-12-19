"""
Utility functions for MCP Scheduler.
"""
from typing import Optional
import datetime


def parse_cron_next_run(cron_expression: str, base_time: Optional[datetime.datetime] = None) -> datetime.datetime:
    """Parse a cron expression and return the next run time."""
    import croniter

    if base_time is None:
        base_time = datetime.datetime.now(datetime.timezone.utc)

    cron = croniter.croniter(cron_expression, base_time)
    return cron.get_next(datetime.datetime)


def format_duration(seconds: int) -> str:
    """Format duration in seconds to a human-readable string."""
    if seconds < 60:
        return f"{seconds} second{'s' if seconds != 1 else ''}"

    minutes = seconds // 60
    if minutes < 60:
        return f"{minutes} minute{'s' if minutes != 1 else ''}"

    hours = minutes // 60
    minutes = minutes % 60
    if hours < 24:
        return f"{hours} hour{'s' if hours != 1 else ''} {minutes} minute{'s' if minutes != 1 else ''}"

    days = hours // 24
    hours = hours % 24
    return f"{days} day{'s' if days != 1 else ''} {hours} hour{'s' if hours != 1 else ''}"


def human_readable_cron(cron_expression: str) -> str:
    """Convert a cron expression to a human-readable string."""
    try:
        # This is a very basic implementation and could be expanded
        parts = cron_expression.split()

        if len(parts) < 5:
            return cron_expression

        seconds = parts[0] if len(parts) >= 6 else "0"
        minutes = parts[1] if len(parts) >= 6 else parts[0]
        hours = parts[2] if len(parts) >= 6 else parts[1]
        day_of_month = parts[3] if len(parts) >= 6 else parts[2]
        month = parts[4] if len(parts) >= 6 else parts[3]
        day_of_week = parts[5] if len(parts) >= 6 else parts[4]

        if seconds == "0" and minutes == "0" and hours == "0" and day_of_month == "*" and month == "*" and day_of_week == "*":
            return "Daily at midnight"

        if seconds == "0" and minutes == "0" and hours == "*" and day_of_month == "*" and month == "*" and day_of_week == "*":
            return "Every hour on the hour"

        if seconds == "0" and minutes == "*" and hours == "*" and day_of_month == "*" and month == "*" and day_of_week == "*":
            return "Every minute"

        # Default to returning the original expression
        return cron_expression

    except Exception:
        return cron_expression
