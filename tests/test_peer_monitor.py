import asyncio

from peer_monitor import PeerMonitor


class FakeNetwork:
    def __init__(self):
        self.connections = {}
        self.handlers = {}
        self.sent = []
        self.disconnected = []

    def register_handler(self, message_type, callback):
        self.handlers[message_type] = callback

    async def send(self, peer_id, message_type, payload):
        self.sent.append((peer_id, message_type, payload))

    async def disconnect(self, peer_id):
        self.disconnected.append(peer_id)
        self.connections.pop(peer_id, None)
        return True

    async def connect(self, peer_id, host, port):
        self.connections[peer_id] = object()
        return True


def test_monitor_registers_handlers():
    network = FakeNetwork()
    monitor = PeerMonitor(network)

    assert "PING" in network.handlers
    assert "PONG" in network.handlers


def test_pong_updates_peer_timestamp():
    async def run():
        network = FakeNetwork()
        monitor = PeerMonitor(network)

        await monitor.handle_pong({
            "sender": "peer_B",
            "payload": {"timestamp": 123}
        })

        assert "peer_B" in monitor.last_pong

    asyncio.run(run())


def test_ping_sends_pong():
    async def run():
        network = FakeNetwork()
        network.connections["peer_A"] = object()

        monitor = PeerMonitor(network)

        await monitor.handle_ping({
            "sender": "peer_A",
            "payload": {}
        })

        assert network.sent[0][1] == "PONG"

    asyncio.run(run())


def test_monitor_start_and_stop():
    async def run():
        network = FakeNetwork()

        monitor = PeerMonitor(
            network,
            heartbeat_interval=0.05
        )

        await monitor.start()

        assert monitor.running is True

        await monitor.stop()

        assert monitor.running is False

    asyncio.run(run())


def test_reconnect_known_peer():
    async def run():
        network = FakeNetwork()

        monitor = PeerMonitor(
            network,
            known_peers={
                "peer_B": ("127.0.0.1", 9001)
            },
            heartbeat_interval=0.05
        )

        await monitor.start()

        await asyncio.sleep(0.1)

        await monitor.stop()

        assert "peer_B" in network.connections

    asyncio.run(run())