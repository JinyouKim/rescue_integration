# -*- coding: utf-8 -*-
import sys
import socketserver
import socket
import threading
import queue
import PyQt5.QtCore
import numpy as np

from PyQt5.QtCore import QTimeLine
from PyQt5.QtGui import QPainter, QPixmap, QImage
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtCore import QObject, Qt

from rescue.rescueclient.ffmpeg_bridge import FfmpegBridge
from rescue.rescueclient.socket_manager import SocketManager
from PyQt5.QtWidgets import QApplication, QDialog, QMessageBox, QStackedWidget, QWidget
from rescue.rescueclient.ui.ui_client_dialog import UiClientDialog
from rescue.rescueclient.ui.ui_signal_widget import UiSignalWidget
from rescue.rescueclient.ui.ui_translucent_widget import UiTranslucentWidget
from rescue.rescueclient.ui.ui_calling_widget import UiCallingWidget
from rescue.rescueclient.sound import SoundManager
from rescue.rescueclient.codec import OpusCodec
from rescue.rescueclient.streaming import VoiceStreaming
from rescue.rescueclient.image_converter import ImageConverter
from rescue.rescueclient.camera_module import CameraModule

from rescue.common import message
from rescue.common.message import Message
from rescue.common.message_util import MessageUtil
from rescue.common.message_header import Header
from rescue.common.message_body import BodyCommonResponse, BodyEmpty

from picamera import PiCamera
from picamera.array import PiRGBArray



HOST = '192.0.1.10'
PORT = 9900

REMOTE = ''

q1 = queue.Queue()
q2 = queue.Queue()
q3 = queue.Queue()

class ThreadedTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    pass

class RequestHandler(socketserver.BaseRequestHandler):
    def handle(self):
        client = self.request
        try:
            while True:
                reqMsg = MessageUtil.receive(client)
                print(reqMsg.Header.MSGTYPE)
                if reqMsg == None:
                    continue
                if reqMsg.Header.MSGTYPE == message.REQ_CALL: 
                    global REMOTE
                    print(self.client_address[0])
                    REMOTE = self.client_address[0]
                    q1.put(0)
                    isAccepted = q2.get()

                    rspMsg = Message()
                    rspMsg.Body = BodyCommonResponse(None)
                    if isAccepted:
                        rspMsg.Body.RESPONSE = message.ACCEPTED
                    else:
                        rspMsg.Body.RESPONSE = message.DENIED

                    rspMsg.Header = Header(None)
                    rspMsg.Header.MSGTYPE = message.REP_CALL
                    print(message.REP_CALL)
                    rspMsg.Header.BODYLEN = rspMsg.Body.getSize()
                    MessageUtil.send(client, rspMsg)

                    continue

                elif reqMsg.Header.MSGTYPE == message.REQ_CALL_STOP:
                    q3.put(0)
                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                    sock.connect((REMOTE, 8001))
                    sock.close()
                
                    continue

        except Exception as err:
            print(err)

class CallSignal(QObject):
    callSignal = pyqtSignal()
    acceptSignal = pyqtSignal()
    
    def emitCallSignal(self):
        print('asdf')
        self.callSignal.emit()

    def emitAcceptSignal(self):
        self.acceptSignal.emit()


class ClientDialog():
    def __init__(self, sm, threadThrift):
        self.sm = sm
        self.threadThrift = threadThrift
        self.soundManager= SoundManager()
        self.isVoiceCalling = False
        self.isClickedSignal = False

        self.multicastVs = VoiceStreaming(self.sm.myIp, self.sm.multicastPort, self.sm.multicastIp, self.sm.multicastPort)
        self.ffmpegBridge = FfmpegBridge(sm)
        self.ffmpegBridge.playAudioStream()
        self.callSignal = CallSignal()
        self.callSignal.callSignal.connect(self.call_handle)
        self.callSignal.acceptSignal.connect(self.accept_handle)
        self.streamThread = threading.Thread(target = self.streaming_handle, args = ("task",))
        self.multicastSendThread = threading.Thread(target = self.multicast_stream_thread, args=("task",))
        self.stopCallThread = threading.Thread(target = self.stop_call_thread)
        
        self.multicastRecvThread = threading.Thread(target = self.multicast_play_thread, args=("task",))
        self.multicastRecvThread.start()
        self.oc = OpusCodec()

        requestListener = ThreadedTCPServer((HOST, PORT), RequestHandler)
        threading.Thread(target=requestListener.serve_forever).start()
        callThread = threading.Thread(target = self.call_thread)
        callThread.start()
        threadThrift.start()
        
    def multicast_stream_thread(self, arg):
        self.soundManager.startRecord()
        t = threading.currentThread()
        while getattr(t, "do_run", True):
            pcm = self.soundManager.getInputFrame().tobytes()
            self.multicastVs.sendVoicePacket(self.oc.encodeFrames(pcm))

        self.soundManager.stopRecord()
        #multicastVs.closeSocket()

    def play_thread(self, arg):
        t = threading.currentThread()
        isStarted = False
        while getattr(t, "do_run", True):
            opusFrame = self.callVs.recvVoicePacket()
            pcm = self.oc.decodeFrames(opusFrame)
            self.soundManager.pushFrame(pcm)
            if isStarted is False:
                 self.soundManager.startPlay()
            isStarted = True

        self.soundManager.stopPlay()

    def multicast_play_thread(self, arg):
        isStarted = False
        t = threading.currentThread()
        while getattr(t, "do_run", True):
            opusFrame = self.multicastVs.recvVoicePacket()
            pcm = self.oc.decodeFrames(opusFrame)
            self.soundManager.pushFrame(pcm)
            if isStarted is False:
                 self.soundManager.startPlay()
            isStarted = True

        #multicastVs.closeSocket()
        self.soundManager.stopPlay()
             
    def accept_handle(self):
        #Calling UI Setting
        self.callingFrame = UiCallingWidget(self.dialog)
        self.callingFrame.stopButton.clicked.connect(self.clickedCallingStopButton)
        self.callingFrame.move(0, 0)
        self.callingFrame.resize(self.dialog.width(), self.dialog.height())
        self.callingFrame.show()


    def streaming_handle(self, arg):
        self.stopCallThread = threading.Thread(target = self.stop_call_thread)
        self.stopCallThread.start()
        self.callSignal.emitAcceptSignal()
        self.soundManager.startRecord()
        self.playThread = threading.Thread(target = self.play_thread, args = ("task",))
        self.playThread.start()
        t = threading.currentThread()        

        while getattr(t, "do_run", True):
            pcm = self.soundManager.getInputFrame().tobytes()
            self.callVs.sendVoicePacket(self.oc.encodeFrames(pcm))

        self.playThread.do_run = False
        self.soundManager.stopRecord()
        self.callVs.closeSocket()
        #self.callVs.closeSocket()
            
        
    def call_handle(self):
        self.soundManager.playRing()
        choice = QMessageBox.question(self.dialog, "Call", "Calling from Rescuee, Accept?", QMessageBox.Yes | QMessageBox.No)
        isAccepted = False
        if choice == QMessageBox.Yes:
            q2.put(True)            
            self.multicastRecvThread.do_run = False
            self.streamThread = threading.Thread(target = self.streaming_handle, args = ("task",))
            self.streamThread.start()
            # rtp Thread
            
        else:
            q2.put(False)
        self.soundManager.stopRing()

    def call_thread(self):
        while True:
            q1.get()            
            self.callVs = VoiceStreaming('192.0.1.10', 8000, REMOTE, 8000)        
            self.callSignal.emitCallSignal()

    def stop_call_thread(self):
        q3.get()
        self.streamThread.do_run = False
        self.callingFrame.close()
        self.multicastRecvThread = threading.Thread(target = self.multicast_play_thread, args=("task",))
        self.multicastRecvThread.start()

    def video_streaming_thread(self, arg):
        q = queue.Queue()
        cm = CameraModule()
        server = self.sm.serverIp
        cm.startStreaming('192.168.0.110', 5000)
        previewThread = threading.Thread(target = cm.startPreview, args = (q,))
        previewThread.start()
        t = threading.currentThread()

        while getattr(t, "do_run", True):
            if q.empty():
                pass
            else:
                pixmap = q.get_nowait()
                pixmap = pixmap.scaled(self.ui.videoUi.frameLabel.width()-15, self.ui.videoUi.frameLabel.height()-15, Qt.KeepAspectRatio)
                self.ui.videoUi.frameLabel.setPixmap(pixmap)

        cm.stopStreaming()
        previewThread.do_run = False


    def showDialog(self):
        app = QApplication(sys.argv)
        self.dialog = QDialog()
        self.ui = UiClientDialog()
        self.ui.setupUi(self.dialog)

        # 클릭 이벤트
        self.ui.cameraButton.clicked.connect(self.clickedCameraButton)
        self.ui.voiceButton.pressed.connect(self.pressedVoiceButton)
        self.ui.voiceButton.released.connect(self.releasedVoiceButton)
        self.ui.signalButton.clicked.connect(self.clickedSignalButton)        
        self.ui.videoUi.stopButton.clicked.connect(self.clickedVideoStopButton)

        self.threadThrift.mapImageReady.connect(self.mapImage_handle)
        self.threadThrift.sensorDataReady.connect(self.sensorData_handle)
       

        self.dialog.show()

        # 시그널 전송 프레임
        self.signalFrame = UiSignalWidget(self.ui.mapLabel)
        self.signalFrame.searchCompleteBtn.clicked.connect(self.clickedSearchCompleteButton)
        self.signalFrame.findRescueeBtn.clicked.connect(self.clickedFindRescueeButton)
        self.signalFrame.findRescuerBtn.clicked.connect(self.clickedFindRescuerButton)
        self.signalFrame.move(50, 50)

        return app.exec_()


    def clickedCallingStopButton(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.connect((REMOTE, 8001))
        sock.close()

        self.streamThread.do_run = False
        self.callingFrame.close()
        self.multicastRecvThread = threading.Thread(target = self.multicast_play_thread, args=("task",))
        self.multicastRecvThread.start()


    def clickedCameraButton(self):
        self.ffmpegBridge.playButton()
        choice = QMessageBox.question(self.dialog, "Video Streaming", "지휘PC로 영상을 전송 하시겠습니까?", QMessageBox.Yes | QMessageBox.No)
        isAccepted = False
        if choice == QMessageBox.Yes:            
            isAccepted = self.sm.requestVideoCall()

            # 카메라 전송 처리
            if isAccepted:
                self.ui.stack.setPage2()
                self.videoStreamingThread = threading.Thread(target = self.video_streaming_thread, args=("task",))
                self.videoStreamingThread.start()
                                

    def clickedVideoStopButton(self):
        isAccepted = self.sm.requestExitVideo()
        if isAccepted:
            pass
        self.videoStreamingThread.do_run = False
        self.ui.stack.setPage1()

    def pressedVoiceButton(self):
        isAccepted = self.sm.requestVoice()

        # 요청 성공
        if isAccepted:
            self.isVoiceCalling = True
            self.ffmpegBridge.playBeep()
            self.popupFrame = UiTranslucentWidget(self.dialog)
            self.popupFrame.move(0, 0)
            self.popupFrame.resize(self.dialog.width(), self.dialog.height())
            self.popupFlag = True
            self.popupFrame.show()

            #self.ffmpegBridge.sendAudioStream()

            # 음성 전송 처리
            self.multicastSendThread = threading.Thread(target = self.multicast_stream_thread, args=("task",))
            self.multicastSendThread.start()        
           
        # 요청 실패
        else:
            None

    def releasedVoiceButton(self):
        if self.isVoiceCalling:
            isAccepted = self.sm.returnToken()
            self.isVoiceCalling = False
            self.popupFrame.close()
            self.popupFlag = False
            self.multicastSendThread.do_run = False

    def clickedSignalButton(self):
        self.ffmpegBridge.playButton()
        if not self.isClickedSignal:

            self.isClickedSignal = not self.isClickedSignal
            self.signalFrame.show()

        else:
            self.isClickedSignal = not self.isClickedSignal
            self.signalFrame.close()

    def clickedSearchCompleteButton(self):
        self.threadThrift.setSearchCount(True)

    def clickedFindRescueeButton(self):
        self.threadThrift.setSearchPeople(True)

    def clickedFindRescuerButton(self):
        self.threadThrift.setSosFman(True)


    def mapImage_handle(self, iplImageData):        
        image = ImageConverter.IplImageDataToQImage(iplImageData.imageData, iplImageData.width, iplImageData.height, iplImageData.nChannels, iplImageData.widthStep, iplImageData.depth)
        pixmap = QPixmap.fromImage(image)
        pixmap = pixmap.scaled(self.ui.mapLabel.width()-15, self.ui.mapLabel.height()-15, Qt.KeepAspectRatio)
        self.ui.mapLabel.setPixmap(pixmap)

    def sensorData_handle(self, sensorData):
        printStr = ''
        printStr = 'Humidity: ' + '%.2f'%sensorData.Humidity + '\t'
        printStr = printStr + 'Smoke: ' + '%.2f'%sensorData.Smoke + '\t'
        printStr = printStr + 'Motion: ' + '%.2f'%sensorData.Motion + '\n'
        printStr = printStr + 'Temperature: ' + '%.2f'%sensorData.Temperature + '\t'
        printStr = printStr + 'Fire: ' + '%.2f'%sensorData.Fire
        
        self.ui.sensorDataLabel.setText(printStr)
