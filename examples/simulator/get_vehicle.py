import asyncio
from intrepid_python_sdk.simulator import Simulator
import json


async def main():
    sim = Simulator()
    await sim.connect()

    # Get vehicle from agent_id
    vehicle = await sim.get_vehicle(vehicle_id=0)
    print(f"vehicle: {vehicle}")
    pos = await vehicle.local_position()
    print(f"position: {pos}")

    # Get partial state
    rot = await vehicle.rotation()
    print(f"rotation: {rot}")

    acc = await vehicle.acceleration()
    print(f"acceleration: {acc}")

    av = await vehicle.angular_velocity()
    print(f"angular_velocity: {av}")

    lv = await vehicle.linear_velocity()
    print(f"lv: {lv}")

    # Get full state
    full_state = await vehicle.state()
    print(f"full_state: {full_state}")

    # Get non-existing vehicle
    non_existing_vehicle = await sim.get_vehicle(vehicle_id=999)
    print(f"non_existing_vehicle: {non_existing_vehicle}")




if __name__ ==  '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
