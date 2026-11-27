
import pytest

from kademlia import xor_distance, RoutingTable


def test_xor_distance():
    assert xor_distance(10, 12) == 6
    assert xor_distance(10, 10) == 0
    assert xor_distance(12, 10) == 6


def test_xor_distance_invalid_type():
    with pytest.raises(TypeError):
        xor_distance("10", 12)


def test_xor_distance_negative():
    with pytest.raises(ValueError):
        xor_distance(-1, 12)


def test_add_peer():
    table = RoutingTable(local_node_id=10, bucket_size=5)

    result = table.add_peer(12, "127.0.0.1", 5001)

    assert result is True
    assert 12 in table.peers


def test_discover_peer():
    table = RoutingTable(local_node_id=10, bucket_size=5)

    result = table.discover_peer(12, "127.0.0.1", 5001)

    assert result is True
    assert 12 in table.peers


def test_duplicate_peer():
    table = RoutingTable(local_node_id=10, bucket_size=5)

    table.discover_peer(12, "127.0.0.1", 5001)

    result = table.discover_peer(12, "127.0.0.1", 5001)

    assert result is False


def test_local_node_rejected():
    table = RoutingTable(local_node_id=10, bucket_size=5)

    result = table.discover_peer(10, "127.0.0.1", 5001)

    assert result is False


def test_find_closest_peers():
    table = RoutingTable(local_node_id=10, bucket_size=5)

    table.add_peer(12, "127.0.0.1", 5001)
    table.add_peer(15, "127.0.0.1", 5002)
    table.add_peer(20, "127.0.0.1", 5003)

    closest = table.find_closest_peers(14, count=3)

    assert closest[0][0] == 15


def test_routing_table_capacity():
    table = RoutingTable(
        local_node_id=10,
        bucket_size=3,
        max_peers=1
    )

    table.add_peer(12, "127.0.0.1", 5001)

    result = table.discover_peer(15, "127.0.0.1", 5002)

    assert result is False
    assert len(table.peers) == 1


def test_peers_are_stored_in_different_buckets():
    table = RoutingTable(local_node_id=10, bucket_size=3)

    table.add_peer(11, "127.0.0.1", 5001)
    table.add_peer(8, "127.0.0.1", 5002)
    table.add_peer(14, "127.0.0.1", 5003)

    assert len(table.get_bucket(0)) == 1
    assert len(table.get_bucket(1)) == 1
    assert len(table.get_bucket(2)) == 1


def test_remove_peer():
    table = RoutingTable(local_node_id=10, bucket_size=3)

    table.add_peer(12, "127.0.0.1", 5001)

    assert table.remove_peer(12) is True
    assert 12 not in table.peers


def test_update_existing_peer():
    table = RoutingTable(local_node_id=10, bucket_size=3)

    table.add_peer(12, "127.0.0.1", 5001)
    table.add_peer(12, "127.0.0.2", 6001)

    assert table.peers[12]["ip_address"] == "127.0.0.2"
    assert table.peers[12]["port"] == 6001
