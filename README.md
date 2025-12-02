# Build and Install


Create a new conda environment with `conda create -n intrepid python=3.10`

Activate environment with

```
conda activate intrepid
```

Install `poetry` with `pip install poetry` and all requirements `pip install -r requirements.txt`

Build Python Intrepid SDK

```Bash
poetry build
poetry install
```
And check that all has been installed correctly

```
python examples/ex0.py
```

This should print

```
Hello from Intrepid SDK
```


<!-- `python3 -m websockets ws://localhost:9999/` -->



# Example for showcasing Python bindings

## Create Python Node

A Python node is created from dashboard and rendered according to the Python function signature that is attached.

A Python SDK allows to
1. register any user-defined function to the runtime and
2. execute the service that exposes such function(s)

In the example below, two functions are declared and registered to the Intrepid runtime. Finally the runtime is started and made ready for execution


```python
import asyncio
from intrepid_python_sdk import Intrepid
from pydantic import BaseModel


def simple_node(a: int, b: int) -> int:
    """Example node that adds two numbers"""
    return a + b

def simple_node_with_defaults(a: int = 10, b: int = 10) -> int:
    """Example node that adds two numbers (with default values)"""
    return a + b


if __name__ == "__main__":
    runtime = Intrepid(namespace="test")
    runtime.register_node(simple_node)
    runtime.register_node(simple_node_with_defaults, label="SimpleNodeDefault", description="A node handling types with default values")
    runtime.start("0.0.0.0", 8765)
```

The code above can be saved to `my_node.py` and executed with `python my_node.py`

```Shell
You can now connect Intrepid Agent to `0.0.0.0:8765`
```


## Start Intrepid Runtime Core

Execute the Intrepid runtime (`intrepid-agent`) with arguments
`run-node` <node_name>
`--load ws://<host>:<port>` where the service is running


```Bash
./intrepid-agent --web --load ws://localhost:8765
```

This should show

```Bash



```

The node is running and computing the callback function, and returning `3.0`

## Publish custom node

In order to be viewed from the dashboard and connected to the rest of the graph, a node must be published.
An authentication token is necessary to publish a node to a user library. Such token can be retrieved from dashboard at https://labs.intrepid.ai from the `Project` section on the left sidebar.


```Bash
./intrepid-agent publish node/sdk/ex1 --load ws://127.0.0.1:9999 https://labs.intrepid.ai/projects/34/r3Gv...otpm

```

If node is published correctly, this will be printed to stdout

```Bash
intrepid.ai/projects/34/Uy66ce2RCqqOniGLBuNGcaUu
2024-10-08T15:15:28.790Z INFO  [exec_graph_connector::plugins] remote plugin initialized: ws://127.0.0.1:9999
2024-10-08T15:15:28.795Z INFO  [exec_graph_connector::http] -> https://labs.intrepid.ai/api/nodes/sdk
2024-10-08T15:15:28.833Z INFO  [exec_graph_connector::http] <- 201, length: 43
```
