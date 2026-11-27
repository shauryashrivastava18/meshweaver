
import asyncio
import json
import uuid
from datetime import datetime, timezone

from resource_monitor import get_resource_info


class GossipProtocol:
    def __init__(self, node_id=None, update_interval=5):
        if update_interval <= 0:
            raise ValueError("Update interval must be positive")

        self.node_id = node_id or str(uuid.uuid4())
        self.update_interval = update_interval
        self.latest_message = None
        self.peer_resources = {}
        self.network = None
        self.running = False

    def attach_network(self, network):
        """Attach the PeerNetwork instance."""
        self.network = network
        self.network.register_handler(
            "GOSSIP",
            self.handle_gossip
        )

    def create_gossip_message(self, resource_info):
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
        resource_info = await asyncio.to_thread(get_resource_info)
        self.latest_message = self.create_gossip_message(resource_info)
        return self.latest_message

    async def handle_gossip(self, message):
        """Store resource information received from another peer."""
        sender = message["sender"]
        payload = message["payload"]

        if sender == self.node_id:
            return

        self.peer_resources[sender] = payload

        print(f"Received Gossip update from {sender}")

    async def broadcast_update(self):
        """Collect resources and broadcast them to connected peers."""
        message = await self.update_resources()

        if self.network is None:
            return message

        results = await self.network.broadcast(
            "GOSSIP",
            message
        )

        return results

    async def run(self):
        """Broadcast resource updates periodically."""
        self.running = True
        print(f"Gossip started for node {self.node_id}")

        try:
            while self.running:
                await self.broadcast_update()
                await asyncio.sleep(self.update_interval)
        except asyncio.CancelledError:
            raise
        finally:
            self.running = False

    def stop(self):
        self.running = False


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
        await network.close()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Gossip monitoring stopped.")
