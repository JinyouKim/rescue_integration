import time
import threading

from PyQt5.QtCore import pyqtSlot, pyqtSignal, QObject
from thrift_ui import ThriftUI

class ThreadThrift(QObject):

    sensorDataReady = pyqtSignal(object)
    mapImageReady = pyqtSignal(object)
    
    def __init__(self, thriftIp, thriftPort, clientId):
        self.clientId = clientId
        self.thriftUIforMap = ThriftUI()
        self.thriftUIforSensor = ThriftUI()
        self.thriftUIforLocation = ThriftUI()
        self.thriftUIforMap.connect(thriftIp, thriftPort, 'definition.thrift')
        self.thriftUIforSensor.connect(thriftIp, thriftPort, 'definition.thrift')
        self.thriftUIforLocation.connect(thriftIp, thriftPort, 'definition.thrift')

        self.mapThread = threading.Thread(target = self.downloadMap_thread, args = ("task", ))
        self.sensorDataThread = threading.Thread(target = self.downloadSensorData_thread, args = ("task", ))
        self.locationThread = threading.Thread(target = self.uploadLocation_thread, args = ("task", ))

        self.lock = threading.Lock()
        self.x = 0
        self.y = 0
        self.isSearchCount = False
        self.isSearchPeople = False
        self.isSosFman = False
        
        super().__init__()

    def start(self):
        self.mapThread.start()
        self.sensorDataThread.start()
        self.locationThread.start()

    def stop(self):
        self.mapThread.do_run = False
        self.sensorDataThread.do_run = False
        self.locationThread.do_run = False
        

    def uploadLocation_thread(self, arg):
        t = threading.currentThread()
        while getattr(t, "do_run", True):
            (x, y) = self.getLocation()
            isSearchCount = self.getSearchCount()
            isSearchPeople = self.getSearchPeople()
            isSosFman = self.getSosFman()
            self.thriftUIforLocation.reportRescuerPosition(self.clientId, x, y, isSearchCount, isSearchPeople, isSosFman)

            if isSearchCount:
                self.setSearchCount(False)

            if isSearchPeople:
                self.setSearchPeople(False)

            if isSosFman:
                self.setSosFman(False)

            time.sleep(1)

    def downloadMap_thread(self, arg):
        t = threading.currentThread()       
        while getattr(t, "do_run", True):           
            iplImageData = self.thriftUIforMap.downloadMapIplImage()
            self.mapImageReady.emit(iplImageData)
            time.sleep(5)

    def downloadSensorData_thread(self, arg):
        t = threading.currentThread()
        while getattr(t, "do_run", True):
            sensorData = self.thriftUIforSensor.retrieveSensorData()
            self.sensorDataReady.emit(sensorData)
            time.sleep(3)

    def setSearchCount(self, isSearchCount):
        with self.lock:
            self.isSearchCount = isSearchCount

    def setSearchPeople(self, isSearchPeople):
        with self.lock:
            self.isSearchPeople = isSearchPeople

    def setSosFman(self, isSosFman):
        with self.lock:
            self.isSosFman = isSosFman
    
    def setLocation(self, x, y):
        with self.lock:
            self.x = x
            self.y = y

    def getSearchCount(self):
        with self.lock:
            return self.isSearchCount

    def getSearchPeople(self):
        with self.lock:
            return self.isSearchPeople

    def getSosFman(self):
        with self.lock:
            return self.isSosFman

    def getLocation(self):
        with self.lock:
            return self.x, self.y

