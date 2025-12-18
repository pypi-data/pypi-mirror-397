"""
MedhaOne Access Control - Background Task Manager

Handles background processing for auto-recalculation and other async tasks.
Allows CRUD operations to return immediately while processing happens in background.

All parameters are configurable via LibraryConfig:
- background_workers: Number of worker threads (default: 5)
- background_queue_size: Maximum queue size (default: 10000)
- background_shutdown_timeout: Graceful shutdown timeout (default: 30.0)
- background_worker_timeout: Worker poll timeout (default: 1.0)
- task_cleanup_max_age_hours: Task history retention (default: 24)
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Callable, TYPE_CHECKING
from datetime import datetime, timezone
from asyncio import Queue, Task
from enum import Enum
import traceback

if TYPE_CHECKING:
    from .config import LibraryConfig

logger = logging.getLogger(__name__)


class TaskPriority(Enum):
    """Task priority levels for queue processing."""
    HIGH = 1    # Critical updates (e.g., permission changes)
    MEDIUM = 2  # Normal recalculations
    LOW = 3     # Batch operations, maintenance


class TaskStatus(Enum):
    """Status of background tasks."""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class BackgroundTask:
    """Represents a background task to be processed."""

    def __init__(
        self,
        task_id: str,
        task_type: str,
        payload: Dict[str, Any],
        priority: TaskPriority = TaskPriority.MEDIUM,
        callback: Optional[Callable] = None
    ):
        self.task_id = task_id
        self.task_type = task_type
        self.payload = payload
        self.priority = priority
        self.callback = callback
        self.status = TaskStatus.PENDING
        self.created_at = datetime.now(timezone.utc)
        self.started_at: Optional[datetime] = None
        self.completed_at: Optional[datetime] = None
        self.error: Optional[str] = None
        self.result: Optional[Any] = None

    def __lt__(self, other):
        """Enable priority queue sorting."""
        return self.priority.value < other.priority.value


class AsyncBackgroundTaskManager:
    """
    Manages background tasks for async processing.

    Features:
    - Priority queue for task processing
    - Multiple worker support
    - Task status tracking
    - Error handling and retry logic
    - Graceful shutdown
    - Fully configurable via LibraryConfig

    All parameters can be configured:
    - num_workers: Number of concurrent workers (config: background_workers)
    - max_queue_size: Maximum tasks in queue (config: background_queue_size)
    - shutdown_timeout: Graceful shutdown timeout (config: background_shutdown_timeout)
    - worker_timeout: Worker poll timeout (config: background_worker_timeout)
    - cleanup_max_age_hours: Task history retention (config: task_cleanup_max_age_hours)
    """

    def __init__(
        self,
        num_workers: int = 5,
        max_queue_size: int = 10000,
        shutdown_timeout: float = 30.0,
        worker_timeout: float = 1.0,
        cleanup_max_age_hours: int = 24,
    ):
        """
        Initialize the background task manager.

        Args:
            num_workers: Number of concurrent workers
            max_queue_size: Maximum tasks in queue
            shutdown_timeout: Graceful shutdown timeout in seconds
            worker_timeout: Worker poll timeout in seconds
            cleanup_max_age_hours: Task history retention in hours
        """
        self.num_workers = num_workers
        self.max_queue_size = max_queue_size
        self.shutdown_timeout = shutdown_timeout
        self.worker_timeout = worker_timeout
        self.cleanup_max_age_hours = cleanup_max_age_hours

        self.queue: asyncio.PriorityQueue = asyncio.PriorityQueue(maxsize=max_queue_size)
        self.workers: List[Task] = []
        self.running = False
        self.tasks: Dict[str, BackgroundTask] = {}  # Track all tasks
        self.task_handlers: Dict[str, Callable] = {}  # Task type handlers
        self._task_counter = 0
        self._lock = asyncio.Lock()

        # Statistics
        self.stats = {
            "total_tasks": 0,
            "completed_tasks": 0,
            "failed_tasks": 0,
            "cancelled_tasks": 0,
            "average_processing_time": 0,
        }

    @classmethod
    def from_config(cls, config: "LibraryConfig") -> "AsyncBackgroundTaskManager":
        """
        Create a task manager from LibraryConfig.

        Args:
            config: LibraryConfig instance with background task parameters

        Returns:
            Configured AsyncBackgroundTaskManager instance

        Example:
            config = LibraryConfig(
                database_url="...",
                secret_key="...",
                background_workers=10,
                background_queue_size=20000,
            )
            task_manager = AsyncBackgroundTaskManager.from_config(config)
        """
        return cls(
            num_workers=config.background_workers,
            max_queue_size=config.background_queue_size,
            shutdown_timeout=config.background_shutdown_timeout,
            worker_timeout=config.background_worker_timeout,
            cleanup_max_age_hours=config.task_cleanup_max_age_hours,
        )

    def reconfigure(
        self,
        num_workers: Optional[int] = None,
        shutdown_timeout: Optional[float] = None,
        worker_timeout: Optional[float] = None,
        cleanup_max_age_hours: Optional[int] = None,
    ) -> None:
        """
        Reconfigure task manager parameters at runtime.

        Note: num_workers change takes effect on next start().
        max_queue_size cannot be changed at runtime.

        Args:
            num_workers: New number of workers (applied on restart)
            shutdown_timeout: New shutdown timeout
            worker_timeout: New worker timeout
            cleanup_max_age_hours: New cleanup age
        """
        if num_workers is not None:
            self.num_workers = num_workers
            logger.info(f"Worker count will be {num_workers} on next start")
        if shutdown_timeout is not None:
            self.shutdown_timeout = shutdown_timeout
        if worker_timeout is not None:
            self.worker_timeout = worker_timeout
        if cleanup_max_age_hours is not None:
            self.cleanup_max_age_hours = cleanup_max_age_hours

    def register_handler(self, task_type: str, handler: Callable):
        """Register a handler for a specific task type."""
        self.task_handlers[task_type] = handler
        logger.info(f"Registered handler for task type: {task_type}")

    async def start(self):
        """Start the background task manager and workers."""
        if self.running:
            logger.warning("Background task manager already running")
            return

        self.running = True
        logger.info(f"Starting background task manager with {self.num_workers} workers")

        # Start worker tasks
        for i in range(self.num_workers):
            worker = asyncio.create_task(self._worker(f"worker-{i}"))
            self.workers.append(worker)

        logger.info("Background task manager started successfully")

    async def stop(self, timeout: Optional[float] = None):
        """
        Stop the background task manager gracefully.

        Args:
            timeout: Maximum time to wait for workers to finish
                     (uses configured shutdown_timeout if not provided)
        """
        if not self.running:
            return

        if timeout is None:
            timeout = self.shutdown_timeout

        logger.info("Stopping background task manager...")
        self.running = False

        # Cancel all workers
        for worker in self.workers:
            worker.cancel()

        # Wait for workers to finish with timeout
        try:
            await asyncio.wait_for(
                asyncio.gather(*self.workers, return_exceptions=True),
                timeout=timeout
            )
        except asyncio.TimeoutError:
            logger.warning(f"Workers did not finish within {timeout} seconds")

        self.workers.clear()
        logger.info("Background task manager stopped")

    async def submit_task(
        self,
        task_type: str,
        payload: Dict[str, Any],
        priority: TaskPriority = TaskPriority.MEDIUM,
        callback: Optional[Callable] = None
    ) -> str:
        """
        Submit a task for background processing.

        Args:
            task_type: Type of task to process
            payload: Task data
            priority: Task priority
            callback: Optional callback when task completes

        Returns:
            Task ID for tracking
        """
        async with self._lock:
            self._task_counter += 1
            task_id = f"{task_type}_{self._task_counter}_{datetime.now(timezone.utc).timestamp()}"

        task = BackgroundTask(
            task_id=task_id,
            task_type=task_type,
            payload=payload,
            priority=priority,
            callback=callback
        )

        # Store task for tracking
        self.tasks[task_id] = task
        self.stats["total_tasks"] += 1

        # Add to queue (non-blocking)
        try:
            self.queue.put_nowait((priority.value, task))
            logger.debug(f"Task {task_id} submitted with priority {priority.name}")
        except asyncio.QueueFull:
            task.status = TaskStatus.FAILED
            task.error = "Queue is full"
            self.stats["failed_tasks"] += 1
            logger.error(f"Failed to submit task {task_id}: Queue is full")
            raise Exception("Background task queue is full")

        return task_id

    async def submit_recalculation_task(
        self,
        user_ids: List[str],
        application: Optional[str] = None,
        priority: TaskPriority = TaskPriority.MEDIUM
    ) -> str:
        """
        Submit a user access recalculation task.

        Args:
            user_ids: List of user IDs to recalculate
            application: Application context
            priority: Task priority

        Returns:
            Task ID for tracking
        """
        payload = {
            "user_ids": user_ids,
            "application": application,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

        return await self.submit_task(
            task_type="recalculate_access",
            payload=payload,
            priority=priority
        )

    async def get_task_status(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Get the status of a specific task."""
        task = self.tasks.get(task_id)
        if not task:
            return None

        return {
            "task_id": task.task_id,
            "task_type": task.task_type,
            "status": task.status.value,
            "created_at": task.created_at.isoformat(),
            "started_at": task.started_at.isoformat() if task.started_at else None,
            "completed_at": task.completed_at.isoformat() if task.completed_at else None,
            "error": task.error,
            "result": task.result
        }

    async def get_queue_stats(self) -> Dict[str, Any]:
        """Get current queue statistics."""
        return {
            "queue_size": self.queue.qsize(),
            "max_queue_size": self.max_queue_size,
            "num_workers": self.num_workers,
            "active_workers": len([w for w in self.workers if not w.done()]),
            "total_tasks": self.stats["total_tasks"],
            "completed_tasks": self.stats["completed_tasks"],
            "failed_tasks": self.stats["failed_tasks"],
            "cancelled_tasks": self.stats["cancelled_tasks"],
            "average_processing_time": self.stats["average_processing_time"],
            "pending_tasks": self.queue.qsize(),
            "shutdown_timeout": self.shutdown_timeout,
            "worker_timeout": self.worker_timeout,
            "cleanup_max_age_hours": self.cleanup_max_age_hours,
        }

    async def _worker(self, worker_name: str):
        """
        Worker coroutine that processes tasks from the queue.

        Args:
            worker_name: Name of the worker for logging
        """
        logger.info(f"{worker_name} started")

        while self.running:
            try:
                # Wait for task with configurable timeout
                priority, task = await asyncio.wait_for(
                    self.queue.get(),
                    timeout=self.worker_timeout
                )

                # Process the task
                await self._process_task(task, worker_name)

            except asyncio.TimeoutError:
                # No task available, continue
                continue
            except asyncio.CancelledError:
                logger.info(f"{worker_name} cancelled")
                break
            except Exception as e:
                logger.error(f"{worker_name} error: {str(e)}\n{traceback.format_exc()}")

        logger.info(f"{worker_name} stopped")

    async def _process_task(self, task: BackgroundTask, worker_name: str):
        """
        Process a single task.

        Args:
            task: Task to process
            worker_name: Name of the worker processing the task
        """
        logger.debug(f"{worker_name} processing task {task.task_id}")

        task.status = TaskStatus.PROCESSING
        task.started_at = datetime.now(timezone.utc)

        try:
            # Get handler for task type
            handler = self.task_handlers.get(task.task_type)
            if not handler:
                raise Exception(f"No handler registered for task type: {task.task_type}")

            # Execute handler
            result = await handler(task.payload)

            # Mark as completed
            task.status = TaskStatus.COMPLETED
            task.completed_at = datetime.now(timezone.utc)
            task.result = result
            self.stats["completed_tasks"] += 1

            # Execute callback if provided
            if task.callback:
                try:
                    await task.callback(task.task_id, result)
                except Exception as e:
                    logger.error(f"Callback error for task {task.task_id}: {str(e)}")

            # Update average processing time
            processing_time = (task.completed_at - task.started_at).total_seconds()
            self._update_average_processing_time(processing_time)

            logger.debug(f"{worker_name} completed task {task.task_id} in {processing_time:.2f}s")

        except asyncio.CancelledError:
            task.status = TaskStatus.CANCELLED
            task.completed_at = datetime.now(timezone.utc)
            self.stats["cancelled_tasks"] += 1
            logger.info(f"Task {task.task_id} cancelled")
            raise

        except Exception as e:
            task.status = TaskStatus.FAILED
            task.completed_at = datetime.now(timezone.utc)
            task.error = str(e)
            self.stats["failed_tasks"] += 1
            logger.error(f"Task {task.task_id} failed: {str(e)}\n{traceback.format_exc()}")

            # Execute error callback if provided
            if task.callback:
                try:
                    await task.callback(task.task_id, None, error=str(e))
                except Exception as callback_error:
                    logger.error(f"Error callback failed for task {task.task_id}: {str(callback_error)}")

    def _update_average_processing_time(self, new_time: float):
        """Update the average processing time statistic."""
        completed = self.stats["completed_tasks"]
        if completed == 0:
            self.stats["average_processing_time"] = new_time
        else:
            current_avg = self.stats["average_processing_time"]
            self.stats["average_processing_time"] = (current_avg * (completed - 1) + new_time) / completed

    async def cleanup_old_tasks(self, max_age_hours: Optional[int] = None):
        """
        Clean up old completed/failed tasks from memory.

        Args:
            max_age_hours: Maximum age of tasks to keep (uses config default if not provided)
        """
        if max_age_hours is None:
            max_age_hours = self.cleanup_max_age_hours

        current_time = datetime.now(timezone.utc)
        tasks_to_remove = []

        for task_id, task in self.tasks.items():
            if task.status in [TaskStatus.COMPLETED, TaskStatus.FAILED, TaskStatus.CANCELLED]:
                if task.completed_at:
                    age_hours = (current_time - task.completed_at).total_seconds() / 3600
                    if age_hours > max_age_hours:
                        tasks_to_remove.append(task_id)

        for task_id in tasks_to_remove:
            del self.tasks[task_id]

        if tasks_to_remove:
            logger.info(f"Cleaned up {len(tasks_to_remove)} old tasks")


# Global instance for singleton pattern (optional)
_global_task_manager: Optional[AsyncBackgroundTaskManager] = None
_global_config: Optional["LibraryConfig"] = None


def configure_task_manager(config: "LibraryConfig") -> None:
    """
    Configure the global background task manager.

    Call this function during application startup to configure
    task manager parameters from your configuration.

    Args:
        config: LibraryConfig instance

    Example:
        from medha_one_access import LibraryConfig
        from medha_one_access.core.background_tasks import configure_task_manager

        config = LibraryConfig(
            database_url="...",
            secret_key="...",
            background_workers=10,
            background_queue_size=20000,
        )
        configure_task_manager(config)
    """
    global _global_task_manager, _global_config
    _global_config = config

    if _global_task_manager is not None:
        # Reconfigure existing manager
        _global_task_manager.reconfigure(
            num_workers=config.background_workers,
            shutdown_timeout=config.background_shutdown_timeout,
            worker_timeout=config.background_worker_timeout,
            cleanup_max_age_hours=config.task_cleanup_max_age_hours,
        )
    else:
        # Will be created with config on first access
        pass


def get_background_task_manager() -> AsyncBackgroundTaskManager:
    """Get the global background task manager instance."""
    global _global_task_manager, _global_config

    if _global_task_manager is None:
        if _global_config is not None:
            _global_task_manager = AsyncBackgroundTaskManager.from_config(_global_config)
        else:
            # Default configuration for backward compatibility
            _global_task_manager = AsyncBackgroundTaskManager()

    return _global_task_manager


def reset_task_manager() -> None:
    """Reset the global task manager (useful for testing)."""
    global _global_task_manager, _global_config
    _global_task_manager = None
    _global_config = None


# Export classes and functions
__all__ = [
    "AsyncBackgroundTaskManager",
    "BackgroundTask",
    "TaskPriority",
    "TaskStatus",
    "configure_task_manager",
    "get_background_task_manager",
    "reset_task_manager",
]
