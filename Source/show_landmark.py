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

from PyQt5 import QtGui, QtWidgets

from DisplayLandmark import Ui_DisplayLandmark


class ShowLandmark(QtWidgets.QDialog, Ui_DisplayLandmark):
    """
    This class implements the gui which presents the user the currently selected landmark. It is
    invoked by pressing the "Show Landmark - K" button.
    
    """

    def __init__(self, ls, parent=None):
        """
        
        :param ls: The LandmarkSelection object (from module landmark_selection)
        """

        QtWidgets.QDialog.__init__(self, parent)
        # Get the name of the currently selected landmark from the LandmarkSelection object.
        landmark = ls.selected_landmark
        # The landmark pictures are stored in subdirectory "landmark_pictures".
        dirname, filename = os.path.split(os.path.abspath(__file__))
        self.picture_dir = os.path.join(dirname, 'landmark_pictures', '')
        self.setupUi(self)
        # Write the name of the landmark under the picture in the gui.
        self.landmark_name.setText("Landmark selected: " + landmark)
        # Load an image of the landmark to be displayed by the gui.
        pixmap = QtGui.QPixmap(self.picture_dir + landmark + '.png')
        self.landmark_picture.setPixmap(pixmap)
        self.buttonBox.accepted.connect(self.ok)

    def ok(self):
        """
        Acknowledgement by the user, close the gui.
        
        :return: -
        """

        self.close()
