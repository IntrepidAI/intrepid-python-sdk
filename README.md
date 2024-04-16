# Build and Install

First install `poetry` with `pip install poetry`

Then build with

`poetry build`

and install with

`poetry install`


python3 -m websockets ws://localhost:9999/



# Example for showcasing Python bindings

## Create Python Node

A Python node is created from dashboard and rendered according to the Python function signature that is attached.

A Python SDK allows to
1. read from the output of a node and
2. write to the input of a node.

Rendering a node means defining inputs and outputs complete with types (only primitive types supported).

```python
from intrepid import Intrepid, Qos


# Callback function to execute when inputs are ready
def my_callback_function(in1: int, in2:int) -> int:
    # Add code here
    # Extract variables from args
    a = args.get('in1', 0)  # Default value 0 if 'a' is not in args
    b = args.get('in2', 0)  # Default value 0 if 'b' is not in args

    return a + b

# Create QoS policy for function node
# qos = Qos(reliability="BestEffort", durability="TransientLocal")
# qos.set_history("KeepLast")
# qos.set_deadline(100)  # Deadline expressed in milliseconds


# Write to Graph
node_0 = Intrepid(node_id="node_type/node_id")
# Attach Qos policy to this node
# node_0.create_qos(qos)

# Request node status
node_status = node_0.status()

# Request node info
# node_info = node_0.info()

# Register callback with node input. Callback and node inputs must have the same signature (same number/name/type)
node_0.register_callback(my_callback_function)
...

node_0.start()



# Write to node output
node_0.write(target="output_1", data=result_f)


# Read from Graph (node)
node_1 = Intrepid(node_id="8268a31d-40cc-4b85-bf06-d425d72f743e")
my_var = node_1.read(source="res")
...

result_f, result_s = foo(my_var, var_b)

...

node_0.write(to="output_1", data=result_f)


# Close sessions
node_0.close()
node_1.close()
```

`node_id`, `input_id`, `output_id` are in the property section of the sidebar of the relative nodes.