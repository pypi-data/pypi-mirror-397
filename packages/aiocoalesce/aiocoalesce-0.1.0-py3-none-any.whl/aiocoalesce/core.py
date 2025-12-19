import asyncio
from typing import Awaitable, Dict, Hashable, TypeVar

T = TypeVar("T")

class Coalescer:
    """
    A best-in-class async request coalescing library.
    Ensures that multiple concurrent requests for the same key share a single execution.
    """
    def __init__(self):
        self._pending: Dict[Hashable, asyncio.Task[T]] = {}

    async def run(self, key: Hashable, awaitable: Awaitable[T]) -> T:
        """
        Execute the given awaitable, coalescing requests with the same key.
        
        If a request with `key` is already running, this call will join that execution
        and await its result. The passed `awaitable` will be closed (never executed).
        
        If no request is running, `awaitable` is executed.
        
        Args:
            key: A unique identifier for the operation (e.g. URL, ID).
            awaitable: The coroutine or awaitable to execute.
            
        Returns:
            The result of the awaitable.
        """
        task = self._pending.get(key)
        
        # If we have a task and it's not done, join it.
        # Check .done() to ensure we don't latch onto a finished task 
        # that hasn't been cleaned up yet (microsecond race).
        if task is not None and not task.done():
            if asyncio.iscoroutine(awaitable):
                awaitable.close()
            # We await the existing task. 
            # Note: If the creator cancels, the task continues.
            # If *we* cancel, we just stop waiting; the task continues.
            # Use shield to prevent cancellation propagation
            return await asyncio.shield(task)

        # Create a new task ensuring it is scheduled on the loop
        # We use create_task to ensure it runs even if we (the caller) get cancelled immediately after.
        # This provides "detached" execution semantics for the work itself, 
        # while tying the result delivery to the caller.
        task = asyncio.create_task(awaitable)
        self._pending[key] = task
        
        def _cleanup(_):
            # Only remove if it is strictly OUR task. 
            # This handles the case where we were overwritten by a newer task.
            if self._pending.get(key) is task:
                del self._pending[key]

        task.add_done_callback(_cleanup)
        
        return await asyncio.shield(task)
