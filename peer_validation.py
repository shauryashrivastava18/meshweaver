"""Validation helpers for MeshWeaver peer connection details."""


def validate_peer_info(peer_info):
    """Check that peer info has a node ID, host, and valid port."""
    if not isinstance(peer_info, dict):
        raise ValueError("Peer information must be a dictionary")

    node_id = peer_info.get("node_id")
    if not isinstance(node_id, str) or not node_id.strip():
        raise ValueError("Peer node_id must be a non-empty string")

    host = peer_info.get("host")
    if not isinstance(host, str) or not host.strip():
        raise ValueError("Peer host must be a non-empty string")

    port = peer_info.get("port")
    if (
        isinstance(port, bool)
        or not isinstance(port, int)
        or not 1 <= port <= 65535
    ):
        raise ValueError("Peer port must be an integer between 1 and 65535")

    return True