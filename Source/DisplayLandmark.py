# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'DisplayLandmark.ui'
#
# Created by: PyQt5 UI code generator 5.6
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_DisplayLandmark(object):
    def setupUi(self, DisplayLandmark):
        DisplayLandmark.setObjectName("DisplayLandmark")
        DisplayLandmark.resize(577, 442)
        font = QtGui.QFont()
        font.setPointSize(10)
        DisplayLandmark.setFont(font)
        DisplayLandmark.setLocale(QtCore.QLocale(QtCore.QLocale.English, QtCore.QLocale.UnitedStates))
        self.landmark_picture = QtWidgets.QLabel(DisplayLandmark)
        self.landmark_picture.setGeometry(QtCore.QRect(9, 9, 560, 373))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.landmark_picture.setFont(font)
        self.landmark_picture.setLocale(QtCore.QLocale(QtCore.QLocale.English, QtCore.QLocale.UnitedStates))
        self.landmark_picture.setText("")
        self.landmark_picture.setObjectName("landmark_picture")
        self.buttonBox = QtWidgets.QDialogButtonBox(DisplayLandmark)
        self.buttonBox.setGeometry(QtCore.QRect(485, 410, 81, 23))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.buttonBox.setFont(font)
        self.buttonBox.setLocale(QtCore.QLocale(QtCore.QLocale.English, QtCore.QLocale.UnitedStates))
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.line = QtWidgets.QFrame(DisplayLandmark)
        self.line.setGeometry(QtCore.QRect(10, 390, 557, 21))
        self.line.setFrameShape(QtWidgets.QFrame.HLine)
        self.line.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line.setObjectName("line")
        self.landmark_name = QtWidgets.QLabel(DisplayLandmark)
        self.landmark_name.setGeometry(QtCore.QRect(10, 410, 451, 16))
        self.landmark_name.setObjectName("landmark_name")

        self.retranslateUi(DisplayLandmark)
        QtCore.QMetaObject.connectSlotsByName(DisplayLandmark)

    def retranslateUi(self, DisplayLandmark):
        _translate = QtCore.QCoreApplication.translate
        DisplayLandmark.setWindowTitle(_translate("DisplayLandmark", "Show Selected Landmark"))
        self.landmark_name.setText(_translate("DisplayLandmark", "TextLabel"))

