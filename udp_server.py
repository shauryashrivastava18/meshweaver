import socket

# Create UDP socket
server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Bind server to localhost and port 12345
server_socket.bind(("127.0.0.1", 12345))

print("UDP Server is running...")

while True:
    data, client_address = server_socket.recvfrom(1024)

    message = data.decode()

    print(f"Received from {client_address}: {message}")

    response = "Message received successfully"
    server_socket.sendto(response.encode(), client_address)