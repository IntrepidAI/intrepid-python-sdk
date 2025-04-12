import asyncio
from intrepid_python_sdk.simulator import Simulator, WorldEntity

async def my_control_foo(client, ts, every_microsec: int):
    print(f"every_microsec: {every_microsec}")
    print(f"from control ts:{ts}")

    # Add your code HERE


    # end of your code



    # set next sync point with simulation in 1 second from now
    sync_sub = client.get_subscription('sync')
    await sync_sub.publish(every_microsec)




async def main():
    sim = Simulator()
    await sim.connect()
    client = sim.client()
    ts = sim.ts()

    await sim.sync(my_control_foo, client, ts, 1_000)




if __name__ ==  '__main__':
    # loop = asyncio.get_event_loop()
    # loop.run_until_complete(main())
    # loop.run_forever()

    asyncio.ensure_future(main())
    loop = asyncio.get_event_loop()
    loop.run_forever()