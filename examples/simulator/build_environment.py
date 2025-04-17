import asyncio
from intrepid_python_sdk.simulator import Simulator, ObstacleType


async def main():
    sim = Simulator()
    await sim.connect()

    for i in range(10):
        src_x = 10 + i*10
        dst_x = src_x + 10

        # Spawn UGV
        ugv_vehicle = await sim.spawn_ugv(vehicle_id=i, position=[i+3, 1, 0], rotation=[0,0,0])
        print(ugv_vehicle)

        # Spawn road segment
        await sim.spawn_road(src=[src_x,5], dest=[dst_x,5])

        # Spawn generic entity
        tree = await sim.spawn_entity(ObstacleType.TREE1, position=[src_x, 7, 0], rotation=[0,0,0])
        print(tree)


if __name__ ==  '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
