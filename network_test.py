
import asyncio
import sys

from serializer import (
    serialize_task,
    serialize_result,
    deserialize_result
)
from task_manager import TaskManager


MAX_MESSAGE_SIZE = 10 * 1024 * 1024


def complex_math(n):
    total = 0

    for i in range(1, n + 1):
        total += i**2 + 3 * i + 5

    return total


def extract_task_result(task_response):
    """
    Extract the actual result from TaskManager's response.
    """

    if isinstance(task_response, dict):
        if task_response.get("status") == "completed":
            return {
                "status": "completed",
                "result": task_response.get("result")
            }

        return {
            "status": "error",
            "message": (
                task_response.get("error")
                or "Task execution failed"
            )
        }

    return {
        "status": "completed",
        "result": task_response
    }


async def send_message(writer, message):
    if len(message) > MAX_MESSAGE_SIZE:
        raise ValueError("Message size exceeds 10 MB limit")

    writer.write(len(message).to_bytes(4, "big"))
    writer.write(message)

    await writer.drain()


async def receive_message(reader):
    size_data = await reader.readexactly(4)

    message_size = int.from_bytes(size_data, "big")

    if message_size > MAX_MESSAGE_SIZE:
        raise ValueError("Message size exceeds 10 MB limit")

    return await reader.readexactly(message_size)


async def handle_peer(reader, writer, task_manager):
    try:
        # Receive serialized task
        task_data = await receive_message(reader)

        # Submit task to TaskManager
        task_id = task_manager.submit_task(task_data)

        # Wait for task execution
        task_response = await task_manager.wait_for_task(task_id)

        # Extract only the actual execution result
        response = extract_task_result(task_response)

        # Serialize and send response
        response_data = serialize_result(response)

        await send_message(writer, response_data)

    except Exception as error:
        print("Server error:", repr(error))

        try:
            error_response = serialize_result({
                "status": "error",
                "message": str(error)
            })

            await send_message(writer, error_response)

        except Exception as send_error:
            print("Response error:", repr(send_error))

    finally:
        writer.close()

        try:
            await writer.wait_closed()
        except Exception:
            pass


async def send_task(host, port, task_data):
    reader, writer = await asyncio.open_connection(
        host,
        port
    )

    try:
        # Send task to remote node
        await send_message(writer, task_data)

        # Receive task result
        response_data = await receive_message(reader)

        response = deserialize_result(response_data)

        return response

    finally:
        writer.close()

        try:
            await writer.wait_closed()
        except Exception:
            pass


async def start_server():
    task_manager = TaskManager()

    server = await asyncio.start_server(
        lambda reader, writer: handle_peer(
            reader,
            writer,
            task_manager
        ),
        "127.0.0.1",
        8888
    )

    print("MeshWeaver Server running on 127.0.0.1:8888")
    print("Waiting for remote tasks...")

    try:
        async with server:
            await server.serve_forever()

    finally:
        await task_manager.close()


async def start_client():
    task_data = serialize_task(
        complex_math,
        (1000,),
        {}
    )

    response = await send_task(
        "127.0.0.1",
        8888,
        task_data
    )

    print("Server response:", response)

    if response["status"] == "completed":
        print("Remote execution result:", response["result"])
    else:
        print("Remote execution failed:", response["message"])


if __name__ == "__main__":

    if len(sys.argv) < 2:
        print("Usage: python network_test.py server/client")

    elif sys.argv[1] == "server":
        asyncio.run(start_server())

    elif sys.argv[1] == "client":
        asyncio.run(start_client())

    else:
        print("Invalid argument. Use server or client.")
