import subprocess
import threading
from picamera import PiCamera
from picamera.array import PiRGBArray
from PyQt5.QtGui import QPainter, QPixmap, QImage

class CameraModule:
    def __init__(self):
        self.camera = PiCamera()
        self.camera.resolution = (1920,1080)
        self.camera.framerate = 30
        self.rawCapture = PiRGBArray(self.camera, size = (1920,1080))
        
        self.camera.hflip = True

    def startStreaming(self, ip, port):
        host = 'host='+ip
        portnum = 'port='+str(port)
        self.gstreamer = subprocess.Popen(['gst-launch-1.0', '-vvvv', '-e', 'fdsrc', '!', 'h264parse', '!', 'rtph264pay', 'pt=96','config-interval=5', '!', 'udpsink', host, portnum] , stdin=subprocess.PIPE)
        self.camera.start_recording(self.gstreamer.stdin, format = 'h264', bitrate = 5000000)
        
    def stopStreaming(self):
        self.camera.stop_recording()        
        self.gstreamer.stdin.close()
        self.gstreamer.wait()

    def startPreview(self, q):
        t = threading.currentThread()
        for frame in self.camera.capture_continuous(self.rawCapture, format = 'rgb', use_video_port = True):
            if not getattr(t, "do_run", True):
                self.camera.close()
                break;
            image = frame.array
            self.rawCapture.truncate(0)                    
            qimage = QImage(image.tobytes(), 1920, 1080, QImage.Format_RGB888)
            pixmap = QPixmap.fromImage(qimage)            
            q.put(pixmap)
