# -*- coding: utf-8; -*-
"""
Copyright (c) 2016 Rolf Hempel, rolf6419@gmx.de

This file is part of the MoonPanoramaMaker tool (MPM).
https://github.com/Rolf-Hempel/MoonPanoramaMaker

MPM is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with MPM.  If not, see <http://www.gnu.org/licenses/>.

"""

from math import degrees

from PyQt4 import QtCore, QtGui

from drift_rate_dialog import Ui_DriftRateDialog


class ComputeDriftRate(QtGui.QDialog, Ui_DriftRateDialog):
    def __init__(self, configuration, al, parent=None):
        self.configuration = configuration
        self.al = al
        QtGui.QDialog.__init__(self, parent)
        self.ui = Ui_DriftRateDialog()
        self.ui.setupUi(self)

        self.ui.tableWidget.setRowCount(len(al.alignment_points))
        flags = QtCore.Qt.ItemFlags()
        flags != QtCore.Qt.ItemIsEnabled
        first_alignment_seconds = al.alignment_points[0]['time_seconds']
        self.time_offsets = []
        self.ra_corrections = []
        self.de_corrections = []
        for i in range(len(al.alignment_points)):
            self.time_offsets.append((al.alignment_points[i][
                                          'time_seconds'] - first_alignment_seconds) / 60.)
            time_string = al.alignment_points[i]['time_string']
            item = QtGui.QTableWidgetItem(time_string)
            item.setTextAlignment(QtCore.Qt.AlignCenter)
            item.setFlags(flags)
            self.ui.tableWidget.setItem(i, 0, item)
            ra_correction = 60. * degrees(
                al.alignment_points[i]['ra_correction'])
            self.ra_corrections.append(ra_correction)
            ra_correction_string = "{:10.2f}".format(ra_correction)
            item = QtGui.QTableWidgetItem(ra_correction_string)
            item.setTextAlignment(QtCore.Qt.AlignCenter)
            item.setFlags(flags)
            self.ui.tableWidget.setItem(i, 1, item)
            de_correction = 60. * degrees(
                al.alignment_points[i]['de_correction'])
            self.de_corrections.append(de_correction)
            de_correction_string = "{:10.2f}".format(de_correction)
            item = QtGui.QTableWidgetItem(de_correction_string)
            item.setTextAlignment(QtCore.Qt.AlignCenter)
            item.setFlags(flags)
            self.ui.tableWidget.setItem(i, 2, item)

        self.ui.mplwidget.plotDataPoints(self.time_offsets,
                                         self.ra_corrections,
                                         self.de_corrections,
                                         self.al.first_index,
                                         self.al.last_index)

        if self.al.drift_disabled:
            self.ui.noRadioButton.setChecked(True)
        if self.al.default_first_drift:
            self.ui.defaultFirstRadioButton.setChecked(True)
        if self.al.default_last_drift:
            self.ui.defaultLastRadioButton.setChecked(True)

        self.ui.spinBoxFirstIndex.setMinimum(1)
        self.ui.spinBoxFirstIndex.setMaximum(len(al.alignment_points) - 1)
        self.ui.spinBoxFirstIndex.setValue(al.first_index + 1)
        self.ui.spinBoxLastIndex.setMinimum(2)
        self.ui.spinBoxLastIndex.setMaximum(len(al.alignment_points))
        # self.ui.spinBoxLastIndex.setValue(len(al.alignment_points))
        self.ui.spinBoxLastIndex.setValue(al.last_index + 1)

        self.ui.buttonBox.accepted.connect(self.compute_drift)
        self.ui.spinBoxFirstIndex.editingFinished.connect(
            self.set_limit_spinBoxLastIndex)
        self.ui.spinBoxFirstIndex.valueChanged.connect(
            self.first_index_changed)
        self.ui.spinBoxLastIndex.editingFinished.connect(
            self.set_limit_spinBoxFirstIndex)
        self.ui.spinBoxLastIndex.valueChanged.connect(self.last_index_changed)
        self.ui.defaultFirstRadioButton.toggled.connect(
            self.toggle_default_first_radio_button)
        self.ui.defaultLastRadioButton.toggled.connect(
            self.toggle_default_last_radio_button)
        self.ui.noRadioButton.toggled.connect(self.toggle_no_radio_button)

    def toggle_default_first_radio_button(self):
        if self.configuration.protocol:
            print "toggle default button for first drift index"
        self.al.default_first_drift = not self.al.default_first_drift

    def toggle_default_last_radio_button(self):
        if self.configuration.protocol:
            print "toggle default button for last drift index"
        self.al.default_last_drift = not self.al.default_last_drift

    def toggle_no_radio_button(self):
        if self.configuration.protocol:
            print "toggle no button"
        self.al.drift_disabled = not self.al.drift_disabled
        if not self.al.drift_disabled:
            if self.configuration.protocol:
                print "drift enabled"
            if self.al.default_first_drift:
                if self.configuration.protocol:
                    print "default first drift index"
                self.ui.labelFirstIndex.setDisabled(True)
                self.ui.spinBoxFirstIndex.setDisabled(True)
            if self.al.default_last_drift:
                if self.configuration.protocol:
                    print "default first drift index"
                self.ui.spinBoxLastIndex.setDisabled(True)
                self.ui.labelLastIndex.setDisabled(True)

    def first_index_changed(self):
        ax = self.ui.mplwidget.plotrect
        for line in ax.lines:
            if line.get_label() == 'drift':
                ax.lines.remove(line)
        ax = self.ui.mplwidget.plotdecl
        for line in ax.lines:
            if line.get_label() == 'drift':
                ax.lines.remove(line)
        self.ui.mplwidget.plotDataPoints(self.time_offsets,
                                         self.ra_corrections,
                                         self.de_corrections, int(
                self.ui.spinBoxFirstIndex.text()) - 1, int(
                self.ui.spinBoxLastIndex.text()) - 1)

    def last_index_changed(self):
        ax = self.ui.mplwidget.plotrect
        for line in ax.lines:
            if line.get_label() == 'drift':
                ax.lines.remove(line)
        ax = self.ui.mplwidget.plotdecl
        for line in ax.lines:
            if line.get_label() == 'drift':
                ax.lines.remove(line)
        self.ui.mplwidget.plotDataPoints(self.time_offsets,
                                         self.ra_corrections,
                                         self.de_corrections, int(
                self.ui.spinBoxFirstIndex.text()) - 1, int(
                self.ui.spinBoxLastIndex.text()) - 1)

    def set_limit_spinBoxLastIndex(self):
        self.ui.spinBoxLastIndex.setMinimum(
            1 + int(self.ui.spinBoxFirstIndex.text()))

    def set_limit_spinBoxFirstIndex(self):
        self.ui.spinBoxFirstIndex.setMaximum(
            int(self.ui.spinBoxLastIndex.text()) - 1)

    def compute_drift(self):
        if self.configuration.protocol:
            print "Enter compute_drift"
        if self.al.drift_disabled:
            if self.configuration.protocol:
                print "noRadioButton is toggled"
            self.al.is_drift_set = False
            self.close()
            return
        if self.al.default_first_drift:
            self.al.first_index = 0
        else:
            self.al.first_index = int(self.ui.spinBoxFirstIndex.text()) - 1
        if self.al.default_last_drift:
            self.al.last_index = len(self.al.alignment_points) - 1
        else:
            self.al.last_index = int(self.ui.spinBoxLastIndex.text()) - 1
        if (self.al.alignment_points[self.al.last_index]['time_seconds'] -
                self.al.alignment_points[self.al.first_index][
                    'time_seconds']) > self.configuration.minimum_drift_seconds:
            if self.configuration.protocol:
                print "Start drift computation, first/last index: ", \
                    self.al.first_index, ", ", self.al.last_index
            self.al.compute_drift_rate()
        elif self.configuration.protocol:
            print "Time interval too short for drift computation"
        self.close()

    def keyPressEvent(self, event):
        if type(event) == QtGui.QKeyEvent:
            if event.key() == 16777220:  # Enter key
                self.compute_drift()
            if event.key() == QtCore.Qt.Key_Escape:
                self.close()
            if event.key() == QtCore.Qt.Key_A:
                # if self.configuration.protocol:
                #     print "A pressed"
                self.ui.spinBoxFirstIndex.setFocus()
            if event.key() == QtCore.Qt.Key_B:
                # if self.configuration.protocol:
                #     print "B pressed"
                self.ui.spinBoxLastIndex.setFocus()

# import sys
# from datetime import datetime
# from time import mktime
# from math import radians
# from configuration import Configuration
#
#
# class alignment():
#     def __init__(self):
#         self.alignment_points = []
#         self.is_drift_set = False
#         self.default_first_drift = True
#         self.default_last_drift = True
#         self.drift_disabled = False
#         self.first_index = 0
#         self.last_index = 4
#         self.minimum_drift_seconds = 30
#
#         al = {}
#         time1 = datetime(2015, 9, 1, 16, 53, 22)
#         al['time_string'] = str(time1)[11:19]
#         al['time_seconds'] = mktime(time1.timetuple())
#         al['ra_correction'] = radians(40. / 60.)
#         al['de_correction'] = radians(-20. / 60)
#         self.alignment_points.append(al)
#
#         al = {}
#         time1 = datetime(2015, 9, 1, 17, 03, 22)
#         al['time_string'] = str(time1)[11:19]
#         al['time_seconds'] = mktime(time1.timetuple())
#         al['ra_correction'] = radians(50. / 60)
#         al['de_correction'] = radians(-15. / 60)
#         self.alignment_points.append(al)
#
#         al = {}
#         time1 = datetime(2015, 9, 1, 17, 13, 22)
#         al['time_string'] = str(time1)[11:19]
#         al['time_seconds'] = mktime(time1.timetuple())
#         al['ra_correction'] = radians(62. / 60)
#         al['de_correction'] = radians(-9. / 60)
#         self.alignment_points.append(al)
#
#         al = {}
#         time1 = datetime(2015, 9, 1, 17, 23, 22)
#         al['time_string'] = str(time1)[11:19]
#         al['time_seconds'] = mktime(time1.timetuple())
#         al['ra_correction'] = radians(73. / 60)
#         al['de_correction'] = radians(-2. / 60)
#         self.alignment_points.append(al)
#
#         al = {}
#         time1 = datetime(2015, 9, 1, 17, 24, 22)
#         al['time_string'] = str(time1)[11:19]
#         al['time_seconds'] = mktime(time1.timetuple())
#         al['ra_correction'] = radians(74. / 60)
#         al['de_correction'] = radians(-1. / 60)
#         self.alignment_points.append(al)
#
#     def compute_drift_rate(self):
#         time_diff = (self.alignment_points[self.last_index]['time_seconds'] -
#                      self.alignment_points[self.first_index]['time_seconds'])
#         if time_diff < 120.:
#             return
#         drift_ra = ((self.alignment_points[self.last_index]['ra_correction'] -
#                      self.alignment_points[self.first_index][
#                          'ra_correction']) /
#                     time_diff)
#         drift_de = ((self.alignment_points[self.last_index]['de_correction'] -
#                      self.alignment_points[self.first_index][
#                          'de_correction']) /
#                     time_diff)
#         print "Drift in Ra: ", degrees(drift_ra) * 216000.
#         print "Drift in De: ", degrees(drift_de) * 216000.
#         self.is_drift_set = True
#
#
# if __name__ == "__main__":
#     c = Configuration()
#     al = alignment()
#
#     app = QtGui.QApplication(sys.argv)
#     myapp = ComputeDriftRate(c, al)
#     myapp.show()
#     sys.exit(app.exec_())
