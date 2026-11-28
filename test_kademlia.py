
import unittest

from kademlia import xor_distance, RoutingTable


class TestXORDistance(unittest.TestCase):

    def test_xor_distance(self):
        self.assertEqual(xor_distance(10, 12), 6)

    def test_same_node_distance(self):
        self.assertEqual(xor_distance(10, 10), 0)

    def test_negative_node_id(self):
        with self.assertRaises(ValueError):
            xor_distance(-1, 10)

    def test_invalid_node_id(self):
        with self.assertRaises(TypeError):
            xor_distance("10", 12)

    def test_boolean_node_id(self):
        with self.assertRaises(TypeError):
            xor_distance(True, 10)


class TestRoutingTable(unittest.TestCase):

    def setUp(self):
        self.table = RoutingTable(local_node_id=10, bucket_size=3)

    def test_add_peer(self):
        self.table.add_peer(12, "127.0.0.1", 5001)
        self.assertIn(12, self.table.peers)

    def test_reject_local_node(self):
        self.table.add_peer(10, "127.0.0.1", 5001)
        self.assertNotIn(10, self.table.peers)

    def test_reject_duplicate_peer(self):
        self.table.add_peer(12, "127.0.0.1", 5001)
        self.table.add_peer(12, "127.0.0.1", 5001)
        self.assertEqual(len(self.table.peers), 1)

    def test_routing_table_capacity(self):
        self.table.add_peer(12, "127.0.0.1", 5001)
        self.table.add_peer(15, "127.0.0.1", 5002)
        self.table.add_peer(20, "127.0.0.1", 5003)
        self.table.add_peer(25, "127.0.0.1", 5004)

        self.assertEqual(len(self.table.peers), 3)
        self.assertNotIn(25, self.table.peers)

    def test_dynamic_peer_discovery(self):
        result = self.table.discover_peer(
            15, "127.0.0.1", 5002
        )

        self.assertTrue(result)
        self.assertIn(15, self.table.peers)

    def test_duplicate_peer_discovery(self):
        self.table.discover_peer(15, "127.0.0.1", 5002)

        result = self.table.discover_peer(
            15, "127.0.0.1", 5002
        )

        self.assertFalse(result)
        self.assertEqual(len(self.table.peers), 1)

    def test_invalid_port(self):
        with self.assertRaises(ValueError):
            self.table.discover_peer(
                15, "127.0.0.1", 70000
            )

    def test_invalid_ip_address(self):
        with self.assertRaises(ValueError):
            self.table.discover_peer(
                15, "", 5002
            )

    def test_find_closest_peers(self):
        self.table.add_peer(12, "127.0.0.1", 5001)
        self.table.add_peer(15, "127.0.0.1", 5002)
        self.table.add_peer(20, "127.0.0.1", 5003)

        closest = self.table.find_closest_peers(14, count=3)

        self.assertEqual(
            [peer[0] for peer in closest],
            [15, 12, 20]
        )

    def test_invalid_lookup_count(self):
        with self.assertRaises(ValueError):
            self.table.find_closest_peers(14, count=0)


if __name__ == "__main__":
    unittest.main(verbosity=2)
