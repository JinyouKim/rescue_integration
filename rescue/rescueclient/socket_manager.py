# -*- coding: utf-8 -*-

import socket
import struct
import time

from rescue.common import message
from rescue.common.message import Message
from rescue.common.message_header import Header
from rescue.common.message_body import BodyEmpty, BodyConnectRequest
from rescue.common.message_util import MessageUtil


class SocketManager():
    def __init__(self, myIp, serverIp, serverPort, multicastIp, multicastPort):
        self.myIp = myIp
        self.serverIp = serverIp
        self.serverPort = serverPort
        self.multicastIp = multicastIp
        self.multicastPort = multicastPort
        self.sockServer = None

    def joinMuticastGroup(self):
        # 멀티캐스트 그룹 조인
        sockMulticast = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        sockMulticast.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        mreq = struct.pack("4sl", socket.inet_aton(self.multicastIp), socket.INADDR_ANY)
        sockMulticast.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

    def connectServer(self):
        self.sockServer = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        try:
            ret = -1
            while ret != 0:
                ret = self.sockServer.connect_ex((self.serverIp, self.serverPort))
                time.sleep(2)

            reqMsg = Message()
            reqMsg.Body = BodyConnectRequest(None)
            reqMsg.Body.RESQUER_ID = '1'
            reqMsg.Header = Header(None)
            reqMsg.Header.MSGTYPE = message.REQ_CONNECT
            reqMsg.Header.BODYLEN = reqMsg.Body.getSize()

            MessageUtil.send(self.sockServer, reqMsg)
            rspMsg = MessageUtil.receive(self.sockServer)

            if rspMsg.Header.MSGTYPE != message.REP_CONNECT:
                print("Error")
                exit(0)
            if rspMsg.Body.RESPONSE != message.ACCEPTED:
                print("Connection is refused.")
                exit(0)

            print("Connected with server")
            return True

        except Exception as err:
            print("Exception")
            print(err)
            return False

    def requestVideoCall(self):
        try:
            reqMsg = Message()
            reqMsg.Body = BodyEmpty()
            reqMsg.Header = Header(None)
            reqMsg.Header.MSGTYPE = message.REQ_VIDEO_STREAMING
            reqMsg.Header.BODYLEN = 0

            # 스트리밍 연결 요청
            MessageUtil.send(self.sockServer, reqMsg)
            # 통화음 또는 연결 화면 보이는 로직 필요

            # 연결 수락 대기
            rspMsg = MessageUtil.receive(self.sockServer)

            if rspMsg.Header.MSGTYPE != message.REP_VIDEO_STREAMING:
                print('Error')
                return False

            # 서버에서 수락하면
            if rspMsg.Body.RESPONSE == message.ACCEPTED:
                return True

            # 서버에서 거절하면
            else:
                return False
        except Exception as err:
            print("Exception")
            print(err)
            return False

    def requestVoice(self):
        try:
            reqMsg = Message()
            reqMsg.Body = BodyEmpty()
            reqMsg.Header = Header(None)
            reqMsg.Header.MSGTYPE = message.REQ_GET_TOKEN
            reqMsg.Header.BODYLEN = 0

            # 토큰 요청
            MessageUtil.send(self.sockServer, reqMsg)

            # 요청 결과
            rspMsg = MessageUtil.receive(self.sockServer)

            if rspMsg.Header.MSGTYPE != message.REP_GET_TOKEN:
                print('Error')
                return False

            # 서버에서 수락하면
            if rspMsg.Body.RESPONSE == message.ACCEPTED:
                print('voice accept')
                # 보이스 전송
                return True
            # 서버에서 거절하면
            else:
                print('voice denied')
                return False
        except Exception as err:
            print("Exception")
            print(err)
            return False

    def returnToken(self):
        reqMsg = Message()
        reqMsg.Body = BodyEmpty()
        reqMsg.Header = Header(None)
        reqMsg.Header.MSGTYPE = message.REQ_RETURN_TOKEN
        reqMsg.Header.BODYLEN = 0

        print("x")
        # 토큰 반납 요청
        MessageUtil.send(self.sockServer, reqMsg)

        print("y")
        # 요청 결과
        rspMsg = MessageUtil.receive(self.sockServer)

        if rspMsg.Header.MSGTYPE != message.REP_RETURN_TOKEN:
            print('Error')
            return False
        print('return accepted')
        return True

    def requestExitVideo(self):
        reqMsg = Message()
        reqMsg.Body = BodyEmpty()
        reqMsg.Header = Header(None)
        reqMsg.Header.MSGTYPE = message.REQ_EXIT_VIDEO_STREAMING
        reqMsg.Header.BODYLEN = 0

        # Ending Video Stream
        MessageUtil.send(self.sockServer, reqMsg)

        # 요청 결과
        rspMsg = MessageUtil.receive(self.sockServer)

        if rspMsg.Header.MSGTYPE != message.REP_EXIT_VIDEO_STREAMING:
            print('Error')
            return False
        print('exit video')
        return True

    def disconnectServer(self):
        self.sockServer.close()
