#!/usr/bin/env python

import asyncio
import inspect
from pydantic import BaseModel
from protocol import (
    Discovery,
    DiscoveryNodeSpec,
    DiscoveryOptions,
    DiscoveryPinContainer,
    DiscoveryPinSpec,
    DiscoveryPinType,
    DiscoveryPinTypeKind,
    Empty,
    ExecReply,
    IncomingMessage,
    InitCommand,
    OutgoingMessage,
)
from typing import Any, Awaitable, Callable, Generic, NewType, TypeVar, get_args, get_origin
from websockets.asyncio.server import serve

T = TypeVar('T')
class Context(Generic[T]):
    state: T | None
    debug_log_callback: Callable[[str], Awaitable[None]]

    def __init__(self, state: T | None, debug_log_callback: Callable[[str], Awaitable[None]]):
        self.state = state
        self.debug_log_callback = debug_log_callback

    async def debug_log(self, message: str) -> None:
        await self.debug_log_callback(message)

Boolean = NewType("Boolean", bool)
F32 = NewType("F32", float)
F64 = NewType("F64", float)
I8 = NewType("I8", int)
I16 = NewType("I16", int)
I32 = NewType("I32", int)
I64 = NewType("I64", int)
I128 = NewType("I128", int)
U8 = NewType("U8", int)
U16 = NewType("U16", int)
U32 = NewType("U32", int)
U64 = NewType("U64", int)
U128 = NewType("U128", int)
String = NewType("String", str)
Text = NewType("Text", str)

class Vec2(BaseModel):
    x: float
    y: float

class Vec3(BaseModel):
    x: float
    y: float
    z: float

class Vec4(BaseModel):
    x: float
    y: float
    z: float
    w: float

class Bivec2(BaseModel):
    xy: float

class Bivec3(BaseModel):
    yz: float
    zx: float
    xy: float

class Rotor2(BaseModel):
    s: float
    xy: float

class Rotor3(BaseModel):
    s: float
    yz: float
    zx: float
    xy: float

class Intrepid:
    class Node(BaseModel):
        func: Callable
        spec: DiscoveryNodeSpec
        first_arg_is_context: bool
        tuple_output: bool
        input_types: list[Any]
        output_types: list[Any]

    namespace: str | None = None
    init_timeout: float = 2
    exec_timeout: float = 2
    all_nodes: dict[str, Node] = {}
    type_map: dict[type, str] = {
        bool: "boolean",
        float: "f64",
        int: "i64",
        str: "string",
        Boolean: "boolean",
        F32: "f32",
        F64: "f64",
        I8: "i8",
        I16: "i16",
        I32: "i32",
        I64: "i64",
        I128: "i128",
        U8: "u8",
        U16: "u16",
        U32: "u32",
        U64: "u64",
        U128: "u128",
        String: "string",
        Text: "text",
        Vec2: "vec2",
        Vec3: "vec3",
        Vec4: "vec4",
        Bivec2: "bivec2",
        Bivec3: "bivec3",
        Rotor2: "rotor2",
        Rotor3: "rotor3",
    }

    def __init__(self, namespace: str | None = None):
        self.namespace = namespace

    async def listen(self, host: str, port: int):
        async with serve(self._websocket_handler, host, port) as server:
            print(f"server is running on ws://{host}:{port}")
            await server.serve_forever()

    def register(
        self,
        func: Callable,
        *,
        name: str | None = None,
        label: str | None = None,
        description: str | None = None,
    ):
        # if callable(name):
        #     raise TypeError(
        #         "@register decorator was used incorrectly, use @register() instead of @register"
        #     )

        def name_to_label(name: str) -> str:
            label = name.split('/')[-1].replace('_', " ")
            return label.title()

        def get_type_name(annotation: type) -> tuple[str, DiscoveryPinContainer]:
            if get_origin(annotation) is list:
                inner_type = get_args(annotation)[0]
                type_name = self.type_map.get(inner_type)
                type_container = DiscoveryPinContainer.ARRAY
                if type_name is None:
                    raise ValueError(f"unsupported inner type in list: {inner_type}")
            else:
                type_name = self.type_map.get(annotation)
                type_container = DiscoveryPinContainer.SINGLE
                if type_name is None:
                    raise ValueError(f"unsupported type: {annotation}")

            return type_name, type_container

        def decorator(func: Callable) -> Callable:
            node_name = name or func.__name__

            if node_name == "<lambda>":
                raise ValueError("you must provide a name for lambda functions")

            full_name = f"{self.namespace}/{node_name}" if self.namespace else node_name
            node_doc = description or func.__doc__ or None

            inputs: list[DiscoveryPinSpec] = []
            outputs: list[DiscoveryPinSpec] = []

            inputs.append(DiscoveryPinSpec(
                label="",
                type=DiscoveryPinType(kind=DiscoveryPinTypeKind.FLOW),
            ))
            outputs.append(DiscoveryPinSpec(
                label="",
                type=DiscoveryPinType(kind=DiscoveryPinTypeKind.FLOW),
            ))

            sig = inspect.signature(func, eval_str=True)
            first_arg_is_context = False
            tuple_output = False
            input_types: list[Any] = []
            output_types: list[Any] = []

            for i, param in enumerate(sig.parameters.values()):
                if param.annotation is Context or get_origin(param.annotation) is Context:
                    if i != 0:
                        raise ValueError(f"context must be the first parameter")

                    first_arg_is_context = True
                    continue

                if param.annotation is inspect.Parameter.empty:
                    raise ValueError(f"parameter {param.name} needs type annotation")

                type_name, type_container = get_type_name(param.annotation)
                inputs.append(DiscoveryPinSpec(
                    label=param.name,
                    type=DiscoveryPinType(kind=DiscoveryPinTypeKind.DATA, data_type=type_name),
                    container=type_container,
                    default=None if param.default is inspect._empty else param.default,
                ))
                input_types.append(param.annotation)

            if sig.return_annotation is not inspect.Parameter.empty:
                if get_origin(sig.return_annotation) is tuple:
                    tuple_output = True
                    for i, inner_type in enumerate(get_args(sig.return_annotation)):
                        type_name, type_container = get_type_name(inner_type)
                        outputs.append(DiscoveryPinSpec(
                            label=f"out{i+1}",
                            type=DiscoveryPinType(kind=DiscoveryPinTypeKind.DATA, data_type=type_name),
                            container=type_container,
                        ))
                        output_types.append(inner_type)
                else:
                    type_name, type_container = get_type_name(sig.return_annotation)
                    outputs.append(DiscoveryPinSpec(
                        label="out",
                        type=DiscoveryPinType(kind=DiscoveryPinTypeKind.DATA, data_type=type_name),
                        container=type_container,
                    ))
                    output_types.append(sig.return_annotation)

            self.all_nodes[full_name] = Intrepid.Node(
                func=func,
                spec=DiscoveryNodeSpec(
                    type=full_name,
                    label=label or name_to_label(node_name),
                    description=node_doc,
                    inputs=inputs,
                    outputs=outputs,
                ),
                first_arg_is_context=first_arg_is_context,
                tuple_output=tuple_output,
                input_types=input_types,
                output_types=output_types,
            )
            return func

        return decorator(func)

    async def _websocket_handler(self, websocket: Any):
        class ActiveNode(BaseModel):
            node: Intrepid.Node
            state: Any

        active_nodes: dict[int, ActiveNode] = {}

        def assert_spec_matches(spec: DiscoveryNodeSpec, command: InitCommand):
            spec_exec_inputs = [input for input in spec.inputs or [] if input.type.kind == DiscoveryPinTypeKind.FLOW]
            if len(command.exec_inputs) != len(spec_exec_inputs):
                raise ValueError("expected %d flow inputs, got %d" % (len(spec_exec_inputs), len(command.exec_inputs)))

            spec_exec_outputs = [output for output in spec.outputs or [] if output.type.kind == DiscoveryPinTypeKind.FLOW]
            if len(command.exec_outputs) != len(spec_exec_outputs):
                raise ValueError("expected %d flow outputs, got %d" % (len(spec_exec_outputs), len(command.exec_outputs)))

            spec_data_inputs = [input for input in spec.inputs or [] if input.type.kind != DiscoveryPinTypeKind.FLOW]
            if len(command.data_inputs) != len(spec_data_inputs):
                raise ValueError("expected %d data inputs, got %d" % (len(spec_data_inputs), len(command.data_inputs)))

            spec_data_outputs = [output for output in spec.outputs or [] if output.type.kind != DiscoveryPinTypeKind.FLOW]
            if len(command.data_outputs) != len(spec_data_outputs):
                raise ValueError("expected %d data outputs, got %d" % (len(spec_data_outputs), len(command.data_outputs)))

        async for data in websocket:
            print(f"<-- {data}")
            command = IncomingMessage.model_validate_json(data)

            try:
                if command.discovery:
                    reply = OutgoingMessage(
                        id=command.id,
                        node=command.node,
                        discovery_ok=Discovery(
                            options=DiscoveryOptions(
                                init_timeout=self.init_timeout,
                                exec_timeout=self.exec_timeout,
                            ),
                            nodes=[self.all_nodes[node].spec for node in self.all_nodes],
                        )
                    )
                elif command.init:
                    node = self.all_nodes[command.init.node_type]
                    if node is None:
                        reply = OutgoingMessage(
                            id=command.id,
                            node=command.node,
                            error=f"node {command.init.node_type} not found",
                        )
                    else:
                        assert_spec_matches(node.spec, command.init)
                        active_nodes[command.node or 0] = ActiveNode(node=node, state=None)
                        reply = OutgoingMessage(
                            id=command.id,
                            node=command.node,
                            init_ok=Empty(),
                        )
                elif command.exec:
                    active_node = active_nodes[command.node or 0]
                    state = active_node.state
                    func = active_node.node.func
                    context = None

                    def deserialize_single_input(data: Any, annotation: Any) -> Any:
                        if issubclass(annotation, BaseModel):
                            return annotation.model_validate(data)
                        else:
                            return data

                    def deserialize_any_input(data: Any, annotation: Any) -> Any:
                        if get_origin(annotation) is list:
                            inner_type = get_args(annotation)[0]
                            return [deserialize_single_input(data, inner_type) for data in data]
                        else:
                            return deserialize_single_input(data, annotation)

                    inputs = []
                    for i, type in enumerate(active_node.node.input_types):
                        inputs.append(deserialize_any_input(command.exec.inputs[i], type))

                    if active_node.node.first_arg_is_context:
                        async def debug_log_callback(message: str) -> None:
                            debug_reply = OutgoingMessage(
                                id=0,
                                node=command.node,
                                debug_message=message,
                            )
                            data = debug_reply.model_dump_json(exclude_none=True)
                            print(f"--> {data}")
                            await websocket.send(data)

                        context = Context(state, debug_log_callback)
                        inputs = [context] + inputs

                    if inspect.iscoroutinefunction(func):
                        result = await func(*inputs)
                    else:
                        result = func(*inputs)

                    if not active_node.node.tuple_output:
                        result = [result]

                    if context is not None:
                        active_nodes[command.node or 0].state = context.state

                    reply = OutgoingMessage(
                        id=command.id,
                        node=command.node,
                        exec_ok=ExecReply(
                            exec_id=command.exec.exec_id,
                            outputs=result,
                        ),
                    )
                else:
                    reply = OutgoingMessage(
                        id=command.id,
                        node=command.node,
                        error="unsupported command",
                    )

                data = reply.model_dump_json(exclude_none=True)

            except Exception as e:
                reply = OutgoingMessage(
                    id=command.id,
                    node=command.node,
                    error=str(e),
                )
                import traceback
                traceback.print_exc()
                data = reply.model_dump_json(exclude_none=True)

            print(f"--> {data}")
            await websocket.send(data)

async def main() -> None:
    runtime = Intrepid("test")

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

    await runtime.listen("0.0.0.0", 8765)

if __name__ == "__main__":
    asyncio.run(main())
