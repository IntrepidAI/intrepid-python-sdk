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
    def __init__(self, opcode: Opcode, payload, timestamp: datetime, recipient: str, priority=int(0)):
        self.opcode = opcode
        self.payload = payload
        self.timestamp = timestamp
        self.recipient = recipient
        self.priority = priority

    def serialize(self, cdr=True) -> bytes:
        # TODO
        return bytes()

    def __str__(self):
        return f"IntrepidMessage(op={self.opcode}, payload={self.payload}, timestamp={self.timestamp}, recipient={self.recipient}, priority={self.priority})"
