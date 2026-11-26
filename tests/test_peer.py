import pytest

from peer import PeerRegistry
from message import Message


def test_peer_registration():
    registry = PeerRegistry()

    registry.add_peer("peer-2", "127.0.0.1", 8001)

    assert registry.count() == 1


def test_peer_retrieval():
    registry = PeerRegistry()

    registry.add_peer("peer-2", "127.0.0.1", 8001)

    assert registry.get_peer("peer-2") is not None


def test_peer_removal():
    registry = PeerRegistry()

    registry.add_peer("peer-2", "127.0.0.1", 8001)

    assert registry.remove_peer("peer-2") is True
    assert registry.count() == 0


def test_message_serialization():
    message = Message(
        "peer-1",
        "peer-2",
        "GOSSIP",
        {"data": "hello"}
    )

    restored = Message.deserialize(message.serialize())

    assert restored["sender"] == "peer-1"
    assert restored["message_type"] == "GOSSIP"
    assert restored["payload"]["data"] == "hello"


def test_invalid_message_type():
    with pytest.raises(ValueError):
        Message(
            "peer-1",
            "peer-2",
            "INVALID",
            {}
        )