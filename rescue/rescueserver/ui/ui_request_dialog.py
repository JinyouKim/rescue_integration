# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'videoRequest.ui'
#
# Created by: PyQt5 UI code generator 5.11.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QMessageBox




class Ui_RequestDialog(object):
    def setupUi(self, Dialog, rescuer_info):
        Dialog.setObjectName("Dialog")
        Dialog.setWindowModality(QtCore.Qt.ApplicationModal)
        Dialog.resize(500, 100)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(Dialog.sizePolicy().hasHeightForWidth())
        Dialog.setSizePolicy(sizePolicy)
        Dialog.setMinimumSize(QtCore.QSize(500, 100))
        Dialog.setMaximumSize(QtCore.QSize(500, 100))
        Dialog.setAutoFillBackground(False)
        Dialog.setSizeGripEnabled(False)
        self.buttonBox = QtWidgets.QDialogButtonBox(Dialog)
        self.buttonBox.setGeometry(QtCore.QRect(0, 70, 341, 32))
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.buttonBox.accepted.connect(self.accept_clicked)
        self.buttonBox.rejected.connect(self.reject_clicked)
        self.textBrowser = QtWidgets.QTextBrowser(Dialog)
        self.textBrowser.setGeometry(QtCore.QRect(0, 0, 501, 201))
        font = QtGui.QFont()
        font.setFamily("함초롬돋움")
        self.textBrowser.setFont(font)
        self.textBrowser.setAutoFillBackground(True)
        self.textBrowser.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.textBrowser.setObjectName("textBrowser")
        self.textBrowser.raise_()
        self.buttonBox.raise_()

        self.retranslateUi(Dialog, rescuer_info)
        self.buttonBox.accepted.connect(Dialog.accept)
        self.buttonBox.rejected.connect(Dialog.reject)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def accept_clicked(self):
        print("123")
        self.ret = 0

    def reject_clicked(self):
        print('234')
        self.ret = 1

    def retranslateUi(self, Dialog, text):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Video Streaming Request"))
        self.textBrowser.setHtml("["+text+"]"+ "로 부터의 영상통신 요청을 수락하시겠습니까?");



