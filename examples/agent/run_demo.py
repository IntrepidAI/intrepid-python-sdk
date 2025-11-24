import asyncio
from intrepid_python_sdk.agent.adapter import action, sensor
from intrepid_python_sdk import Intrepid, Qos, Node, IntrepidType, Type
from intrepid_python_sdk.intrepid_types import TYPE_MAP, Context, Vec3



if __name__ == "__main__":
    runtime = Intrepid(namespace="test")

    def simple_node(a: int, b: int) -> int:
        """Example node that adds two numbers"""
        return a + b

    def simple_node_with_defaults(a: int = 10, b: int = 10) -> int:
        """Example node that adds two numbers (with default values)"""
        return a + b

    def node_with_array_type(a: list[int]) -> int:
        """Example node that calculates length of an array"""
        return len(a)

    def node_with_multiple_outputs(a: int, b: int) -> tuple[int, int]:
        """Example node that returns two numbers"""
        return a + b, a - b

    def node_with_complex_types(a: Vec3, b: Vec3) -> Vec3:
        """Example node that adds two vectors"""
        return Vec3(x=a.x + b.x, y=a.y + b.y, z=a.z + b.z)

    async def async_node(a: int, b: int) -> int:
        """Example async node"""
        await asyncio.sleep(0.2)
        return a + b

    async def node_with_feedback(ctx: Context, message: str):
        """Example node that logs a message (note that it must be async)"""
        await ctx.debug_log("My message is:")
        await ctx.debug_log(message)

    async def node_with_state(ctx: Context[int]) -> int:
        """Example node that increments a number on each call"""
        if ctx.state is None:
            ctx.state = 0
        ctx.state += 1
        return ctx.state

    runtime.register(simple_node)
    runtime.register(simple_node_with_defaults)
    runtime.register(node_with_array_type)
    runtime.register(node_with_multiple_outputs)
    runtime.register(node_with_complex_types)
    runtime.register(async_node)
    runtime.register(node_with_feedback)
    runtime.register(node_with_state)
    runtime.start("0.0.0.0", 8765)
