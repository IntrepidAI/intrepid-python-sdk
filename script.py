import asyncio
import sys
import time

from intrepid import *
# from intrepid.cache_manager import SqliteCacheManager
# from intrepid.config import DecisionApi, Bucketing
# from intrepid.hits import Screen
# from intrepid.tracking_manager import TrackingManagerConfig


def init():
    print(sys.version)

    handle = Intrepid("custom/node/4224")
    node_info = handle.info()
    node_status = handle.status()

    print(node_info)
    print(node_status)

    handle.close()

    time.sleep(2)


init()