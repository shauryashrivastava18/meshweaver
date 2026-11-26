
class Bootstrap:
    def __init__(self, node, peer_registry):
        self.node = node
        self.peer_registry = peer_registry

    def join_network(self, bootstrap_peer=None):
        if bootstrap_peer is None:
            print("Starting as the first node in the network.")
            return True

        if bootstrap_peer["node_id"] == self.node.node_id:
            print("A node cannot connect to itself.")
            return False

        self.peer_registry.add_peer(bootstrap_peer)

        print(
            f"Node {self.node.node_id} joined "
            f"through {bootstrap_peer['node_id']}"
        )

        return True


if __name__ == "__main__":
    from mesh_node import MeshNode
    from peer_registry import PeerRegistry

    node = MeshNode(port=5001)
    registry = PeerRegistry()

    bootstrap = Bootstrap(node, registry)

    bootstrap.join_network()

    print("Known Peers:", registry.get_all_peers())
