"""
./single_robot_behavior --agent_id 1 ...
./single_robot_behavior --agent_id 2 ...
./single_robot_behavior --agent_id 3 ...
./single_robot_behavior --agent_id 4 ...
./single_robot_behavior --agent_id 5 ...

"""

import asyncio
from functools import partial
from intrepid_python_sdk.simulator import Simulator, WorldEntity, Position, Rotation
import cv2
from base64 import b64decode


async def my_control_foo(robot_id, camera, sim: Simulator):
    # Add your code HERE
    imgbuf = await camera.capture()
    header, encoded = imgbuf.split("base64,", 1)
    data = b64decode(encoded)
    with open("image.png", "wb") as f:
        f.write(data)

    # end of your code



async def main():
    sim = Simulator()
    await sim.connect()

    vehicle = await sim.get_vehicle(vehicle_id=1)
    camera = await vehicle.spawn_camera(position=[0,0,0],
                                        rotation=[0,0,0],
                                        size=[320, 240],
                                        fov_degrees=120,
                                        format="image/png"
                                        )

    sim.set_step_duration(500)
    sim.sync(partial(my_control_foo, 1, camera))




if __name__ ==  '__main__':
    asyncio.ensure_future(main())
    loop = asyncio.get_event_loop()
    loop.run_forever()