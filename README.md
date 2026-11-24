
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
