import asyncio
from intrepid_python_sdk.simulator import Simulator, WorldEntity
import math


async def my_control_foo(client):
    # Add your code HERE

    robot_id = 42
    angle = (2 * math.pi)

    entity = await client.rpc('map.spawn_uav', {
        'robot_id': robot_id,
        'position': {
            'x': 1. * math.cos(angle),
            'y': 1. * math.sin(angle),
            'z': 0,
        },
    })
    print(entity)

    # end of your code



async def main():
    sim = Simulator()
    await sim.connect()
    sim.set_step_duration(500)
    sim.sync(my_control_foo)



if __name__ ==  '__main__':
    asyncio.ensure_future(main())
    loop = asyncio.get_event_loop()
    loop.run_forever()