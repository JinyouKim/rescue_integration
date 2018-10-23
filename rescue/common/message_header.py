# -*- coding: utf-8 -*-
from .message import ISerializable
import struct

class Header(ISerializable):
    def __init__(self, buffer):
        self.struct_fmt = '=2I'
        self.struct_len = struct.calcsize(self.struct_fmt)

        if buffer != None:
            unpacked = struct.unpack(self.struct_fmt, buffer)

            self.MSGTYPE = unpacked[0]
            self.BODYLEN = unpacked[1]

    def getBytes(self):
        return struct.pack(self.struct_fmt, *(self.MSGTYPE, self.BODYLEN))

    def getSize(self):
        return self.struct_len