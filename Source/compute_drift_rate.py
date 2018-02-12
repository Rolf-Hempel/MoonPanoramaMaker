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
from miscellaneous import Miscellaneous


class ComputeDriftRate(QtGui.QDialog, Ui_DriftRateDialog):
    """
    This class implements the logic behind the drift_rate_dialog gui which controls how the mount
    drift rate is to be determined. In particular, the rules for selecting the first and last
    alignment points to be used for drift rate computation are set.

    """

    def __init__(self, configuration, al, parent=None):
        """
        Initialize drift computation and produce a table and plots for showing the available
        alignment points for drift computation.

        :param configuration: object containing parameters set by the user
        :param al: alignment object (instance of class Alignment)
        """
        self.configuration = configuration
        self.al = al
        # Open the gui window.
        QtGui.QDialog.__init__(self, parent)
        self.ui = Ui_DriftRateDialog()
        self.ui.setupUi(self)

        # Create a table with alignment point info
        self.ui.tableWidget.setRowCount(len(al.alignment_points))
        flags = QtCore.Qt.ItemFlags()
        flags != QtCore.Qt.ItemIsEnabled
        # Take the time of the first alignment point as start point for time computations.
        first_alignment_seconds = al.alignment_points[0]['time_seconds']
        # Initialize lists for time (since first alignment) and corrections in RA and DE.
        self.time_offsets = []
        self.ra_corrections = []
        self.de_corrections = []
        # For each alignment point: Add the data to the three above lists.
        for i in range(len(al.alignment_points)):
            # For the 2D plot (below), time is counted in minutes.
            self.time_offsets.append(
                (al.alignment_points[i]['time_seconds'] - first_alignment_seconds) / 60.)
            # Look up the time string to be displayed in the table.
            time_string = al.alignment_points[i]['time_string']
            item = QtGui.QTableWidgetItem(time_string)
            item.setTextAlignment(QtCore.Qt.AlignCenter)
            item.setFlags(flags)
            # Put time info into the first table column.
            self.ui.tableWidget.setItem(i, 0, item)
            # The alignment corrections in RA and DE are counted in arc minutes.
            ra_correction = 60. * degrees(al.alignment_points[i]['ra_correction'])
            self.ra_corrections.append(ra_correction)
            ra_correction_string = "{:10.2f}".format(ra_correction)
            item = QtGui.QTableWidgetItem(ra_correction_string)
            item.setTextAlignment(QtCore.Qt.AlignCenter)
            item.setFlags(flags)
            # Put the RA correction into the second table column.
            self.ui.tableWidget.setItem(i, 1, item)
            de_correction = 60. * degrees(al.alignment_points[i]['de_correction'])
            self.de_corrections.append(de_correction)
            de_correction_string = "{:10.2f}".format(de_correction)
            item = QtGui.QTableWidgetItem(de_correction_string)
            item.setTextAlignment(QtCore.Qt.AlignCenter)
            item.setFlags(flags)
            # Put the DE correction into the third table column.
            self.ui.tableWidget.setItem(i, 2, item)

        # Plot the table data as two Matplotlib graphs.
        self.ui.mplwidget.plotDataPoints(self.time_offsets, self.ra_corrections,
                                         self.de_corrections, self.al.first_index,
                                         self.al.last_index)

        # Initialize radio buttons. Between calls to the drift rate dialog, info regarding whether
        # or not drift computation is enabled, and if the user wants to use default values for
        # the first and last alignment point to be used for drift computations, is held in the
        # alignment object (al).
        if self.al.drift_disabled:
            self.ui.noRadioButton.setChecked(True)
        if self.al.default_first_drift:
            self.ui.defaultFirstRadioButton.setChecked(True)
        if self.al.default_last_drift:
            self.ui.defaultLastRadioButton.setChecked(True)

        # Create spin boxes for the selection of the first and last alignment point for drift
        # computation.
        self.ui.spinBoxFirstIndex.setMinimum(1)
        self.ui.spinBoxFirstIndex.setMaximum(len(al.alignment_points) - 1)
        self.ui.spinBoxFirstIndex.setValue(al.first_index + 1)
        self.ui.spinBoxLastIndex.setMinimum(2)
        self.ui.spinBoxLastIndex.setMaximum(len(al.alignment_points))
        self.ui.spinBoxLastIndex.setValue(al.last_index + 1)

        # If the OK button is pressed, start the drift computation.
        self.ui.buttonBox.accepted.connect(self.compute_drift)
        # Connect events in the gui with methods to store the entered data.
        self.ui.spinBoxFirstIndex.editingFinished.connect(self.set_limit_spinBoxLastIndex)
        self.ui.spinBoxFirstIndex.valueChanged.connect(self.first_index_changed)
        self.ui.spinBoxLastIndex.editingFinished.connect(self.set_limit_spinBoxFirstIndex)
        self.ui.spinBoxLastIndex.valueChanged.connect(self.last_index_changed)
        self.ui.defaultFirstRadioButton.toggled.connect(self.toggle_default_first_radio_button)
        self.ui.defaultLastRadioButton.toggled.connect(self.toggle_default_last_radio_button)
        self.ui.noRadioButton.toggled.connect(self.toggle_no_radio_button)

    def toggle_default_first_radio_button(self):
        """
        For the first alignment point, toggle on/off the default choice (first available data point)

        :return: -
        """

        if self.configuration.protocol_level > 2:
            Miscellaneous.protocol("Drift computation: Toggle default button for first drift index")
        self.al.default_first_drift = not self.al.default_first_drift
        if self.ui.defaultFirstRadioButton.isChecked():
            self.ui.spinBoxFirstIndex.setValue(1)
            self.al.first_index = 0
            self.first_index_changed()

    def toggle_default_last_radio_button(self):
        """
        For the last alignment point, toggle on/off the default choice (last available data point)

        :return: -
        """

        if self.configuration.protocol_level > 2:
            Miscellaneous.protocol("Drift computation: Toggle default button for last drift index")
        self.al.default_last_drift = not self.al.default_last_drift
        if self.ui.defaultLastRadioButton.isChecked():
            self.al.last_index = len(self.al.alignment_points) - 1
            self.ui.spinBoxLastIndex.setValue(self.al.last_index + 1)
            self.last_index_changed()

    def toggle_no_radio_button(self):
        """
        Toggle on/off if drift correction should be included in computing telescope coordinates

        :return: -
        """

        if self.configuration.protocol_level > 2:
            Miscellaneous.protocol("Drift computation: Toggle no button")
        self.al.drift_disabled = not self.al.drift_disabled

        # Drift computation is enabled.
        if not self.al.drift_disabled:
            if self.configuration.protocol_level > 2:
                Miscellaneous.protocol("Drift computation: Drift enabled")
            # Check if for the first alignment point the default is selected.
            if self.al.default_first_drift:
                if self.configuration.protocol_level > 2:
                    Miscellaneous.protocol("Drift computation: Default first drift index")
                # In this case disable the gui elements for alignment point number selection.
                self.ui.labelFirstIndex.setDisabled(True)
                self.ui.spinBoxFirstIndex.setDisabled(True)
            # Same as above for the end of the drift computation interval.
            if self.al.default_last_drift:
                if self.configuration.protocol_level > 2:
                    Miscellaneous.protocol("Drift computation: Default first drift index")
                self.ui.spinBoxLastIndex.setDisabled(True)
                self.ui.labelLastIndex.setDisabled(True)

    def first_index_changed(self):
        """
        In the Matplotlib plots of RA and DE drift, the first and last alignment points are
        connected with a red line. Repeat plotting these lines when the first point changes
        because the user chooses another point index.

        :return: -
        """

        ax = self.ui.mplwidget.plotrect
        for line in ax.lines:
            if line.get_label() == 'drift':
                ax.lines.remove(line)
        ax = self.ui.mplwidget.plotdecl
        for line in ax.lines:
            if line.get_label() == 'drift':
                ax.lines.remove(line)
        self.ui.mplwidget.plotDataPoints(self.time_offsets, self.ra_corrections,
                                         self.de_corrections,
                                         int(self.ui.spinBoxFirstIndex.text()) - 1,
                                         int(self.ui.spinBoxLastIndex.text()) - 1)

    def last_index_changed(self):
        """
        Same as above if the end point of the drift computation interval changes.

        :return: -
        """

        ax = self.ui.mplwidget.plotrect
        for line in ax.lines:
            if line.get_label() == 'drift':
                ax.lines.remove(line)
        ax = self.ui.mplwidget.plotdecl
        for line in ax.lines:
            if line.get_label() == 'drift':
                ax.lines.remove(line)
        self.ui.mplwidget.plotDataPoints(self.time_offsets, self.ra_corrections,
                                         self.de_corrections,
                                         int(self.ui.spinBoxFirstIndex.text()) - 1,
                                         int(self.ui.spinBoxLastIndex.text()) - 1)

    def set_limit_spinBoxLastIndex(self):
        """
        In case the user chooses an alignment point with index>0 for the beginning of drift
        computation, make sure that the spin box for selecting the end point starts with the
        next higher index.

        :return: -
        """

        self.ui.spinBoxLastIndex.setMinimum(1 + int(self.ui.spinBoxFirstIndex.text()))

    def set_limit_spinBoxFirstIndex(self):
        """
        The corresponding reduction of range for the selection of the first alignment point index
        in case the user has not chosen the last available index for the end of the drift
        computation interval.

        :return: -
        """

        self.ui.spinBoxFirstIndex.setMaximum(int(self.ui.spinBoxLastIndex.text()) - 1)

    def compute_drift(self):
        """
        Compute new values for telescope drift in RA and DE

        :return: -
        """

        # If drift correction is disabled, set the flag in the alignment object (al) and close.
        if self.al.drift_disabled:
            if self.configuration.protocol_level > 0:
                Miscellaneous.protocol("Drift computation is disabled: No correction for drift.")
            self.al.is_drift_set = False
            self.close()
            return
        # The default for the first alignment point is the first available point (index 0).
        if self.al.default_first_drift:
            self.al.first_index = 0
        else:
            # If default is de-selected: Get the value from spin box.
            self.al.first_index = int(self.ui.spinBoxFirstIndex.text()) - 1
        # Same for end point of drift interval.
        if self.al.default_last_drift:
            self.al.last_index = len(self.al.alignment_points) - 1
        else:
            self.al.last_index = int(self.ui.spinBoxLastIndex.text()) - 1

        # Drift rates are computed only if the chosen alignment points span a large enough time
        # interval. Otherwise the results would not be reliable enough.
        if (self.al.alignment_points[self.al.last_index]['time_seconds'] -
                self.al.alignment_points[self.al.first_index][
                    'time_seconds']) > self.configuration.minimum_drift_seconds:
            if self.configuration.protocol_level > 2:
                Miscellaneous.protocol("Start drift computation, first/last index: " +
                                       str(self.al.first_index) + ", " + str(self.al.last_index))
            # The actual logic for drift rate computation is in method compute_drift_rate in class
            # Alignment.
            self.al.compute_drift_rate()
        elif self.configuration.protocol_level > 1:
            Miscellaneous.protocol("Time between alignments too short for drift computation.")

        # Close the gui.
        self.close()

    def keyPressEvent(self, event):
        """
        The gui should be usable without a mouse. Therefore, keystrokes (A and B) are used to
        change the focus, to accept the input and start the computation (Enter), or to leave the
        dialog (Esc).
        :param event: keyPressEvent sent from the user interface.
        :return: -
        """

        if type(event) == QtGui.QKeyEvent:
            if event.key() == 16777220:  # Enter key
                self.compute_drift()
            if event.key() == QtCore.Qt.Key_Escape:
                self.close()
            if event.key() == QtCore.Qt.Key_A:
                self.ui.spinBoxFirstIndex.setFocus()
            if event.key() == QtCore.Qt.Key_B:
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
