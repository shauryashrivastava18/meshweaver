import asyncio
import pytest

from task_manager import TaskManager
from serializer import serialize_task


# Shared test variables
priority_execution_order = []

active_tasks = 0
maximum_active_tasks = 0


# Test functions
def multiply(a, b):
    return a * b


async def slow_task():
    await asyncio.sleep(5)
    return "Finished"


async def record_priority(value):
    priority_execution_order.append(value)
    return value


async def track_concurrency():
    global active_tasks, maximum_active_tasks

    active_tasks += 1

    maximum_active_tasks = max(
        maximum_active_tasks,
        active_tasks
    )

    try:
        await asyncio.sleep(0.05)
        return "done"
    finally:
        active_tasks -= 1


# 1. Basic task submission
def test_task_submission():
    async def run():
        manager = TaskManager()

        task_id = manager.submit_task(
            serialize_task(multiply, (5, 10), {})
        )

        await manager.wait_for_task(task_id)

        assert manager.get_status(task_id) == "completed"

        await manager.close()

    asyncio.run(run())


# 2. Task result
def test_task_result():
    async def run():
        manager = TaskManager()

        task_id = manager.submit_task(
            serialize_task(multiply, (5, 10), {})
        )

        await manager.wait_for_task(task_id)

        assert manager.get_result(task_id) == 50

        await manager.close()

    asyncio.run(run())


# 3. Task status and timestamps
def test_task_status():
    async def run():
        manager = TaskManager()

        task_id = manager.submit_task(
            serialize_task(multiply, (2, 3), {})
        )

        await manager.wait_for_task(task_id)

        task = manager.get_task(task_id)

        assert task["status"] == "completed"
        assert task["started_at"] is not None
        assert task["finished_at"] is not None

        await manager.close()

    asyncio.run(run())


# 4. Duplicate task detection
def test_duplicate_task_detection():
    async def run():
        manager = TaskManager()

        data = serialize_task(multiply, (5, 10), {})

        task1 = manager.submit_task(
            data,
            idempotency_key="task-001"
        )

        task2 = manager.submit_task(
            data,
            idempotency_key="task-001"
        )

        assert task1 == task2

        await manager.wait_for_task(task1)

        assert len(manager.list_tasks()) == 1

        await manager.close()

    asyncio.run(run())


# 5. Task execution history
def test_task_history():
    async def run():
        manager = TaskManager()

        task_id = manager.submit_task(
            serialize_task(multiply, (3, 4), {})
        )

        await manager.wait_for_task(task_id)

        statuses = [
            event["status"]
            for event in manager.get_history(task_id)
        ]

        assert "pending" in statuses
        assert "running" in statuses
        assert "completed" in statuses

        await manager.close()

    asyncio.run(run())


# 6. Task cancellation
def test_task_cancellation():
    async def run():
        manager = TaskManager()

        task_id = manager.submit_task(
            serialize_task(slow_task, (), {})
        )

        cancelled = await manager.cancel_task(task_id)

        assert cancelled is True
        assert manager.get_status(task_id) == "cancelled"

        await manager.close()

    asyncio.run(run())


# 7. Unknown task handling
def test_unknown_task():
    manager = TaskManager()

    assert manager.get_status("unknown") is None
    assert manager.get_task("unknown") is None
    assert manager.get_result("unknown") is None


# 8. Priority execution
def test_priority_execution():
    async def run():
        priority_execution_order.clear()

        manager = TaskManager(max_concurrency=1)

        low = manager.submit_task(
            serialize_task(record_priority, ("low",), {}),
            priority=1
        )

        high = manager.submit_task(
            serialize_task(record_priority, ("high",), {}),
            priority=10
        )

        medium = manager.submit_task(
            serialize_task(record_priority, ("medium",), {}),
            priority=5
        )

        await asyncio.gather(
            manager.wait_for_task(low),
            manager.wait_for_task(high),
            manager.wait_for_task(medium)
        )

        assert priority_execution_order == [
            "high",
            "medium",
            "low"
        ]

        await manager.close()

    asyncio.run(run())


# 9. Delayed task execution
def test_delayed_task_execution():
    async def run():
        manager = TaskManager()

        task_id = manager.submit_task(
            serialize_task(multiply, (4, 5), {}),
            delay=0.1
        )

        assert manager.get_status(task_id) == "pending"

        await manager.wait_for_task(task_id)

        assert manager.get_result(task_id) == 20

        await manager.close()

    asyncio.run(run())


# 10. Maximum concurrency
def test_maximum_concurrency():
    async def run():
        global active_tasks, maximum_active_tasks

        active_tasks = 0
        maximum_active_tasks = 0

        manager = TaskManager(max_concurrency=2)

        task_ids = [
            manager.submit_task(
                serialize_task(track_concurrency, (), {})
            )
            for _ in range(6)
        ]

        await asyncio.gather(
            *(
                manager.wait_for_task(task_id)
                for task_id in task_ids
            )
        )

        assert maximum_active_tasks <= 2
        assert maximum_active_tasks == 2

        await manager.close()

    asyncio.run(run())


# 11. Execution statistics
def test_execution_statistics():
    async def run():
        manager = TaskManager()

        task_id = manager.submit_task(
            serialize_task(multiply, (5, 5), {})
        )

        await manager.wait_for_task(task_id)

        stats = manager.get_statistics()

        assert stats["total"] == 1
        assert stats["completed"] == 1
        assert stats["failed"] == 0
        assert stats["pending"] == 0

        await manager.close()

    asyncio.run(run())


# 12. Cancel scheduled task
def test_cancel_scheduled_task():
    async def run():
        manager = TaskManager()

        task_id = manager.submit_task(
            serialize_task(multiply, (5, 5), {}),
            delay=5
        )

        result = await manager.cancel_task(task_id)

        assert result is True
        assert manager.get_status(task_id) == "cancelled"

        await manager.close()

    asyncio.run(run())


# 13. Invalid concurrency
def test_invalid_concurrency():
    with pytest.raises(ValueError):
        TaskManager(max_concurrency=0)