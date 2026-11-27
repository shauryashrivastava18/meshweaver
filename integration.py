
import asyncio
import uuid

from protocol import create_message, decode_message
from mesh_node import MeshNode
from peer_registry import PeerRegistry
from bootstrap import Bootstrap
from message_handler import MessageHandler
from peer_network import PeerNetwork
from kademlia_network import KademliaNetwork


class MeshIntegration:
    """Integrate MeshNode, TCP networking and Kademlia."""

    def __init__(self, host="127.0.0.1", port=5000):
        self.node = MeshNode(host, port)

        self.peer_registry = PeerRegistry()

        # Convert UUID identity into a stable 128-bit integer.
        self.kademlia_node_id = uuid.UUID(
            self.node.node_id
        ).int

        # TCP peer identity uses the Kademlia integer ID.
        self.peer_network = PeerNetwork(
            peer_id=str(self.kademlia_node_id),
            host=host,
            port=port
        )

        self.kademlia = KademliaNetwork(
            network=self.peer_network,
            node_id=self.kademlia_node_id,
            host=host,
            port=port
        )

        self.bootstrap = Bootstrap(
            self.node,
            self.peer_registry,
            self.kademlia
        )

        self.message_handler = MessageHandler(
            self.peer_registry
        )

        self.started = False

    async def start_async(self, bootstrap_peer=None):
        """Start the node and join the network."""

        if self.started:
            return

        self.node.start()

        try:
            await self.kademlia.start()

            # Keep the actual listening port in node information.
            self.node.port = self.peer_network.port

            if bootstrap_peer is not None:
                await self.bootstrap.join_network_async(
                    bootstrap_peer
                )
            else:
                await self.bootstrap.join_network_async()

            self.started = True

            print("\nMeshWeaver Node Started")
            print(self.node.get_node_info())
            print("Kademlia Node ID:", self.kademlia_node_id)
            print("Listening Port:", self.peer_network.port)

        except Exception:
            await self.peer_network.close()
            self.node.stop()
            raise

    async def stop_async(self):
        """Stop the TCP network and node."""

        if self.started or self.peer_network.server is not None:
            await self.peer_network.close()

        self.node.stop()
        self.started = False

    def start(self):
        """Legacy synchronous startup for existing demonstrations."""

        self.node.start()
        self.bootstrap.join_network()

    def stop(self):
        """Legacy synchronous stop for existing demonstrations."""

        self.node.stop()

    def prepare_ping(self):
        """Prepare the legacy PING protocol message."""

        return create_message("PING", {
            "node_id": self.node.node_id,
            "host": self.node.host,
            "port": self.node.port
        })

    def process_response(self, response):
        """Process a legacy protocol response."""

        decoded = decode_message(response)
        return self.message_handler.handle_message(decoded)

    def get_known_peers(self):
        """Return currently known Kademlia peers."""

        return self.kademlia.routing_table.find_closest_peers(
            self.kademlia_node_id,
            count=20
        )


async def run_node(host="127.0.0.1", port=5000, bootstrap_peer=None):
    """Run one asynchronous MeshWeaver node."""

    integration = MeshIntegration(host, port)

    try:
        await integration.start_async(bootstrap_peer)

        print("\nKnown Kademlia Peers:")
        print(integration.get_known_peers())

        await asyncio.Event().wait()

    finally:
        await integration.stop_async()


if __name__ == "__main__":
    try:
        asyncio.run(run_node())
    except KeyboardInterrupt:
        print("\nMeshWeaver stopped.")
