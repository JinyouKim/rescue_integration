# -*- coding: utf-8 -*-
import sys
from PyQt5.QtWidgets import QApplication, QDialog
from rescue.rescueserver.ui.ui_request_dialog import Ui_RequestDialog


class RequestDialog():
    def __init__(self, rescuer_info):
        self.rescuer_info = rescuer_info

    def showDialog(self):
        app = QApplication(sys.argv)
        window = QDialog()
        ui = Ui_RequestDialog()
        ui.setupUi(window, self.rescuer_info)
        window.show()

        app.exec_()
        return ui.ret

