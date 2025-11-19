# actions.py
import asyncio
import uuid
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, Optional, AsyncIterator

class ActionStatus(Enum):
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    SUCCEEDED = "SUCCEEDED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"

@dataclass
class ActionRequest:
    action_type: str
    params: Dict[str, Any]
    request_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: float = field(default_factory=time.time)

@dataclass
class ActionFeedback:
    progress: float = 0.0
    message: str = ""

@dataclass
class ActionResult:
    status: ActionStatus
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

class ActionHandle:
    """
    Adapter returns an ActionHandle for a started action.
    The runtime uses this handle to monitor progress/result/cancel.
    """

    def __init__(self):
        self._feedback_q: asyncio.Queue[ActionFeedback] = asyncio.Queue()
        self._done = asyncio.Event()
        self._result: Optional[ActionResult] = None
        self._cancel_requested = False

    async def send_feedback(self, fb: ActionFeedback):
        """Adapter pushes feedback for the running action."""
        await self._feedback_q.put(fb)

    async def feedback_iter(self) -> AsyncIterator[ActionFeedback]:
        """Runtime can iterate this to stream feedback to UI/logs."""
        while not (self._done.is_set() and self._feedback_q.empty()):
            try:
                fb = await asyncio.wait_for(self._feedback_q.get(), timeout=0.2)
                yield fb
            except asyncio.TimeoutError:
                if self._done.is_set():
                    break

    def set_result(self, result: ActionResult):
        """Adapter sets final result when action ends."""
        self._result = result
        self._done.set()

    async def wait_result(self, timeout: Optional[float] = None) -> ActionResult:
        await asyncio.wait_for(self._done.wait(), timeout=timeout)
        assert self._result is not None
        return self._result

    def cancel(self):
        """Runtime can request cancellation. Adapters should handle cancel gracefully."""
        self._cancel_requested = True

    @property
    def cancel_requested(self) -> bool:
        return self._cancel_requested

    @property
    def done(self) -> bool:
        return self._done.is_set()
