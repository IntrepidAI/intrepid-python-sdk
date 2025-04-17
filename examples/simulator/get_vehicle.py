import asyncio
from intrepid_python_sdk.simulator import Simulator


async def main():
    sim = Simulator()
    await sim.connect()

    # Get vehicle from agent_id
    vehicle = await sim.get_vehicle(vehicle_id=1)
    print(f"vehicle: {vehicle}")
    pos = await vehicle.position()
    print(f"pos: {pos}")

    # Get partial state
    rot = await vehicle.rotation()
    print(f"rot: {rot}")
    acc = await vehicle.acceleration()
    print(f"acc: {acc}")
    av = await vehicle.angular_velocity()
    print(f"av: {av}")
    lv = await vehicle.linear_velocity()
    print(f"lv: {lv}")

    # Get full state
    full_state = await vehicle.state()
    print(f"state: {full_state}")

    # Get non-existing vehicle
    non_existing_vehicle = await sim.get_vehicle(vehicle_id=999)
    print(f"non_existing_vehicle: {non_existing_vehicle}")




if __name__ ==  '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
