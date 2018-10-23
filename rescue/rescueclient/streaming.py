import sys
import random
import socket
import time
import struct

RTP_HEADER_SIZE = 12

class RtpPacket:
    def __init__(self):
        self.header = bytearray(RTP_HEADER_SIZE)

    def encode(self, version, padding, extension, cc, seqnum, marker, pt, ssrc, payload):
        timestamp = int(time.time())
        self.header[0] = self.header[0] | version << 6
        self.header[0] = self.header[0] | padding << 5
        self.header[0] = self.header[0] | extension << 4
        self.header[0] = self.header[0] | cc
        self.header[1] = marker << 7
        self.header[1] = self.header[1] | pt

        self.header[2] = seqnum >> 8
        self.header[3] = (seqnum >> 0) & 0xff

        
        self.header[4] = (timestamp >> 24) & 0xFF
        self.header[5] = (timestamp >> 16) & 0xFF
        self.header[6] = (timestamp >> 8) & 0xFF
        self.header[7] = timestamp & 0xFF

        self.header[8] = (ssrc >> 24) & 0xFF
        self.header[9] = (ssrc >> 16) & 0xFF
        self.header[10] = (ssrc >> 8) & 0xFF
        self.header[11] = ssrc & 0xFF

        self.payload = payload

    def decode(self, byteStream):
        self.header = bytearray(byteStream[:RTP_HEADER_SIZE])
        self.payload = byteStream[RTP_HEADER_SIZE:]

    def getPayload(self):
        return self.payload

    def getPacket(self):
        return self.header + self.payload

class VoiceStreaming:
    def __init__(self, myIp, myPort, remoteIp, remotePort):        
        self.ssrc = int(random.randrange(0,2147483647))
        self.localIp = myIp
        self.localPort = myPort
        self.remoteIp = remoteIp
        self.remotePort = remotePort
        self.sndRtpPacket = RtpPacket()
        self.recvRtpPacket = RtpPacket()
        self.sndSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.recvSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
#        self.recvSocket.settimeout(0.5)

        self.sndSeqNum = 0x00
        self.recvSeqNum = 0x00
        
        try:
            print(self.localIp)
            print(self.localPort)
            self.recvSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.recvSocket.bind((self.localIp, self.localPort))
        except Exception as err:
            print(err)


    def sendVoicePacket(self, voiceData):
        self.sndRtpPacket.encode(2, 0, 0, 0, self.sndSeqNum, 0, 18, self.ssrc, voiceData)
        self.sndSocket.sendto(self.sndRtpPacket.getPacket(), (self.remoteIp, self.remotePort))

        if self.sndSeqNum != 0xffff:
            self.sndSeqNum = self.sndSeqNum + 0x0001
        else:
            self.sndSeqNum = 0x0000

    def recvVoicePacket(self):
        data, addr = self.recvSocket.recvfrom(256)
        self.sndRtpPacket.decode(data)
        return self.sndRtpPacket.getPayload()

    def closeSocket(self):
        self.sndSocket.close()
        self.recvSocket.close()


        
        
if __name__ == '__main__':
    vs= VoiceStreaming('192.168.1.61', 8000)
    a = vs.recvVoicePacket()
    print(a)
    
    






