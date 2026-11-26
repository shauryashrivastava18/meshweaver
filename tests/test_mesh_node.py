
import unittest
from mesh_node import MeshNode


class TestMeshNode(unittest.TestCase):

    def test_node_initialization(self):
        node = MeshNode()

        self.assertEqual(node.host, "127.0.0.1")
        self.assertEqual(node.port, 5000)

    def test_node_id_exists(self):
        node = MeshNode()

        self.assertIsNotNone(node.node_id)

    def test_get_node_info(self):
        node = MeshNode()
        info = node.get_node_info()

        self.assertIn("node_id", info)
        self.assertIn("host", info)
        self.assertIn("port", info)


if __name__ == "__main__":
    unittest.main()
