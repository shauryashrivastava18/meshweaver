import asyncio

from executor import execute_task
from serializer import serialize_task, deserialize_result


def multiply(a, b):
    return a * b


def test_execute_task():
    task_data = serialize_task(multiply, (10, 20), {})
    response_data = asyncio.run(execute_task(task_data))
    response = deserialize_result(response_data)

    assert response["status"] == "success"
    assert response["result"] == 200


def test_execute_task_with_error():
    def divide(a, b):
        return a / b

    task_data = serialize_task(divide, (10, 0), {})
    response_data = asyncio.run(execute_task(task_data))
    response = deserialize_result(response_data)

    assert response["status"] == "error"


async def async_multiply(a, b):
    await asyncio.sleep(1)
    return a * b


def test_async_task_execution():
    task_data = serialize_task(async_multiply, (5, 10), {})
    response_data = asyncio.run(execute_task(task_data))
    response = deserialize_result(response_data)

    assert response["status"] == "success"
    assert response["result"] == 50


def test_invalid_task_data():
    response_data = asyncio.run(execute_task("invalid data"))
    response = deserialize_result(response_data)

    assert response["status"] == "error"


def test_task_retry_success():
    attempts = {"count": 0}

    def temporary_failure():
        attempts["count"] += 1

        if attempts["count"] < 2:
            raise ValueError("Temporary failure")

        return "Success after retry"

    task_data = serialize_task(temporary_failure, (), {})

    response_data = asyncio.run(
        execute_task(task_data, max_retries=3, retry_delay=0)
    )

    response = deserialize_result(response_data)

    assert response["status"] == "success"
    assert response["result"] == "Success after retry"
    assert response["attempts"] == 2


def test_task_retry_failure():
    def always_fail():
        raise ValueError("Task failed")

    task_data = serialize_task(always_fail, (), {})

    response_data = asyncio.run(
        execute_task(task_data, max_retries=2, retry_delay=0)
    )

    response = deserialize_result(response_data)

    assert response["status"] == "error"
    assert response["attempts"] == 3
    import time


def test_sync_task_timeout():
    def slow_task():
        time.sleep(1)
        return "Finished"

    task_data = serialize_task(slow_task, (), {})

    response_data = asyncio.run(
        execute_task(
            task_data,
            max_retries=0,
            task_timeout=0.1
        )
    )

    response = deserialize_result(response_data)

    assert response["status"] == "error"
    assert response["attempts"] == 1


def test_async_task_timeout():
    async def slow_task():
        await asyncio.sleep(1)
        return "Finished"

    task_data = serialize_task(slow_task, (), {})

    response_data = asyncio.run(
        execute_task(
            task_data,
            max_retries=0,
            task_timeout=0.1
        )
    )

    response = deserialize_result(response_data)

    assert response["status"] == "error"
    assert response["attempts"] == 1