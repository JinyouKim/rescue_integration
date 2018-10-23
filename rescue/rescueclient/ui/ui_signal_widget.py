# -*- coding: utf-8 -*-
from PyQt5 import QtWidgets, QtGui, QtCore

class UiSignalWidget(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(UiSignalWidget, self).__init__(parent)
        self.setObjectName("SignalWidget")
        width = parent.width() - 100
        height = parent.height() - 100
        self.resize(width, height)
        self.setWindowFlags(QtCore.Qt.CustomizeWindowHint)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)

        self.fillColor = QtGui.QColor(30, 30, 30, 120)
        self.penColor = QtGui.QColor("#333333")

        font = QtGui.QFont()
        font.setPixelSize(24)
        font.setBold(True)

        # 레이아웃
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setSpacing(30)
        self.verticalLayout.setObjectName("verticalLayout")

        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)


        self.searchCompleteBtn = QtWidgets.QPushButton("현위치 탐색 완료")
        self.searchCompleteBtn.setFont(font)
        self.searchCompleteBtn.setStyleSheet('background-color: rgb(133,232,224);border:3px solid rgb(20,179,120)')
        self.searchCompleteBtn.setSizePolicy(sizePolicy)
        self.verticalLayout.addWidget(self.searchCompleteBtn)
        #self.searchCompleteBtn.clicked.connect(self._onpopup)

        self.findRescueeBtn = QtWidgets.QPushButton("현위치 생존자 발견")
        self.findRescueeBtn.setFont(font)
        self.findRescueeBtn.setStyleSheet('background-color: rgb(255,255,61);border:3px solid rgb(240,202,77)')
        self.findRescueeBtn.setSizePolicy(sizePolicy)
        self.verticalLayout.addWidget(self.findRescueeBtn)
        #self.searchCompleteBtn.clicked.connect(self._onpopup)

        self.findRescuerBtn = QtWidgets.QPushButton("현위치 소방관 조난")
        self.findRescuerBtn.setFont(font)
        self.findRescuerBtn.setSizePolicy(sizePolicy)
        self.findRescuerBtn.setStyleSheet('background-color: rgb(255,93,78);border:3px solid rgb(237,55,82)')
        self.verticalLayout.addWidget(self.findRescuerBtn)
        #self.searchCompleteBtn.clicked.connect(self._onpopup)

        self.setLayout(self.verticalLayout)

    def resizeEvent(self, event):
        None

    def paintEvent(self, event):
        None
