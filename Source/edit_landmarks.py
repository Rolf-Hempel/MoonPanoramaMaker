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

import os
from math import radians, pi

from PyQt4 import QtGui

from ViewLandmarks import Ui_ViewLandmarks


class EditLandmarks(QtGui.QDialog, Ui_ViewLandmarks):
    def __init__(self, selected_landmark, landmarks, colong, parent=None):
        QtGui.QDialog.__init__(self, parent)
        self.selected_landmark = selected_landmark
        self.picture_dir = os.getcwd() + '\\landmark_pictures\\'
        # print self.picture_dir
        self.setupUi(self)
        self.landmarks = landmarks
        if pi / 2. <= colong <= 3. * pi / 2.:
            self.lower_longitude_limit = -pi / 2.
            self.upper_longitude_limit = -colong + pi
        elif 3. * pi / 2. < colong <= 2. * pi:
            self.lower_longitude_limit = 2. * pi - colong
            self.upper_longitude_limit = pi / 2.
        else:
            self.lower_longitude_limit = -colong
            self.upper_longitude_limit = pi / 2.
        self.filenames = self.combobox()
        if self.selected_landmark != "":
            self.comboBox.setCurrentIndex(
                self.filenames.index(self.selected_landmark))
        else:
            self.comboBox.setCurrentIndex(0)
        self.refresh()
        self.buttonBox.accepted.connect(self.ok)
        self.buttonBox.rejected.connect(self.cancel)
        self.comboBox.currentIndexChanged.connect(self.refresh)

    def combobox(self):
        filenames = []
        for file in os.listdir(self.picture_dir):
            filename = os.path.splitext(file)[0]
            # if os.path.splitext(file)[1] == ".png":
            #     print "landmark: ", filename, ", longitude: ",\
            #         self.landmarks[filename][0], ", lower limit: ",\
            #         degrees(self.lower_longitude_limit), ", upper limit: ",\
            #         degrees(self.upper_longitude_limit)
            if os.path.splitext(file)[1] == ".png" and \
                                    self.lower_longitude_limit <= radians(
                                self.landmarks[filename][
                                    0]) <= self.upper_longitude_limit or \
                            filename == 'Moon Center':
                filenames.append(filename)

        self.comboBox.clear()
        self.comboBox.addItems(filenames)
        return filenames

    def refresh(self):
        self.combobox_filename = str(self.comboBox.currentText())
        pixmap = QtGui.QPixmap(
            self.picture_dir + self.combobox_filename + '.png')
        self.label.setPixmap(pixmap)

    def ok(self):
        self.selected_landmark = self.combobox_filename
        self.close()

    def cancel(self):
        self.close()

# if __name__ == '__main__':
#     app = QtGui.QApplication(sys.argv)
#     myapp = EditLandmarks()
#     myapp.exec_()
#     print myapp.landmark_chosen
