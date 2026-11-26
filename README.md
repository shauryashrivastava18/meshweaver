
# MeshWeaver: Zero-Dependency P2P Async Task Broker

## 1. Project Overview

MeshWeaver is a Peer-to-Peer (P2P) asynchronous task broker designed to allow multiple nodes to communicate and share tasks without depending on a central server.

The project is being developed using Python.

## 2. Project Objectives

- Establish communication between multiple nodes.
- Implement asynchronous UDP communication.
- Exchange PING and PONG messages.
- Serialize Python functions and transfer them between nodes.
- Execute tasks remotely and return results.
- Monitor node availability and resource usage.

## 3. Technologies Used

- Python
- Socket Programming
- Asyncio
- JSON
- Unit Testing
- Git and GitHub

## 4. Project Structure

```text
meshweaver/
│
├── tests/
│   ├── __init__.py
│   ├── test_protocol.py
│   ├── test_mesh_node.py
│   ├── test_peer_registry.py
│   └── test_message_handler.py
│
├── protocol.py
├── mesh_node.py
├── integration.py
├── bootstrap.py
├── peer_registry.py
├── message_handler.py
├── main.py
└── README.md
```

## 5. Current Implementation

The following modules have been implemented:

- protocol.py: Creates and decodes messages.
- mesh_node.py: Initializes a mesh node with a unique ID, host and port.
- peer_registry.py: Manages peer information.
- bootstrap.py: Provides a basic network joining workflow.
- message_handler.py: Handles PING, PONG and JOIN messages.
- integration.py: Integrates the backend modules.
- main.py: Starts the MeshWeaver application.

## 6. Testing

Unit tests are written using Python's pytest framework.

To run all tests:

```bash
python -m pytest -v
```

### Current Test Results

- MeshNode tests: 3 passed.
- Peer Registry tests: 5 passed.
- Message Handler tests: 6 passed.
- Total project tests: 47 passed (previously reported).

## 7. How to Run

Run the application using:

```bash
python main.py
```

## 8. Development Status

Week 1 basic modules and initial unit tests have been completed.

Week 2 backend development and basic module integration are in progress.

## 9. Week 2 Backend Progress

### Implemented Modules

- MeshNode lifecycle management.
- Peer Registry for managing peer information.
- Bootstrap module for basic network joining.
- Message Handler for PING, PONG and JOIN messages.
- Integration of backend modules.

### Testing Results

- MeshNode tests: 3 passed.
- Peer Registry tests: 5 passed.
- Message Handler tests: 6 passed.
- Total project tests: 47 passed (previously reported).

### Pending Integration

- Kademlia DHT.
- Gossip Protocol.
- Peer-to-Peer Communication.
- 10-node network discovery testing.

## 10. Backend Architecture

MeshWeaver follows a modular backend architecture where each component
has a specific responsibility.

### 10.1 Node Management

The MeshNode module manages the identity and lifecycle of each node.

- Generates a unique node ID.
- Stores host and port information.
- Supports node initialization.
- Tracks node status.
- Provides node information.

### 10.2 Peer Registry

The PeerRegistry module manages information about known peers.

- Add new peers.
- Remove existing peers.
- Retrieve peer information.
- Update peer details.
- Maintain a collection of known peers.

### 10.3 Bootstrap Management

The Bootstrap module provides the initial network joining workflow.

- Initializes the bootstrap process.
- Handles the basic network joining workflow.
- Registers bootstrap peer information.
- Connects the joining workflow with the peer registry.

### 10.4 Message Handling

The MessageHandler module processes incoming application messages.

Supported message types include:

- PING
- PONG
- JOIN
- FIND_NODE (pending integration)
- STORE (pending integration)
- GOSSIP (pending integration)

### 10.5 Backend Integration

The MeshIntegration module connects the core backend components.

It coordinates node initialization, peer registry,
bootstrap operations and message handling.

## 11. Testing Strategy

The project uses automated tests to verify individual modules.

Testing includes:

- Node initialization and lifecycle testing.
- Peer registration and removal testing.
- Peer information update testing.
- Message validation testing.
- PING and PONG message handling.
- Invalid message handling.
- Backend integration checks.

Run the complete test suite using:

```bash
python -m pytest -v
```

## 12. Future Development

The following features are planned for upcoming development:

1. Kademlia Distributed Hash Table.
2. Dynamic peer discovery.
3. Gossip-based resource sharing.
4. CPU and RAM monitoring.
5. Asynchronous peer-to-peer communication.
6. Task routing based on node resources.
7. Heartbeat monitoring.
8. Secure communication using TLS/SSL.
9. Cryptographic message signatures.
10. Multi-node network testing.

## 13. Backend Module API Reference

### 13.1 MeshNode Class

The MeshNode class represents an individual node in the MeshWeaver network.

Available methods:

- `__init__()` initializes a node.
- `start()` changes the node status to running.
- `stop()` changes the node status to stopped.
- `get_status()` returns the current node status.
- `get_node_info()` returns node identification details.

Example:

```python
from mesh_node import MeshNode

node = MeshNode(host="127.0.0.1", port=5000)

node.start()
print(node.get_node_info())
print(node.get_status())
node.stop()
```

### 13.2 PeerRegistry Class

The PeerRegistry class maintains information about known peers.

Available methods:

- `add_peer()` registers a new peer.
- `remove_peer()` removes an existing peer.
- `get_peer()` retrieves a specific peer.
- `get_all_peers()` returns all registered peers.
- `update_peer()` updates peer information.
- `get_peer_count()` returns the number of registered peers.

### 13.3 Bootstrap Class

The Bootstrap class manages the basic network joining workflow.

Responsibilities:

- Initialize the bootstrap component.
- Identify the local node.
- Accept optional bootstrap peer information.
- Register bootstrap peer information.
- Provide a basic network joining operation.

Available method:

- `join_network()` starts the basic joining workflow.

### 13.4 MessageHandler Class

The MessageHandler class processes application-level messages.

Supported message operations:

- PING: Checks node availability.
- PONG: Handles ping responses.
- JOIN: Registers peer information.
- FIND_NODE: Reserved for Kademlia integration.
- STORE: Reserved for Kademlia integration.
- GOSSIP: Reserved for Gossip integration.

The handler also validates incoming message formats
and reports invalid or unsupported messages.

### 13.5 Integration Workflow

The MeshIntegration class coordinates the core backend modules.

The basic workflow includes:

1. Initialize the MeshNode.
2. Create the PeerRegistry.
3. Initialize the Bootstrap component.
4. Initialize the MessageHandler.
5. Start the node.
6. Prepare application messages.
7. Process messages.
8. Stop the node.

### 13.6 Error Handling

The current backend includes basic validation for:

- Missing message types.
- Invalid message formats.
- Missing peer identifiers.
- Unknown message types.
- Invalid peer registration requests.

### 13.7 Future Improvements

Further development will focus on:

- Actual network-based bootstrap operations.
- Dynamic peer discovery.
- Distributed routing tables.
- Resource-aware task scheduling.
- Improved network failure handling.
- Secure remote task execution.
