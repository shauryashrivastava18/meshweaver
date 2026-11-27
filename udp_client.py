
import socket
import json

from kademlia import RoutingTable

SERVER_IP = "127.0.0.1"
SERVER_PORT = 12345

NODE_ID = 30

MAX_RETRIES = 3
TIMEOUT = 2


# Create a routing table for this client
routing_table = RoutingTable(local_node_id=NODE_ID, bucket_size=10)


def discover_peers(client):
    request = {
        "type": "DISCOVER",
        "node_id": NODE_ID
    }

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            client.sendto(
                json.dumps(request).encode(),
                (SERVER_IP, SERVER_PORT)
            )

            print(f"Discovery request sent. Attempt {attempt}")

            data, address = client.recvfrom(4096)
            response = json.loads(data.decode())

            if response.get("type") == "PEERS":
                peers = response.get("peers", [])

                print("\nDiscovered Peers:")

                for peer in peers:
                    node_id = peer["node_id"]
                    ip_address = peer["ip_address"]
                    port = peer["port"]

                    print(
                        f"Node ID: {node_id}, "
                        f"IP: {ip_address}, "
                        f"Port: {port}"
                    )

                    # Add discovered peer to Kademlia routing table
                    if node_id != NODE_ID:
                        added = routing_table.discover_peer(
                            node_id,
                            ip_address,
                            port
                        )

                        if added:
                            print(f"Node {node_id} added to routing table.")

                print("\nUpdated Kademlia Routing Table:")
                routing_table.display_peers()

                return

            print("Unexpected server response.")

        except socket.timeout:
            print("No response received.")

            if attempt < MAX_RETRIES:
                print("Retrying...")

        except (OSError, json.JSONDecodeError, KeyError, TypeError) as error:
            print(f"Communication error: {error}")
            return

    print("Peer discovery failed after maximum retries.")


def send_message(client, message):
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            client.sendto(
                message.encode(),
                (SERVER_IP, SERVER_PORT)
            )

            print(f"Sent: {message!r} (Attempt {attempt})")

            data, address = client.recvfrom(1024)
            print(f"Server response: {data.decode()}")
            return

        except socket.timeout:
            print("No response received.")

            if attempt < MAX_RETRIES:
                print("Retrying...")
            else:
                print("Maximum retries reached.")

        except OSError as error:
            print(f"Communication error: {error}")
            return


def start_client():
    client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    client.settimeout(TIMEOUT)

    print("UDP Client started.")
    print("Commands: PING, DISCOVER, EXIT")

    try:
        while True:
            message = input("\nEnter command: ").strip()

            if message.upper() == "EXIT":
                print("Closing UDP client...")
                break

            elif message.upper() == "DISCOVER":
                discover_peers(client)

            elif message.upper() == "PING":
                send_message(client, "PING")

            else:
                print("Invalid command. Try PING, DISCOVER or EXIT.")

    except KeyboardInterrupt:
        print("\nClient interrupted.")

    finally:
        client.close()
        print("UDP Client closed.")


if __name__ == "__main__":
    start_client()
