import asyncio
from intrepid_python_sdk import Simulator


async def main():
    sim = Simulator()
    await sim.connect()
    vehicle = await sim.spawn_uav(vehicle_id=1, position=[0,0,0], rotation=[0,0,0])
    print(vehicle)



if __name__ ==  '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
