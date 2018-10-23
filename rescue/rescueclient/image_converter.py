from PyQt5.QtGui import QImage, qRgb, QPixmap
from thrift_ui import ThriftUI

import numpy as np

IPL_DEPTH_SIGN = 0x80000000
IPL_DEPTH_1U = 1
IPL_DEPTH_8S = (IPL_DEPTH_SIGN | 8)
IPL_DEPTH_8U = 8
IPL_DEPTH_16S = (IPL_DEPTH_SIGN | 16)
IPL_DEPTH_16U = 16
IPL_DEPTH_32S = (IPL_DEPTH_SIGN | 32)
IPL_DEPTH_32F = 32
IPL_DEPTH_64F = 64

gray_color_table = [qRgb(i, i, i) for i in range(256)]


class ImageConverter():
    @staticmethod
    def IplImageDataToQImage(imageData, width, height, channels, widthStep, depth):
        width = int(widthStep / channels)
        depth2dtype = {IPL_DEPTH_8U: 'uint8', IPL_DEPTH_8S: 'int8', IPL_DEPTH_16U: 'uint16', IPL_DEPTH_16S: 'int16', IPL_DEPTH_32S: 'int32', IPL_DEPTH_32F: 'float32', IPL_DEPTH_64F: 'float64',}
        imgArray = np.frombuffer(imageData, dtype=depth2dtype[depth], count = width * height * channels)
        imgArray.shape = (height, width, channels)

        if imgArray.dtype == np.uint8:
            if len(imgArray.shape) == 2:
                qimage = QImage(imgArray.data, imgArray.shape[1], imgArray.shape[0], imgArray.strides[0], QImage.Format_Indexed8)
                qimage.setColorTable(gray_color_table)
                return qimage.copy()
            
            elif len(imgArray.shape) == 3:
                if imgArray.shape[2] == 3:
                    idx = ()
                    for i in range(width):
                        idx = idx + ((i+1)*3, )
                    imgArray = imgArray.reshape((height, width * channels))
                    imgArray = np.insert(imgArray, idx, 0, axis = 1)                    
                    imgArray = imgArray.reshape((height, width, 4))
                    qimage = QImage(imgArray.data, imgArray.shape[1], imgArray.shape[0],QImage.Format_RGB32);
                    return qimage.copy()

                elif imgArray.shape[2] == 4:
                    qimage = QImage(imgArray.data, imgArray.shape[1], imgArray.shape[0], imgArray.strides[0], QImage.Format_ARGB32);
                    return qimage.copy()

    @staticmethod
    def numpyArrayToQImage(array, width, height, channels, widthStep, depth):
        width = int(widthStep / channels)
        depth2dtype = {IPL_DEPTH_8U: 'uint8', IPL_DEPTH_8S: 'int8', IPL_DEPTH_16U: 'uint16', IPL_DEPTH_16S: 'int16', IPL_DEPTH_32S: 'int32', IPL_DEPTH_32F: 'float32', IPL_DEPTH_64F: 'float64',}
        imgArray = array
        imgArray.shape = (height, width, channels)

        if imgArray.dtype == np.uint8:
            if len(imgArray.shape) == 2:
                qimage = QImage(imgArray.data, imgArray.shape[1], imgArray.shape[0], imgArray.strides[0], QImage.Format_Indexed8)
                qimage.setColorTable(gray_color_table)
                return qimage.copy()
            
            elif len(imgArray.shape) == 3:
                if imgArray.shape[2] == 3:
                    idx = ()
                    for i in range(width):
                        idx = idx + ((i+1)*3, )
                    imgArray = imgArray.reshape((height, width * channels))
                    imgArray = np.insert(imgArray, idx, 0, axis = 1)                    
                    imgArray = imgArray.reshape((height, width, 4))
                    qimage = QImage(imgArray.data, imgArray.shape[1], imgArray.shape[0],QImage.Format_RGB32);
                    return qimage.copy()

                elif imgArray.shape[2] == 4:
                    qimage = QImage(imgArray.data, imgArray.shape[1], imgArray.shape[0], imgArray.strides[0], QImage.Format_ARGB32);
                    return qimage.copy()




if __name__ == '__main__':
    thriftUI = ThriftUI()
    thriftUI.connect('192.168.0.110', 9090, 'definition.thrift')
    thriftUI.reportRescuerPosition(1, 1, 2, False, True)
    sensorData = thriftUI.retrieveSensorData()
    iplImageData = thriftUI.downloadMapIplImage()
    a = ImageConverter.IplImageDataToQImage(iplImageData.imageData, iplImageData.width, iplImageData.height, iplImageData.nChannels, iplImageData.widthStep, iplImageData.depth)
    print(a.width())
    a.save('image.png')
    b = QPixmap('image.png')
#    b = QPixmap.fromImage(a).scaled(1000,400,QtCore.Qt.keepAspectRatio)

    
    
