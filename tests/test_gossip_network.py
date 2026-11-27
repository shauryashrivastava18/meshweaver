
import asyncio

from peer_network import PeerNetwork
from gossip import GossipProtocol


def test_gossip_message_received_by_connected_peer():
    async def run():
        node_a = PeerNetwork("node-A", port=0)
        node_b = PeerNetwork("node-B", port=0)

        gossip_a = GossipProtocol(
            node_id="node-A",
            update_interval=5
        )

        gossip_b = GossipProtocol(
            node_id="node-B",
            update_interval=5
        )

        gossip_a.attach_network(node_a)
        gossip_b.attach_network(node_b)

        try:
            await node_a.start()
            await node_b.start()

            await node_a.connect(
                "node-B",
                "127.0.0.1",
                node_b.port
            )

            resource_data = {
                "cpu_percent": 15.5,
                "ram_percent": 60.2,
                "ram_used_mb": 8000,
                "ram_total_mb": 16000
            }

            message = gossip_a.create_gossip_message(
                resource_data
            )

            await node_a.broadcast("GOSSIP", message)

            for _ in range(30):
                if "node-A" in gossip_b.peer_resources:
                    break
                await asyncio.sleep(0.1)

            assert "node-A" in gossip_b.peer_resources

            received = gossip_b.peer_resources["node-A"]

            assert received["cpu_percent"] == 15.5
            assert received["ram_percent"] == 60.2

        finally:
            await node_a.close()
            await node_b.close()

    asyncio.run(run())
