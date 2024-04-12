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
    Intrepid.start('__env_id__', '__api_key__', DecisionApi(timeout=3000,
                                                            cache_manager=SqliteCacheManager(),
                                                            log_level=LogLevel.ALL,
                                                            tracking_manager_config=TrackingManagerConfig(
                                                                time_interval=10000,
                                                                max_pool_size=5)))  ## Demo

    visitor = Intrepid.new_visitor('visitor-A', context={'testing_tracking_manager': True})
    visitor.fetch_flags()
    visitor.get_flag("my_flag", 'default').value()
    visitor.send_hit(Screen("screen 1"))
    time.sleep(2)




init()