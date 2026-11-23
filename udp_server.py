
import asyncio
import socket

# Server configuration
SERVER_IP = "127.0.0.1"
SERVER_PORT = 12345


class UDPServer(asyncio.DatagramProtocol):

    def connection_made(self, transport):
        self.transport = transport
        print("UDP Server is running...")

    def datagram_received(self, data, addr):
        try:
            message = data.decode().strip().upper()
            print(f"Received from {addr}: {message}")

            if message == "PING":
                self.transport.sendto(b"PONG", addr)
                print(f"Sent PONG to {addr}")

            elif message == "":
                print("Empty message received")

            else:
                print("Invalid message received")

        except Exception as error:
            print(f"Communication error: {error}")

    def error_received(self, error):
        print(f"Communication error occurred: {error}")

        if getattr(error, "winerror", None) == 10054:
            print("A UDP client may have closed its connection.")


async def main():
    loop = asyncio.get_running_loop()

    # Create UDP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setblocking(False)

    # Bind socket to configured IP address and port
    sock.bind((SERVER_IP, SERVER_PORT))

    # Create asynchronous UDP server
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
