import asyncio

from task_manager import TaskManager
from serializer import serialize_task


def multiply(a, b):
    return a * b


async def slow_task():
    await asyncio.sleep(5)
    return "Finished"


def test_task_submission():
    async def run():
        manager = TaskManager()

        task_data = serialize_task(multiply, (5, 10), {})
        task_id = manager.submit_task(task_data)

        assert task_id is not None

        await manager.wait_for_task(task_id)

        assert manager.get_status(task_id) == "completed"

    asyncio.run(run())


def test_task_result():
    async def run():
        manager = TaskManager()

        task_data = serialize_task(multiply, (5, 10), {})
        task_id = manager.submit_task(task_data)

        await manager.wait_for_task(task_id)

        assert manager.get_result(task_id) == 50

    asyncio.run(run())


def test_task_status():
    async def run():
        manager = TaskManager()

        task_data = serialize_task(multiply, (2, 3), {})
        task_id = manager.submit_task(task_data)

        await manager.wait_for_task(task_id)

        task = manager.get_task(task_id)

        assert task["status"] == "completed"
        assert task["started_at"] is not None
        assert task["finished_at"] is not None

    asyncio.run(run())


def test_duplicate_task_detection():
    async def run():
        manager = TaskManager()

        task_data = serialize_task(multiply, (5, 10), {})

        task1 = manager.submit_task(
            task_data,
            idempotency_key="task-001"
        )

        task2 = manager.submit_task(
            task_data,
            idempotency_key="task-001"
        )

        assert task1 == task2

        await manager.wait_for_task(task1)

        assert len(manager.list_tasks()) == 1

    asyncio.run(run())


def test_task_history():
    async def run():
        manager = TaskManager()

        task_data = serialize_task(multiply, (3, 4), {})
        task_id = manager.submit_task(task_data)

        await manager.wait_for_task(task_id)

        history = manager.get_history(task_id)

        statuses = [event["status"] for event in history]

        assert "pending" in statuses
        assert "running" in statuses
        assert "completed" in statuses

    asyncio.run(run())


def test_task_cancellation():
    async def run():
        manager = TaskManager(task_timeout=10)

        task_data = serialize_task(slow_task, (), {})
        task_id = manager.submit_task(task_data)

        cancelled = await manager.cancel_task(task_id)

        assert cancelled is True
        assert manager.get_status(task_id) == "cancelled"

    asyncio.run(run())


def test_unknown_task():
    manager = TaskManager()

    assert manager.get_status("unknown") is None
    assert manager.get_task("unknown") is None
    assert manager.get_result("unknown") is None
    import asyncio

from task_manager import TaskManager
from serializer import serialize_task


def multiply(a, b):
    return a * b


async def slow_task():
    await asyncio.sleep(5)
    return "Finished"


def test_task_submission():
    async def run():
        manager = TaskManager()
        task_data = serialize_task(multiply, (5, 10), {})
        task_id = manager.submit_task(task_data)

        await manager.wait_for_task(task_id)

        assert manager.get_status(task_id) == "completed"

    asyncio.run(run())


def test_task_result():
    async def run():
        manager = TaskManager()
        task_data = serialize_task(multiply, (5, 10), {})
        task_id = manager.submit_task(task_data)

        await manager.wait_for_task(task_id)

        assert manager.get_result(task_id) == 50

    asyncio.run(run())


def test_task_status():
    async def run():
        manager = TaskManager()
        task_data = serialize_task(multiply, (2, 3), {})
        task_id = manager.submit_task(task_data)

        await manager.wait_for_task(task_id)

        task = manager.get_task(task_id)

        assert task["status"] == "completed"
        assert task["started_at"] is not None
        assert task["finished_at"] is not None

    asyncio.run(run())


def test_duplicate_task_detection():
    async def run():
        manager = TaskManager()
        task_data = serialize_task(multiply, (5, 10), {})

        task1 = manager.submit_task(
            task_data, idempotency_key="task-001"
        )
        task2 = manager.submit_task(
            task_data, idempotency_key="task-001"
        )

        assert task1 == task2

        await manager.wait_for_task(task1)

        assert len(manager.list_tasks()) == 1

    asyncio.run(run())


def test_task_history():
    async def run():
        manager = TaskManager()
        task_data = serialize_task(multiply, (3, 4), {})
        task_id = manager.submit_task(task_data)

        await manager.wait_for_task(task_id)

        history = manager.get_history(task_id)
        statuses = [event["status"] for event in history]

        assert "pending" in statuses
        assert "running" in statuses
        assert "completed" in statuses

    asyncio.run(run())


def test_task_cancellation():
    async def run():
        manager = TaskManager(task_timeout=10)
        task_data = serialize_task(slow_task, (), {})

        task_id = manager.submit_task(task_data)
        cancelled = await manager.cancel_task(task_id)

        assert cancelled is True
        assert manager.get_status(task_id) == "cancelled"

    asyncio.run(run())


def test_unknown_task():
    manager = TaskManager()

    assert manager.get_status("unknown") is None
    assert manager.get_task("unknown") is None
    assert manager.get_result("unknown") is None