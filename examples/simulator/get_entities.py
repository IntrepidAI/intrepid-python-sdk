import asyncio
from intrepid_python_sdk.simulator import Simulator


async def main():
    sim = Simulator()
    await sim.connect()

    # Get all entities
    entities = await sim.get_entities()
    print(f"Found {len(entities)} entities")

    # Get all vehicles
    vehicles = await sim.get_vehicles()
    print(f"Found {len(vehicles)} vehicles")



if __name__ ==  '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
