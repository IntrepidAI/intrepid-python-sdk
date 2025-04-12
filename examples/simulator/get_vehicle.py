import asyncio
from intrepid_python_sdk import Simulator


async def main():
    sim = Simulator()
    await sim.connect()

    # Get vehicle from agent_id
    vehicle = await sim.get_vehicle(agent_id=1)
    print(f"vehicle: {vehicle}")

    # Get non-existing vehicle
    non_existing_vehicle = await sim.get_vehicle(agent_id=999)
    print(f"non_existing_vehicle: {non_existing_vehicle}")

    # Get vehicle state
    state = await sim.get_vehicle_state(vehicle)
    pos = state["position"]
    rot = state["rotation"]
    vel = state["velocity"]
    print(f"pos: {pos}")
    print(f"rot: {rot}")
    print(f"vel: {vel}")




if __name__ ==  '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
