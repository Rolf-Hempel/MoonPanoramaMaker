# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'tile_number_input_dialog.ui'
#
# Created by: PyQt5 UI code generator 5.6
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_TileNumberInputDialog(object):
    def setupUi(self, TileNumberInputDialog):
        TileNumberInputDialog.setObjectName("TileNumberInputDialog")
        TileNumberInputDialog.resize(258, 106)
        font = QtGui.QFont()
        font.setPointSize(10)
        TileNumberInputDialog.setFont(font)
        TileNumberInputDialog.setFocusPolicy(QtCore.Qt.TabFocus)
        self.buttonBox = QtWidgets.QDialogButtonBox(TileNumberInputDialog)
        self.buttonBox.setGeometry(QtCore.QRect(40, 60, 201, 32))
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.label = QtWidgets.QLabel(TileNumberInputDialog)
        self.label.setGeometry(QtCore.QRect(10, 10, 151, 31))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.label.setFont(font)
        self.label.setObjectName("label")
        self.spinBox = QtWidgets.QSpinBox(TileNumberInputDialog)
        self.spinBox.setGeometry(QtCore.QRect(170, 20, 61, 22))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.spinBox.setFont(font)
        self.spinBox.setMaximum(1000)
        self.spinBox.setObjectName("spinBox")

        self.retranslateUi(TileNumberInputDialog)
        self.buttonBox.accepted.connect(TileNumberInputDialog.accept)
        self.buttonBox.rejected.connect(TileNumberInputDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(TileNumberInputDialog)
        TileNumberInputDialog.setTabOrder(self.spinBox, self.buttonBox)

    def retranslateUi(self, TileNumberInputDialog):
        _translate = QtCore.QCoreApplication.translate
        TileNumberInputDialog.setWindowTitle(_translate("TileNumberInputDialog", "Tile Chooser"))
        self.label.setText(_translate("TileNumberInputDialog", "Enter tile number:"))

