import asyncio
from intrepid_python_sdk.simulator import Simulator

async def main():
    sim = Simulator()
    await sim.connect()

    if sim is not None:
        print(f"sim: {sim} is already connected!")


if __name__ ==  '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())

