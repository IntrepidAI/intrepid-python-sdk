# adapter.py
import inspect
import asyncio
from typing import Callable, Dict, Any
from .actions import ActionRequest, ActionHandle

# Registries (module-level for MVP)
ACTION_REGISTRY: Dict[str, Callable] = {}
SENSOR_REGISTRY: Dict[str, Callable] = {}

# Decorators for adapter authors
def action(name: str):
    """Register an action handler for name"""
    def decorator(fn: Callable):
        ACTION_REGISTRY[name] = fn
        return fn
    return decorator

def sensor(name: str):
    """Register a sensor handler (pushes world updates)"""
    def decorator(fn: Callable):
        SENSOR_REGISTRY[name] = fn
        return fn
    return decorator


class Adapter:
    def __init__(self, adapter_name: str = "intrepid-adapter"):
        pass

    async def listen(host: str, port: int):
        pass

    async def on_start(self):
        """Optional lifecycle hook called by runtime before graph starts."""
        pass




class AdapterBase:
    """
    Base class for an in-process adapter.
    Adapter implementations SHOULD:
      - implement action handlers decorated with @action("Name")
      - push world updates via self.runtime (passed in constructor)
      - call runtime.notify_action_started / finished if you want richer tracing
    """

    def __init__(self, runtime_client, robot_id: str = "robot-01"):
        """
        runtime_client: small object exposing methods:
            - world: WorldState (mutate with world updates)
            - notify_action_started(req: ActionRequest)
            - notify_action_feedback(req_id, ActionFeedback)
            - notify_action_result(req_id, ActionResult)
        """
        self._runtime = runtime_client
        self.robot_id = robot_id
        # allow adapters to have their own tasks
        self._tasks = []

    async def on_start(self):
        """Optional lifecycle hook called by runtime before graph starts."""
        pass

    async def on_stop(self):
        """Optional lifecycle hook to clean up resources."""
        for t in self._tasks:
            if not t.done():
                t.cancel()
        await asyncio.gather(*[t for t in self._tasks if not t.done()], return_exceptions=True)

    async def handle_action_request(self, req: ActionRequest) -> ActionHandle:
        """
        Called by runtime when an ActionRequest needs to be executed by this adapter.
        Default implementation: dispatch to registered function in ACTION_REGISTRY.
        """
        if req.action_type not in ACTION_REGISTRY:
            raise RuntimeError(f"No handler for action '{req.action_type}' registered in adapter.")
        handler = ACTION_REGISTRY[req.action_type]
        # If handler is a bound method, it expects (self, params)
        if inspect.iscoroutinefunction(handler):
            # if handler is defined as function(adapter, params)
            return await handler(self, req.params)
        else:
            # sync handler -> run in executor
            loop = asyncio.get_event_loop()
            return await loop.run_in_executor(None, lambda: handler(self, req.params))

    # helper to push world updates
    @property
    def runtime(self):
        return self._runtime

    # small helper to schedule background tasks owned by adapter
    def spawn(self, coro):
        t = asyncio.create_task(coro)
        self._tasks.append(t)
        return t
