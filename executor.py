import asyncio
import inspect

from serializer import deserialize_task, serialize_result


async def execute_task(task_data, max_retries=3, retry_delay=1):
    """
    Deserialize and execute a task.
    Retry failed tasks up to max_retries times.
    Return the result in serialized form.
    """

    try:
        if not isinstance(task_data, bytes):
            raise TypeError("Task data must be in bytes format")

        func, args, kwargs = deserialize_task(task_data)

        if not callable(func):
            raise TypeError("Received task is not callable")

        if not isinstance(args, (tuple, list)):
            raise TypeError("Task arguments must be a tuple or list")

        if not isinstance(kwargs, dict):
            raise TypeError("Keyword arguments must be a dictionary")

        if max_retries < 0:
            raise ValueError("max_retries cannot be negative")

        if retry_delay < 0:
            raise ValueError("retry_delay cannot be negative")

        for attempt in range(max_retries + 1):
            try:
                result = func(*args, **kwargs)

                if inspect.isawaitable(result):
                    result = await result

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