
import asyncio
import secrets
import uuid

from kademlia import RoutingTable


class KademliaNetwork:
    """Network-based Kademlia peer discovery over TCP."""

    def __init__(
        self,
        network,
        node_id=None,
        host="127.0.0.1",
        port=0,
        bucket_size=3,
        lookup_timeout=3
    ):
        self.network = network
        self.node_id = (
            node_id if node_id is not None else secrets.randbits(160)
        )

        if not isinstance(self.node_id, int) or isinstance(self.node_id, bool):
            raise TypeError("node_id must be an integer")

        if self.node_id < 0:
            raise ValueError("node_id must be non-negative")

        self.host = host
        self.port = port
        self.lookup_timeout = lookup_timeout

        self.routing_table = RoutingTable(
            local_node_id=self.node_id,
            bucket_size=bucket_size
        )

        self.pending = {}

        self.network.register_handler("HELLO", self.handle_hello)
        self.network.register_handler("KAD", self.handle_message)

    async def start(self):
        await self.network.start()
        self.port = self.network.port
        return self.port

    async def handle_hello(self, message):
        """Register a newly connected peer in the routing table."""

        sender = message.get("sender")
        payload = message.get("payload", {})

        if not isinstance(payload, dict):
            return

        host = payload.get("host")
        port = payload.get("port")

        if not isinstance(sender, str) or not sender.isdigit():
            return

        if not isinstance(host, str) or not host.strip():
            return

        if (
            not isinstance(port, int)
            or isinstance(port, bool)
            or not 1 <= port <= 65535
        ):
            return

        peer_id = int(sender)

        if peer_id == self.node_id:
            return

        self.routing_table.add_peer(peer_id, host, port)

    async def handle_message(self, message):
        """Handle Kademlia requests and responses."""

        payload = message.get("payload", {})
        sender = message.get("sender")

        if not isinstance(payload, dict):
            return

        action = payload.get("action")

        if action == "FIND_NODE":
            target_id = payload.get("target_id")
            request_id = payload.get("request_id")

            if (
                not isinstance(target_id, int)
                or isinstance(target_id, bool)
                or target_id < 0
                or not isinstance(request_id, str)
            ):
                return

            peers = self.routing_table.find_closest_peers(
                target_id,
                count=self.routing_table.bucket_size
            )

            peer_list = [
                {
                    "node_id": peer_id,
                    "host": details["ip_address"],
                    "port": details["port"]
                }
                for peer_id, details in peers
            ]

            await self.network.send(
                sender,
                "KAD",
                {
                    "action": "FIND_NODE_RESPONSE",
                    "request_id": request_id,
                    "target_id": target_id,
                    "peers": peer_list
                }
            )

        elif action == "FIND_NODE_RESPONSE":
            request_id = payload.get("request_id")
            future = self.pending.get(request_id)

            if future is not None and not future.done():
                peers = payload.get("peers", [])

                if isinstance(peers, list):
                    future.set_result(peers)
                else:
                    future.set_result([])

    async def add_known_peer(self, node_id, host, port, connect=True):
        if node_id == self.node_id:
            return False

        added = self.routing_table.add_peer(node_id, host, port)

        if not added and node_id not in self.routing_table.peers:
            return False

        if connect:
            await self.network.connect(str(node_id), host, port)

        return True

    async def find_node(self, peer_id, target_id):
        peer_id = str(peer_id)

        if peer_id not in self.network.connections:
            details = self.routing_table.peers.get(int(peer_id))

            if details is None:
                raise ConnectionError(f"Unknown peer: {peer_id}")

            await self.network.connect(
                peer_id,
                details["ip_address"],
                details["port"]
            )

        request_id = str(uuid.uuid4())

        future = asyncio.get_running_loop().create_future()
        self.pending[request_id] = future

        try:
            await self.network.send(
                peer_id,
                "KAD",
                {
                    "action": "FIND_NODE",
                    "request_id": request_id,
                    "target_id": target_id
                }
            )

            return await asyncio.wait_for(
                future,
                timeout=self.lookup_timeout
            )

        finally:
            self.pending.pop(request_id, None)

    async def lookup(self, target_id, count=3, max_rounds=8):
        """Iteratively discover closer peers."""

        queried = set()

        for _ in range(max_rounds):
            candidates = self.routing_table.find_closest_peers(
                target_id,
                count=max(count, self.routing_table.bucket_size)
            )

            next_peer = None

            for peer_id, details in candidates:
                if peer_id not in queried:
                    next_peer = (peer_id, details)
                    break

            if next_peer is None:
                break

            peer_id, details = next_peer
            queried.add(peer_id)

            try:
                if str(peer_id) not in self.network.connections:
                    await self.network.connect(
                        str(peer_id),
                        details["ip_address"],
                        details["port"]
                    )

                discovered = await self.find_node(
                    peer_id,
                    target_id
                )

                for peer in discovered:
                    if not isinstance(peer, dict):
                        continue

                    try:
                        discovered_id = peer["node_id"]
                        host = peer["host"]
                        port = peer["port"]

                        if (
                            not isinstance(discovered_id, int)
                            or isinstance(discovered_id, bool)
                            or not isinstance(host, str)
                            or not isinstance(port, int)
                            or isinstance(port, bool)
                            or not 1 <= port <= 65535
                        ):
                            continue

                        self.routing_table.add_peer(
                            discovered_id,
                            host,
                            port
                        )

                    except (KeyError, TypeError, ValueError):
                        continue

            except (
                ConnectionError,
                OSError,
                asyncio.TimeoutError
            ):
                self.routing_table.remove_peer(peer_id)

        return self.routing_table.find_closest_peers(
            target_id,
            count=count
        )

    async def join(self, bootstrap_host, bootstrap_port, bootstrap_id):
        """Join an existing network through a bootstrap node."""

        if bootstrap_id == self.node_id:
            raise ValueError("Cannot join through yourself")

        await self.network.connect(
            str(bootstrap_id),
            bootstrap_host,
            bootstrap_port
        )

        self.routing_table.add_peer(
            bootstrap_id,
            bootstrap_host,
            bootstrap_port
        )

        await self.lookup(self.node_id)

        return self.routing_table.find_closest_peers(
            self.node_id,
            count=self.routing_table.bucket_size
        )

    async def close(self):
        for future in self.pending.values():
            if not future.done():
                future.cancel()

        self.pending.clear()
        await self.network.close()
