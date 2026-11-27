
import asyncio
import socket
import json

SERVER_IP = "127.0.0.1"
SERVER_PORT = 12345
SERVER_NODE_ID = 10


class UDPServer(asyncio.DatagramProtocol):

    def __init__(self):
        self.peers = {}

    def connection_made(self, transport):
        self.transport = transport
        print("UDP Server is running...")

    def datagram_received(self, data, addr):
        try:
            message = data.decode().strip()

            # Handle existing PING/PONG communication
            if message.upper() == "PING":
                self.transport.sendto(b"PONG", addr)
                print(f"PING received from {addr}")
                return

            # Handle peer discovery
            request = json.loads(message)

            if request.get("type") == "DISCOVER":
                node_id = request.get("node_id")

                if not isinstance(node_id, int) or isinstance(node_id, bool) or node_id < 0:
                    print("Invalid node ID received.")
                    return

                if node_id == SERVER_NODE_ID:
                    print("Cannot register the server as a peer.")
                    return

                # Register the discovered peer using its actual address
                self.peers[node_id] = {
                    "ip_address": addr[0],
                    "port": addr[1]
                }

                print(f"Peer {node_id} discovered from {addr}")

                # Prepare known peer information
                known_peers = [
                    {
                        "node_id": SERVER_NODE_ID,
                        "ip_address": SERVER_IP,
                        "port": SERVER_PORT
                    }
                ]

                for peer_id, details in self.peers.items():
                    known_peers.append({
                        "node_id": peer_id,
                        "ip_address": details["ip_address"],
                        "port": details["port"]
                    })

                response = {
                    "type": "PEERS",
                    "peers": known_peers
                }

                self.transport.sendto(
                    json.dumps(response).encode(),
                    addr
                )

                print(f"Sent {len(known_peers)} peer records to {addr}")

            else:
                print("Invalid message received.")

        except (UnicodeDecodeError, json.JSONDecodeError):
            print("Invalid message format received.")

        except Exception as error:
            print(f"Communication error: {error}")

    def error_received(self, error):
        print(f"Communication error occurred: {error}")

        if getattr(error, "winerror", None) == 10054:
            print("A UDP client may have closed its connection.")


async def main():
    loop = asyncio.get_running_loop()

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setblocking(False)
    sock.bind((SERVER_IP, SERVER_PORT))

    transport, protocol = await loop.create_datagram_endpoint(
        UDPServer,
        sock=sock
    )

    print(f"Server listening on {SERVER_IP}:{SERVER_PORT}")

    try:
        await asyncio.Future()

    finally:
        transport.close()
        print("UDP Server closed.")


if __name__ == "__main__":
    try:
        asyncio.run(main())

    except KeyboardInterrupt:
        print("\nUDP Server stopped.")
