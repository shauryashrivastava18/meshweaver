
class TaskRouter:
    """
    Selects the available peer with the lowest CPU utilization.
    """

    def __init__(self):
        self.peers = {}

    def update_peer(self, peer_id, cpu_usage, available=True):
        """Update a peer's CPU usage and availability."""
        self.peers[peer_id] = {
            "cpu_usage": float(cpu_usage),
            "available": bool(available)
        }

    def remove_peer(self, peer_id):
        """Remove a peer from the routing list."""
        self.peers.pop(peer_id, None)

    def select_peer(self):
        """Return the available peer with the lowest CPU usage."""
        available_peers = {
            peer_id: details
            for peer_id, details in self.peers.items()
            if details["available"]
            and 0 <= details["cpu_usage"] <= 100
        }

        if not available_peers:
            raise RuntimeError("No available peers found")

        return min(
            available_peers,
            key=lambda peer_id: available_peers[peer_id]["cpu_usage"]
        )

    def get_peer_load(self, peer_id):
        """Get CPU utilization of a peer."""
        if peer_id not in self.peers:
            raise KeyError(f"Peer {peer_id} not found")

        return self.peers[peer_id]["cpu_usage"]
