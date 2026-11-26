import asyncio

from peer_network import PeerNetwork
from gossip import GossipRouter


def test_gossip_propagates_across_three_real_peers():
    async def run():
        peer_a = PeerNetwork("peer_A")
        peer_b = PeerNetwork("peer_B")
        peer_c = PeerNetwork("peer_C")

        router_a = GossipRouter(peer_a)
        router_b = GossipRouter(peer_b)
        router_c = GossipRouter(peer_c)

        try:
            await peer_a.start()
            await peer_b.start()
            await peer_c.start()

            # Create a three-peer chain: A -> B -> C
            await peer_a.connect(
                "peer_B",
                "127.0.0.1",
                peer_b.port
            )

            await peer_b.connect(
                "peer_C",
                "127.0.0.1",
                peer_c.port
            )

            # Allow connections to establish.
            await asyncio.sleep(0.2)

            # Publish a message from peer A.
            message_id = await router_a.publish(
                "Hello from peer A"
            )

            async def wait_for_delivery():
                while message_id not in router_c.seen_messages:
                    await asyncio.sleep(0.05)

            await asyncio.wait_for(
                wait_for_delivery(),
                timeout=3
            )

            assert message_id in router_b.seen_messages
            assert message_id in router_c.seen_messages

        finally:
            await peer_a.close()
            await peer_b.close()
            await peer_c.close()

    asyncio.run(run())