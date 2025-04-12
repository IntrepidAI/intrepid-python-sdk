import asyncio
from intrepid_python_sdk import Simulator


async def main():
    sim = Simulator()
    await sim.connect()
    goal = await sim.set_goal(position=[10,5,0])
    print(f"goal entity: {goal}")



if __name__ ==  '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
