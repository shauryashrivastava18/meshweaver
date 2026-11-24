
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

    def display_peers(self):
        """Display all stored peers."""

        print("\nKademlia Routing Table")

        if not self.peers:
            print("No peers available.")
            return

        for node_id, details in self.peers.items():
            distance = xor_distance(
                self.local_node_id, node_id
            )

            print(
                f"Node ID: {node_id}, "
                f"IP: {details['ip_address']}, "
                f"Port: {details['port']}, "
                f"XOR Distance: {distance}"
            )


if __name__ == "__main__":

    print("Kademlia XOR Distance Calculator")

    assert xor_distance(10, 12) == 6
    assert xor_distance(10, 10) == 0
    assert xor_distance(12, 10) == 6

    print("XOR distance tests passed!")

    # Create a routing table for local node 10
    routing_table = RoutingTable(local_node_id=10)

    # Add three peers
    routing_table.add_peer(12, "127.0.0.1", 5001)
    routing_table.add_peer(15, "127.0.0.1", 5002)
    routing_table.add_peer(20, "127.0.0.1", 5003)

    # Try adding a fourth peer
    routing_table.add_peer(25, "127.0.0.1", 5004)

    # Display stored peers
    routing_table.display_peers()

    print("\nAll tests completed!")
