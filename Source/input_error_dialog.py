# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'input_error_dialog.ui'
#
# Created: Mon Aug 24 14:41:44 2015
#      by: PyQt4 UI code generator 4.9.5
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s


class Ui_InputErrorDialog(object):
    def setupUi(self, InputErrorDialog):
        InputErrorDialog.setObjectName(_fromUtf8("InputErrorDialog"))
        InputErrorDialog.resize(262, 178)
        self.okbutton = QtGui.QPushButton(InputErrorDialog)
        self.okbutton.setGeometry(QtCore.QRect(170, 140, 75, 23))
        self.okbutton.setObjectName(_fromUtf8("okbutton"))
        self.message = QtGui.QLabel(InputErrorDialog)
        self.message.setGeometry(QtCore.QRect(10, 10, 241, 121))
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setBold(True)
        font.setWeight(75)
        self.message.setFont(font)
        self.message.setObjectName(_fromUtf8("message"))

        self.retranslateUi(InputErrorDialog)
        QtCore.QMetaObject.connectSlotsByName(InputErrorDialog)

    def retranslateUi(self, InputErrorDialog):
        InputErrorDialog.setWindowTitle(
            QtGui.QApplication.translate("InputErrorDialog", "Input Error",
                                         None, QtGui.QApplication.UnicodeUTF8))
        self.okbutton.setText(
            QtGui.QApplication.translate("InputErrorDialog", "OK", None,
                                         QtGui.QApplication.UnicodeUTF8))
        self.message.setText(QtGui.QApplication.translate("InputErrorDialog",
                                                          "Invalid input for parameter",
                                                          None,
                                                          QtGui.QApplication.UnicodeUTF8))
