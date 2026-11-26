import asyncio
import uuid
import time


class GossipRouter:
    """Manages gossip message propagation between MeshWeaver peers."""

    def __init__(self, network, max_hops=5, message_ttl=60):
        if max_hops < 1:
            raise ValueError("max_hops must be positive")

        self.network = network
        self.max_hops = max_hops
        self.message_ttl = message_ttl

        self.seen_messages = {}
        self.lock = asyncio.Lock()

        self.network.register_handler(
            "GOSSIP",
            self.handle_message
        )

    async def publish(self, payload):
        message_id = str(uuid.uuid4())

        async with self.lock:
            self.seen_messages[message_id] = time.time()

        await self._forward(
            message_id,
            payload,
            self.max_hops,
            exclude=None
        )

        return message_id

    async def handle_message(self, message):
        payload = message.get("payload", {})

        message_id = payload.get("gossip_id")
        content = payload.get("content")
        hops = payload.get("hops")

        if not message_id or hops is None:
            return False

        if not isinstance(hops, int) or hops <= 0:
            return False

        async with self.lock:
            self._cleanup()

            if message_id in self.seen_messages:
                return False

            self.seen_messages[message_id] = time.time()

        await self._forward(
            message_id,
            content,
            hops - 1,
            exclude=message.get("sender")
        )

        return True

    async def _forward(
        self,
        message_id,
        content,
        hops,
        exclude=None
    ):
        if hops <= 0:
            return

        payload = {
            "gossip_id": message_id,
            "content": content,
            "hops": hops
        }

        for peer_id in list(self.network.connections):
            if peer_id == exclude:
                continue

            try:
                await self.network.send_gossip(
                    peer_id,
                    payload
                )
            except (ConnectionError, OSError):
                continue

    def _cleanup(self):
        now = time.time()

        expired = [
            message_id
            for message_id, timestamp in self.seen_messages.items()
            if now - timestamp > self.message_ttl
        ]

        for message_id in expired:
            del self.seen_messages[message_id]

    def get_statistics(self):
        self._cleanup()

        return {
            "known_messages": len(self.seen_messages),
            "max_hops": self.max_hops,
            "message_ttl": self.message_ttl
        }