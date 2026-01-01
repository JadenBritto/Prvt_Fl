from typing import Any, Dict, Optional
from datetime import datetime, timezone
from arq.connections import RedisSettings
from src.app.settings import get_settings
from .redis import get_redis_pool


class WorkerSettings:
    """
    Worker configuration for ARQ asynchronous task processing.

    This class defines:
        - Redis connection settings
        - Max concurrent jobs
        - Job timeout
        - Queue name for this project
        - List of registered task functions

    NOTE:
        - Add your ARQ task functions to the `functions` list.
        - This class is automatically discovered by ARQ workers when running:
              arq src.app.tasks.WorkerSettings
        - Ensure that Redis is reachable using the credentials from settings.

    Attributes:
        functions (list):
            List of coroutine functions that ARQ can execute.
            Example:
                functions = [send_email_task, process_report_task]

        redis_settings (RedisSettings):
            Redis connection credentials for ARQ queue.

        max_jobs (int):
            Maximum number of jobs processed concurrently.

        job_timeout (int):
            Timeout for each job (in seconds).

        queue_name (str):
            Unique queue identifier for this project. Helps avoid conflicts
            across environments and microservices.

    Usage:
        # Start worker
        arq src.app.tasks.WorkerSettings

        # Submit job
        await schedule_task("send_email_task", {"user_id": 25})
    """

    functions = []  # list of task functions
    settings = get_settings()

    redis_settings = RedisSettings(
        host=settings.redis.redis_host,
        port=settings.redis.redis_port,
        password=settings.redis.redis_password
    )

    max_jobs = 100
    job_timeout = 60
    queue_name = f"arq:queue:{settings.app.project_name}"


async def schedule_task(
    func_name: str,
    kwargs: Optional[Dict[str, Any]] = None,
    *,
    run_at: Optional[datetime] = None,
    delay_seconds: Optional[int] = None,
) -> None:
    """
    Schedule an asynchronous background task using ARQ.

    This function provides three scheduling modes:
        1. Immediate execution
        2. Delayed execution (run after N seconds)
        3. Scheduled execution at a specific datetime (UTC aware)

    NOTE:
        - `func_name` must match a function exposed in WorkerSettings.functions.
        - Always pass timezone-aware datetimes for `run_at`.
          If a naive datetime is provided, it is automatically converted to UTC.
        - This function uses Redis connection pooling via get_redis_pool().

    Parameters:
        func_name (str):
            Name of the function to execute (string reference).

        kwargs (dict | None):
            Keyword arguments forwarded to the task function.

        run_at (datetime | None):
            Exact datetime when the task should run.
            Example:
                run_at=datetime(2025, 1, 1, 10, 0, tzinfo=timezone.utc)

        delay_seconds (int | None):
            Delay execution by N seconds.
            Example:
                delay_seconds=30   # run after 30 seconds

    Returns:
        None

    Usage:
        # 1. Run immediately
        await schedule_task("refresh_campaigns")

        # 2. Run after delay
        await schedule_task("sync_contacts", {"limit": 100}, delay_seconds=60)

        # 3. Run at specific time
        await schedule_task(
            "send_reminder_email",
            {"user_id": 10},
            run_at=datetime(2024, 12, 31, 23, 59, tzinfo=timezone.utc)
        )
    """

    if kwargs is None:
        kwargs = {}

    redis_pool = await get_redis_pool()

    if run_at:
        if run_at.tzinfo is None:
            run_at = run_at.replace(tzinfo=timezone.utc)

        print(f"[DEBUG] Scheduling job '{func_name}' at {run_at}")
        job_id = await redis_pool.enqueue_job(func_name, kwargs, _defer_until=run_at)

    elif delay_seconds is not None:
        print(f"[DEBUG] Scheduling job '{func_name}' in {delay_seconds}s")
        job_id = await redis_pool.enqueue_job(
            func_name, kwargs, _defer_by=delay_seconds
        )

    else:
        print(f"[DEBUG] Scheduling job '{func_name}' immediately")
        job_id = await redis_pool.enqueue_job(func_name, kwargs)

    print(f"[DEBUG] job_id={job_id}, kwargs={kwargs}")
