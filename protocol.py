
import json


def create_message(message_type, data=None):
    """Create a standard message for node communication."""
    message = {
        "type": message_type,
        "data": data
    }
    return json.dumps(message).encode("utf-8")


def decode_message(raw_message):
    """Decode a received message."""
    return json.loads(raw_message.decode("utf-8"))


# Basic test
if __name__ == "__main__":
    ping = create_message("PING")
    print("Encoded message:", ping)

    decoded = decode_message(ping)
    print("Decoded message:", decoded)
