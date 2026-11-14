import asyncio
import argparse
import struct

from serializer import serialize_task, deserialize_result
from executor import execute_task


HOST = "127.0.0.1"
PORT = 8888
MAX_MESSAGE_SIZE = 10 * 1024 * 1024


# Example task
def multiply(a, b):
    return a * b


# Send length-prefixed data
async def send_message(writer, data):
    if len(data) > MAX_MESSAGE_SIZE:
        raise ValueError("Message is too large")

    writer.write(struct.pack("!I", len(data)) + data)
    await writer.drain()


# Receive length-prefixed data
async def receive_message(reader):
    header = await reader.readexactly(4)
    size = struct.unpack("!I", header)[0]

    if size > MAX_MESSAGE_SIZE:
        raise ValueError("Message is too large")

    return await reader.readexactly(size)


# Peer B: Receive and execute task
async def handle_peer(reader, writer):
    address = writer.get_extra_info("peername")
    print(f"\nConnected to peer: {address}")

    try:
        task_data = await receive_message(reader)

        print("Task received!")
        print("Executing task...")

        response_data = await execute_task(task_data)

        await send_message(writer, response_data)

        print("Task executed and result returned!")

    except Exception as error:
        print("Network error:", error)

    finally:
        writer.close()
        await writer.wait_closed()


# Start Peer B
async def start_server():
    server = await asyncio.start_server(
        handle_peer,
        HOST,
        PORT
    )

    print(f"MeshWeaver Peer B running on {HOST}:{PORT}")

    async with server:
        await server.serve_forever()


# Peer A: Send task and receive result
async def start_client():
    reader, writer = await asyncio.open_connection(
        HOST,
        PORT
    )

    try:
        task_data = serialize_task(multiply, (10, 20), {})

        print("Sending task to Peer B...")

        await send_message(writer, task_data)

        response_data = await receive_message(reader)

        response = deserialize_result(response_data)

        print("\n========== TASK RESULT ==========")
        print("Status:", response["status"])

        if response["status"] == "success":
            print("Result:", response["result"])
        else:
            print("Error:", response["error"])

        print("=================================")

    finally:
        writer.close()
        await writer.wait_closed()


# Main program
if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "mode",
        choices=["server", "client"]
    )

    args = parser.parse_args()

    if args.mode == "server":
        asyncio.run(start_server())

    else:
        asyncio.run(start_client())