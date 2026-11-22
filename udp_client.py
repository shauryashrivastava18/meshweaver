
import socket

SERVER_IP = "127.0.0.1"
SERVER_PORT = 12345

MAX_RETRIES = 3
TIMEOUT = 2


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

            if attempt < MAX_RETRIES:
                print("Retrying...")
            else:
                print("Maximum retries reached.")


def start_client():
    client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    client.settimeout(TIMEOUT)

    print("UDP Client started.")
    print("Type 'exit' to close the client.")

    try:
        while True:
            message = input("\nEnter message: ")

            if message.lower() == "exit":
                print("Closing UDP client...")
                break

            send_message(client, message)

    except KeyboardInterrupt:
        print("\nClient interrupted.")

    finally:
        client.close()
        print("UDP Client closed.")


if __name__ == "__main__":
    start_client()
