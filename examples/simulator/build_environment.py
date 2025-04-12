import asyncio
# from intrepid_python_sdk import Simulator
from intrepid_python_sdk.simulator import Simulator, WorldEntity


async def main():
    sim = Simulator()
    await sim.connect()

    for i in range(10):
        src_x = 10 + i*10
        dst_x = src_x + 10
        print(src_x, dst_x)
        road_block = await sim.spawn_road(src=[src_x,5], dest=[dst_x,5])

        await sim.spawn_entity(WorldEntity.TREE, position=[src_x, 7, 0], rotation=[0,0,0])
    print(f"road entity: {road_block}")



if __name__ ==  '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
