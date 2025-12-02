# runtime.py
import asyncio
from typing import List, Optional, Dict
from .actions import ActionRequest, ActionResult, ActionStatus
from .world import WorldState
from .adapter import AdapterBase

# TOD this is a server
class RuntimeClient:
    """
    Minimal runtime client used by adapters in MVP.
    In production, the runtime would be a separate server (Rust or Python) and adapters
    would connect via IPC. For MVP we keep runtime in-process.
    """
    def __init__(self, graph: dict):
        self.graph = graph
        self.world = WorldState()
        self.adapters: Optional[Dict[str, AdapterBase]] = None
        self._running = False
        # Maps: adapter_id -> { req_id -> ActionRequest }
        self._action_map: Dict[str, Dict[str, ActionRequest]] = {}

    async def register_adapter(self, adapter: AdapterBase):

        """
        Register a new adapter.
        Multiple adapters can be registered (e.g., robot1, robot2).
        """
        self.adapters[adapter_id] = adapter
        self._action_map[adapter_id] = {}

        await adapter.on_start()
        print(f"[runtime] adapter '{adapter_id}' registered")

    async def start(self):
        self._running = True
        # for MVP, just run the simple loop that checks for "next action"
        asyncio.create_task(self._main_loop())
        print("[runtime] started")


    async def _main_loop(self):
        while self._running:
            # For now just sleep — the adapter drives actions,
            # the graph logic will plug here.
            # Real runtime loads the graph IR and evaluates nodes / transitions.
            await asyncio.sleep(0.1)

    async def stop(self):
        self._running = False

        for adapter_id, adapter in self.adapters.items():
            await adapter.on_stop()
            print(f"[runtime] stopped adapter '{adapter_id}'")

        print("[runtime] fully stopped")

    # adapter helpers (adapter calls these to inform runtime of action events)
    def notify_action_started(self, adapter_id: str, req: ActionRequest):
        """
        Called by adapter when it begins executing an action.
        """
        if adapter_id not in self._action_map:
            self._action_map[adapter_id] = {}
        self._action_map[adapter_id][req.request_id] = req

        print(f"[runtime] adapter {adapter_id}: action {req.request_id} started")

    def notify_action_result(self, adapter_id: str, req_id: str, result: ActionResult):
        """
        Adapter reports an action result.
        Runtime uses this to trigger graph transitions.
        """
        if adapter_id in self._action_map:
            self._action_map[adapter_id].pop(req_id, None)

        print(
            f"[runtime] adapter {adapter_id}: action {req_id} "
            f"finished with status={result.status}, result={result.result}"
        )
