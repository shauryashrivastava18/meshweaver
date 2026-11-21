
import socket

SERVER_IP = "127.0.0.1"
SERVER_PORT = 12345

def start_client():
    client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    client.settimeout(2)

    print("UDP Client started.")
    print("Type 'exit' to close the client.")

    try:
        while True:
            message = input("\nEnter message: ")

            if message.lower() == "exit":
                print("Closing UDP client...")
                break

            try:
                client.sendto(
                    message.encode(),
                    (SERVER_IP, SERVER_PORT)
                )

                print(f"Sent: {message!r}")

                data, address = client.recvfrom(1024)
                print(f"Server response: {data.decode()}")

            except socket.timeout:
                print("No response received from server.")

            except OSError as error:
                print(f"Communication error: {error}")

    except KeyboardInterrupt:
        print("\nClient interrupted.")

    finally:
        client.close()
        print("UDP Client closed.")


if __name__ == "__main__":
    start_client()
