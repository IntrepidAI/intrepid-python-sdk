import struct
from datetime import datetime
from enum import Enum

class Opcode(Enum):
    READ = 1
    WRITE = 2
    INFO = 3
    STATUS = 4
    SPECS = 5
    STOP = 6
    PING = 9
    PONG = 10


class IntrepidMessage:
    def __init__(self, opcode: Opcode, payload, timestamp: datetime, node_id: str, priority=int(0), qos=None):
        self.opcode = opcode
        self.payload = payload
        self.timestamp = timestamp
        self.node_id = node_id
        self.priority = priority
        self.qos = qos

    def serialize(self, cdr=True) -> bytes:
        # TODO
        return bytes()

