import asyncio
import sys
import time
import signal
import sys


# from intrepid import *
from intrepid import Intrepid, Qos
# from intrepid.cache_manager import SqliteCacheManager
# from intrepid.config import DecisionApi, Bucketing
# from intrepid.hits import Screen
# from intrepid.tracking_manager import TrackingManagerConfig



# def signal_handler(sig, frame):
#     print("Ctrl+C detected. Goodbye...")
#     sys.exit(0)

# # Set up the signal handler for SIGINT (Ctrl+C)
# signal.signal(signal.SIGINT, signal_handler)


# Callback function to execute when inputs are ready
def my_callback_function(in1: int, in2:int) -> int:
    # Add code here

    return in1 + in2


def init():
    print(sys.version)

    # Create QoS policy for function node
    qos = Qos(reliability="BestEffort", durability="TransientLocal")
    qos.set_history("KeepLast")
    qos.set_deadline(100)  # Deadline expressed in milliseconds

    # Write to Graph
    node_0 = Intrepid(node_id="node_type/node_id")

    # Attach Qos policy to this node
    node_0.create_qos(qos)

    # Request node status
    node_status = node_0.status()

    # Request node info
    node_info = node_0.info()

    # Register callback with node input. Callback and node inputs must have the same signature (same number/name/type)
    node_0.register_callback(my_callback_function)

    # Start server and node execution
    node_0.start()


try:
    while True:
        init()        # Your main program logic goes here
except KeyboardInterrupt:
    print("KeyboardInterrupt detected. Goodbye...")
    sys.exit(0)

