
import pytest
from message_handler import MessageHandler
from peer_registry import PeerRegistry


@pytest.fixture
def handler():
    registry = PeerRegistry()
    return MessageHandler(registry)


def test_ping_message(handler):
    response = handler.handle_message({"type": "PING"})
    assert response["type"] == "PONG"
    assert response["status"] == "success"


def test_pong_message(handler):
    response = handler.handle_message({"type": "PONG"})
    assert response["status"] == "success"


def test_join_message(handler):
    peer = {
        "node_id": "node-001",
        "host": "127.0.0.1",
        "port": 5001
    }

    response = handler.handle_message({
        "type": "JOIN",
        "peer_info": peer
    })

    assert response["status"] == "success"
    assert handler.peer_registry.get_peer("node-001") == peer


def test_invalid_message(handler):
    response = handler.handle_message("INVALID")
    assert response["status"] == "error"


def test_missing_message_type(handler):
    response = handler.handle_message({})
    assert response["status"] == "error"


def test_unknown_message(handler):
    response = handler.handle_message({"type": "UNKNOWN"})
    assert response["status"] == "error"
