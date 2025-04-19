import asyncio
from intrepid_python_sdk.simulator import Simulator


async def main():
    sim = Simulator()
    await sim.connect()

    # Get vehicle from agent_id
    vehicle = await sim.get_vehicle(vehicle_id=1)

    # Attach abstract sensor to vehicle
    sensor = vehicle.spawn_abstract_sensor(radius=5.0)

    # Capture surrounding obstacles
    detected_entities = await sensor.capture()
    for de in detected_entities:
        position = await de.local_position()
        rotation = await de.rotation()
        print(f"Found obstacle type: '{de.entity_type()}' at pos: {position} rot: {rotation}")


if __name__ ==  '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
