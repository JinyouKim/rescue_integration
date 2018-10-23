# -*- coding: utf-8 -*-
from rescue.common import message
from .message import Message
from .message_header import Header
from .message_body import BodyCommonResponse
from .message_body import BodyConnectRequest


class MessageUtil:
    @staticmethod
    def send(sock, msg):
        sent = 0
        buffer = msg.getBytes()
        while sent < msg.getSize():
            sent += sock.send(buffer)

    @staticmethod
    def receive(sock):
        totalRecv = 0
        sizeToRead = 8  # 헤더의 크기
        hBuffer = bytes()  # 헤더 버퍼

        # 헤더 읽기
        while sizeToRead > 0:
            buffer = sock.recv(sizeToRead)
            if len(buffer) == 0:
                return None

            hBuffer += buffer
            totalRecv += len(buffer)
            sizeToRead -= len(buffer)

        header = Header(hBuffer)

        print(header.MSGTYPE);
        print(header.BODYLEN);
        totalRecv = 0
        bBuffer = bytes()
        sizeToRead = header.BODYLEN

        while sizeToRead > 0:
            buffer = sock.recv(sizeToRead)
            if len(buffer) == 0:
                return None

            bBuffer += buffer
            totalRecv += len(buffer)
            sizeToRead -= len(buffer)

        body = None

        if header.MSGTYPE == message.REQ_CONNECT:
            body = BodyConnectRequest(bBuffer)
        elif header.MSGTYPE == message.REP_CONNECT or header.MSGTYPE == message.REP_VIDEO_STREAMING or header.MSGTYPE == message.REP_GET_TOKEN:
            body = BodyCommonResponse(bBuffer)
        elif header.MSGTYPE == message.REQ_GET_TOKEN\
                or header.MSGTYPE == message.REQ_RETURN_TOKEN\
                or header.MSGTYPE == message.REP_RETURN_TOKEN\
                or header.MSGTYPE == message.REQ_VIDEO_STREAMING\
                or header.MSGTYPE == message.REQ_EXIT_VIDEO_STREAMING\
                or header.MSGTYPE == message.REP_EXIT_VIDEO_STREAMING\
				or header.MSGTYPE == message.REQ_CALL\
                or header.MSGTYPE == message.REQ_CALL_STOP:
            body = None
        else:
            raise Exception(
                "Unknown MSGTYPE : {0}".
                    format(header.MSGTYPE))

        msg = Message()
        msg.Header = header
        msg.Body = body

        return msg
