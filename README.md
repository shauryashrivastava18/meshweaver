@'
# MeshWeaver
## Zero-Dependency P2P Async Task Broker

MeshWeaver is an asynchronous task management and peer communication system built using Python.

## 1. Advanced Task Management

### Features
- Priority-based task execution
- Configurable concurrent workers
- Delayed task scheduling
- Automatic task retries
- Task timeout handling
- Task cancellation
- Duplicate task prevention
- Task execution history
- Execution statistics
- Result retrieval

## 2. TCP Networking Integration

MeshWeaver supports remote task execution using Python asyncio TCP networking.

### Architecture

```text
Peer A (Client)
       |
       | Serialized Task
       v
TCP Connection
       |
       v
Peer B (Server)
       |
       v
Task Manager
       |
       v
Task Executor
       |
       v
Execution Result
       |
       v
Peer A (Client)
## Gossip Propagation

MeshWeaver includes a GossipRouter for propagating messages between connected peers.

Features:
- Gossip message publishing
- Message ID-based duplicate prevention
- Hop-count limits
- Message expiration and cleanup
- Forwarding messages to connected peers
- Gossip propagation across multiple peers

## Peer Health Monitoring

MeshWeaver includes a PeerMonitor for maintaining peer connectivity.

Features:
- Periodic PING messages
- PONG responses
- Heartbeat timeout detection
- Disconnection of unresponsive peers
- Automatic reconnection attempts
- Configurable heartbeat and reconnection intervals

## Peer Communication Testing

The test suite includes:
- Message serialization tests
- Peer registry tests
- TCP communication tests
- Kademlia message transport tests
- Gossip propagation tests
- Heartbeat monitoring tests
- Three-peer TCP integration tests

Latest verified test result: 48 passed.
