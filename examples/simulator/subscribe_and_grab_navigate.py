"""
./single_robot_behavior --agent_id 1 ...
./single_robot_behavior --agent_id 2 ...
./single_robot_behavior --agent_id 3 ...
./single_robot_behavior --agent_id 4 ...
./single_robot_behavior --agent_id 5 ...

"""
import argparse
import asyncio

from functools import partial
from typing import List
from intrepid_python_sdk.simulator import Simulator, WorldEntity, Position, \
    Rotation, Vehicle, Entity, Camera
from base64 import b64decode
# import cv2

GOAL_REACHED_THRESHOLD = 1

class VehicleState:
    def __init__(self, vehicle: Vehicle, camera: Camera, waypoints: List[Position]):
        self.vehicle = vehicle
        self.camera = camera
        self.waypoints = waypoints
        self.current_waypoint_index = 0


async def my_control_foo(state: VehicleState, sim: Simulator):
    # Add your code HERE

    # Capture video footage
    imgbuf = await state.camera.capture()
    header, encoded = imgbuf.split("base64,", 1)
    data = b64decode(encoded)
    with open("image.png", "wb") as f:
        f.write(data)

    # Navigate
    current_position = await state.vehicle.local_position()
    target_position = state.waypoints[state.current_waypoint_index]
    await state.vehicle.position_control(target_position)

    if current_position.distance(target_position) < GOAL_REACHED_THRESHOLD:
        state.current_waypoint_index += 1
        if state.current_waypoint_index >= len(state.waypoints):
            state.current_waypoint_index = 0

    # end of your code


async def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--vehicle_id", type=int, default=1, help="ID of the vehicle")
    args = parser.parse_args()
    vehicle_id = args.vehicle_id

    sim = Simulator()
    await sim.connect()

    # HEIGHT = 2

    waypoints = []
    waypoints.append(Position(  6,   0, 1))
    waypoints.append(Position( 26,   0, 1.2))
    waypoints.append(Position( 60,   2, 1.4))
    waypoints.append(Position( 70,  -1, 1.5))
    waypoints.append(Position(112,  40, 1.6))
    waypoints.append(Position( 79,  75, 1.7))
    waypoints.append(Position(130,  75, 1.7))
    waypoints.append(Position(130, 130, 1.7))
    waypoints.append(Position(150,  75, 1.8))

    # remove all existing goals and set new ones
    commands = []
    existing_goals = await sim.get_entities(groups=["goal"])
    for entity in existing_goals:
        commands.append(entity.despawn())
    for waypoint in waypoints:
        waypoint_ground = Position(waypoint.x, waypoint.y, 0)
        commands.append(sim.set_goal(waypoint_ground, height=waypoint.z + GOAL_REACHED_THRESHOLD * 1.5))
    await asyncio.gather(*commands)

    vehicle = await sim.get_vehicle(vehicle_id)
    camera = await vehicle.spawn_camera(position=[0,0,0],
                                        rotation=[0,0,0],
                                        size=[320, 240],
                                        fov_degrees=120,
                                        format="image/png"
                                        )

    sim.set_step_duration(500)
    sim.sync(partial(my_control_foo, VehicleState(vehicle, camera, waypoints)))




if __name__ ==  '__main__':
    asyncio.ensure_future(main())
    loop = asyncio.get_event_loop()
    loop.run_forever()