
class Bootstrap:
    """Manage MeshWeaver network joining through a bootstrap peer."""

    def __init__(self, node, peer_registry, kademlia_network=None):
        self.node = node
        self.peer_registry = peer_registry
        self.kademlia_network = kademlia_network

    def join_network(self, bootstrap_peer=None):
        """Legacy synchronous registration method."""

        if bootstrap_peer is None:
            print("Starting as the first node in the network.")
            return True

        if not isinstance(bootstrap_peer, dict):
            raise ValueError("Invalid bootstrap peer information")

        if bootstrap_peer.get("node_id") == self.node.node_id:
            print("A node cannot connect to itself.")
            return False

        self.peer_registry.add_peer(bootstrap_peer)

        print(
            f"Node {self.node.node_id} joined "
            f"through {bootstrap_peer['node_id']}"
        )

        return True

    async def join_network_async(self, bootstrap_peer=None):
        """Join an existing network using an actual TCP connection."""

        if self.kademlia_network is None:
            raise RuntimeError("KademliaNetwork is not configured")

        if bootstrap_peer is None:
            print("Starting as the first node in the network.")
            return True

        if not isinstance(bootstrap_peer, dict):
            raise ValueError("Invalid bootstrap peer information")

        required = ("node_id", "host", "port")

        if not all(key in bootstrap_peer for key in required):
            raise ValueError("Bootstrap peer needs node_id, host and port")

        bootstrap_id = bootstrap_peer["node_id"]

        if not isinstance(bootstrap_id, int) or isinstance(bootstrap_id, bool):
            raise ValueError("Bootstrap node_id must be an integer")

        if bootstrap_id == self.kademlia_network.node_id:
            raise ValueError("A node cannot connect to itself")

        host = bootstrap_peer["host"]
        port = bootstrap_peer["port"]

        if not isinstance(host, str) or not host.strip():
            raise ValueError("Invalid bootstrap host")

        if not isinstance(port, int) or isinstance(port, bool):
            raise ValueError("Invalid bootstrap port")

        if not 1 <= port <= 65535:
            raise ValueError("Bootstrap port must be between 1 and 65535")

        await self.kademlia_network.join(
            bootstrap_host=host,
            bootstrap_port=port,
            bootstrap_id=bootstrap_id
        )

        peer_info = {
            "node_id": str(bootstrap_id),
            "host": host,
            "port": port
        }

        self.peer_registry.add_peer(peer_info)

        print(
            f"Node {self.kademlia_network.node_id} joined "
            f"through {bootstrap_id}"
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
