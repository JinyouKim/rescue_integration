# -*- coding: utf-8 -*-
import os
import socketserver
import subprocess
import threading

from rescue.common import message
from rescue.common.message import Message
from rescue.common.message_util import MessageUtil
from rescue.common.message_header import Header
from rescue.common.message_body import BodyCommonResponse, BodyEmpty
from rescue.rescueserver.request_dialog import RequestDialog

HOST = ''
PORT = 9111
GSTREAMER_PATH = 'D:\\gstreamer\\1.0\\x86_64\\bin\gst-launch-1.0'


class RescuerManager:
    def __init__(self):
        self.rescuers = {}  # {rescuer ID: (socket, address), ...}
        self.isCalling = False
        self.tokenLender = None
        self.hasToken = True
        self.lock = threading.Lock();

    def addRescuer(self, rescuerId, conn, address):
        if rescuerId in self.rescuers:
            conn.send()

    def lockCall(self):
        with self.lock:
            self.isCalling = True

    def freeCall(self):
        with self.lock:
            self.isCalling = False

    def getCallStatus(self):
        with self.lock:
            return self.isCalling

    def lockToken(self, tokenLender):
        with self.lock:
            self.tokenLender = tokenLender
            self.hasToken = False

    def freeToken(self):
        with self.lock:
            self.tokenLender = None
            self.hasToken = True

    def getTokenStatus(self):
        with self.lock:
            return self.hasToken, self.tokenLender


class RequestHandler(socketserver.BaseRequestHandler):
    rm = RescuerManager()
    def handle(self):
        print("클라이언트 접속: {0}".format(self.client_address[0]))
        client = self.request  # client socket

        try:
            while True:
                reqMsg = MessageUtil.receive(client);
                if reqMsg == None:
                    continue

                if reqMsg.Header.MSGTYPE == message.REQ_CONNECT:  # 전송 요청 처리
                    rspMsg = Message()
                    rspMsg.Body = BodyCommonResponse(None)
                    rspMsg.Body.RESPONSE = message.ACCEPTED

                    rspMsg.Header = Header(None)
                    rspMsg.Header.MSGTYPE = message.REP_CONNECT
                    rspMsg.Header.BODYLEN = rspMsg.Body.getSize()

                    MessageUtil.send(client, rspMsg)
                    continue

                # 음성 토큰 요청 처리
                elif reqMsg.Header.MSGTYPE == message.REQ_GET_TOKEN:
                    rspMsg = Message()
                    rspMsg.Body = BodyCommonResponse(None)
                    rspMsg.Body.RESPONSE = message.ACCEPTED

                    rspMsg.Header = Header(None)
                    rspMsg.Header.MSGTYPE = message.REP_GET_TOKEN
                    rspMsg.Header.BODYLEN = rspMsg.Body.getSize()
                    (hasToken, tokenLender) = self.rm.getTokenStatus()

                    if hasToken:
                        self.rm.lockToken(self.client_address[0])
                        print('token 방출')
                    else:
                        rspMsg.Body.RESPONSE = message.DENIED
                        print('token 없음')

                    MessageUtil.send(client, rspMsg)
                    continue

                # 음성 토큰 반납 처리
                elif reqMsg.Header.MSGTYPE == message.REQ_RETURN_TOKEN:
                    rspMsg = Message()
                    rspMsg.Body = BodyEmpty()

                    rspMsg.Header = Header(None)
                    rspMsg.Header.MSGTYPE = message.REP_RETURN_TOKEN
                    rspMsg.Header.BODYLEN = rspMsg.Body.getSize()

                    self.rm.freeToken()

                    print("토큰 획득")

                    MessageUtil.send(client, rspMsg)
                    continue

                elif reqMsg.Header.MSGTYPE == message.REQ_VIDEO_STREAMING:
                    if not self.rm.getCallStatus():
                        self.rm.lockCall()
                        requestDialog = RequestDialog("구조대원")

                        # ret == 0: 연결 수락 / ret == 1: 연결 거절
                        ret = requestDialog.showDialog()
                        rspMsg = Message()
                        rspMsg.Header = Header(None)
                        rspMsg.Body = BodyCommonResponse(None)
                        rspMsg.Body.RESPONSE = message.ACCEPTED

                        rspMsg.Header.MSGTYPE = message.REP_VIDEO_STREAMING
                        rspMsg.Header.BODYLEN = rspMsg.Body.getSize()
                        print(ret)
                        if (ret == 0):
                            MessageUtil.send(client, rspMsg)

                            # 플레이어 실행
                            #os.system("D:\\gstreamer\\1.0\\x86_64\\bin\\gst-launch-1.0 -e -v udpsrc port=5000 ! application/x-rtp, payload=96 ! rtpjitterbuffer ! rtph264depay ! avdec_h264 ! fpsdisplaysink sync=false text-overlay=false")
                            self.gstreamer = subprocess.Popen('D:\\gstreamer\\1.0\\x86_64\\bin\\gst-launch-1.0 -e -v udpsrc port=5000 ! application/x-rtp, payload=96 ! rtpjitterbuffer ! rtph264depay ! avdec_h264 ! fpsdisplaysink sync=false text-overlay=false', shell=True)

                        else:
                            rspMsg.Body.RESPONSE = message.DENIED
                            MessageUtil.send(client, rspMsg)

                        self.rm.freeCall()
                    else:
                        None

                    continue

                elif reqMsg.Header.MSGTYPE == message.REQ_EXIT_VIDEO_STREAMING:
                    if self.rm.getCallStatus():
                            self.rm.freeCall()

                    rspMsg = Message()
                    rspMsg.Body = BodyEmpty()

                    rspMsg.Header = Header(None)
                    rspMsg.Header.MSGTYPE = message.REP_EXIT_VIDEO_STREAMING
                    rspMsg.Header.BODYLEN = rspMsg.Body.getSize()

                    MessageUtil.send(client, rspMsg)

                    #self.gstreamer.kill()
                    subprocess.Popen("TASKKILL /F /PID {pid} /T".format(pid=self.gstreamer.pid))

                    print('통화종료 요청')

                    continue
                elif reqMsg.Header.MSGTYPE == message.REP_EXIT_VIDEO_STREAMING:
                    None
        except Exception as err:
            print("Exception")
            print(err);
            (hasToken, tokenLender) = self.rm.getTokenStatus()

            if not hasToken and tokenLender == self.client_address[0]:
                self.rm.freeToken()
            return False


class ThreadedTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    pass

if __name__ == '__main__':
    server = ThreadedTCPServer((HOST, PORT), RequestHandler)
    threading.Thread(target=server.serve_forever).start()
