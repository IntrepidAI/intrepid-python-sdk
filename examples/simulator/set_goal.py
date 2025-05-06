import asyncio
from intrepid_python_sdk.simulator import Simulator, Position


async def main():
    sim = Simulator()
    await sim.connect()
    goal_pos = Position(10,8,0)
    goal = await sim.set_goal(goal_pos)
    print(f"goal entity: {goal}")



if __name__ ==  '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
