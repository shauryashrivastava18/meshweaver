import asyncio
import uuid

from datetime import datetime, timezone

from executor import execute_task
from serializer import deserialize_result


class TaskManager:
    """
    Manages task submission, execution, status,
    cancellation, history and result retrieval.
    """

    def __init__(
        self,
        max_retries=3,
        retry_delay=1,
        task_timeout=10
    ):
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.task_timeout = task_timeout

        self.tasks = {}
        self.running_tasks = {}
        self.idempotency_keys = {}

        self.history = []

    def _timestamp(self):
        return datetime.now(timezone.utc).isoformat()

    def _record_event(self, task_id, status):
        self.history.append({
            "task_id": task_id,
            "status": status,
            "timestamp": self._timestamp()
        })

    def submit_task(self, task_data, idempotency_key=None):
        """Submit a task for asynchronous execution."""

        if not isinstance(task_data, bytes):
            raise TypeError("Task data must be bytes")

        if idempotency_key is not None:
            if idempotency_key in self.idempotency_keys:
                return self.idempotency_keys[idempotency_key]

        task_id = str(uuid.uuid4())

        self.tasks[task_id] = {
            "task_id": task_id,
            "status": "pending",
            "result": None,
            "error": None,
            "attempts": 0,
            "created_at": self._timestamp(),
            "started_at": None,
            "finished_at": None,
            "duration_seconds": None
        }

        if idempotency_key is not None:
            self.idempotency_keys[idempotency_key] = task_id

        self._record_event(task_id, "pending")

        running_task = asyncio.create_task(
            self._execute(task_id, task_data)
        )

        self.running_tasks[task_id] = running_task

        return task_id

    async def _execute(self, task_id, task_data):
        """Execute and monitor a submitted task."""

        task = self.tasks[task_id]

        try:
            task["status"] = "running"
            task["started_at"] = self._timestamp()

            self._record_event(task_id, "running")

            start_time = asyncio.get_running_loop().time()

            response_data = await execute_task(
                task_data,
                max_retries=self.max_retries,
                retry_delay=self.retry_delay,
                task_timeout=self.task_timeout
            )

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
            raise

        except Exception as error:
            task["status"] = "failed"
            task["error"] = str(error)

        finally:
            if task["started_at"] is not None:
                task["finished_at"] = self._timestamp()

                task["duration_seconds"] = (
                    asyncio.get_running_loop().time() - start_time
                    if "start_time" in locals()
                    else None
                )

            self._record_event(task_id, task["status"])

            self.running_tasks.pop(task_id, None)

    def get_status(self, task_id):
        """Get the current status of a task."""

        task = self.tasks.get(task_id)

        if task is None:
            return None

        return task["status"]

    def get_task(self, task_id):
        """Retrieve task information."""

        task = self.tasks.get(task_id)

        if task is None:
            return None

        return task.copy()

    def get_result(self, task_id):
        """Retrieve the result of a completed task."""

        task = self.tasks.get(task_id)

        if task is None:
            return None

        if task["status"] == "completed":
            return task["result"]

        return None

    async def cancel_task(self, task_id):
        """Cancel a pending or running task."""

        task = self.tasks.get(task_id)

        if task is None:
            return False

        if task["status"] not in ("pending", "running"):
            return False

        running_task = self.running_tasks.get(task_id)

        if running_task is not None:
            running_task.cancel()

            await asyncio.gather(
                running_task,
                return_exceptions=True
            )

        # Handle cancellation before execution starts.
        if task["status"] in ("pending", "running"):
            task["status"] = "cancelled"
            task["finished_at"] = self._timestamp()
            self._record_event(task_id, "cancelled")

        return True

    async def wait_for_task(self, task_id):
        """Wait until a submitted task finishes."""

        running_task = self.running_tasks.get(task_id)

        if running_task is not None:
            await asyncio.gather(
                running_task,
                return_exceptions=True
            )

        return self.get_task(task_id)

    def get_history(self, task_id=None):
        """Retrieve execution history."""

        if task_id is None:
            return list(self.history)

        return [
            event.copy()
            for event in self.history
            if event["task_id"] == task_id
        ]

    def list_tasks(self):
        """List all registered tasks."""

        return [
            task.copy()
            for task in self.tasks.values()
        ]