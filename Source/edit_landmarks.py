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

from PyQt5 import QtGui, QtWidgets

from ViewLandmarks import Ui_ViewLandmarks


class EditLandmarks(QtWidgets.QDialog, Ui_ViewLandmarks):
    """
    This class implements the landmark selection by the user. A gui is presented with a list
    of available landmarks. If the user selects a landmark from the combobox, the corresponding
    picture of the landmark is displayed. The user acknowledges the landmark selection with pressing
    the OK button.
    
    """

    def __init__(self, selected_landmark, landmarks, colong, parent=None):
        """
        
        :param selected_landmark: start value for the selected landmark name (string)
        :param landmarks: dictionary with landmark names and selenographic coordinates
        :param colong: current selenographic co-longitude of the sun
        """

        QtWidgets.QDialog.__init__(self, parent)
        self.selected_landmark = selected_landmark
        # For each landmark a picture is stored in subdirectory "landmark_pictures".
        self.picture_dir = os.path.join(os.getcwd(), 'landmark_pictures', '')
        self.setupUi(self)
        self.landmarks = landmarks
        # Compute the range of selenographic longitudes of the sunlit part of the moon. A
        # landmark must be in this range to be visible.
        if pi / 2. <= colong <= 3. * pi / 2.:
            self.lower_longitude_limit = -pi / 2.
            self.upper_longitude_limit = -colong + pi
        elif 3. * pi / 2. < colong <= 2. * pi:
            self.lower_longitude_limit = 2. * pi - colong
            self.upper_longitude_limit = pi / 2.
        else:
            self.lower_longitude_limit = -colong
            self.upper_longitude_limit = pi / 2.
        # Set up the list of sunlit landmarks and add them to the comboBox of the gui.
        self.filenames = self.combobox()
        # If a landmark is selected, set the current comboBox index to this landmark, otherwise to 0.
        if self.selected_landmark != "":
            self.comboBox.setCurrentIndex(self.filenames.index(self.selected_landmark))
        else:
            self.comboBox.setCurrentIndex(0)
        self.refresh()
        # The user has selected the landmark, keep its name.
        self.OKButton.clicked.connect(self.ok)
        self.comboBox.currentIndexChanged.connect(self.refresh)

    def combobox(self):
        """
        Populate the comboBox with the sunlit landmarks.
        
        :return: list with names of sunlit landmarks.
        """

        filenames = []
        # For each landmark there is a picture in subdirectory "picture_dir".
        for file in os.listdir(self.picture_dir):
            filename = os.path.splitext(file)[0]
            # Find out if the landmark is within the sunlit range of longitudes. File "Moon Center"
            # is always selected (to avoid that the list can be empty).
            if os.path.splitext(file)[1] == ".png" and self.lower_longitude_limit <= radians(
                    self.landmarks[filename][
                        0]) <= self.upper_longitude_limit or filename == 'Moon Center':
                filenames.append(filename)

        # Fill the comboBox with the list of file names.
        self.comboBox.clear()
        self.comboBox.addItems(filenames)
        return filenames

    def refresh(self):
        """
        When the comboBox index changes, get the picture of the selected landmark and display it.
        
        :return: -
        """

        self.combobox_filename = str(self.comboBox.currentText())
        pixmap = QtGui.QPixmap(self.picture_dir + self.combobox_filename + '.png')
        self.label.setPixmap(pixmap)

    def ok(self):
        """
        Store the name of the landmark eventually selected and close the gui.
        
        :return: -
        """
        self.selected_landmark = self.combobox_filename
        self.close()
