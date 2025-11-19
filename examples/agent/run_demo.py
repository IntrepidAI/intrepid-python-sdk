# run_demo.py
import asyncio
# from intrepid_python_sdk.agent.adapters import DemoAdapter, PX4Adapter, ROS2Adapter
# from intrepid_python_sdk.agent.adapter import action, sensor
from intrepid_python_sdk import Intrepid, Qos, Node, IntrepidType, Type



# TODO
# what if adapters need to exchange large payloads (via runtime)
# VSC extension from capabilities, generate boiler plate with actions to write an adapter for


# creates `demo_adapter/my_node_1` and `demo_adapter/my_node_2`
# async def main():
    # runtime = Intrepid()
    # @runtime.action("ActionName1")
    # async def my_node_1():
    #     # YOUR CODE HERE
    #     pass
    # @runtime.action("ActionName2")
    # async def my_node_2(params):
    #     # YOUR CODE HERE
    #     pass
    # runtime.listen(1111)
    # then run
    # ./intrepid-agent -l ws://localhost:1111 --web run ./graph.json



# async def main():
#     # TODO can load from file (or pass file path directly)
#     # graph = {}  # for MVP: can be a stub; runtime is tiny
#     # capabilities = {}

#     # TODO define robot capabilities for action validation
#     # TODO from dash user can create an action node. Such node must be mapped to an adapter.
#     # if not, abort.
#     # action node has inputs, outputs, node_name (same as action name to be mapped to adapter)

#     # Create my node
#     mynode = Node()
#     mynode.from_def("./node.toml")

#     runtime = Intrepid()
#     runtime.register_node(mynode)

#     @runtime.action("ActionName1")
#     async def my_node_1():
#         # YOUR CODE HERE
#         pass

#     @runtime.action("ActionName2")
#     async def my_node_2(params):
#         # YOUR CODE HERE
#         pass


#     # load from file
#     # runtime.load_capabilities("filepath/caps.toml")
#     # load from file
#     # runtime.load_graph("filepath/graph.json")
#     # load graph from hub
#     # runtime.load_graph("graph_id")

#     # runtime.set_capabilities(capabilities)
#     # runtime.set_graph(graph)

#     # Create adapters
#     # demo_adapter = DemoAdapter(runtime, robot_id="demo-01")
#     # control_adapter = PX4Adapter()
#     # # heavy_cv_detector = CVAdapter()

#     # await runtime.register_adapter("demo-adapter", demo_adapter)
#     # await runtime.register_adapter("control-adapter", control_adapter)
#     # await runtime.register_adapter("cv-adapter", heavy_cv_detector)

#     # Validate all graph actions are mapped to adapters and start (or abort)
#     await runtime.start()



#     # runtime = RuntimeClient(graph)
#     # runtime.set_capabilities(capabilities)
#     # at this point agent shows appropriate node library
#     # define adapters and register
#     # demo_adapter = DemoAdapter(runtime, robot_id="demo-01")
#     # control_adapter = PX4Adapter()
#     # heavy_cv_detector = CVAdapter()
#     # await runtime.register_adapter("demo-adapter", demo_adapter)
#     # await runtime.register_adapter("control-adapter", control_adapter)
#     # TODO validate that graph is satisfied (all adapters are registered)
#     # await runtime.start()
#     # In real usage: load behavior graph, runtime will request actions, call adapter.handle_action_request(...)
#     # await asyncio.sleep(10)
#     # await runtime.stop()

# # if __name__ == "__main__":
# #     asyncio.run(main())

# Create my node
mynode = Node()
mynode.from_def("./node.toml")

runtime = Intrepid()
runtime.register_node(mynode)

# @runtime.action("ActionName1")
# async def my_node_1():
#     # YOUR CODE HERE
#     pass

# @runtime.action("ActionName2")
# async def my_node_2(params):
#     # YOUR CODE HERE
#     pass

def foo():
    pass

runtime.register_action("action_1", foo)
# runtime.register_action("action_1", foo)

runtime.start(port=1111)
