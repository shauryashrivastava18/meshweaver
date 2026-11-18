import asyncio
import uuid
import heapq

from datetime import datetime, timezone

from executor import execute_task
from serializer import deserialize_result


class TaskManager:
    """
    Advanced MeshWeaver Task Manager.

    Features:
    - Priority-based execution
    - Maximum concurrent execution
    - Delayed task scheduling
    - Automatic retry through executor
    - Task cancellation
    - Idempotency
    - Execution history
    - Execution statistics
    """

    def __init__(
        self,
        max_retries=3,
        retry_delay=1,
        task_timeout=10,
        max_concurrency=4
    ):
        if max_concurrency < 1:
            raise ValueError("max_concurrency must be at least 1")

        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.task_timeout = task_timeout
        self.max_concurrency = max_concurrency

        self.tasks = {}
        self.running_tasks = {}
        self.idempotency_keys = {}
        self.history = []

        self.queue = []
        self.sequence = 0

        self.workers = []
        self.scheduled_handles = {}
        self.completion_futures = {}

        self.closed = False

    def _timestamp(self):
        return datetime.now(timezone.utc).isoformat()

    def _record_event(self, task_id, status):
        self.history.append({
            "task_id": task_id,
            "status": status,
            "timestamp": self._timestamp()
        })

    def _start_workers(self):
        if self.closed:
            raise RuntimeError("TaskManager is closed")

        while len(self.workers) < self.max_concurrency:
            worker = asyncio.create_task(self._worker())
            self.workers.append(worker)

    def submit_task(
        self,
        task_data,
        idempotency_key=None,
        priority=0,
        delay=0
    ):
        """Submit a task with optional priority and scheduling delay."""

        if not isinstance(task_data, bytes):
            raise TypeError("Task data must be bytes")

        if not isinstance(priority, int):
            raise TypeError("Priority must be an integer")

        if delay < 0:
            raise ValueError("Delay cannot be negative")

        if self.closed:
            raise RuntimeError("TaskManager is closed")

        asyncio.get_running_loop()

        if idempotency_key is not None:
            if idempotency_key in self.idempotency_keys:
                return self.idempotency_keys[idempotency_key]

        self._start_workers()

        task_id = str(uuid.uuid4())

        self.tasks[task_id] = {
            "task_id": task_id,
            "status": "pending",
            "priority": priority,
            "result": None,
            "error": None,
            "attempts": 0,
            "created_at": self._timestamp(),
            "started_at": None,
            "finished_at": None,
            "duration_seconds": None
        }

        self.completion_futures[task_id] = (
            asyncio.get_running_loop().create_future()
        )

        if idempotency_key is not None:
            self.idempotency_keys[idempotency_key] = task_id

        self._record_event(task_id, "pending")

        if delay > 0:
            loop = asyncio.get_running_loop()

            handle = loop.call_later(
                delay,
                self._enqueue,
                task_id,
                task_data
            )

            self.scheduled_handles[task_id] = handle
        else:
            self._enqueue(task_id, task_data)

        return task_id

    def _enqueue(self, task_id, task_data):
        """Add a task to the priority queue."""

        task = self.tasks.get(task_id)

        if task is None or task["status"] != "pending":
            return

        self.scheduled_handles.pop(task_id, None)

        self.sequence += 1

        heapq.heappush(
            self.queue,
            (
                -task["priority"],
                self.sequence,
                task_id,
                task_data
            )
        )

    async def _worker(self):
        """Continuously process tasks from the priority queue."""

        while True:
            if not self.queue:
                await asyncio.sleep(0.01)
                continue

            _, _, task_id, task_data = heapq.heappop(self.queue)

            task = self.tasks.get(task_id)

            if task is None or task["status"] != "pending":
                continue

            await self._execute(task_id, task_data)

    async def _execute(self, task_id, task_data):
        """Execute one task and record its result."""

        task = self.tasks[task_id]

        start_time = asyncio.get_running_loop().time()

        task["status"] = "running"
        task["started_at"] = self._timestamp()

        self._record_event(task_id, "running")

        execution = asyncio.create_task(
            execute_task(
                task_data,
                max_retries=self.max_retries,
                retry_delay=self.retry_delay,
                task_timeout=self.task_timeout
            )
        )

        self.running_tasks[task_id] = execution

        try:
            response_data = await execution
            response = deserialize_result(response_data)

            task["attempts"] = response.get("attempts", 0)

            if response["status"] == "success":
                task["status"] = "completed"
                task["result"] = response.get("result")
            else:
                task["status"] = "failed"
                task["error"] = response.get("error")

        except asyncio.CancelledError:
            task["status"] = "cancelled"

        except Exception as error:
            task["status"] = "failed"
            task["error"] = str(error)

        finally:
            task["finished_at"] = self._timestamp()

            task["duration_seconds"] = (
                asyncio.get_running_loop().time() - start_time
            )

            self.running_tasks.pop(task_id, None)

            self._record_event(task_id, task["status"])

            future = self.completion_futures.get(task_id)

            if future is not None and not future.done():
                future.set_result(task.copy())

    def get_status(self, task_id):
        task = self.tasks.get(task_id)
        return task["status"] if task else None

    def get_task(self, task_id):
        task = self.tasks.get(task_id)
        return task.copy() if task else None

    def get_result(self, task_id):
        task = self.tasks.get(task_id)

        if task and task["status"] == "completed":
            return task["result"]

        return None

    async def wait_for_task(self, task_id):
        future = self.completion_futures.get(task_id)

        if future is None:
            return None

        return await asyncio.shield(future)

    async def cancel_task(self, task_id):
        task = self.tasks.get(task_id)

        if task is None:
            return False

        if task["status"] not in ("pending", "running"):
            return False

        handle = self.scheduled_handles.pop(task_id, None)

        if handle is not None:
            handle.cancel()

        execution = self.running_tasks.get(task_id)

        if execution is not None:
            execution.cancel()

        elif task["status"] == "pending":
            task["status"] = "cancelled"
            task["finished_at"] = self._timestamp()

            self._record_event(task_id, "cancelled")

            future = self.completion_futures.get(task_id)

            if future is not None and not future.done():
                future.set_result(task.copy())

        return True

    def get_history(self, task_id=None):
        if task_id is None:
            return [event.copy() for event in self.history]

        return [
            event.copy()
            for event in self.history
            if event["task_id"] == task_id
        ]

    def list_tasks(self):
        return [
            task.copy()
            for task in self.tasks.values()
        ]

    def get_statistics(self):
        """Return task execution statistics."""

        total = len(self.tasks)

        completed = sum(
            task["status"] == "completed"
            for task in self.tasks.values()
        )

        failed = sum(
            task["status"] == "failed"
            for task in self.tasks.values()
        )

        pending = sum(
            task["status"] == "pending"
            for task in self.tasks.values()
        )

        running = sum(
            task["status"] == "running"
            for task in self.tasks.values()
        )

        cancelled = sum(
            task["status"] == "cancelled"
            for task in self.tasks.values()
        )

        return {
            "total": total,
            "completed": completed,
            "failed": failed,
            "pending": pending,
            "running": running,
            "cancelled": cancelled
        }

    async def close(self):
        """Stop workers and cancel unfinished tasks."""

        if self.closed:
            return

        self.closed = True

        for handle in self.scheduled_handles.values():
            handle.cancel()

        self.scheduled_handles.clear()

        for task_id, task in self.tasks.items():
            if task["status"] in ("pending", "running"):
                await self.cancel_task(task_id)

        for worker in self.workers:
            worker.cancel()

        await asyncio.gather(
            *self.workers,
            return_exceptions=True
        )

        self.workers.clear()