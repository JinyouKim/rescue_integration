# -*- coding: utf-8 -*-
from PyQt5 import QtWidgets, QtGui, QtCore

class UiVideoWidget(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(UiVideoWidget, self).__init__(parent)

        # make the window frameless
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)

        self.verticalLayout = QtWidgets.QVBoxLayout(self)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setSpacing(0)
        self.verticalLayout.setObjectName("verticalLayout")
        
        self.frameLabel = QtWidgets.QLabel(self)
        self.frameLabel.setMaximumSize(480,800)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.frameLabel.sizePolicy().hasHeightForWidth())
        self.frameLabel.setSizePolicy(sizePolicy)
        self.frameLabel.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frameLabel.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frameLabel.setLineWidth(1)
        self.frameLabel.setObjectName("frameLabel")
        self.verticalLayout.addWidget(self.frameLabel)
        
        self.line = QtWidgets.QFrame(self)
        self.line.setFrameShape(QtWidgets.QFrame.HLine)
        self.line.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line.setObjectName("line")
        self.verticalLayout.addWidget(self.line)

        self.stopButton = QtWidgets.QPushButton(self)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.stopButton.sizePolicy().hasHeightForWidth())
        self.stopButton.setSizePolicy(sizePolicy)
        self.stopButton.setMinimumSize(QtCore.QSize(150, 150))
        self.stopButton.setText("Stop")
        self.stopButton.setCheckable(False)
        self.stopButton.setObjectName("stopButton")
        self.verticalLayout.addWidget(self.stopButton)

   


