#!/usr/bin/python3

import thriftpy
from thriftpy.rpc import make_client

class ThriftUI:
    def __init__(self):
        pass

    # ip_addr : server ip in string format
    # port : port number in int format (9090 default)
    def connect(self, ip_addr, port, thrift_file_path):
        self.ui_thrift = thriftpy.load(thrift_file_path);
        self.THRIFT_SMS_FMAN_DATA = self.ui_thrift.THRIFT_SMS_FMAN_DATA
        self.THRIFT_MAP_IMAGE = self.ui_thrift.THRIFT_MAP_IMAGE
        self.THRIFT_SENSOR_DATA = self.ui_thrift.THRIFT_SENSOR_DATA
        self.THRIFT_IPLIMAGE = self.ui_thrift.THRIFT_IPLIMAGE
        self.THRIFT_QIMAGE = self.ui_thrift.THRIFT_QIMAGE

        self.client = make_client(self.ui_thrift.Control, ip_addr, port)

    # refer threadDwm1000.cpp, mainwindow.cpp
    def reportRescuerPosition(self, objid, x, y, isSearchCount, isSearchPeople, isSosFman):
        fman_data = self.THRIFT_SMS_FMAN_DATA(objid, x, y, isSearchCount, isSearchPeople, isSosFman)
        self.client.rescuerPosition(fman_data)

    # deprecated (no camera image upload)
    def uploadSceneImage(self, sceneImage):
        pass

    # return THRIFT_SENSOR_DATA class
    # attributes
    # 1. Temperature (double)
    # 2. Fire (double)
    # 3. Smoke (double)
    # 4. Humidity (double)
    # 5. Motion (double)
    def retrieveSensorData(self):
        return self.client.sensorData()

    # return THRIFT_IPLIMAGE
    # 1. width (i16=int16)
    # 2. height (i16=int16)
    # 3. nChannels (i16=int16)
    # 4. widthStep (i16=int16)
    # 5. depth (i16=int16)
    # 6. imageData (binary?)
    # you may need OpenCV library to recover and utilize IplImage class
    def downloadMapIplImage(self):
        return self.client.mapIplImage()


