import asyncio
import pytest
from intrepid_python_sdk.simulator import Simulator, ObstacleType


@pytest.mark.asyncio
async def test_get_vehicle():
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

    sim = Simulator()
    await sim.connect()
    sim.set_step_duration(500)
    sim.sync(my_control_foo)


    await sim.disconnect()


