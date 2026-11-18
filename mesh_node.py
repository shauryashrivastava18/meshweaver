
import socket
import uuid


class MeshNode:
    def __init__(self, host="127.0.0.1", port=5000):
        self.node_id = str(uuid.uuid4())
        self.host = host
        self.port = port

    def get_node_info(self):
        return {
            "node_id": self.node_id,
            "host": self.host,
            "port": self.port
        }


if __name__ == "__main__":
    node = MeshNode()

    print("Mesh Node Initialized!")
    print(node.get_node_info())
