from __future__ import absolute_import
from __future__ import unicode_literals

import importlib_metadata
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



class Intrepid:
    __instance = None

    def __init__(self, node_id):
        """
        Initialize the Intrepid SDK.

        @param node_id: Unique identifier of the node managed by this handler
        @param qos: Dictionary that specifies the QoS applied to this node (Not Implemented)
        @return:
        """
        # self.__instance = None
        self.node_id = str(node_id)
        self.qos = None

    @staticmethod
    def config():
        """
        Return the current used intrepid configuration.
        @return: _IntrepidConfig
        """
        return Intrepid.__get_instance().configuration_manager.intrepid_config


    @staticmethod
    def create_qos(qos: Qos):
        """
        Return the details of this node
        @return: Status.
        """
        return Intrepid.__get_instance().create_qos(qos)


    # @staticmethod
    def info(self) -> Node:
        """
        Return the details of this node
        @return: Status.
        """
        return Intrepid.__get_instance().info(self.node_id)


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
            self.status = Status.NOT_INITIALIZED
            self.configuration_manager = ConfigManager()
            self.device_context = {}

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

        def info(self, node_id: str) -> Node:
            recipient = node_id
            msg = IntrepidMessage(Opcode.INFO, payload=None, timestamp=datetime.now(), recipient=recipient, priority=0)
            print(msg)
            # TODO send msg over websocket

            node = Node()
            node.add_input("in1", DataType.INTEGER)
            node.add_input("in2", DataType.INTEGER)
            node.add_output("out1", DataType.FLOAT)
            return node

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
