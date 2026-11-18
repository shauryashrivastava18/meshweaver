
from protocol import create_message, decode_message
from mesh_node import MeshNode


class MeshIntegration:
    def __init__(self):
        self.node = MeshNode()

    def prepare_ping(self):
        return create_message("PING", {
            "node_id": self.node.node_id,
            "host": self.node.host,
            "port": self.node.port
        })

    def process_response(self, response):
        return decode_message(response)


if __name__ == "__main__":
    integration = MeshIntegration()

    ping_message = integration.prepare_ping()

    print("Node Information:")
    print(integration.node.get_node_info())

    print("\nPrepared PING Message:")
    print(ping_message)

    print("\nDecoded PING:")
    print(decode_message(ping_message))
