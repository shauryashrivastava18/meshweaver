
import asyncio
import sys

from serializer import serialize_task, serialize_result, deserialize_result
from task_manager import TaskManager


def complex_math(n):
    total = 0

    for i in range(1, n + 1):
        total += i**2 + 3 * i + 5

    return total


async def handle_client(reader, writer, task_manager):
    print("Client connected!")

    try:
        size_data = await reader.readexactly(8)
        task_size = int.from_bytes(size_data, "big")

        task_data = await reader.readexactly(task_size)

        print("Task received!")
        print("Submitting task to Task Manager...")

        # submit_task is synchronous: do not use await
        task_id = task_manager.submit_task(task_data)

        # wait_for_task is asynchronous
        result = await task_manager.wait_for_task(task_id)

        response = serialize_result({
            "status": "completed",
            "result": result
        })

        writer.write(len(response).to_bytes(8, "big"))
        writer.write(response)
        await writer.drain()

        print("Remote task completed!")
        print("Result:", result)

    except Exception as error:
        print("Server error:", repr(error))

        try:
            response = serialize_result({
                "status": "error",
                "message": str(error)
            })
            writer.write(len(response).to_bytes(8, "big"))
            writer.write(response)
            await writer.drain()
        except Exception as send_error:
            print("Response error:", repr(send_error))

    finally:
        writer.close()
        await writer.wait_closed()


async def start_server():
    task_manager = TaskManager()

    server = await asyncio.start_server(
        lambda reader, writer: handle_client(
            reader, writer, task_manager
        ),
        "127.0.0.1",
        8888
    )

    print("MeshWeaver Server running on 127.0.0.1:8888")
    print("Waiting for remote tasks...")

    async with server:
        await server.serve_forever()


async def send_task():
    reader, writer = await asyncio.open_connection(
        "127.0.0.1",
        8888
    )

    try:
        print("Connected to remote server!")

        task_data = serialize_task(
            complex_math,
            (1000,),
            {}
        )

        writer.write(len(task_data).to_bytes(8, "big"))
        writer.write(task_data)
        await writer.drain()

        print("Complex task sent!")

        size_data = await reader.readexactly(8)
        result_size = int.from_bytes(size_data, "big")

        response_data = await reader.readexactly(result_size)
        response = deserialize_result(response_data)

        print("Server response:", response)

        if response["status"] == "completed":
            print("Remote execution result:", response["result"])
        else:
            print("Remote execution failed:", response["message"])

    finally:
        writer.close()
        await writer.wait_closed()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python network_test.py server/client")
    elif sys.argv[1] == "server":
        asyncio.run(start_server())
    elif sys.argv[1] == "client":
        asyncio.run(send_task())
    else:
        print("Invalid argument. Use server or client.")
