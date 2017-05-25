# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'DisplayLandmark.ui'
#
# Created: Thu May 25 15:42:04 2017
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

class Ui_DisplayLandmark(object):
    def setupUi(self, DisplayLandmark):
        DisplayLandmark.setObjectName(_fromUtf8("DisplayLandmark"))
        DisplayLandmark.resize(577, 442)
        font = QtGui.QFont()
        font.setPointSize(10)
        DisplayLandmark.setFont(font)
        DisplayLandmark.setLocale(QtCore.QLocale(QtCore.QLocale.English, QtCore.QLocale.UnitedStates))
        self.landmark_picture = QtGui.QLabel(DisplayLandmark)
        self.landmark_picture.setGeometry(QtCore.QRect(9, 9, 560, 373))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.landmark_picture.setFont(font)
        self.landmark_picture.setLocale(QtCore.QLocale(QtCore.QLocale.English, QtCore.QLocale.UnitedStates))
        self.landmark_picture.setText(_fromUtf8(""))
        self.landmark_picture.setObjectName(_fromUtf8("landmark_picture"))
        self.buttonBox = QtGui.QDialogButtonBox(DisplayLandmark)
        self.buttonBox.setGeometry(QtCore.QRect(485, 410, 81, 23))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.buttonBox.setFont(font)
        self.buttonBox.setLocale(QtCore.QLocale(QtCore.QLocale.English, QtCore.QLocale.UnitedStates))
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.line = QtGui.QFrame(DisplayLandmark)
        self.line.setGeometry(QtCore.QRect(10, 390, 557, 21))
        self.line.setFrameShape(QtGui.QFrame.HLine)
        self.line.setFrameShadow(QtGui.QFrame.Sunken)
        self.line.setObjectName(_fromUtf8("line"))
        self.landmark_name = QtGui.QLabel(DisplayLandmark)
        self.landmark_name.setGeometry(QtCore.QRect(10, 410, 451, 16))
        self.landmark_name.setObjectName(_fromUtf8("landmark_name"))

        self.retranslateUi(DisplayLandmark)
        QtCore.QMetaObject.connectSlotsByName(DisplayLandmark)

    def retranslateUi(self, DisplayLandmark):
        DisplayLandmark.setWindowTitle(_translate("DisplayLandmark", "Show Selected Landmark", None))
        self.landmark_name.setText(_translate("DisplayLandmark", "TextLabel", None))

