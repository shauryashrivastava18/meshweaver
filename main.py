
from integration import MeshIntegration


def main():
    print("Starting MeshWeaver...")

    integration = MeshIntegration(
        host="127.0.0.1",
        port=5000
    )

    try:
        integration.start()

        print("\nNode Information:")
        print(integration.node.get_node_info())

        print("\nKnown Peers:")
        print(integration.peer_registry.get_all_peers())

        ping_message = integration.prepare_ping()

        print("\nPING Message:")
        print(ping_message)

        decoded_ping = integration.message_handler.handle_message(
            integration.process_response(
                integration.prepare_ping()
            )
        ) if False else integration.message_handler.handle_message(
            {"type": "PING"}
        )

        print("\nPING Response:")
        print(decoded_ping)

    finally:
        integration.stop()
        print("\nMeshWeaver stopped.")


if __name__ == "__main__":
    main()
