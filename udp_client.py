
import socket
import asyncio


class UDPClientProtocol(asyncio.DatagramProtocol):

    def __init__(self, response_future):
        self.response_future = response_future
        self.transport = None

    def connection_made(self, transport):
        self.transport = transport
        print("UDP client is ready.")

    def datagram_received(self, data, address):
        message = data.decode("utf-8").strip()
        print("Received:", message)

        if message.upper() == "PONG":
            if not self.response_future.done():
                self.response_future.set_result(message)

    def error_received(self, error):
        print("Communication error:", error)
        if not self.response_future.done():
            self.response_future.set_exception(error)

    def connection_lost(self, error):
        if error and not self.response_future.done():
            self.response_future.set_exception(error)


async def main():

    server_ip = input("Enter server IP address: ").strip()

    try:
        server_port = int(input("Enter server port: "))
    except ValueError:
        print("Invalid port number.")
        return

    loop = asyncio.get_running_loop()
    response_future = loop.create_future()
    transport = None

    try:
        transport, protocol = await loop.create_datagram_endpoint(
            lambda: UDPClientProtocol(response_future),
            remote_addr=(server_ip, server_port),
            family=socket.AF_INET
        )

        transport.sendto(b"PING")
        print("Sent: PING")

        try:
            response = await asyncio.wait_for(
                response_future, timeout=3
            )
            print("Server replied:", response)

        except asyncio.TimeoutError:
            print("Timeout: Server did not respond.")

    except OSError as error:
        print("UDP communication failed:", error)

    finally:
        if transport:
            transport.close()


if __name__ == "__main__":
    asyncio.run(main())
