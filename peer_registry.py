
class PeerRegistry:
    def __init__(self):
        self.peers = {}

    def add_peer(self, peer_info):
        node_id = peer_info.get("node_id")

        if not node_id:
            raise ValueError("Peer node_id is required")

        self.peers[node_id] = peer_info
        return True

    def remove_peer(self, node_id):
        if node_id in self.peers:
            del self.peers[node_id]
            return True

        return False

    def get_peer(self, node_id):
        return self.peers.get(node_id)

    def get_all_peers(self):
        return list(self.peers.values())

    def update_peer(self, node_id, updated_info):
        if node_id not in self.peers:
            return False

        self.peers[node_id].update(updated_info)
        return True

    def get_peer_count(self):
        return len(self.peers)


if __name__ == "__main__":
    registry = PeerRegistry()

    peer = {
        "node_id": "node-001",
        "host": "127.0.0.1",
        "port": 5001
    }

    registry.add_peer(peer)

    print("All Peers:", registry.get_all_peers())
    print("Peer Count:", registry.get_peer_count())
