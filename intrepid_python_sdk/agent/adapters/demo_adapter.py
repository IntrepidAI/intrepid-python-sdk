# example_adapter.py
import asyncio
from intrepid_python_sdk.agent.actions import ActionHandle, ActionResult, ActionStatus, ActionFeedback
from intrepid_python_sdk.agent.adapter import action, sensor

# class DemoAdapter(AdapterBase):
#     def __init__(self, runtime_client, robot_id="demo-robot"):
#         super().__init__(runtime_client, robot_id=robot_id)
#     @action("MoveTo")
#     async def move_to(self, params):
#         """
#         params: {"goal": {"x":..,"y":..,"z":..}}
#         returns: ActionHandle
#         """
#         handle = ActionHandle()
#         # run the motion in background so we can stream feedback
#         async def run_motion():
#             try:
#                 handle.set_result(ActionResult(status=ActionStatus.RUNNING))
#                 # simulate movement with feedback
#                 for p in [0.0, 0.2, 0.5, 0.8, 1.0]:
#                     if handle.cancel_requested:
#                         handle.set_result(ActionResult(status=ActionStatus.CANCELLED, result={}))
#                         return
#                     await handle.send_feedback(ActionFeedback(progress=p, message="moving"))
#                     await asyncio.sleep(0.4)
#                 handle.set_result(ActionResult(status=ActionStatus.SUCCEEDED, result={"arrived": True}))
#             except Exception as e:
#                 handle.set_result(ActionResult(status=ActionStatus.FAILED, error=str(e)))
#         self.spawn(run_motion())
#         return handle
#     @sensor("camera")
#     def camera_cb(self, img):
#         # convert incoming image to detection and push to runtime world state
#         det = {"id": "p1", "confidence": 0.9}
#         self.runtime.world.add_person_detection(self.robot_id, det)


@action("MoveTo")
async def move_to(self, params):
    # YOUR CODE GOES HERE

    for i in range(10):
        print("I am running...")
    return True
