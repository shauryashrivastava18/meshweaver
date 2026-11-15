
from mesh_node import MeshNode


def main():
    print("Starting MeshWeaver...")

    node = MeshNode(host="127.0.0.1", port=5000)

    print("Node is ready!")
    print("Node Information:")
    print(node.get_node_info())


if __name__ == "__main__":
    main()
