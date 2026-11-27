
from collections import defaultdict


def xor_distance(node_id_a, node_id_b):
    """Calculate XOR distance between two node IDs."""

    for node_id in (node_id_a, node_id_b):
        if not isinstance(node_id, int) or isinstance(node_id, bool):
            raise TypeError("Node IDs must be integers.")

        if node_id < 0:
            raise ValueError("Node IDs must be non-negative.")

    return node_id_a ^ node_id_b


class RoutingTable:
    """Kademlia routing table using XOR-distance buckets."""

    def __init__(self, local_node_id, bucket_size=3, max_peers=None):

        if not isinstance(local_node_id, int) or isinstance(local_node_id, bool):
            raise TypeError("Local node ID must be an integer.")

        if local_node_id < 0:
            raise ValueError("Local node ID must be non-negative.")

        if not isinstance(bucket_size, int) or isinstance(bucket_size, bool):
            raise TypeError("Bucket size must be an integer.")

        if bucket_size <= 0:
            raise ValueError("Bucket size must be positive.")

        if max_peers is not None:
            if not isinstance(max_peers, int) or isinstance(max_peers, bool):
                raise TypeError("max_peers must be an integer.")

            if max_peers <= 0:
                raise ValueError("max_peers must be positive.")

        self.local_node_id = local_node_id
        self.bucket_size = bucket_size
        self.max_peers = max_peers

        self.peers = {}
        self.buckets = defaultdict(dict)

    def _bucket_index(self, node_id):
        distance = xor_distance(self.local_node_id, node_id)

        if distance == 0:
            return None

        return distance.bit_length() - 1

    def add_peer(self, node_id, ip_address, port):
        """Add or update a peer."""

        if not isinstance(node_id, int) or isinstance(node_id, bool):
            raise TypeError("Node ID must be an integer.")

        if node_id < 0:
            raise ValueError("Node ID must be non-negative.")

        if node_id == self.local_node_id:
            return False

        if not isinstance(ip_address, str) or not ip_address.strip():
            raise ValueError("A valid IP address is required.")

        if not isinstance(port, int) or isinstance(port, bool):
            raise TypeError("Port must be an integer.")

        if not 1 <= port <= 65535:
            raise ValueError("Port must be between 1 and 65535.")

        bucket_index = self._bucket_index(node_id)

        # Update an existing peer.
        if node_id in self.peers:
            details = self.peers[node_id]

            details["ip_address"] = ip_address
            details["port"] = port

            self.buckets[bucket_index][node_id] = details

            return True

        # Check optional global capacity.
        if self.max_peers is not None:
            if len(self.peers) >= self.max_peers:
                return False

        bucket = self.buckets[bucket_index]

        if len(bucket) >= self.bucket_size:
            return False

        details = {
            "ip_address": ip_address,
            "port": port
        }

        bucket[node_id] = details
        self.peers[node_id] = details

        return True

    def discover_peer(self, node_id, ip_address, port):
        """Discover and register a new peer."""

        if node_id in self.peers:
            return False

        return self.add_peer(node_id, ip_address, port)

    def remove_peer(self, node_id):
        """Remove a peer from the routing table."""

        if node_id not in self.peers:
            return False

        bucket_index = self._bucket_index(node_id)

        self.buckets[bucket_index].pop(node_id, None)
        self.peers.pop(node_id, None)

        return True

    def get_bucket(self, bucket_index):
        """Return peers from a specific bucket."""

        if not isinstance(bucket_index, int) or isinstance(bucket_index, bool):
            raise TypeError("Bucket index must be an integer.")

        if bucket_index < 0:
            raise ValueError("Bucket index must be non-negative.")

        return dict(self.buckets.get(bucket_index, {}))

    def find_closest_peers(self, target_id, count=3):
        """Find closest peers using XOR distance."""

        if not isinstance(target_id, int) or isinstance(target_id, bool):
            raise TypeError("Target ID must be an integer.")

        if target_id < 0:
            raise ValueError("Target ID must be non-negative.")

        if not isinstance(count, int) or isinstance(count, bool):
            raise TypeError("Count must be an integer.")

        if count <= 0:
            raise ValueError("Count must be positive.")

        return sorted(
            self.peers.items(),
            key=lambda peer: xor_distance(peer[0], target_id)
        )[:count]

    def display_peers(self):
        """Display peers grouped by routing bucket."""

        print("\nKademlia Routing Table")

        if not self.peers:
            print("No peers available.")
            return

        for bucket_index in sorted(self.buckets):

            print(f"\nBucket {bucket_index}:")

            for node_id, details in self.buckets[bucket_index].items():

                distance = xor_distance(
                    self.local_node_id,
                    node_id
                )

                print(
                    f"Node ID: {node_id}, "
                    f"IP: {details['ip_address']}, "
                    f"Port: {details['port']}, "
                    f"XOR Distance: {distance}"
                )
