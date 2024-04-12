import struct
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
    def __init__(self, opcode, payload, timestamp, node_id, priority=0, qos=None):
        self.opcode = opcode
        self.payload = payload
        self.timestamp = timestamp
        self.node_id = node_id
        self.priority = priority
        self.qos = qos

    def serialize(self, cdr=True) -> bytes:
        # TODO
        return

