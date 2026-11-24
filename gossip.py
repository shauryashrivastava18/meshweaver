import asyncio
import json
import uuid
from datetime import datetime, timezone
from resource_monitor import get_resource_info


class GossipProtocol:
    def __init__(self, node_id=None, update_interval=5):
        self.node_id = node_id or str(uuid.uuid4())
        self.update_interval = update_interval
        self.latest_message = None

    def create_gossip_message(self, resource_info):
        """Create a message containing this node's resources."""
        message = {
            "message_type": "GOSSIP",
            "node_id": self.node_id,
            "cpu_percent": resource_info["cpu_percent"],
            "ram_percent": resource_info["ram_percent"],
            "ram_used_mb": resource_info["ram_used_mb"],
            "ram_total_mb": resource_info["ram_total_mb"],
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        return message

    async def update_resources(self):
        """Collect resources and create a new Gossip message."""
        resource_info = await asyncio.to_thread(get_resource_info)
        self.latest_message = self.create_gossip_message(resource_info)
        return self.latest_message

    async def run(self):
        """Update and display Gossip information every 5 seconds."""
        print("Gossip monitoring started.")
        print(f"Node ID: {self.node_id}")
        print(f"Update interval: {self.update_interval} seconds")
        print("Press Ctrl+C to stop.\n")

        try:
            while True:
                message = await self.update_resources()

                print("New Gossip message:")
                print(json.dumps(message, indent=4))
                print("-" * 50)

                await asyncio.sleep(self.update_interval)

        except asyncio.CancelledError:
            print("Gossip monitoring stopped.")
            raise


async def main():
    gossip = GossipProtocol(update_interval=5)
    await gossip.run()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nGossip monitoring stopped.")