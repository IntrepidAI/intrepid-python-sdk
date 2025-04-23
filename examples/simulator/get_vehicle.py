import asyncio
from intrepid_python_sdk.simulator import Simulator
import json


async def main():
    sim = Simulator()
    await sim.connect()

    # Get vehicle from agent_id
    vehicle = await sim.get_vehicle(vehicle_id=1)
    print(f"vehicle: {vehicle}")
    pos = await vehicle.local_position()
    print(f"position: {json.dumps(pos, indent=4)}")

    # Get partial state
    rot = await vehicle.rotation()
    print(f"rotation: {json.dumps(rot, indent=4)}")

    acc = await vehicle.acceleration()
    print(f"acceleration: {json.dumps(acc, indent=4)}")

    av = await vehicle.angular_velocity()
    print(f"acceleration: {json.dumps(av, indent=4)}")

    lv = await vehicle.linear_velocity()
    print(f"lv: {json.dumps(lv, indent=4)}")

    # Get full state
    full_state = await vehicle.state()
    print(f"full_state: {json.dumps(full_state, indent=4)}")

    # Get non-existing vehicle
    non_existing_vehicle = await sim.get_vehicle(vehicle_id=999)
    print(f"non_existing_vehicle: {non_existing_vehicle}")




if __name__ ==  '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
