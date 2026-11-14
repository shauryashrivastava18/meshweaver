import asyncio
import argparse
import struct

from serializer import (
    serialize_task,
    deserialize_result,
    serialize_result
)

from task_manager import TaskManager


HOST = "127.0.0.1"
PORT = 8888
MAX_MESSAGE_SIZE = 10 * 1024 * 1024


def multiply(a, b):
    return a * b


async def send_message(writer, data):
    """Send a length-prefixed network message."""

    if not isinstance(data, bytes):
        raise TypeError("Message must be bytes")

    if len(data) > MAX_MESSAGE_SIZE:
        raise ValueError("Message is too large")

    writer.write(struct.pack("!I", len(data)) + data)
    await writer.drain()


async def receive_message(reader):
    """Receive a length-prefixed network message."""

    header = await reader.readexactly(4)
    size = struct.unpack("!I", header)[0]

    if size > MAX_MESSAGE_SIZE:
        raise ValueError("Message is too large")

    return await reader.readexactly(size)


async def handle_peer(reader, writer, manager):
    """Receive a task, submit it to TaskManager and return its result."""

    address = writer.get_extra_info("peername")
    print(f"\nConnected to peer: {address}")

    try:
        task_data = await receive_message(reader)

        print("Task received!")
        print("Submitting task to Task Manager...")

        task_id = manager.submit_task(
            task_data,
            priority=0
        )

        result = await manager.wait_for_task(task_id)

        response_data = serialize_result(result)

        await send_message(writer, response_data)

        print("Remote task completed!")
        print("Task ID:", task_id)
        print("Status:", result["status"])

    except Exception as error:
        error_response = {
            "status": "error",
            "error": str(error)
        }

        try:
            await send_message(
                writer,
                serialize_result(error_response)
            )
        except Exception:
            pass

        print("Network error:", error)

    finally:
        writer.close()

        try:
            await writer.wait_closed()
        except Exception:
            pass


async def start_server():
    """Start a TCP peer with an integrated Task Manager."""

    manager = TaskManager(
        max_retries=3,
        retry_delay=1,
        task_timeout=10,
        max_concurrency=4
    )

    server = await asyncio.start_server(
        lambda reader, writer: handle_peer(
            reader,
            writer,
            manager
        ),
        HOST,
        PORT
    )

    print(f"MeshWeaver Peer B running on {HOST}:{PORT}")
    print("Task Manager connected!")
    print("Waiting for remote tasks...")

    try:
        async with server:
            await server.serve_forever()

    finally:
        await manager.close()


async def send_task(host, port, task_data):
    """Send a task to a remote peer and retrieve its result."""

    reader, writer = await asyncio.open_connection(
        host,
        port
    )

    try:
        await send_message(writer, task_data)

        response_data = await receive_message(reader)

        return deserialize_result(response_data)

    finally:
        writer.close()
        await writer.wait_closed()


async def start_client():
    """Submit an example remote task."""

    task_data = serialize_task(
        multiply,
        (10, 20),
        {}
    )

    print("Sending task to Peer B...")

    response = await send_task(
        HOST,
        PORT,
        task_data
    )

    print("\n========== REMOTE TASK RESULT ==========")

    print("Status:", response["status"])

    if response["status"] == "completed":
        print("Result:", response["result"])

    elif response["status"] == "success":
        print("Result:", response["result"])

    else:
        print("Error:", response.get("error"))

    print("========================================")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="MeshWeaver TCP Task Networking"
    )

    parser.add_argument(
        "mode",
        choices=["server", "client"]
    )

    args = parser.parse_args()

    if args.mode == "server":
        asyncio.run(start_server())

    else:
        asyncio.run(start_client())