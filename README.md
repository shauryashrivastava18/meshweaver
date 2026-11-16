
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
│   └── test_mesh_node.py
│
├── protocol.py
├── mesh_node.py
├── integration.py
├── main.py
└── README.md
```

## 5. Current Implementation

The following basic modules have been implemented:

- protocol.py: Creates and decodes messages.
- mesh_node.py: Initializes a mesh node with a unique ID, host and port.
- main.py: Starts the MeshWeaver application.
- integration.py: Prepares PING messages and processes responses.

## 6. Testing

Unit tests are written using Python's unittest framework.

To run all tests:

```bash
python -m unittest discover -s tests -v
```

### Current Test Results

- Protocol tests: 3 passed.
- Mesh Node tests: 3 passed.
- Total: 6 tests passed.

## 7. How to Run

Run the application using:

```bash
python main.py
```

## 8. Development Status

Week 1 basic modules and initial unit tests have been completed.

UDP communication, remote task execution and further integration are still under development.
