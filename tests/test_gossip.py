import asyncio

from gossip import GossipRouter


class FakeNetwork:
    def __init__(self):
        self.connections = {}
        self.handlers = {}
        self.sent = []

    def register_handler(self, message_type, callback):
        self.handlers[message_type] = callback

    async def send_gossip(self, peer_id, payload):
        self.sent.append((peer_id, payload))


def test_gossip_publish():
    async def run():
        network = FakeNetwork()
        network.connections = {
            "peer_B": object(),
            "peer_C": object()
        }

        router = GossipRouter(network)

        message_id = await router.publish("Hello MeshWeaver")

        assert message_id
        assert len(network.sent) == 2

    asyncio.run(run())


def test_gossip_duplicate_prevention():
    async def run():
        network = FakeNetwork()
        router = GossipRouter(network)

        message = {
            "sender": "peer_A",
            "payload": {
                "gossip_id": "message-123",
                "content": "Hello",
                "hops": 4
            }
        }

        first = await router.handle_message(message)
        second = await router.handle_message(message)

        assert first is True
        assert second is False

    asyncio.run(run())


def test_gossip_hop_limit():
    async def run():
        network = FakeNetwork()
        network.connections = {"peer_B": object()}

        router = GossipRouter(network, max_hops=3)

        await router.publish("Hello")

        assert len(network.sent) == 1

    asyncio.run(run())


def test_gossip_statistics():
    network = FakeNetwork()
    router = GossipRouter(network)

    stats = router.get_statistics()

    assert stats["known_messages"] == 0
    assert stats["max_hops"] == 5


def test_invalid_hop_limit():
    try:
        GossipRouter(FakeNetwork(), max_hops=0)
        assert False
    except ValueError:
        assert True