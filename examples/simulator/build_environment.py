import asyncio
from intrepid_python_sdk.simulator import Simulator, ObstacleType, Position, Rotation


async def main():
    sim = Simulator()
    await sim.connect()

    for i in range(10):
        src_x = 10 + i*10
        dst_x = src_x + 10

        # Spawn UGV
        position = Position(i+3, 1, 0)
        rotation = Rotation(0,0,0)
        ugv_vehicle = await sim.spawn_ugv(i, position, rotation)
        print(ugv_vehicle)

        # Spawn road segment
        position_src = Position(src_x, 5, 0)
        position_dst = Position(dst_x, 5, 0)
        await sim.spawn_road(position_src, position_dst)

        # Spawn generic entity
        position = Position(src_x, 7, 0)
        rotation = Rotation(0,0,0)
        tree = await sim.spawn_entity(ObstacleType.TREE1, position, rotation)
        print(tree)


if __name__ ==  '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
