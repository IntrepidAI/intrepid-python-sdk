from __future__ import absolute_import
from __future__ import unicode_literals
import logging
from typing import Callable, Dict, List, Optional
import asyncio
import importlib_metadata
import os, sys
import subprocess
from websockets.server import serve, unix_serve
from intrepid.config import _IntrepidConfig
import signal
from intrepid.config_manager import ConfigManager
from intrepid.constants import TAG_STATUS, TAG_HTTP_REQUEST, \
    INFO_STATUS_CHANGED, TAG_INITIALIZATION, INFO_CALLBACK_REGISTERED, \
    INFO_READY, INFO_WSSERVER_READY, INFO_STOPPED, INFO_SDK_READY, \
    ERROR_CONFIGURATION, ERROR_PARAM_TYPE, ERROR_PARAM_NUM, ERROR_PARAM_NAME, ERROR_REGISTER_CALLBACK
from intrepid.decorators import param_types_validator
from intrepid.errors import InitializationParamError
from intrepid.log_manager import LogLevel
from intrepid.utils import log, log_exception, signal_handler
from intrepid.status import Status
from intrepid.node import Node, DataType, DataElement
from intrepid.qos import Qos
from intrepid.message import IntrepidMessage, Opcode
from datetime import datetime

__name__ = 'intrepid'
__version__ = importlib_metadata.distribution(__name__).version


# Set up the signal handler for SIGINT (Ctrl+C)
signal.signal(signal.SIGINT, signal_handler)



# TODO remove this and use log_manager
# Configure logging
# logging.basicConfig(level=logging.INFO)  # Set the logging level to INFO or desired level
# Define ANSI escape codes for colors
# COLOR_RED = "\033[91m"
# COLOR_RESET = "\033[0m"

# Custom logging format with timestamp
# log_format = "%(asctime)s - %(levelname)s - %(message)s"
# logging.basicConfig(format=log_format)
# logger = logging.getLogger(__name__)  # Create a logger instance



async def handler(websocket):
    async for message in websocket:
        # TODO inspect message and execute action

        await websocket.send(message)

# TODO now it just echoes
async def wsserver(unix_socket_path: str):
    # Remove the socket file if it already exists
    if os.path.exists(unix_socket_path):
        os.remove(unix_socket_path)

    port = 9999
    # logger.info("Listening on port {}".format(port))
    log(TAG_HTTP_REQUEST, LogLevel.INFO, INFO_WSSERVER_READY.format(port))
    command = f"socat TCP-LISTEN:{port} UNIX-CONNECT:{unix_socket_path}"
    subprocess.Popen(command, shell=True)

    async with unix_serve(handler, unix_socket_path):
        await asyncio.Future()  # run forever


class Intrepid:
    __instance = None

    def __init__(self, node_id):
        """
        Initialize the Intrepid SDK.

        @param node_id: Unique identifier of the node managed by this handler
        @param qos: Dictionary that specifies the QoS applied to this node (Not Implemented)
        @return:
        """

        self.node_id = str(node_id)
        self.qos = None
        self.__unix_socket_path = None
        self.__node_info = None
        self.__callback = None

    def start(self):
        if self.__callback is None:
            log(TAG_HTTP_REQUEST, LogLevel.ERROR, ERROR_REGISTER_CALLBACK)
            sys.exit(1)
        # Define the Unix domain socket path
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        unix_socket_path = f"/tmp/intrepid-ws-{timestamp}.sock"
        # logger.info("Intrepid SDK started at {}".format(unix_socket_path))
        log(TAG_HTTP_REQUEST, LogLevel.INFO, INFO_SDK_READY.format(unix_socket_path))

        self.__unix_socket_path = unix_socket_path
        asyncio.run(wsserver(self.__unix_socket_path))

    @staticmethod
    def config():
        """
        Return the current used intrepid configuration.
        @return: _IntrepidConfig
        """
        return Intrepid.__get_instance().configuration_manager.intrepid_config


    def register_callback(self, func):
        if self.__callback is None:
            log(TAG_HTTP_REQUEST, LogLevel.INFO, INFO_CALLBACK_REGISTERED)
            self.__callback = func
        else:
            if isinstance(self.__node_specs, Node):
                return Intrepid.__get_instance().__register_callback(func, self.__node_info)
            else:
                # logger.error(ERROR_REGISTER_CALLBACK)
                log(TAG_HTTP_REQUEST, LogLevel.ERROR, ERROR_REGISTER_CALLBACK)


    @staticmethod
    def create_qos(qos: Qos):
        """
        Return the details of this node
        @return: Status.
        """
        return Intrepid.__get_instance().create_qos(qos)

    def __node_specs(self, specs: Node):
        """
        Return the details of this node
        @return: Status.
        """

        # TODO this should be received from websocket client
        # TODO validate specs
        node = Node()
        node.add_input("in1", DataType.INTEGER)
        node.add_input("in2", DataType.INTEGER)
        node.add_output("out1", DataType.FLOAT)

        return Intrepid.__get_instance().__node_specs(node)

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
        return Intrepid.__get_instance().write(self.node_id, target, data)

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
        if not Intrepid.__instance:
            Intrepid.__instance = Intrepid.__Intrepid()
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

        def __node_specs(self, specs):
            self.node_specs = specs

        def __register_callback(self, func):
            is_valid = self.__validate_callback_parameters(self.node_specs, func)

            self.callback = func

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

        def info(self):
            self.node_specs

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
            callback_params = callback.__code__.co_varnames[:callback.__code__.co_argcount]

            # Get input names and data types of the node
            node_input_names = [input_element.name for input_element in node.inputs]
            node_input_data_types = [input_element.data_type for input_element in node.inputs]

            # Check if the number of parameters match
            if len(callback_params) != len(node_input_names):
                logger.error(ERROR_PARAM_NUM.format(len(node_input_names)))
                return False

            # Check if parameter names and data types match
            for param_name, input_name, input_type in zip(callback_params, node_input_names, node_input_data_types):
                if param_name != input_name:
                    # logger.error(ERROR_PARAM_NAME.format(param_name, input_name))
                    log(TAG_HTTP_REQUEST, LogLevel.ERROR, ERROR_PARAM_NAME.format(param_name, input_name))

                    # TODO check the type too
                    return False
                # You may want to add more sophisticated type checking here
                # For simplicity, I'm just checking if the data types match exactly
                if not isinstance(input_type, DataType):
                    return False

            return True


