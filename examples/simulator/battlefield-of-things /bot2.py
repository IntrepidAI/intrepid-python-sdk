"""
Intrepid AI Battlefield of Things 2 - 2025

"""


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
from commons import intersect_sphere_line, generate_random_position_around_xy, hvt_position, attacker_id, distance_from_hvt
GOAL_REACHED_THRESHOLD = 1

class VehicleState:
    def __init__(self, vehicle: Vehicle, camera: Camera):
        self.vehicle = vehicle
        self.camera = camera


async def my_control_foo(state: VehicleState, sim: Simulator):
    # Add your code HERE


    # Spawn abstract sensor
    sensor = state.vehicle.spawn_abstract_sensor(radius=50.0, groups=["obstacle", "vehicle"])
    # Capture surrounding entities
    detected_entities = await sensor.capture()
    for de in detected_entities:
        position = detected_entities[de]["position"]
        rotation = detected_entities[de]["rotation"]
        robot_id = detected_entities[de]["robot_id"]
        group = detected_entities[de]["group"]
        print(f"Found entity type: '{group}' id: {robot_id}, at pos: {position} rot: {rotation}")
        if robot_id == attacker_id:
            print(f"OH SHIT!!")
            attacker_pos = position
            attacker_rotation = rotation

            # Calculate line from hvt_pos to attacker_pos
            await sim.draw_line(attacker_pos, hvt_position, "#FF0000")

            # Randomly position around the line with spread proportional to distance
            await sim.draw_sphere(hvt_position, distance_from_hvt, "#FF0000")
            intersection = intersect_sphere_line(hvt_position, distance_from_hvt, attacker_pos)

            # Calculate target position 

    # Capture video footage
    # imgbuf = await state.camera.capture()
    # header, encoded = imgbuf.split("base64,", 1)
    # data = b64decode(encoded)
    # with open("image.png", "wb") as f:
    #     f.write(data)

    # Navigate
    current_position = await state.vehicle.local_position()
    print(f"Currently at {current_position}")

    # target_position = state.waypoints[state.current_waypoint_index]
    # await state.vehicle.position_control(target_position)
    # if current_position.distance(target_position) < GOAL_REACHED_THRESHOLD:
    #     state.current_waypoint_index += 1
    #     if state.current_waypoint_index >= len(state.waypoints):
    #         state.current_waypoint_index = 0

    # end of your code


async def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--vehicle_id", type=int, default=1, help="ID of the vehicle")
    args = parser.parse_args()
    vehicle_id = args.vehicle_id

    sim = Simulator()
    await sim.connect()

    # remove all existing goals and set new ones
    commands = []
    existing_goals = await sim.get_entities(groups=["goal"])
    for entity in existing_goals:
        commands.append(entity.despawn())
    await asyncio.gather(*commands)

    # Spawn vehicle around HVT (defender)
    random_position = generate_random_position_around_xy(hvt_position, offset_range=10)
    vehicle = await sim.spawn_uav(vehicle_id=vehicle_id,
                                    position=random_position,
                                    rotation=Rotation(0,0,0))

    # Spawn a camera (not used)
    camera = await vehicle.spawn_camera(position=[0,0,0],
                                        rotation=[0,0,0],
                                        size=[320, 240],
                                        fov_degrees=120,
                                        format="image/png"
                                        )

    sim.set_step_duration(500)
    sim.sync(partial(my_control_foo, VehicleState(vehicle, camera)))




if __name__ ==  '__main__':
    asyncio.ensure_future(main())
    loop = asyncio.get_event_loop()
    loop.run_forever()