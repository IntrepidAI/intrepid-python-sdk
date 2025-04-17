import asyncio
import pytest
from intrepid_python_sdk.simulator import Simulator, ObstacleType


@pytest.mark.asyncio
async def test_get_vehicle():

    sim = Simulator()
    await sim.connect()

    for i in range(10):
        src_x = 10 + i*10
        dst_x = src_x + 10

        # Spawn UGV
        ugv_vehicle = await sim.spawn_ugv(vehicle_id=i, position=[i+3, 1, 0], rotation=[0,0,0])
        assert ugv_vehicle is not None

        # Spawn road segment
        await sim.spawn_road(src=[src_x,5], dest=[dst_x,5])

        # Spawn generic entity
        tree = await sim.spawn_entity(ObstacleType.TREE1, position=[src_x, 7, 0], rotation=[0,0,0])
        assert tree is not None

    await sim.disconnect()



@pytest.mark.asyncio
async def test_set_goal():

    sim = Simulator()
    await sim.connect()
    goal = await sim.set_goal(position=[10,5,0])
    assert goal is not None
    await sim.disconnect()
