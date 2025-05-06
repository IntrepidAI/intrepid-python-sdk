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
# import math

async def my_control_foo(robot_id, sim: Simulator):
    # Add your code HERE

    vehicle = await sim.spawn_uav(robot_id, Position(0,0,0), Rotation(0,0,0))
    print(vehicle)

    # end of your code



async def main():
    sim = Simulator()
    await sim.connect()

    sim.set_step_duration(100)
    sim.sync(partial(my_control_foo, 1))




if __name__ ==  '__main__':
    asyncio.ensure_future(main())
    loop = asyncio.get_event_loop()
    loop.run_forever()