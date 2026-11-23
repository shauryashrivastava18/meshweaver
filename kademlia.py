def xor_distance(node_id_a, node_id_b):
    """
    Calculate the XOR distance between two Kademlia node IDs.
    """

    if not isinstance(node_id_a, int) or isinstance(node_id_a, bool):
        raise TypeError("Node IDs must be integers.")

    if not isinstance(node_id_b, int) or isinstance(node_id_b, bool):
        raise TypeError("Node IDs must be integers.")

    if node_id_a < 0 or node_id_b < 0:
        raise ValueError("Node IDs must be non-negative.")

    return node_id_a ^ node_id_b


if __name__ == "__main__":

    node_a = 10
    node_b = 12

    distance = xor_distance(node_a, node_b)

    print("Kademlia XOR Distance Calculator")
    print(f"Node A ID: {node_a}")
    print(f"Node B ID: {node_b}")
    print(f"XOR Distance: {distance}")

    # Basic tests
    assert xor_distance(10, 12) == 6
    assert xor_distance(10, 10) == 0
    assert xor_distance(12, 10) == 6

    print("All tests passed!")