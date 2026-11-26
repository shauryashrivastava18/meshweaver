from dataclasses import dataclass, field
from datetime import datetime, timezone


@dataclass
class Peer:
    peer_id: str
    host: str
    port: int
    connected: bool = True
    last_seen: str = field(
        default_factory=lambda: datetime.now(
            timezone.utc
        ).isoformat()
    )


class PeerRegistry:
    """Maintain information about connected MeshWeaver peers."""

    def __init__(self):
        self.peers = {}

    def add_peer(self, peer_id, host, port):
        if not peer_id:
            raise ValueError("Peer ID cannot be empty")

        if not isinstance(port, int) or not 1 <= port <= 65535:
            raise ValueError("Invalid peer port")

        peer = Peer(
            peer_id=peer_id,
            host=host,
            port=port
        )

        self.peers[peer_id] = peer

        return peer

    def get_peer(self, peer_id):
        return self.peers.get(peer_id)

    def remove_peer(self, peer_id):
        return self.peers.pop(peer_id, None) is not None

    def update_last_seen(self, peer_id):
        peer = self.get_peer(peer_id)

        if peer:
            peer.last_seen = datetime.now(
                timezone.utc
            ).isoformat()

    def list_peers(self):
        return list(self.peers.values())

    def get_connected_peers(self):
        return [
            peer
            for peer in self.peers.values()
            if peer.connected
        ]

    def count(self):
        return len(self.get_connected_peers())