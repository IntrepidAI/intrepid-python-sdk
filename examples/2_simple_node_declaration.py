"""
Intrepid Python SDK example:

- Node is declared with SDK utility functions
- Callback function is declared and type annotated.
- Callback is registered as a closure

"""

from intrepid_python_sdk import Intrepid, Qos, Node, Type, IntrepidType
import time


# Callback function to execute when inputs are ready
def my_callback_function(in1: int, in2:int) -> (float, bool):
    # Add code here
    time.sleep(0.5)
    return 1. * (in1 + in2), True


# Create QoS policy for function node
qos = Qos(reliability="BestEffort", durability="TransientLocal")
qos.set_history("KeepLast")
qos.set_deadline(100)  # Deadline expressed in milliseconds


# Create my node
node_type = "node/sdk/2-node"
mynode = Node(node_type)
mynode.add_input("flow", IntrepidType(Type.FLOW))
mynode.add_input("in1", IntrepidType(Type.INTEGER))
mynode.add_input("in2", IntrepidType(Type.INTEGER))
mynode.add_output("flow", IntrepidType(Type.FLOW))
mynode.add_output("out1", IntrepidType(Type.FLOAT))
mynode.add_output("is_float", IntrepidType(Type.BOOLEAN))

# Write to Graph
service_handler = Intrepid()
service_handler.register_node(mynode)

# Attach Qos policy to this node
service_handler.create_qos(qos)

# Register callback with node input. Callback and node inputs must have the same signature (same number/name/type)
service_handler.register_callback(lambda: my_callback_function)

# Start server and node execution
service_handler.start()