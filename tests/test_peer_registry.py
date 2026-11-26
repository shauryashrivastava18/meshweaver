
import pytest
from peer_registry import PeerRegistry


def test_add_peer():
    registry = PeerRegistry()

    peer = {
        "node_id": "node-001",
        "host": "127.0.0.1",
        "port": 5001
    }

    assert registry.add_peer(peer) is True
    assert registry.get_peer_count() == 1


def test_get_peer():
    registry = PeerRegistry()

    peer = {
        "node_id": "node-001",
        "host": "127.0.0.1",
        "port": 5001
    }

    registry.add_peer(peer)

    assert registry.get_peer("node-001") == peer


def test_remove_peer():
    registry = PeerRegistry()

    peer = {
        "node_id": "node-001",
        "host": "127.0.0.1",
        "port": 5001
    }

    registry.add_peer(peer)

    assert registry.remove_peer("node-001") is True
    assert registry.get_peer_count() == 0


def test_update_peer():
    registry = PeerRegistry()

    peer = {
        "node_id": "node-001",
        "host": "127.0.0.1",
        "port": 5001
    }

    registry.add_peer(peer)

    assert registry.update_peer(
        "node-001", {"port": 6000}
    ) is True

    assert registry.get_peer("node-001")["port"] == 6000


def test_invalid_peer():
    registry = PeerRegistry()

    with pytest.raises(ValueError):
        registry.add_peer({"host": "127.0.0.1"})
