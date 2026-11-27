
import asyncio

from integration import MeshIntegration


async def main():
    total_nodes = 10
    nodes = []

    try:
        print("Starting MeshWeaver 10-node cluster...")

        # Start bootstrap node.
        bootstrap = MeshIntegration(
            host="127.0.0.1",
            port=0
        )

        await bootstrap.start_async()
        nodes.append(bootstrap)

        bootstrap_info = {
            "node_id": bootstrap.kademlia_node_id,
            "host": "127.0.0.1",
            "port": bootstrap.peer_network.port
        }

        print("\nBootstrap node started:", bootstrap_info)

        # Start remaining nodes.
        for index in range(1, total_nodes):
            node = MeshIntegration(
                host="127.0.0.1",
                port=0
            )

            await node.start_async(
                bootstrap_peer=bootstrap_info
            )

            nodes.append(node)

            await asyncio.sleep(0.2)

            print(
                f"Node {index + 1}/{total_nodes} joined. "
                f"Known peers: "
                f"{len(node.kademlia.routing_table.peers)}"
            )

        print("\nAll 10 nodes started.")
        print("Waiting 7 seconds for Gossip updates...")

        # Allow the 5-second Gossip cycle to run.
        await asyncio.sleep(15)

        print("\n========== CLUSTER SUMMARY ==========")

        for index, node in enumerate(nodes, start=1):
            peers = node.kademlia.routing_table.peers
            resources = node.gossip.peer_resources

            print(f"\nNode {index}")
            print("Node ID:", node.kademlia_node_id)
            print("Port:", node.peer_network.port)
            print("Known Kademlia peers:", len(peers))
            print("Gossip updates received:", len(resources))

            for peer_id, info in resources.items():
                print(
                    f"  Peer {peer_id}: "
                    f"CPU={info['cpu_percent']}%, "
                    f"RAM={info['ram_percent']}%"
                )

        print("\n10-node cluster test finished.")

    finally:
        for node in reversed(nodes):
            await node.stop_async()

        print("\nAll nodes stopped.")


if __name__ == "__main__":
    asyncio.run(main())
