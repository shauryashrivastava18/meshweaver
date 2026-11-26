
from protocol import create_message, decode_message
from mesh_node import MeshNode
from peer_registry import PeerRegistry
from bootstrap import Bootstrap
from message_handler import MessageHandler


class MeshIntegration:
    def __init__(self, host="127.0.0.1", port=5000):
        self.node = MeshNode(host, port)

        self.peer_registry = PeerRegistry()

        self.bootstrap = Bootstrap(
            self.node,
            self.peer_registry
        )

        self.message_handler = MessageHandler(
            self.peer_registry
        )

    def start(self):
        self.node.start()
        self.bootstrap.join_network()

    def stop(self):
        self.node.stop()

    def prepare_ping(self):
        return create_message("PING", {
            "node_id": self.node.node_id,
            "host": self.node.host,
            "port": self.node.port
        })

    def process_response(self, response):
        decoded = decode_message(response)
        return self.message_handler.handle_message(decoded)


if __name__ == "__main__":
    integration = MeshIntegration()

    integration.start()

    print("\nNode Information:")
    print(integration.node.get_node_info())

    ping_message = integration.prepare_ping()

    print("\nPrepared PING Message:")
    print(ping_message)

    decoded_ping = decode_message(ping_message)

    print("\nDecoded PING:")
    print(decoded_ping)

    print("\nMessage Handler Response:")
    print(integration.message_handler.handle_message(decoded_ping))

    integration.stop()
