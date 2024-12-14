from __future__ import absolute_import
from __future__ import unicode_literals
import logging
from typing import Callable, Dict, List, Optional
from collections.abc import Iterable
import asyncio
import importlib_metadata
import os, sys
import subprocess
from websockets.server import serve, unix_serve
from intrepid_python_sdk.config import _IntrepidConfig
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
from datetime import datetime


import aiohttp
from aiohttp import web, WSCloseCode
import asyncio
import json


__name__ = 'intrepid_python_sdk'
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
    __instance = None
    __restarted = None
    __original_callback = None

    def __init__(self):
        """
        Initialize the Intrepid SDK.

        @param node_id: Unique identifier of the node managed by this handler
        @param qos: Dictionary that specifies the QoS applied to this node (Not Implemented)
        @return:
        """

        self.qos = None
        self.__unix_socket_path = None
        self.__node = None
        self.__node_info = None
        self.__callback = None

    async def websocket_handler(self, request):
        ws = web.WebSocketResponse()
        await ws.prepare(request)
        logger.info("WebSocket connection established.")
        func = self.__callback()

        closed_abnormally = False  # Flag to determine if restart is needed
        try:
            async for msg in ws:
                # print(msg)
                if msg.type == aiohttp.WSMsgType.TEXT:
                    msg_dict = json.loads(msg.data)
                    request_id = msg_dict.get("id")
                    discovery_object = msg_dict.get("discovery")
                    init_object = msg_dict.get("init")
                    # print(init_object)
                    if init_object is not None:
                        logger.info("Agent reset. Restarting node...")
                        # self.restart_node()

                    exec_object = msg_dict.get("exec")
                    if discovery_object is not None:
                        await ws.send_json({
                            "id": request_id,
                            "discovery_ok": {"nodes": [self.__node.to_dict()]},
                        })
                    elif init_object is not None:
                        irm = InitRequest(init_object["node_id"], init_object["node_type"])
                        irm.exec_inputs = init_object["exec_inputs"]
                        irm.exec_outputs = init_object["exec_outputs"]
                        await ws.send_json({
                            "id": request_id,
                            "init_ok": {},
                        })
                    elif exec_object is not None:
                        exec_id = exec_object.get("exec_id")
                        time = exec_object.get("time")
                        inputs = exec_object.get("inputs")
                        if exec_id is not None and time is not None and inputs is not None:
                            exec_resp = ExecResponse()
                            exec_resp.time = time
                            exec_resp.exec_id = 0
                            # Execute callback function and return ExecResponse object
                            # out = self.__callback(*inputs)
                            out = func(*inputs)
                            exec_resp.outputs = out if isinstance(out, tuple) else (out,)
                            await ws.send_json({
                                "id": request_id,
                                "exec_ok": exec_resp.to_dict(),
                            })
                        else:
                            logger.error("ExecRequest has invalid payload")
                elif msg.type == aiohttp.WSMsgType.error:
                    logger.error(f"WebSocket connection error: {ws.exception()}")
                    closed_abnormally = True
                    break
                # elif msg.type == aiohttp.WSMsgType.CLOSE:
                #     logger.info("WebSocket close message received.")
                #     break
        except Exception as e:
            logger.error(f"WebSocket handler exception: {e}")
            closed_abnormally = True

        # if ws.closed:
        #     print("websocket closed")

        # finally:
            # if ws.closed:
            #     logger.info(f"WebSocket connection closed. Abnormal: {closed_abnormally}")
            #     if closed_abnormally:
            #         logger.info("WebSocket closed abnormally. Restarting node...")
            #         print("Restarting node...")
            #         await self.restart_node()
            #     else:
            #         logger.info("WebSocket closed normally.")
            # else:
            #     logger.warning("WebSocket connection finalized unexpectedly.")
        return ws


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
        app = web.Application()
        app.add_routes([
            # web.get('/',   self.http_handler),
            web.get('/', self.websocket_handler),
        ])
        return web.AppRunner(app)

    async def start_server(self, host=WS_HOST, port=WS_PORT):
        runner = self.create_runner()
        print("\nListening on host {}:{}".format(host, port))
        await runner.setup()
        site = web.TCPSite(runner, host, port)
        await site.start()

    def start(self):
        if self.__callback is None:
            log(TAG_HTTP_REQUEST, LogLevel.ERROR, ERROR_REGISTER_CALLBACK)
            sys.exit(1)
        # # Define the Unix domain socket path
        # timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        # unix_socket_path = f"/tmp/intrepid-ws-{timestamp}.sock"
        # # logger.info("Intrepid SDK started at {}".format(unix_socket_path))
        # log(TAG_HTTP_REQUEST, LogLevel.INFO, INFO_SDK_READY.format(unix_socket_path))

        # self.__unix_socket_path = unix_socket_path
        # asyncio.run(wsserver(self.__unix_socket_path))

        loop = asyncio.get_event_loop()
        loop.run_until_complete(self.start_server())
        loop.run_forever()

    @staticmethod
    def config():
        """
        Return the current used intrepid configuration.
        @return: _IntrepidConfig
        """
        return Intrepid.__get_instance().configuration_manager.intrepid_config

    def register_node(self, node: Node):
        print("Registering node")
        print(node)
        self.__node = node

    def register_callback(self, func):
        if self.__callback is None:
            log(TAG_HTTP_REQUEST, LogLevel.INFO, INFO_CALLBACK_REGISTERED)
            # is_valid = Intrepid.__get_instance().__register_callback(func, self.__node)
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
        print("\nAttaching QoS policy")
        print(qos)
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
        # if not Intrepid.__instance:
        #     Intrepid.__instance = Intrepid.__Intrepid()
        # return Intrepid.__instance
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
            self.status = Status.NOT_INITIALIZED
            self.configuration_manager = ConfigManager()
            self.device_context = {}

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
            callback_param_types = callback().__annotations__  # This is a dictionary of parameter names and types
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

