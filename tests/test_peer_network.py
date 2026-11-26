import asyncio

from peer_network import PeerNetwork


def test_gossip_message_transport():
    async def run_test():
        peer_a = PeerNetwork("peer_A")
        peer_b = PeerNetwork("peer_B")

        received = asyncio.Event()
        messages = []

        async def handler(message):
            messages.append(message)
            received.set()

        peer_b.register_handler("GOSSIP", handler)

        try:
            await peer_a.start()
            await peer_b.start()

            await peer_a.connect("peer_B", "127.0.0.1", peer_b.port)

            await peer_a.send_gossip(
                "peer_B",
                {"content": "Hello from Peer A"}
            )

            await asyncio.wait_for(received.wait(), timeout=3)

            assert messages[0]["sender"] == "peer_A"
            assert messages[0]["payload"]["content"] == "Hello from Peer A"

        finally:
            await peer_a.close()
            await peer_b.close()

    asyncio.run(run_test())


def test_kademlia_message_transport():
    async def run_test():
        peer_a = PeerNetwork("peer_A")
        peer_b = PeerNetwork("peer_B")

        received = asyncio.Event()
        messages = []

        async def handler(message):
            messages.append(message)
            received.set()

        peer_b.register_handler("KAD", handler)

        try:
            await peer_a.start()
            await peer_b.start()

            await peer_a.connect("peer_B", "127.0.0.1", peer_b.port)

            await peer_a.send_kademlia(
                "peer_B",
                {"operation": "FIND_NODE"}
            )

            await asyncio.wait_for(received.wait(), timeout=3)

            assert messages[0]["sender"] == "peer_A"
            assert messages[0]["payload"]["operation"] == "FIND_NODE"

        finally:
            await peer_a.close()
            await peer_b.close()

    asyncio.run(run_test())
