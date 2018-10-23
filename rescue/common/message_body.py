# -*- coding: utf-8 -*-
from .message import ISerializable
import struct


class BodyCommonResponse(ISerializable):
    def __init__(self, buffer):
        self.struct_fmt = '=I'
        self.struct_len = struct.calcsize(self.struct_fmt)

        if buffer != None:
            unpacked = struct.unpack(self.struct_fmt, buffer)
            self.RESPONSE = unpacked[0]

    def getBytes(self):
        return struct.pack(self.struct_fmt, self.RESPONSE)

    def getSize(self):
        return self.struct_len


class BodyConnectRequest(ISerializable):
    def __init__(self, buffer):
        if buffer != None:
            slen = len(buffer)
            self.struct_fmt = str.format('{0}s', slen)
            self.struct_len = struct.calcsize(self.struct_fmt)
            unpacked = struct.unpack(self.struct_fmt, buffer)
            self.RESQUER_ID = unpacked[0]

        else:
            self.struct_fmt = str.format('{0}s', 0)
            self.struct_len = struct.calcsize(self.struct_fmt)
            self.RESQUER_ID = ""

    def getBytes(self):
        buffer = self.RESQUER_ID.encode(encoding='utf-8')

        # 1 unsigned long long, N character
        self.struct_fmt = str.format('{0}s', len(buffer))

        return struct.pack(self.struct_fmt, buffer)

    def getSize(self):
        buffer = self.RESQUER_ID.encode(encoding='utf-8')

        self.struct_fmt = str.format('{0}s', len(buffer))
        self.struct_len = struct.calcsize(self.struct_fmt)
        return self.struct_len


class BodyEmpty(ISerializable):
    def __init__(self):
        None

    def getBytes(self):
        return bytes()

    def getSize(self):
        return 0
