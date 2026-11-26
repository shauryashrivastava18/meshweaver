
def xor_distance(node_id_a, node_id_b):
    """Calculate XOR distance between two node IDs."""

    if not isinstance(node_id_a, int) or isinstance(node_id_a, bool):
        raise TypeError("Node IDs must be integers.")

    if not isinstance(node_id_b, int) or isinstance(node_id_b, bool):
        raise TypeError("Node IDs must be integers.")

    if node_id_a < 0 or node_id_b < 0:
        raise ValueError("Node IDs must be non-negative.")

    return node_id_a ^ node_id_b


class RoutingTable:
    """Store information about known peers."""

    def __init__(self, local_node_id, bucket_size=3):
        self.local_node_id = local_node_id
        self.bucket_size = bucket_size
        self.peers = {}

    def add_peer(self, node_id, ip_address, port):
        """Add a peer to the routing table."""

        if not isinstance(node_id, int) or isinstance(node_id, bool):
            raise TypeError("Node ID must be an integer.")

        if node_id < 0:
            raise ValueError("Node ID must be non-negative.")

        if node_id == self.local_node_id:
            print("Cannot add the local node.")
            return

        if node_id in self.peers:
            print(f"Node {node_id} already exists.")
            return

        if len(self.peers) >= self.bucket_size:
            print("Routing table is full.")
            return

        self.peers[node_id] = {
            "ip_address": ip_address,
            "port": port
        }

        print(f"Peer {node_id} added successfully.")

    def discover_peer(self, node_id, ip_address, port):
        """Discover and add a new peer dynamically."""

        if not isinstance(node_id, int) or isinstance(node_id, bool):
            raise TypeError("Node ID must be an integer.")

        if node_id < 0:
            raise ValueError("Node ID must be non-negative.")

        if not isinstance(ip_address, str) or not ip_address.strip():
            raise ValueError("A valid IP address is required.")

        if not isinstance(port, int) or isinstance(port, bool):
            raise TypeError("Port must be an integer.")

        if not 1 <= port <= 65535:
            raise ValueError("Port must be between 1 and 65535.")

        if node_id == self.local_node_id:
            print("Cannot discover the local node.")
            return False

        if node_id in self.peers:
            print(f"Peer {node_id} is already known.")
            return False

        if len(self.peers) >= self.bucket_size:
            print("Routing table is full. Cannot discover peer.")
            return False

        self.add_peer(node_id, ip_address, port)
        return node_id in self.peers

    def display_peers(self):
        """Display all stored peers."""

        print("\nKademlia Routing Table")

        if not self.peers:
            print("No peers available.")
            return

        for node_id, details in self.peers.items():
            distance = xor_distance(self.local_node_id, node_id)

            print(
                f"Node ID: {node_id}, "
                f"IP: {details['ip_address']}, "
                f"Port: {details['port']}, "
                f"XOR Distance: {distance}"
            )

    def find_closest_peers(self, target_id, count=3):
        """Find the closest peers to a target node ID."""

        if not isinstance(target_id, int) or isinstance(target_id, bool):
            raise TypeError("Target ID must be an integer.")

        if target_id < 0:
            raise ValueError("Target ID must be non-negative.")

        if not isinstance(count, int) or isinstance(count, bool):
            raise TypeError("Count must be an integer.")

        if count <= 0:
            raise ValueError("Count must be positive.")

        closest_peers = sorted(
            self.peers.items(),
            key=lambda peer: xor_distance(peer[0], target_id)
        )

        return closest_peers[:count]


if __name__ == "__main__":

    print("Kademlia DHT Implementation")

    # XOR distance tests
    assert xor_distance(10, 12) == 6
    assert xor_distance(10, 10) == 0
    assert xor_distance(12, 10) == 6

    print("\nXOR distance tests passed!")

    # Create routing table
    routing_table = RoutingTable(local_node_id=10, bucket_size=5)

    # Add initial peers
    routing_table.add_peer(12, "127.0.0.1", 5001)
    routing_table.add_peer(15, "127.0.0.1", 5002)
    routing_table.add_peer(20, "127.0.0.1", 5003)

    # Display initial peers
    routing_table.display_peers()

    # Dynamic peer discovery
    print("\n--- Dynamic Peer Discovery ---")

    result = routing_table.discover_peer(
        25, "127.0.0.1", 5004
    )
    assert result is True

    # Test duplicate peer
    result = routing_table.discover_peer(
        25, "127.0.0.1", 5004
    )
    assert result is False

    # Test local node rejection
    result = routing_table.discover_peer(
        10, "127.0.0.1", 5005
    )
    assert result is False

    print("\nUpdated routing table:")
    routing_table.display_peers()

    # Node lookup
    target_id = 14

    print(f"\nFinding closest peers to target ID: {target_id}")

    closest_peers = routing_table.find_closest_peers(
        target_id, count=3
    )

    for node_id, details in closest_peers:
        distance = xor_distance(node_id, target_id)

        print(
            f"Node ID: {node_id}, "
            f"XOR Distance: {distance}, "
            f"IP: {details['ip_address']}, "
            f"Port: {details['port']}"
        )

    assert closest_peers[0][0] == 15

    print("\nNode lookup tests passed!")
    print("All tests completed successfully!")
