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

from PyQt4 import QtGui

from DisplayLandmark import Ui_DisplayLandmark


class ShowLandmark(QtGui.QDialog, Ui_DisplayLandmark):
    def __init__(self, ls, parent=None):
        QtGui.QDialog.__init__(self, parent)
        self.landmark = ls.selected_landmark
        self.picture_dir = os.getcwd() + '\\landmark_pictures\\'
        self.setupUi(self)
        self.landmark_name.setText("Landmark selected: " + self.landmark)
        pixmap = QtGui.QPixmap(
            self.picture_dir + self.landmark + '.png')
        self.landmark_picture.setPixmap(pixmap)
        self.buttonBox.accepted.connect(self.ok)

    def ok(self):
        self.close()
