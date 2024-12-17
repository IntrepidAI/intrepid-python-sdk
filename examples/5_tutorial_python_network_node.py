from intrepid_python_sdk import Intrepid, Qos, Node, IntrepidType, Type
import math



# Callback function to execute when inputs are ready
def my_callback_function():
    counter = 0

    def closure(dest_host: str, dest_port: int, header: str, message: str) -> (int, str):
        # Extract components
        # TODO

        nonlocal counter

        status = 200
        response = "hello world"

        return status, response

    return closure



# Create my node
mynode = Node()
mynode.from_def("./netnode_config.toml")
inputs = mynode.get_inputs()

# Write to Graph
service_handler = Intrepid()
service_handler.register_node(mynode)

# Create QoS policy for function node
qos = Qos(reliability="BestEffort", durability="TransientLocal")
qos.set_history("KeepLast")
qos.set_deadline(100)  # Deadline expressed in milliseconds
service_handler.create_qos(qos)

# Register callback with node input. Callback and node inputs must have the same signature (same number/name/type)
service_handler.register_callback(my_callback_function)

# Start server and node execution
service_handler.start()
