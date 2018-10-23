# -*- coding: utf-8 -*-
# 메세지 타입
REQ_CONNECT = 0x01
REP_CONNECT = 0x02
REQ_GET_TOKEN = 0x03
REP_GET_TOKEN = 0x04
REQ_RETURN_TOKEN = 0x05
REP_RETURN_TOKEN = 0x06
REQ_VIDEO_STREAMING = 0x07
REP_VIDEO_STREAMING = 0x08
REQ_EXIT_VIDEO_STREAMING = 0x09
REP_EXIT_VIDEO_STREAMING = 0x0A
REQ_CALL = 0x0B
REP_CALL = 0x0C
REQ_CALL_STOP = 0x0D

# 수락/ 거절 여부
ACCEPTED = 0x00
DENIED = 0x01


class ISerializable:
    def getBytes(self):
        pass

    def getSize(self):
        pass

class Message(ISerializable):
    def __init__(self):
        self.Header = ISerializable()
        self.Body = ISerializable()

    def getBytes(self):
        buffer = bytes(self.getSize())
        header = self.Header.getBytes()
        body = self.Body.getBytes()

        return header + body

    def getSize(self):
        return self.Header.getSize() + self.Body.getSize()
