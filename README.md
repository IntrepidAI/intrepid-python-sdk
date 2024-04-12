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



# Write to Graph
i_sdk0 = Intrepid(topic="5b374215-f829-4efa-9719-cbb4f6c4596b")
node_specs = i_sdk0.info()
node_status = i_sdk0.status()

...

i_sdk0.write("output_1", result_f)


# Read from Graph
i_sdk1 = Intrepid(topic="8268a31d-40cc-4b85-bf06-d425d72f743e")
my_var = i_sdk.read("res")
...
i_sdk0.write("output_1", result_f)



# Create QoS policy for function node
qos = intrepid.create_qos(intrepid.DEFAULT_QOS_POLICY)
in_nodes = list(<node_id>)
out_nodes = list(<node_id>)
# intrepid.init(qos, in_nodes, out_nodes)
intrepid.init("5b374215-f829-4efa-9719-cbb4f6c4596b")

var_a = intrepid.read(<node_id>, <output_id>)
var_b = intrepid.read(<node_id>, <output_id>)

result_f, result_s = foo(var_a, var_b)

# Write float and str values and return
intrepid.write(<node_id>, <input_id>, result_f)
intrepid.write(<node_id>, <input_id>, result_s)

# Close session
intrepid.close()
```

`node_id`, `input_id`, `output_id` are in the property section of the sidebar of the relative nodes.