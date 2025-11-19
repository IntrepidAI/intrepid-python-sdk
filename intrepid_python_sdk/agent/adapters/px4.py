from intrepid.actions import ActionHandle, ActionResult, ActionStatus, ActionFeedback
from intrepid.adapter import AdapterBase, action, sensor
from intrepid.world import Pose3D, PersonDetection
from mavsdk import System
import asyncio

# class PX4Adapter(AdapterBase):
#     def __init__(self):
#         self.drone = System()

#     @action("Takeoff")
#     async def takeoff(self):
#         await self.drone.action.arm()
#         await self.drone.action.takeoff()

#     @action("MoveTo")
#     async def go_to(self, pos):
#         await self.drone.action.goto_location(pos.lat, pos.lon, pos.alt, 0)


class PX4Adapter(AdapterBase):
    def __init__(self, runtime, drone_uri="udp://:14540", robot_id="px4-sitl-01"):
        super().__init__(runtime)
        self.system = System()
        self.drone_uri = drone_uri
        self.robot_id = robot_id
        self._task = asyncio.create_task(self._connect_and_stream_pose())

    async def _connect_and_stream_pose(self):
        await self.system.connect(self.drone_uri)
        async for v in self.system.telemetry.position_velocity_ned():
            pose = Pose3D(x=v.position.latitude_deg, y=v.position.longitude_deg, z=v.position.absolute_altitude_m)
            self.runtime.update_world_robot_pose(self.robot_id, pose)

    @action("Takeoff")
    async def takeoff(self, params):
        handle = ActionHandle()
        async def run():
            try:
                await self.system.action.arm()
                await self.system.action.takeoff()
                # wait for some altitude...
                await asyncio.sleep(3)
                handle.set_result(ActionResult(status=ActionStatus.SUCCEEDED, result={"taken_off": True}))
            except Exception as e:
                handle.set_result(ActionResult(status=ActionStatus.FAILED, error=str(e)))
        asyncio.create_task(run())
        return handle

    @action("MoveTo")
    async def move_to(self, params):
        handle = ActionHandle()
        goal = params["goal"]  # expect dict with x,y,z in local frame
        async def run():
            try:
                # perform offboard setpoint streaming until arrival
                await self._send_position_setpoint(goal, handle)
                handle.set_result(ActionResult(status=ActionStatus.SUCCEEDED, result={"arrived": True}))
            except Exception as e:
                handle.set_result(ActionResult(status=ActionStatus.FAILED, error=str(e)))
        asyncio.create_task(run())
        return handle

    async def _send_position_setpoint(self, goal, handle):
        # Implementation detail: create offboard setpoint loop until within tolerance
        pass

    @action("OrbitAround")
    async def orbit(self, params):
        handle = ActionHandle()
        async def run():
            center = params["center"]
            radius = params.get("radius", 5.0)
            duration = params.get("duration", 10.0)
            start_t = asyncio.get_event_loop().time()
            while asyncio.get_event_loop().time() - start_t < duration:
                # compute point on circle and send setpoint
                await self._send_position_setpoint({...}, handle)
                await handle.send_feedback(ActionFeedback(progress=(asyncio.get_event_loop().time() - start_t)/duration, message="orbiting"))
                await asyncio.sleep(0.2)
            handle.set_result(ActionResult(status=ActionStatus.SUCCEEDED))
        asyncio.create_task(run())
        return handle
