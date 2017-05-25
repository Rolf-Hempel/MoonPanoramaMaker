# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ViewLandmarks.ui'
#
# Created: Thu May 25 15:50:56 2017
#      by: PyQt4 UI code generator 4.9.6
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

class Ui_ViewLandmarks(object):
    def setupUi(self, ViewLandmarks):
        ViewLandmarks.setObjectName(_fromUtf8("ViewLandmarks"))
        ViewLandmarks.resize(577, 442)
        font = QtGui.QFont()
        font.setPointSize(10)
        ViewLandmarks.setFont(font)
        ViewLandmarks.setLocale(QtCore.QLocale(QtCore.QLocale.English, QtCore.QLocale.UnitedStates))
        self.label = QtGui.QLabel(ViewLandmarks)
        self.label.setGeometry(QtCore.QRect(9, 9, 560, 373))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.label.setFont(font)
        self.label.setLocale(QtCore.QLocale(QtCore.QLocale.English, QtCore.QLocale.UnitedStates))
        self.label.setText(_fromUtf8(""))
        self.label.setObjectName(_fromUtf8("label"))
        self.comboBox = QtGui.QComboBox(ViewLandmarks)
        self.comboBox.setGeometry(QtCore.QRect(10, 410, 461, 22))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.comboBox.setFont(font)
        self.comboBox.setLocale(QtCore.QLocale(QtCore.QLocale.English, QtCore.QLocale.UnitedStates))
        self.comboBox.setObjectName(_fromUtf8("comboBox"))
        self.line = QtGui.QFrame(ViewLandmarks)
        self.line.setGeometry(QtCore.QRect(10, 390, 557, 21))
        self.line.setFrameShape(QtGui.QFrame.HLine)
        self.line.setFrameShadow(QtGui.QFrame.Sunken)
        self.line.setObjectName(_fromUtf8("line"))
        self.OKButton = QtGui.QPushButton(ViewLandmarks)
        self.OKButton.setGeometry(QtCore.QRect(490, 410, 75, 23))
        self.OKButton.setObjectName(_fromUtf8("OKButton"))

        self.retranslateUi(ViewLandmarks)
        self.comboBox.setCurrentIndex(-1)
        QtCore.QMetaObject.connectSlotsByName(ViewLandmarks)

    def retranslateUi(self, ViewLandmarks):
        ViewLandmarks.setWindowTitle(_translate("ViewLandmarks", "Select Landmark", None))
        self.OKButton.setText(_translate("ViewLandmarks", "OK", None))

