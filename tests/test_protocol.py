
import unittest
from protocol import create_message, decode_message


class TestProtocol(unittest.TestCase):

    def test_create_ping_message(self):
        message = create_message("PING")
        self.assertIsInstance(message, bytes)

    def test_decode_ping_message(self):
        message = create_message("PING")
        decoded = decode_message(message)
        self.assertEqual(decoded["type"], "PING")

    def test_message_with_data(self):
        data = {"node_id": "node-123", "port": 5000}
        message = create_message("PING", data)
        decoded = decode_message(message)
        self.assertEqual(decoded["data"], data)


if __name__ == "__main__":
    unittest.main()
