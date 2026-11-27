
import asyncio
import inspect
import struct

from message import Message
from peer import PeerRegistry


MAX_MESSAGE_SIZE = 10 * 1024 * 1024


class PeerNetwork:
    """Asynchronous TCP communication between MeshWeaver peers."""

    def __init__(self, peer_id, host="127.0.0.1", port=0):
        if not isinstance(peer_id, str) or not peer_id:
            raise ValueError("Peer ID cannot be empty")

        if not isinstance(port, int) or isinstance(port, bool):
            raise ValueError("Invalid port")

        if not 0 <= port <= 65535:
            raise ValueError("Invalid port")

        self.peer_id = peer_id
        self.host = host
        self.port = port

        self.server = None
        self.registry = PeerRegistry()
        self.connections = {}
        self.read_tasks = set()
        self.connection_tasks = {}
        self.handlers = {}
        self.connection_lock = asyncio.Lock()
        self.closed = False

    def register_handler(self, message_type, callback):
        if not callable(callback):
            raise TypeError("Handler must be callable")

        self.handlers[message_type] = callback

    async def start(self):
        if self.closed:
            raise RuntimeError("PeerNetwork is closed")

        if self.server is not None:
            return

        self.server = await asyncio.start_server(
            self._accept_connection,
            self.host,
            self.port
        )

        self.port = self.server.sockets[0].getsockname()[1]

        print(
            f"Peer {self.peer_id} listening "
            f"on {self.host}:{self.port}"
        )

    async def _send_frame(self, writer, data):
        if not isinstance(data, bytes):
            raise TypeError("Network data must be bytes")

        if not data or len(data) > MAX_MESSAGE_SIZE:
            raise ValueError("Invalid message size")

        writer.write(struct.pack("!I", len(data)) + data)
        await writer.drain()

    async def _receive_frame(self, reader):
        header = await reader.readexactly(4)
        size = struct.unpack("!I", header)[0]

        if size == 0 or size > MAX_MESSAGE_SIZE:
            raise ValueError("Invalid message size")

        return await reader.readexactly(size)

    async def _accept_connection(self, reader, writer):
        task = asyncio.create_task(
            self._read_loop(reader, writer)
        )

        self.read_tasks.add(task)
        task.add_done_callback(self.read_tasks.discard)

    async def connect(self, remote_peer_id, host, port):
        if self.closed:
            raise RuntimeError("PeerNetwork is closed")

        if remote_peer_id == self.peer_id:
            raise ValueError("Cannot connect to yourself")

        async with self.connection_lock:
            existing = self.connections.get(remote_peer_id)

            if existing and not existing.is_closing():
                return True

            reader, writer = await asyncio.open_connection(
                host, port
            )

            self.connections[remote_peer_id] = writer

            self.registry.add_peer(
                remote_peer_id,
                host,
                port
            )

            task = asyncio.create_task(
                self._read_loop(reader, writer)
            )

            self.read_tasks.add(task)
            self.connection_tasks[remote_peer_id] = task
            task.add_done_callback(self.read_tasks.discard)

        await self.send(
            remote_peer_id,
            "HELLO",
            {
                "peer_id": self.peer_id,
                "host": self.host,
                "port": self.port
            }
        )

        return True

    async def _read_loop(self, reader, writer):
        remote_peer_id = None

        try:
            while not self.closed:
                data = await self._receive_frame(reader)
                message = Message.deserialize(data)

                remote_peer_id = message["sender"]

                if remote_peer_id == self.peer_id:
                    raise ValueError("Received message from self")

                if message["receiver"] != self.peer_id:
                    raise ValueError("Message receiver mismatch")

                self.registry.update_last_seen(remote_peer_id)

                if remote_peer_id not in self.connections:
                    self.connections[remote_peer_id] = writer

                message_type = message["message_type"]

                if message_type == "HELLO":
                    payload = message.get("payload", {})

                    if not isinstance(payload, dict):
                        raise ValueError("Invalid HELLO payload")

                    host = payload.get("host")
                    port = payload.get("port")

                    if (
                        not isinstance(host, str)
                        or not host.strip()
                        or not isinstance(port, int)
                        or isinstance(port, bool)
                        or not 1 <= port <= 65535
                    ):
                        raise ValueError("Invalid peer address")

                    self.registry.add_peer(
                        remote_peer_id,
                        host,
                        port
                    )

                callback = self.handlers.get(message_type)

                if callback:
                    result = callback(message)

                    if inspect.isawaitable(result):
                        await result

        except (
            asyncio.IncompleteReadError,
            ConnectionError,
            OSError,
            ValueError
        ):
            pass

        finally:
            if remote_peer_id:
                if self.connections.get(remote_peer_id) is writer:
                    self.connections.pop(remote_peer_id, None)
                    self.registry.remove_peer(remote_peer_id)

            if not writer.is_closing():
                writer.close()

                try:
                    await writer.wait_closed()
                except OSError:
                    pass

    async def send(self, peer_id, message_type, payload):
        if self.closed:
            raise RuntimeError("PeerNetwork is closed")

        writer = self.connections.get(peer_id)

        if writer is None or writer.is_closing():
            raise ConnectionError(
                f"Peer {peer_id} is not connected"
            )

        message = Message(
            sender=self.peer_id,
            receiver=peer_id,
            message_type=message_type,
            payload=payload
        )

        await self._send_frame(
            writer,
            message.serialize()
        )

        return message.message_id

    async def send_kademlia(self, peer_id, payload):
        return await self.send(peer_id, "KAD", payload)

    async def send_gossip(self, peer_id, payload):
        return await self.send(peer_id, "GOSSIP", payload)

    async def broadcast(self, message_type, payload):
        results = {}

        for peer_id in list(self.connections):
            try:
                results[peer_id] = await self.send(
                    peer_id,
                    message_type,
                    payload
                )
            except (ConnectionError, OSError) as error:
                results[peer_id] = str(error)

        return results

    async def disconnect(self, peer_id):
        writer = self.connections.pop(peer_id, None)
        task = self.connection_tasks.pop(peer_id, None)

        self.registry.remove_peer(peer_id)

        if writer is None:
            return False

        if task and task is not asyncio.current_task():
            task.cancel()

        if not writer.is_closing():
            writer.close()

            try:
                await writer.wait_closed()
            except OSError:
                pass

        return True

    def get_peers(self):
        return self.registry.list_peers()

    async def close(self):
        if self.closed:
            return

        self.closed = True

        if self.server:
            self.server.close()
            await self.server.wait_closed()

        writers = list({
            id(writer): writer
            for writer in self.connections.values()
        }.values())

        for writer in writers:
            if not writer.is_closing():
                writer.close()

        if writers:
            await asyncio.gather(
                *(writer.wait_closed() for writer in writers),
                return_exceptions=True
            )

        for task in list(self.read_tasks):
            task.cancel()

        if self.read_tasks:
            await asyncio.gather(
                *self.read_tasks,
                return_exceptions=True
            )

        self.connections.clear()
        self.connection_tasks.clear()
        self.registry.peers.clear()
