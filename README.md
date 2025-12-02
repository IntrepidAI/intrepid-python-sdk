
# Build and Install

## Build from pip

`pip install intrepid-python-sdk`

## Build from sources

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
You can now connect Intrepid Agent to 0.0.0.0:8765
```


## Start Intrepid Runtime Core

Execute the Intrepid runtime (`intrepid-agent`) with arguments
`--web` to expose the control dashboard to localhost
`--load ws://<host>:<port>` where the service is running


```Bash
./intrepid-agent --web --load ws://localhost:8765
```

This should show

```Bash


  ╔══════════════════════════════════╗
  ║                                  ║
  ║ 🚀  Web service is running on:   ║
  ║                                  ║
  ║ 🔗  http://127.0.0.1:9180        ║
  ║                                  ║
  ╚══════════════════════════════════╝

```

Point the browser to `http://127.0.0.1:9180` and search for the exposed nodes (right click and search)
At this point you can create the behavior you need, by importing and connecting the nodes you need.
Click `Run` to execute such behavior.


## Publish node

Not yet implemented.

# Examples

An exhaustive list of sample nodes is provided in `examples/agent/run_demo.py`.

An example to call ROS2 utilities is provided in `examples/agent/ros2_demo.py`