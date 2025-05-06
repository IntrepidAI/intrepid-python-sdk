import asyncio
from intrepid_python_sdk.simulator import Simulator, Entity


async def main():
    sim = Simulator()
    await sim.connect()

    # Get vehicle from agent_id
    vehicle = await sim.get_vehicle(vehicle_id=1)

    # Attach abstract sensor to vehicle
    sensor = vehicle.spawn_abstract_sensor(radius=50.0,
                                           groups=["obstacle"])

    # Capture surrounding entities
    detected_entities = await sensor.capture()
    for de in detected_entities:
        position = detected_entities[de]["position"]
        rotation = detected_entities[de]["rotation"]
        group = detected_entities[de]["group"]
        print(f"Found entity type: '{group}' at pos: {position} rot: {rotation}")


if __name__ ==  '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
