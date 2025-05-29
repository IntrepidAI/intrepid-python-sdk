import asyncio
# from intrepid_python_sdk import Simulator
from intrepid_python_sdk.simulator import Simulator, ObstacleType, Position, Rotation
from commons import hvt_position
import random



async def main():
    sim = Simulator()
    await sim.connect()

    # Spawn HVT
    goal = await sim.set_goal(hvt_position)



if __name__ ==  '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
