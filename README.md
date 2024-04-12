# Build and Install

First install `poetry` with `pip install poetry`

Then build with

`poetry build`

and install with

`poetry install`



# Example for showcasing Python bindings

## Create Python Node

A Python node is created from dashboard and rendered according to the Python function signature that is attached.

A Python SDK allows to
1. read from the output of a node and
2. write to the input of a node.

Rendering a node means defining inputs and outputs complete with types (only primitive types supported).

```python
import intrepid

def foo(a: int, b: int) -> (float, str):
  # ADD CODE HERE


# Create QoS policy for function node
qos = intrepid.create_qos(intrepid.DEFAULT_QOS_POLICY)

# Write to Graph
node_0 = Intrepid(node_id="5b374215-f829-4efa-9719-cbb4f6c4596b", qos=qos)
node_specs = node_0.info()
node_status = node_0.status()

...

node_0.write(to="output_1", data=result_f)


# Read from Graph
node_1 = Intrepid(node_id="8268a31d-40cc-4b85-bf06-d425d72f743e")
my_var = node_1.read("res")
...

result_f, result_s = foo(my_var, var_b)

...

node_0.write(to="output_1", data=result_f)


# Close sessions
node_0.close()
node_1.close()
```

`node_id`, `input_id`, `output_id` are in the property section of the sidebar of the relative nodes.