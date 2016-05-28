# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'tile_number_input_dialog.ui'
#
# Created: Mon Aug 24 14:42:53 2015
#      by: PyQt4 UI code generator 4.9.5
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_TileNumberInputDialog(object):
    def setupUi(self, TileNumberInputDialog):
        TileNumberInputDialog.setObjectName(_fromUtf8("TileNumberInputDialog"))
        TileNumberInputDialog.resize(258, 106)
        font = QtGui.QFont()
        font.setPointSize(10)
        TileNumberInputDialog.setFont(font)
        TileNumberInputDialog.setFocusPolicy(QtCore.Qt.TabFocus)
        self.buttonBox = QtGui.QDialogButtonBox(TileNumberInputDialog)
        self.buttonBox.setGeometry(QtCore.QRect(40, 60, 201, 32))
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.label = QtGui.QLabel(TileNumberInputDialog)
        self.label.setGeometry(QtCore.QRect(10, 10, 151, 31))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.label.setFont(font)
        self.label.setObjectName(_fromUtf8("label"))
        self.spinBox = QtGui.QSpinBox(TileNumberInputDialog)
        self.spinBox.setGeometry(QtCore.QRect(170, 20, 61, 22))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.spinBox.setFont(font)
        self.spinBox.setMaximum(1000)
        self.spinBox.setObjectName(_fromUtf8("spinBox"))

        self.retranslateUi(TileNumberInputDialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), TileNumberInputDialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), TileNumberInputDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(TileNumberInputDialog)
        TileNumberInputDialog.setTabOrder(self.spinBox, self.buttonBox)

    def retranslateUi(self, TileNumberInputDialog):
        TileNumberInputDialog.setWindowTitle(QtGui.QApplication.translate("TileNumberInputDialog", "Tile Chooser", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("TileNumberInputDialog", "Enter tile number:", None, QtGui.QApplication.UnicodeUTF8))

