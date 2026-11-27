
import asyncio
import pytest

from peer_network import PeerNetwork


def test_two_peers_can_connect_and_exchange_messages():
    async def run():
        node_a = PeerNetwork("node-A", port=0)
        node_b = PeerNetwork("node-B", port=0)

        received_messages = []
        message_received = asyncio.Event()

        async def handle_ping(message):
            received_messages.append(message)
            message_received.set()

        node_b.register_handler("PING", handle_ping)

        try:
            await node_a.start()
            await node_b.start()

            # Node A connects to Node B
            connected = await node_a.connect(
                "node-B",
                "127.0.0.1",
                node_b.port
            )

            assert connected is True

            # Node A sends a message to Node B
            await node_a.send(
                "node-B",
                "PING",
                {"text": "Hello from Node A"}
            )

            # Wait for Node B to receive the message
            await asyncio.wait_for(
                message_received.wait(),
                timeout=3
            )

            assert len(received_messages) == 1

            message = received_messages[0]

            assert message["sender"] == "node-A"
            assert message["receiver"] == "node-B"
            assert message["message_type"] == "PING"
            assert message["payload"]["text"] == "Hello from Node A"

        finally:
            await node_a.close()
            await node_b.close()

    asyncio.run(run())


def test_peer_network_rejects_self_connection():
    async def run():
        node = PeerNetwork("node-A")

        with pytest.raises(ValueError):
            await node.connect(
                "node-A",
                "127.0.0.1",
                5001
            )

        await node.close()

    asyncio.run(run())
