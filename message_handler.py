
class MessageHandler:
    def __init__(self, peer_registry):
        self.peer_registry = peer_registry

    def handle_message(self, message):
        if not isinstance(message, dict):
            return {"status": "error", "message": "Invalid message format"}

        message_type = message.get("type")

        if not message_type:
            return {"status": "error", "message": "Message type missing"}

        if message_type == "PING":
            return {
                "status": "success",
                "type": "PONG",
                "message": "Node is alive"
            }

        elif message_type == "PONG":
            return {
                "status": "success",
                "message": "PONG received"
            }

        elif message_type == "JOIN":
            peer_info = message.get("peer_info")

            if not isinstance(peer_info, dict):
                return {"status": "error", "message": "Invalid peer information"}

            try:
                self.peer_registry.add_peer(peer_info)
            except (ValueError, AttributeError):
                return {"status": "error", "message": "Unable to add peer"}

            return {
                "status": "success",
                "message": "Peer joined successfully"
            }

        elif message_type in ("FIND_NODE", "STORE"):
            return {
                "status": "pending",
                "message": "Kademlia handler will be integrated"
            }

        elif message_type == "GOSSIP":
            return {
                "status": "pending",
                "message": "Gossip handler will be integrated"
            }

        return {
            "status": "error",
            "message": "Unknown message type"
        }


if __name__ == "__main__":
    from peer_registry import PeerRegistry

    registry = PeerRegistry()
    handler = MessageHandler(registry)

    response = handler.handle_message({"type": "PING"})

    print("Response:", response)
