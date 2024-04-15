from __future__ import absolute_import
from __future__ import unicode_literals

import asyncio
import importlib_metadata
import os
import subprocess
from websockets.server import serve, unix_serve
from intrepid.config import _IntrepidConfig
from intrepid.config_manager import ConfigManager
from intrepid.constants import TAG_STATUS, INFO_STATUS_CHANGED, TAG_INITIALIZATION, INFO_READY, ERROR_CONFIGURATION, INFO_STOPPED
from intrepid.decorators import param_types_validator
from intrepid.errors import InitializationParamError
from intrepid.log_manager import LogLevel
from intrepid.status import Status
from intrepid.utils import log
from intrepid.node import Node, DataType, DataElement
from intrepid.qos import Qos
from intrepid.message import IntrepidMessage, Opcode
from datetime import datetime

__name__ = 'intrepid'
__version__ = importlib_metadata.distribution(__name__).version




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
    print("Listening on port ", port)
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

    def start(self):
        # Define the Unix domain socket path
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        unix_socket_path = f"/tmp/intrepid-ws-{timestamp}.sock"
        print("Intrepid SDK started at ", unix_socket_path)
        self.__unix_socket_path = unix_socket_path

        asyncio.run(wsserver(unix_socket_path))

    @staticmethod
    def config():
        """
        Return the current used intrepid configuration.
        @return: _IntrepidConfig
        """
        return Intrepid.__get_instance().configuration_manager.intrepid_config


    @staticmethod
    def register_callback(func, node_info: Node):
        return Intrepid.__get_instance().__register_callback(func, node_info)


    @staticmethod
    def create_qos(qos: Qos):
        """
        Return the details of this node
        @return: Status.
        """
        return Intrepid.__get_instance().create_qos(qos)

    # @staticmethod
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

        def __register_callback(self, func, node_info):
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
            print(msg)
            # TODO send msg over websocket


        def __log(self, tag, level, message):
            try:
                configured_log_manager = self.configuration_manager.intrepid_config.log_manager
                if configured_log_manager is not None:
                    configured_log_manager.log(tag, level, message)
            except Exception as e:
                pass
