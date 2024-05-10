import asyncio
import sys
import time
import signal
import sys
import json

# from intrepid import *
from intrepid import Intrepid, Qos, Node, DataType
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
def my_callback_function(in1: int, in2:int) -> (float, bool):
    # Add code here
    time.sleep(0.02)
    return 1. * (in1 + in2), True


def init():
    print(sys.version)

    # Create QoS policy for function node
    qos = Qos(reliability="BestEffort", durability="TransientLocal")
    qos.set_history("KeepLast")
    qos.set_deadline(100)  # Deadline expressed in milliseconds

    # Create my node
    mynode = Node("my_type")
    mynode.add_input("flow", DataType.FLOW)
    mynode.add_input("in1", DataType.INTEGER)
    mynode.add_input("in2", DataType.INTEGER)
    # mynode.add_input("in3", DataType.STRING)
    # mynode.add_input("in4", DataType.FLOW)
    # mynode.add_input("in5", DataType.ANY)
    # mynode.add_input("in5", DataType.ANY_OR_FLOW)
    # mynode.add_input("in5", DataType.WILDCARD)
    mynode.add_output("flow", DataType.FLOW)
    mynode.add_output("out1", DataType.FLOAT)
    mynode.add_output("is_float", DataType.BOOLEAN)

    mynode.get_inputs()
    mynode_json = mynode.to_json()
    print(mynode_json)

    # Write to Graph
    node_handler = Intrepid(node_id="python/project/node_type/node_id")

    node_handler.register_node(mynode)


    # Attach Qos policy to this node
    node_handler.create_qos(qos)

    # Request node status
    node_status = node_handler.status()

    # Request node info
    node_info = node_handler.info()

    # Register callback with node input. Callback and node inputs must have the same signature (same number/name/type)
    node_handler.register_callback(my_callback_function)

    # Start server and node execution
    node_handler.start()



try:
    while True:
        init()        # Your main program logic goes here
except KeyboardInterrupt:
    print("KeyboardInterrupt detected. Goodbye...")
    sys.exit(0)

