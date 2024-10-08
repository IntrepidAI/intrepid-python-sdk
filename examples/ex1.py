from intrepid import Intrepid, Qos, Node, DataType
import time


# Callback function to execute when inputs are ready
def my_callback_function(in1: int, in2:int) -> (float, bool):
    # Add code here
    time.sleep(0.5)
    return 1. * (in1 + in2), True


# Create QoS policy for function node
# Create QoS policy for function node
qos = Qos(reliability="BestEffort", durability="TransientLocal")
qos.set_history("KeepLast")
qos.set_deadline(100)  # Deadline expressed in milliseconds


# Create my node
node_type = "node/sdk/ex1"
mynode = Node(node_type)
mynode.add_input("flow", DataType.FLOW)
mynode.add_input("in1", DataType.INTEGER)
mynode.add_input("in2", DataType.INTEGER)
mynode.add_output("flow", DataType.FLOW)
mynode.add_output("out1", DataType.FLOAT)
mynode.add_output("is_float", DataType.BOOLEAN)
print("Created node ", mynode.get_type())

# Write to Graph
service_handler = Intrepid()
service_handler.register_node(mynode)

# Attach Qos policy to this node
service_handler.create_qos(qos)
print("Attached QoS policy to node")

# Register callback with node input. Callback and node inputs must have the same signature (same number/name/type)
service_handler.register_callback(my_callback_function)
print("Callback registered to node")

# Start server and node execution
service_handler.start()