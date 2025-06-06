"""
Intrepid Python SDK example:

- Node is declared via toml configuration file
- Callback function is implemented with a closure, in order to use in-scope variables
- Callback is registered as a regular function

"""

from intrepid_python_sdk import Intrepid, Qos, Node, IntrepidType, Type


# Callback function to execute when inputs are ready
def my_callback_function():
    my_vars = []

    def foo(agent_id: int) -> float:
        # do something with my_vars
        return (1.0, 1.0)
    return foo


# Create QoS policy for function node
qos = Qos(reliability="BestEffort", durability="TransientLocal")
qos.set_history("KeepLast")
qos.set_deadline(100)  # Deadline expressed in milliseconds

# Create my node
mynode = Node()
mynode.from_def("./3_node_config.toml")
# Write to Graph
service_handler = Intrepid()
service_handler.register_node(mynode)
# Attach QoS policy to this node
service_handler.create_qos(qos)
# Register callback with node input. Callback and node inputs must have the same signature (same number/name/type)
service_handler.register_callback(my_callback_function)
# Start server and node execution
service_handler.start()