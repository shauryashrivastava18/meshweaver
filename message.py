import uuid
import cloudpickle

from datetime import datetime, timezone


SUPPORTED_TYPES = {
    "HELLO",
    "PING",
    "PONG",
    "KAD",
    "GOSSIP",
    "TASK",
    "TASK_RESULT"
}


class Message:
    """Standard message format for MeshWeaver peer communication."""

    def __init__(
        self,
        sender,
        receiver,
        message_type,
        payload
    ):
        if not isinstance(sender, str) or not sender:
            raise ValueError("Sender must be a non-empty string")

        if not isinstance(receiver, str) or not receiver:
            raise ValueError("Receiver must be a non-empty string")

        if message_type not in SUPPORTED_TYPES:
            raise ValueError("Unsupported message type")

        self.message_id = str(uuid.uuid4())
        self.sender = sender
        self.receiver = receiver
        self.message_type = message_type
        self.payload = payload

        self.timestamp = datetime.now(
            timezone.utc
        ).isoformat()

    def to_dict(self):
        return {
            "message_id": self.message_id,
            "sender": self.sender,
            "receiver": self.receiver,
            "message_type": self.message_type,
            "payload": self.payload,
            "timestamp": self.timestamp
        }

    def serialize(self):
        return cloudpickle.dumps(self.to_dict())

    @staticmethod
    def deserialize(data):
        if not isinstance(data, bytes):
            raise TypeError("Message data must be bytes")

        message_data = cloudpickle.loads(data)

        if not isinstance(message_data, dict):
            raise ValueError("Invalid message format")

        required = {
            "message_id",
            "sender",
            "receiver",
            "message_type",
            "payload",
            "timestamp"
        }

        if not required.issubset(message_data):
            raise ValueError("Message fields are missing")

        if message_data["message_type"] not in SUPPORTED_TYPES:
            raise ValueError("Unsupported message type")

        return message_data