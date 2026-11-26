import asyncio
import time


class PeerMonitor:
    """Monitor peer health and reconnect to known peers."""

    def __init__(
        self,
        network,
        known_peers=None,
        heartbeat_interval=5,
        heartbeat_timeout=10,
        reconnect_interval=5
    ):
        if heartbeat_interval <= 0:
            raise ValueError("Heartbeat interval must be positive")

        if heartbeat_timeout <= 0:
            raise ValueError("Heartbeat timeout must be positive")

        if reconnect_interval <= 0:
            raise ValueError("Reconnect interval must be positive")

        self.network = network
        self.known_peers = known_peers or {}

        self.heartbeat_interval = heartbeat_interval
        self.heartbeat_timeout = heartbeat_timeout
        self.reconnect_interval = reconnect_interval

        self.pending_pings = {}
        self.last_pong = {}
        self.last_reconnect_attempt = {}

        self.running = False
        self.monitor_task = None

        self.network.register_handler("PING", self.handle_ping)
        self.network.register_handler("PONG", self.handle_pong)

    async def handle_ping(self, message):
        sender = message["sender"]

        if sender in self.network.connections:
            await self.network.send(
                sender,
                "PONG",
                {"timestamp": time.time()}
            )

    async def handle_pong(self, message):
        sender = message["sender"]

        self.last_pong[sender] = time.monotonic()
        self.pending_pings.pop(sender, None)

    async def _check_connections(self):
        now = time.monotonic()

        for peer_id in list(self.network.connections):
            pending_since = self.pending_pings.get(peer_id)

            if (
                pending_since is not None
                and now - pending_since > self.heartbeat_timeout
            ):
                await self.network.disconnect(peer_id)
                self.pending_pings.pop(peer_id, None)
                continue

            if pending_since is None:
                try:
                    await self.network.send(
                        peer_id,
                        "PING",
                        {"timestamp": time.time()}
                    )

                    self.pending_pings[peer_id] = now

                except (ConnectionError, OSError):
                    self.pending_pings.pop(peer_id, None)

    async def _reconnect_peers(self):
        now = time.monotonic()

        for peer_id, address in self.known_peers.items():
            if peer_id in self.network.connections:
                continue

            last_attempt = self.last_reconnect_attempt.get(peer_id, 0)

            if now - last_attempt < self.reconnect_interval:
                continue

            self.last_reconnect_attempt[peer_id] = now

            try:
                await self.network.connect(
                    peer_id,
                    address[0],
                    address[1]
                )

            except (ConnectionError, OSError, RuntimeError):
                continue

    async def _monitor_loop(self):
        while self.running:
            await self._check_connections()
            await self._reconnect_peers()

            await asyncio.sleep(self.heartbeat_interval)

    async def start(self):
        if self.running:
            return

        self.running = True

        self.monitor_task = asyncio.create_task(
            self._monitor_loop()
        )

    async def stop(self):
        self.running = False

        if self.monitor_task:
            self.monitor_task.cancel()

            await asyncio.gather(
                self.monitor_task,
                return_exceptions=True
            )

            self.monitor_task = None