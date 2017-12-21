# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ViewLandmarks.ui'
#
# Created by: PyQt5 UI code generator 5.6
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_ViewLandmarks(object):
    def setupUi(self, ViewLandmarks):
        ViewLandmarks.setObjectName("ViewLandmarks")
        ViewLandmarks.resize(577, 442)
        font = QtGui.QFont()
        font.setPointSize(10)
        ViewLandmarks.setFont(font)
        ViewLandmarks.setLocale(QtCore.QLocale(QtCore.QLocale.English, QtCore.QLocale.UnitedStates))
        self.label = QtWidgets.QLabel(ViewLandmarks)
        self.label.setGeometry(QtCore.QRect(9, 9, 560, 373))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.label.setFont(font)
        self.label.setLocale(QtCore.QLocale(QtCore.QLocale.English, QtCore.QLocale.UnitedStates))
        self.label.setText("")
        self.label.setObjectName("label")
        self.comboBox = QtWidgets.QComboBox(ViewLandmarks)
        self.comboBox.setGeometry(QtCore.QRect(10, 410, 461, 22))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.comboBox.setFont(font)
        self.comboBox.setLocale(QtCore.QLocale(QtCore.QLocale.English, QtCore.QLocale.UnitedStates))
        self.comboBox.setObjectName("comboBox")
        self.line = QtWidgets.QFrame(ViewLandmarks)
        self.line.setGeometry(QtCore.QRect(10, 390, 557, 21))
        self.line.setFrameShape(QtWidgets.QFrame.HLine)
        self.line.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line.setObjectName("line")
        self.OKButton = QtWidgets.QPushButton(ViewLandmarks)
        self.OKButton.setGeometry(QtCore.QRect(490, 410, 75, 23))
        self.OKButton.setObjectName("OKButton")

        self.retranslateUi(ViewLandmarks)
        self.comboBox.setCurrentIndex(-1)
        QtCore.QMetaObject.connectSlotsByName(ViewLandmarks)

    def retranslateUi(self, ViewLandmarks):
        _translate = QtCore.QCoreApplication.translate
        ViewLandmarks.setWindowTitle(_translate("ViewLandmarks", "Select Landmark"))
        self.OKButton.setText(_translate("ViewLandmarks", "OK"))

