
import socket

SERVER_IP = "127.0.0.1"
SERVER_PORT = 12345

def send_message(message):
    client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    client.settimeout(2)

    try:
        client.sendto(message.encode(), (SERVER_IP, SERVER_PORT))
        print(f"Sent: {message!r}")

        try:
            data, address = client.recvfrom(1024)
            print(f"Received: {data.decode()}")

        except socket.timeout:
            print("No response received from server.")

    finally:
        client.close()


if __name__ == "__main__":
    send_message("PING")
    send_message("PING")
    send_message("HELLO")
    send_message("")
