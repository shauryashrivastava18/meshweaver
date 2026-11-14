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