
import asyncio
import uuid
from datetime import datetime, timezone

from resource_monitor import get_resource_info


class GossipProtocol:
    """Share CPU and RAM information with connected MeshWeaver peers."""

    def __init__(self, node_id=None, update_interval=5):
        if (
            not isinstance(update_interval, (int, float))
            or isinstance(update_interval, bool)
            or update_interval <= 0
        ):
            raise ValueError("Update interval must be positive")

        self.node_id = node_id or str(uuid.uuid4())
        self.update_interval = update_interval

        self.latest_message = None
        self.peer_resources = {}

        self.network = None
        self.running = False
        self.task = None

    def attach_network(self, network):
        """Attach the PeerNetwork instance."""
        self.network = network

        self.network.register_handler(
            "GOSSIP",
            self.handle_gossip
        )

    def create_gossip_message(self, resource_info):
        """Create a JSON-compatible resource message."""

        return {
            "message_type": "GOSSIP",
            "node_id": self.node_id,
            "cpu_percent": resource_info["cpu_percent"],
            "ram_percent": resource_info["ram_percent"],
            "ram_used_mb": resource_info["ram_used_mb"],
            "ram_total_mb": resource_info["ram_total_mb"],
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

    async def update_resources(self):
        """Collect current CPU and RAM usage."""

        resource_info = await asyncio.to_thread(
            get_resource_info
        )

        self.latest_message = self.create_gossip_message(
            resource_info
        )

        return self.latest_message

    async def handle_gossip(self, message):
        """Validate and store a peer's resource information."""

        if not isinstance(message, dict):
            return False

        sender = message.get("sender")
        payload = message.get("payload")

        if not isinstance(sender, str) or not sender:
            return False

        if sender == self.node_id:
            return False

        if not isinstance(payload, dict):
            return False

        required = (
            "cpu_percent",
            "ram_percent",
            "ram_used_mb",
            "ram_total_mb",
            "timestamp"
        )

        if not all(key in payload for key in required):
            return False

        try:
            cpu = float(payload["cpu_percent"])
            ram = float(payload["ram_percent"])
            used = float(payload["ram_used_mb"])
            total = float(payload["ram_total_mb"])

            if not all(
                0 <= value <= 100
                for value in (cpu, ram)
            ):
                return False

            if used < 0 or total <= 0 or used > total:
                return False

            datetime.fromisoformat(payload["timestamp"])

        except (TypeError, ValueError):
            return False

        self.peer_resources[sender] = dict(payload)

        print(
            f"Gossip received from {sender}: "
            f"CPU={cpu}%, RAM={ram}%"
        )

        return True

    async def broadcast_update(self):
        """Collect resources and broadcast to connected peers."""

        message = await self.update_resources()

        if self.network is None:
            return {}

        return await self.network.broadcast(
            "GOSSIP",
            message
        )

    async def run(self):
        """Continuously broadcast resource updates."""

        if self.running:
            return

        self.running = True

        print(
            f"Gossip started for node {self.node_id}. "
            f"Interval: {self.update_interval} seconds"
        )

        try:
            while self.running:
                await self.broadcast_update()
                await asyncio.sleep(self.update_interval)

        finally:
            self.running = False

    def start_background(self):
        """Start Gossip without blocking the node."""

        if self.task and not self.task.done():
            return self.task

        self.task = asyncio.create_task(self.run())
        return self.task

    async def stop(self):
        """Stop the background Gossip task."""

        self.running = False

        if self.task and not self.task.done():
            self.task.cancel()

            try:
                await self.task
            except asyncio.CancelledError:
                pass

        self.task = None


async def main():
    from peer_network import PeerNetwork

    network = PeerNetwork("node-A")

    gossip = GossipProtocol(
        node_id="node-A",
        update_interval=5
    )

    gossip.attach_network(network)

    await network.start()

    try:
        await gossip.run()

    finally:
        await gossip.stop()
        await network.close()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Gossip monitoring stopped.")
