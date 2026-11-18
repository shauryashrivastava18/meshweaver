import asyncio
import pytest

from network_test import (
    send_message,
    receive_message,
    send_task
)

from serializer import (
    serialize_task
)


def multiply(a, b):
    return a * b


class DummyWriter:
    def write(self, data):
        raise AssertionError("write should not be called")

    async def drain(self):
        pass


def test_send_message_size_validation():
    async def run():
        writer = DummyWriter()

        with pytest.raises(ValueError):
            await send_message(
                writer,
                b"x" * (10 * 1024 * 1024 + 1)
            )

    asyncio.run(run())


def test_receive_message():
    async def run():
        server_reader = asyncio.StreamReader()

        message = b"MeshWeaver test message"

        server_reader.feed_data(
            len(message).to_bytes(4, "big") + message
        )

        received = await receive_message(server_reader)

        assert received == message

    asyncio.run(run())


def test_receive_message_too_large():
    async def run():
        reader = asyncio.StreamReader()

        size = 10 * 1024 * 1024 + 1

        reader.feed_data(size.to_bytes(4, "big"))

        with pytest.raises(ValueError):
            await receive_message(reader)

    asyncio.run(run())


def test_remote_task_execution():
    async def run():
        from task_manager import TaskManager
        from network_test import handle_peer

        manager = TaskManager(max_concurrency=2)

        server = await asyncio.start_server(
            lambda reader, writer: handle_peer(
                reader,
                writer,
                manager
            ),
            "127.0.0.1",
            0
        )

        host, port = server.sockets[0].getsockname()[:2]

        try:
            task_data = serialize_task(
                multiply,
                (10, 20),
                {}
            )

            response = await send_task(
                host,
                port,
                task_data
            )

            assert response["status"] == "completed"
            assert response["result"] == 200

        finally:
            server.close()
            await server.wait_closed()
            await manager.close()

    asyncio.run(run())


def test_remote_task_with_different_arguments():
    async def run():
        from task_manager import TaskManager
        from network_test import handle_peer

        manager = TaskManager()

        server = await asyncio.start_server(
            lambda reader, writer: handle_peer(
                reader,
                writer,
                manager
            ),
            "127.0.0.1",
            0
        )

        host, port = server.sockets[0].getsockname()[:2]

        try:
            task_data = serialize_task(
                multiply,
                (7, 8),
                {}
            )

            response = await send_task(
                host,
                port,
                task_data
            )

            assert response["status"] == "completed"
            assert response["result"] == 56

        finally:
            server.close()
            await server.wait_closed()
            await manager.close()

    asyncio.run(run())