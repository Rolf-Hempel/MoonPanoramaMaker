# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'qtgui.ui'
#
# Created: Tue Oct 17 20:26:58 2017
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

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName(_fromUtf8("MainWindow"))
        MainWindow.resize(850, 274)
        MainWindow.setLocale(QtCore.QLocale(QtCore.QLocale.English, QtCore.QLocale.UnitedStates))
        self.centralwidget = QtGui.QWidget(MainWindow)
        self.centralwidget.setObjectName(_fromUtf8("centralwidget"))
        self.gridLayout = QtGui.QGridLayout(self.centralwidget)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.prompt_text_browser = QtGui.QTextBrowser(self.centralwidget)
        font = QtGui.QFont()
        font.setPointSize(10)
        self.prompt_text_browser.setFont(font)
        self.prompt_text_browser.setUndoRedoEnabled(True)
        self.prompt_text_browser.setObjectName(_fromUtf8("prompt_text_browser"))
        self.gridLayout.addWidget(self.prompt_text_browser, 4, 0, 1, 5)
        self.goto_focus_area = QtGui.QPushButton(self.centralwidget)
        self.goto_focus_area.setObjectName(_fromUtf8("goto_focus_area"))
        self.gridLayout.addWidget(self.goto_focus_area, 1, 2, 1, 1)
        self.start_continue_recording = QtGui.QPushButton(self.centralwidget)
        self.start_continue_recording.setObjectName(_fromUtf8("start_continue_recording"))
        self.gridLayout.addWidget(self.start_continue_recording, 0, 3, 1, 1)
        self.set_tile_unprocessed = QtGui.QPushButton(self.centralwidget)
        self.set_tile_unprocessed.setObjectName(_fromUtf8("set_tile_unprocessed"))
        self.gridLayout.addWidget(self.set_tile_unprocessed, 2, 3, 1, 1)
        self.select_tile = QtGui.QPushButton(self.centralwidget)
        self.select_tile.setObjectName(_fromUtf8("select_tile"))
        self.gridLayout.addWidget(self.select_tile, 1, 3, 1, 1)
        self.set_all_tiles_unprocessed = QtGui.QPushButton(self.centralwidget)
        self.set_all_tiles_unprocessed.setObjectName(_fromUtf8("set_all_tiles_unprocessed"))
        self.gridLayout.addWidget(self.set_all_tiles_unprocessed, 3, 3, 1, 1)
        self.alignment = QtGui.QPushButton(self.centralwidget)
        self.alignment.setEnabled(True)
        self.alignment.setObjectName(_fromUtf8("alignment"))
        self.gridLayout.addWidget(self.alignment, 3, 0, 1, 1)
        self.new_landmark_selection = QtGui.QPushButton(self.centralwidget)
        self.new_landmark_selection.setObjectName(_fromUtf8("new_landmark_selection"))
        self.gridLayout.addWidget(self.new_landmark_selection, 2, 0, 1, 1)
        self.restart = QtGui.QPushButton(self.centralwidget)
        self.restart.setObjectName(_fromUtf8("restart"))
        self.gridLayout.addWidget(self.restart, 1, 0, 1, 1)
        self.edit_configuration = QtGui.QPushButton(self.centralwidget)
        self.edit_configuration.setObjectName(_fromUtf8("edit_configuration"))
        self.gridLayout.addWidget(self.edit_configuration, 0, 0, 1, 1)
        self.rotate_camera = QtGui.QPushButton(self.centralwidget)
        self.rotate_camera.setObjectName(_fromUtf8("rotate_camera"))
        self.gridLayout.addWidget(self.rotate_camera, 0, 1, 1, 1)
        self.set_focus_area = QtGui.QPushButton(self.centralwidget)
        font = QtGui.QFont()
        font.setPointSize(8)
        self.set_focus_area.setFont(font)
        self.set_focus_area.setObjectName(_fromUtf8("set_focus_area"))
        self.gridLayout.addWidget(self.set_focus_area, 1, 1, 1, 1)
        self.move_to_selected_tile = QtGui.QPushButton(self.centralwidget)
        self.move_to_selected_tile.setObjectName(_fromUtf8("move_to_selected_tile"))
        self.gridLayout.addWidget(self.move_to_selected_tile, 1, 4, 1, 1)
        self.set_all_tiles_processed = QtGui.QPushButton(self.centralwidget)
        self.set_all_tiles_processed.setObjectName(_fromUtf8("set_all_tiles_processed"))
        self.gridLayout.addWidget(self.set_all_tiles_processed, 3, 4, 1, 1)
        self.show_landmark = QtGui.QPushButton(self.centralwidget)
        font = QtGui.QFont()
        font.setPointSize(8)
        self.show_landmark.setFont(font)
        self.show_landmark.setObjectName(_fromUtf8("show_landmark"))
        self.gridLayout.addWidget(self.show_landmark, 2, 1, 1, 1)
        self.configure_drift_correction = QtGui.QPushButton(self.centralwidget)
        self.configure_drift_correction.setObjectName(_fromUtf8("configure_drift_correction"))
        self.gridLayout.addWidget(self.configure_drift_correction, 3, 2, 1, 1)
        self.autoalignment = QtGui.QPushButton(self.centralwidget)
        self.autoalignment.setObjectName(_fromUtf8("autoalignment"))
        self.gridLayout.addWidget(self.autoalignment, 3, 1, 1, 1)
        MainWindow.setCentralWidget(self.centralwidget)
        self.statusbar = QtGui.QStatusBar(MainWindow)
        self.statusbar.setObjectName(_fromUtf8("statusbar"))
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)
        MainWindow.setTabOrder(self.edit_configuration, self.restart)
        MainWindow.setTabOrder(self.restart, self.new_landmark_selection)
        MainWindow.setTabOrder(self.new_landmark_selection, self.alignment)
        MainWindow.setTabOrder(self.alignment, self.rotate_camera)
        MainWindow.setTabOrder(self.rotate_camera, self.set_focus_area)
        MainWindow.setTabOrder(self.set_focus_area, self.show_landmark)
        MainWindow.setTabOrder(self.show_landmark, self.autoalignment)
        MainWindow.setTabOrder(self.autoalignment, self.goto_focus_area)
        MainWindow.setTabOrder(self.goto_focus_area, self.configure_drift_correction)
        MainWindow.setTabOrder(self.configure_drift_correction, self.start_continue_recording)
        MainWindow.setTabOrder(self.start_continue_recording, self.select_tile)
        MainWindow.setTabOrder(self.select_tile, self.set_tile_unprocessed)
        MainWindow.setTabOrder(self.set_tile_unprocessed, self.set_all_tiles_unprocessed)
        MainWindow.setTabOrder(self.set_all_tiles_unprocessed, self.move_to_selected_tile)
        MainWindow.setTabOrder(self.move_to_selected_tile, self.set_all_tiles_processed)
        MainWindow.setTabOrder(self.set_all_tiles_processed, self.prompt_text_browser)

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(_translate("MainWindow", "MoonPanoramaMaker", None))
        self.prompt_text_browser.setToolTip(_translate("MainWindow", "Window to show user instructions", None))
        self.goto_focus_area.setToolTip(_translate("MainWindow", "Move the telescope for focus adjustment", None))
        self.goto_focus_area.setText(_translate("MainWindow", "GoTo Focus Area - G", None))
        self.goto_focus_area.setShortcut(_translate("MainWindow", "G", None))
        self.start_continue_recording.setToolTip(_translate("MainWindow", "Continue recording with next unprocessed tile", None))
        self.start_continue_recording.setText(_translate("MainWindow", "Start / Continue Recording - S", None))
        self.start_continue_recording.setShortcut(_translate("MainWindow", "S", None))
        self.set_tile_unprocessed.setToolTip(_translate("MainWindow", "Remove current tile number from list of processed tiles", None))
        self.set_tile_unprocessed.setText(_translate("MainWindow", "Set Tile(s) Unprocessed - U", None))
        self.set_tile_unprocessed.setShortcut(_translate("MainWindow", "U", None))
        self.select_tile.setToolTip(_translate("MainWindow", "Select tile number for next recording", None))
        self.select_tile.setText(_translate("MainWindow", "Select Tile - T", None))
        self.select_tile.setShortcut(_translate("MainWindow", "T", None))
        self.set_all_tiles_unprocessed.setToolTip(_translate("MainWindow", "Mark all tiles as unprocessed", None))
        self.set_all_tiles_unprocessed.setText(_translate("MainWindow", "Set All Tiles Unprocessed - V", None))
        self.set_all_tiles_unprocessed.setShortcut(_translate("MainWindow", "V", None))
        self.alignment.setToolTip(_translate("MainWindow", "Align (or re-align) telescope with landmark", None))
        self.alignment.setText(_translate("MainWindow", "Alignment - A", None))
        self.alignment.setShortcut(_translate("MainWindow", "A", None))
        self.new_landmark_selection.setToolTip(_translate("MainWindow", "Select new landmark for alignment in planetarium program", None))
        self.new_landmark_selection.setText(_translate("MainWindow", "New Landmark Selection - L", None))
        self.new_landmark_selection.setShortcut(_translate("MainWindow", "L", None))
        self.restart.setToolTip(_translate("MainWindow", "Restart from scratch (new tile layout)", None))
        self.restart.setText(_translate("MainWindow", "Restart - R", None))
        self.restart.setShortcut(_translate("MainWindow", "R", None))
        self.edit_configuration.setToolTip(_translate("MainWindow", "Input configuration parameters for location, camera, telescope and window layout", None))
        self.edit_configuration.setText(_translate("MainWindow", "Edit Configuration - C", None))
        self.edit_configuration.setShortcut(_translate("MainWindow", "C", None))
        self.rotate_camera.setToolTip(_translate("MainWindow", "Align short side of sensor with Moon limb", None))
        self.rotate_camera.setText(_translate("MainWindow", "Camera Orientation - O", None))
        self.rotate_camera.setShortcut(_translate("MainWindow", "O", None))
        self.set_focus_area.setToolTip(_translate("MainWindow", "Mark current view as the place where the telescope focus is to be set", None))
        self.set_focus_area.setText(_translate("MainWindow", "Select Focus Area - F", None))
        self.set_focus_area.setShortcut(_translate("MainWindow", "F", None))
        self.move_to_selected_tile.setToolTip(_translate("MainWindow", "Move the telescope to the selected tile", None))
        self.move_to_selected_tile.setText(_translate("MainWindow", "Move to Selected Tile - M", None))
        self.move_to_selected_tile.setShortcut(_translate("MainWindow", "M", None))
        self.set_all_tiles_processed.setToolTip(_translate("MainWindow", "Mark all tiles as processed", None))
        self.set_all_tiles_processed.setText(_translate("MainWindow", "Set All Tiles Processed - P", None))
        self.set_all_tiles_processed.setShortcut(_translate("MainWindow", "P", None))
        self.show_landmark.setToolTip(_translate("MainWindow", "Show a picture of the landmark currently selected ", None))
        self.show_landmark.setText(_translate("MainWindow", "Show Landmark - K", None))
        self.show_landmark.setShortcut(_translate("MainWindow", "K", None))
        self.configure_drift_correction.setToolTip(_translate("MainWindow", "Select alignment points for drift computation and compensation", None))
        self.configure_drift_correction.setText(_translate("MainWindow", "Correct for Drift - D", None))
        self.configure_drift_correction.setShortcut(_translate("MainWindow", "D", None))
        self.autoalignment.setToolTip(_translate("MainWindow", "Switch on / off auto-alignment", None))
        self.autoalignment.setText(_translate("MainWindow", "Auto-Alignment on - B", None))
        self.autoalignment.setShortcut(_translate("MainWindow", "B", None))

