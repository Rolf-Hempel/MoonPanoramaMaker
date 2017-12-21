# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'input_error_dialog.ui'
#
# Created by: PyQt5 UI code generator 5.6
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_InputErrorDialog(object):
    def setupUi(self, InputErrorDialog):
        InputErrorDialog.setObjectName("InputErrorDialog")
        InputErrorDialog.resize(262, 178)
        self.okbutton = QtWidgets.QPushButton(InputErrorDialog)
        self.okbutton.setGeometry(QtCore.QRect(170, 140, 75, 23))
        self.okbutton.setObjectName("okbutton")
        self.message = QtWidgets.QLabel(InputErrorDialog)
        self.message.setGeometry(QtCore.QRect(10, 10, 241, 121))
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setBold(True)
        font.setWeight(75)
        self.message.setFont(font)
        self.message.setObjectName("message")

        self.retranslateUi(InputErrorDialog)
        QtCore.QMetaObject.connectSlotsByName(InputErrorDialog)

    def retranslateUi(self, InputErrorDialog):
        _translate = QtCore.QCoreApplication.translate
        InputErrorDialog.setWindowTitle(_translate("InputErrorDialog", "Input Error"))
        self.okbutton.setText(_translate("InputErrorDialog", "OK"))
        self.message.setText(_translate("InputErrorDialog", "Invalid input for parameter"))

