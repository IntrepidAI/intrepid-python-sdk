from __future__ import absolute_import
from __future__ import unicode_literals
import logging
from typing import Callable, Dict, List, Optional, get_args, get_origin
from collections.abc import Iterable
import asyncio
import inspect
import importlib_metadata
import os, sys
# import subprocess
from pydantic import BaseModel
from websockets.server import serve, unix_serve
from intrepid_python_sdk.config import _IntrepidConfig
from datetime import datetime
import signal
from intrepid_python_sdk.config_manager import ConfigManager
from intrepid_python_sdk.constants import WS_HOST, WS_PORT, TAG_STATUS, TAG_HTTP_REQUEST, \
    INFO_STATUS_CHANGED, TAG_INITIALIZATION, INFO_CALLBACK_REGISTERED, \
    INFO_READY, INFO_WSSERVER_READY, INFO_STOPPED, INFO_SDK_READY, \
    ERROR_CONFIGURATION, ERROR_PARAM_TYPE, ERROR_PARAM_NUM, ERROR_PARAM_NAME, ERROR_REGISTER_CALLBACK
from intrepid_python_sdk.decorators import param_types_validator
from intrepid_python_sdk.errors import InitializationParamError
from intrepid_python_sdk.log_manager import LogLevel
from intrepid_python_sdk.utils import log, log_exception, signal_handler
from intrepid_python_sdk.status import Status
from intrepid_python_sdk.node import Node, Type, IntrepidType, DataElement
from intrepid_python_sdk.qos import Qos
from intrepid_python_sdk.message import IntrepidMessage, Opcode, InitRequest, ExecRequest, ExecResponse

# from intrepid_python_sdk.simulator import Simulator
# from intrepid_python_sdk.entity import Entity, WorldEntity
# from intrepid_python_sdk.vehicle import Vehicle
# from intrepid_python_sdk.sim_client import SimClient
# from simulator.simulator import Simulator

import aiohttp
from aiohttp import web, WSCloseCode
import asyncio
import json
from typing import Callable, Dict, Any
from .protocol import (
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
from .intrepid_types import TYPE_MAP, Context
from . import constants
from .constants import TAG_APP_NAME

__name__ = TAG_APP_NAME
__version__ = importlib_metadata.distribution(__name__).version


# Set up the signal handler for SIGINT (Ctrl+C)
signal.signal(signal.SIGINT, signal_handler)

# TODO remove this and use log_manager
# Configure logging
logging.basicConfig(level=logging.INFO)  # Set the logging level to INFO or desired level
# Define ANSI escape codes for colors
# COLOR_RED = "\033[91m"
# COLOR_RESET = "\033[0m"

# Custom logging format with timestamp
log_format = "%(asctime)s - %(levelname)s - %(message)s"
logging.basicConfig(format=log_format)
logger = logging.getLogger(__name__)  # Create a logger instance



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
    debug_mode: bool = False

    __instance = None
    __restarted = None
    __original_callback = None

    def __init__(self, *, namespace: str | None = None):
        """
        Initialize the Intrepid SDK.

        @param node_id: Unique identifier of the node managed by this handler
        @param qos: Dictionary that specifies the QoS applied to this node (Not Implemented)
        @return:
        """

        self.namespace = namespace
        self.qos = None
        # self.__unix_socket_path = None
        self.__node = None
        self.__node_info = None
        self.__callback = None
        # websocket server extended by decorated functions (endpoints)
        self.__app = None
        self.__runner = self.create_runner()

    async def websocket_handler(self, request: Any):
        websocket = web.WebSocketResponse()
        await websocket.prepare(request)

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

        async for message in websocket:
            data = message.data
            if self.debug_mode:
                logger.info(f"<-- {data}")
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
                            if self.debug_mode:
                                logger.info(f"--> {data}")
                            await websocket.send_str(data)

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
                        error= constants.ERROR_UNSUPPORTED_COMMAND,
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

            if self.debug_mode:
                logger.info(f"--> {data}")
            await websocket.send_str(data)

        return websocket

    async def restart_node(self):
        """
        Restart the node by re-registering and resetting its state.
        """
        logger.info("Restarting the node...")
        await asyncio.sleep(1.0)  # Allow loop to settle

        # if self.__node:
        #     self.register_node(self.__node)
        #     if self.__callback:
        #         self.register_callback(self.__callback)
        # else:
        #     logger.warning("Node is not registered. Skipping restart.")

        # current_loop = asyncio.get_event_loop()
        # tasks = asyncio.all_tasks(current_loop)
        # for task in tasks:
        #     task.cancel()
        # try:
        #     current_loop.stop()
        # except Exception as e:
        #     logger.warning(f"Error stopping the current loop: {e}")
        # finally:
        #     await asyncio.sleep(0.1)  # Allow loop to settle


        logger.info(self.__original_callback)
        # self.register_callback(self.__callback)
        self.__callback = None
        # Reset node information if needed
        self.__node = None
        self.__node_info = None

        # Restart the node by re-registering the callback
        if self.__original_callback is not None:
            logger.info("Re-registering the original callback...")
            self.register_callback(self.__original_callback)

        self.__restarted = True
        logger.info("Node restart completed.")
        await asyncio.sleep(1.0)  # Allow loop to settle
        # Close and clean up resources
        self.cleanup()

    def create_runner(self):
        self.__app = web.Application()
        self.__app.add_routes([
            web.get('/', self.websocket_handler),
        ])
        return web.AppRunner(self.__app)

    async def start_server(self, host, port):
        logger.info("\nYou can now connect Intrepid Agent to host {}:{}".format(host, port))
        await self.__runner.setup()
        site = web.TCPSite(self.__runner, host, port)
        await site.start()

    def start(self, host=WS_HOST, port=WS_PORT):
        # if self.__callback is None and not ACTION_REGISTRY and not SENSOR_REGISTRY:
        #     log(TAG_HTTP_REQUEST, LogLevel.ERROR, ERROR_REGISTER_CALLBACK)
        #     sys.exit(1)

        # # Define the Unix domain socket path
        # timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        # unix_socket_path = f"/tmp/intrepid-ws-{timestamp}.sock"
        # # logger.info("Intrepid SDK started at {}".format(unix_socket_path))
        # log(TAG_HTTP_REQUEST, LogLevel.INFO, INFO_SDK_READY.format(unix_socket_path))

        # self.__unix_socket_path = unix_socket_path
        # asyncio.run(wsserver(self.__unix_socket_path))

        for route in self.__app.router.routes():
            logger.debug(route)

        loop = asyncio.get_event_loop()
        loop.run_until_complete(self.start_server(host, port))
        loop.run_forever()

    @property
    def nodes(self)->Dict[str, Node]:
        return Intrepid.__get_instance().nodes

    @staticmethod
    def config():
        """
        Return the current used intrepid configuration.
        @return: _IntrepidConfig
        """
        return Intrepid.__get_instance().configuration_manager.intrepid_config

    def register_node(
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
                type_name = TYPE_MAP.get(inner_type)
                type_container = DiscoveryPinContainer.ARRAY
                if type_name is None:
                    raise ValueError(f"unsupported inner type in list: {inner_type}")
            else:
                type_name = TYPE_MAP.get(annotation)
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

    # TODO make obsolete
    def register_callback(self, func):
        if self.__callback is None:
            log(TAG_HTTP_REQUEST, LogLevel.INFO, INFO_CALLBACK_REGISTERED)

            is_valid = Intrepid.__Intrepid().__register_callback(func, self.__node)
            if is_valid:
                self.__original_callback = func
                self.__callback = func
            else:
                logger.error("Aborting...")
        else:
            if isinstance(self.__node, Node):
                self.__original_callback = func
                return Intrepid.__get_instance().__register_callback(func, self.__node_info)
            else:
                logger.error(ERROR_REGISTER_CALLBACK)
                log(TAG_HTTP_REQUEST, LogLevel.ERROR, ERROR_REGISTER_CALLBACK)

    @staticmethod
    def create_qos(qos: Qos):
        """
        Return the details of this node
        @return: Status.
        """
        logger.info("\nAttaching QoS policy")
        logger.info(qos)
        return Intrepid.__get_instance().create_qos(qos)

    # @staticmethod
    def info(self) -> Node:
        return Intrepid.__get_instance().node_specs

    @staticmethod
    def status():
        """
        Return the current SDK status.
        @return: Status.
        """
        return Intrepid.__get_instance().status

    # @staticmethod
    def write(self, target, data):
        """
        Write data to node output target.
        @return
        """
        return Intrepid.__get_instance().write(target, data)

    @staticmethod
    def stop():
        """
        Stop and reset the Intrepid instance.
        @return:
        """
        return Intrepid.__get_instance().stop()

    @staticmethod
    def __get_instance():
        """
        Get the intrepid singleton instance.

        :return: Intrepid
        """

        if Intrepid.__instance is None:
            Intrepid.__instance = Intrepid.__Intrepid()  # Create the inner class instance
        return Intrepid.__instance

    @staticmethod
    def _update_status(new_status):
        Intrepid.__get_instance().update_status(new_status)

    class __Intrepid:
        def __init__(self):
            self.qos = None
            # Node input/output types and names
            self.node_specs = None
            self.__nodes: Dict[str, Node] = {}
            self.status = Status.NOT_INITIALIZED
            self.configuration_manager = ConfigManager()
            self.device_context = {}

        @property
        def nodes(self)->Dict[str, Node]:
            return self.__nodes

        def __register_node(self, node: Node):
            logger.info("Registering node")
            # runtime can have multiple nodes
            if node.name not in self.__nodes:
                # import pdb; pdb.set_trace();
                self.__nodes[node.name] = node
                logger.info("nodes: ", self.__nodes)
                return True
            else:
                logger.info("Node already registered under the same name ", node.name)
                return False

        def __register_adapter(self, action_name, adapter) -> bool:
            return True

        def __register_action(self, action_name: str, func: Callable) -> bool:
            if action_name in ACTION_REGISTRY:
                if ACTION_REGISTRY[action_name] is not None:
                    logger.info("Action already registered...returning")
                    return False
            print(action_name)
            # this action_name is for a node
            if action_name in self.__nodes:
                # Get node with same action name
                node = self.__nodes[action_name]
                print(node)

                # is_valid = self.__validate_callback_parameters(node, func)
                is_valid = True
                print("Callback is valid: ", is_valid)
                if is_valid:
                    logger.info("Callback is valid. Proceeding...")
                    # self.callback = func
                    ACTION_REGISTRY[action_name] = func
                    print("ACTION_REGISTRY: ", ACTION_REGISTRY)
                    logger.info("Callback registered to node")
                    return True
                else:
                    logger.info("Callback input not valid. Aborting...")
                    return False

            # register the action normally
            ACTION_REGISTRY[action_name] = func
            print("ACTION_REGISTRY: ", ACTION_REGISTRY)
            return True

        def __register_callback(self, func, node: Node) -> bool:
            logger.info("Callback registered to node")
            # print("Node specs: ", node)
            is_valid = self.__validate_callback_parameters(node, func)
            # print("Callback is valid: ", is_valid)
            if is_valid:
                logger.info("Callback is valid. Proceeding...")
                self.callback = func
                return True
            else:
                logger.info("Callback input not valid. Aborting...")
                return False

        # @param_types_validator(True, str, str, [_IntrepidConfig, None])
        def start(self, env_id, api_key, intrepid_config):
            # self.update_status(intrepid_config, Status.STARTING)
            if not env_id or not api_key:
                raise InitializationParamError()
            self.update_status(intrepid_config, Status.STARTING)
            self.configuration_manager.init(env_id, api_key, intrepid_config, self.update_status)
            # self.update_status(intrepid_config, Status.STARTING)
            if self.configuration_manager.is_set() is False:
                self.update_status(self.configuration_manager.intrepid_config, Status.NOT_INITIALIZED)
                self.__log(TAG_INITIALIZATION, LogLevel.ERROR, ERROR_CONFIGURATION)

        def update_status(self, intrepid_config, new_status):
            if intrepid_config is not None and new_status is not None and new_status != self.status:
                old_status = self.status
                self.status = new_status
                log(TAG_STATUS, LogLevel.DEBUG, INFO_STATUS_CHANGED.format(str(new_status)), intrepid_config)
                if new_status is Status.READY:
                    log(TAG_INITIALIZATION, LogLevel.INFO,
                        INFO_READY.format(str(__version__), str(intrepid_config)))
                self.configuration_manager.intrepid_status_update(new_status, old_status)
                if intrepid_config.status_listener is not None:
                    intrepid_config.status_listener.on_status_changed(new_status)

        def close(self):
            self.status = Status.NOT_INITIALIZED
            # log(TAG_TERMINATION, LogLevel.INFO, INFO_STOPPED)
            self.configuration_manager.reset()

        def create_qos(self, qos: Qos):
            # TODO make request and set local if success
            self.qos = qos

        def stop(self):
            # Create STOP message
            msg = IntrepidMessage(Opcode.STOP, None, datetime.now(), self.node_id).serialize()

            # TODO send msg over websocket
            self.status = Status.NOT_INITIALIZED

        def write(self, node_id, target, data):
            recipient = node_id + '/' + target
            msg = IntrepidMessage(Opcode.WRITE, payload=data, timestamp=datetime.now(), recipient=recipient, priority=0)
            # logger.debug(msg)
            log(TAG_HTTP_REQUEST, LogLevel.DEBUG, msg)

            # TODO send msg over websocket

        def __log(self, tag, level, message):
            try:
                configured_log_manager = self.configuration_manager.intrepid_config.log_manager
                if configured_log_manager is not None:
                    configured_log_manager.log(tag, level, message)
            except Exception as e:
                pass

        @staticmethod
        def __validate_callback_parameters(node: Node, callback: Callable) -> bool:
            """
            Validates if the parameters of the callback function match the inputs of the node.
            """
            # Get parameter names of the callback function
            # callback_params = callback().__code__.co_varnames[:callback.__code__.co_argcount]
            # import pdb; pdb.set_trace();

            callback_param_types = callback().__annotations__  # This is a dictionary of parameter names and types
            print(callback_param_types)
            callback_return_values = []
            if 'return' in callback_param_types:
                callback_retval = callback_param_types['return']
                if not isinstance(callback_retval, Iterable):
                    callback_return_values.append(callback_retval)
                else:
                    callback_return_values = callback_retval
                callback_param_types.pop('return', None)

            callback_params = list(callback_param_types.keys())

            # Get input names and data types of the node
            node_input_names = [input_element.label for input_element in node.inputs]
            if 'flow' in node_input_names:
                node_input_names.remove('flow')

            node_output_names = [output_element.label for output_element in node.outputs]
            if 'flow' in node_output_names:
                node_output_names.remove('flow')

            node_input_data_types = []
            for input_element in node.inputs:
                if input_element.type.is_flow():
                    continue
                else:
                    node_input_data_types.append(input_element)
            node_output_data_types = []
            for output_element in node.outputs:
                if output_element.type.is_flow():
                    continue
                else:
                    node_output_data_types.append(output_element)

            # Check if the number of parameters match
            if len(callback_params) != len(node_input_names):
                logger.error(ERROR_PARAM_NUM.format(len(node_input_names)))
                return False

            # # Check if parameter names and data types match
            for param_name, input_name, input_type in zip(callback_params, node_input_names, node_input_data_types):
                if param_name != input_name:
                    # logger.error(ERROR_PARAM_NAME.format(param_name, input_name))
                    log(TAG_HTTP_REQUEST, LogLevel.ERROR, ERROR_PARAM_NAME.format(param_name, input_name))
                    # TODO check the type too
                    return False

                if callback_param_types[input_name] != input_type.type.to_python_type():
                    logger.error("Unexpected input type. Expected ", input_type.type.to_python_type(), "Found ", callback_param_types[input_name])
                    return False

            for retval, output_type in zip(callback_return_values, node_output_data_types):
                if retval != output_type.type.to_python_type():
                    logger.error("Unexpected input type. Expected ", output_type.type.to_python_type(), "Found ", callback_param_types[input_name])
                    return False

            return True

