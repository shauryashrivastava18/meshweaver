import asyncio
import inspect

from serializer import deserialize_task, serialize_result


async def run_task(func, args, kwargs, task_timeout):
    """Execute a task with timeout support."""

    if inspect.iscoroutinefunction(func):
        operation = func(*args, **kwargs)
    else:
        operation = asyncio.to_thread(func, *args, **kwargs)

    if task_timeout is None:
        result = await operation
    else:
        result = await asyncio.wait_for(
            operation,
            timeout=task_timeout
        )

    # Support functions that return awaitable objects
    if inspect.isawaitable(result):
        if task_timeout is None:
            result = await result
        else:
            result = await asyncio.wait_for(
                result,
                timeout=task_timeout
            )

    return result


async def execute_task(
    task_data,
    max_retries=3,
    retry_delay=1,
    task_timeout=10
):
    """
    Deserialize and execute a task.
    Supports automatic retries and timeout handling.
    """

    try:
        if not isinstance(task_data, bytes):
            raise TypeError("Task data must be in bytes format")

        if max_retries < 0:
            raise ValueError("max_retries cannot be negative")

        if retry_delay < 0:
            raise ValueError("retry_delay cannot be negative")

        if task_timeout is not None and task_timeout <= 0:
            raise ValueError("task_timeout must be positive")

        func, args, kwargs = deserialize_task(task_data)

        if not callable(func):
            raise TypeError("Received task is not callable")

        if not isinstance(args, (tuple, list)):
            raise TypeError("Task arguments must be a tuple or list")

        if not isinstance(kwargs, dict):
            raise TypeError("Keyword arguments must be a dictionary")

        for attempt in range(max_retries + 1):
            try:
                result = await run_task(
                    func,
                    args,
                    kwargs,
                    task_timeout
                )

                response = {
                    "status": "success",
                    "result": result,
                    "attempts": attempt + 1
                }

                break

            except Exception as error:
                if attempt == max_retries:
                    response = {
                        "status": "error",
                        "error": str(error),
                        "attempts": attempt + 1
                    }
                else:
                    await asyncio.sleep(retry_delay)

    except Exception as error:
        response = {
            "status": "error",
            "error": str(error),
            "attempts": 0
        }

    return serialize_result(response)