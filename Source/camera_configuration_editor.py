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

from PyQt5 import QtWidgets

from camera_dialog import Ui_CameraDialog
from miscellaneous import Miscellaneous


class CameraConfigurationEditor(QtWidgets.QDialog, Ui_CameraDialog):
    """
    Update the info stored for a specific camera model in the configuration object. The
    interaction with the user is through the camera_dialog.ui gui.
    
    """

    def __init__(self, configuration, camera_name, parent=None):
        """
        Read the current camera information from the configuration object and populate the text
        fields of the editor gui.
        
        :param configuration: object containing parameters set by the user
        :param camera_name: String with the name of the camera
        """
        QtWidgets.QDialog.__init__(self, parent)
        self.setupUi(self)
        self.c = configuration
        self.section_name = 'Camera ' + camera_name

        # Read the current camera parameters from the configuration object
        self.new_name = self.c.conf.get(self.section_name, 'name')
        self.new_pixel_size = self.c.conf.get(self.section_name, 'pixel size')
        self.new_pixel_horizontal = self.c.conf.get(self.section_name, 'pixel horizontal')
        self.new_pixel_vertical = self.c.conf.get(self.section_name, 'pixel vertical')
        self.new_repetition_count = self.c.conf.get(self.section_name, 'repetition count')
        self.new_external_margin_pixel = self.c.conf.get(self.section_name, 'external margin pixel')
        self.new_tile_overlap_pixel = self.c.conf.get(self.section_name, 'tile overlap pixel')

        # Fill the gui text fields with the current parameters
        self.input_camera_name.setText(self.new_name)
        self.input_camera_name.setReadOnly(True)
        self.input_pixel_size.setText(self.new_pixel_size)
        self.input_pixel_horizontal.setText(self.new_pixel_horizontal)
        self.input_pixel_vertical.setText(self.new_pixel_vertical)
        self.input_repetition_count.setText(self.new_repetition_count)
        self.input_external_margin.setText(self.new_external_margin_pixel)
        self.input_tile_overlap.setText(self.new_tile_overlap_pixel)

        # The configuration_changed flag indicates if at least one parameter has been changed by
        # the user. Initialize to False.
        self.configuration_changed = False

        # Connect changes to the gui text fields with the methods below.
        self.input_pixel_size.textChanged.connect(self.pixel_size_write)
        self.input_pixel_horizontal.textChanged.connect(self.pixel_horizontal_write)
        self.input_pixel_vertical.textChanged.connect(self.pixel_vertical_write)
        self.input_repetition_count.textChanged.connect(self.repetition_count_write)
        self.input_external_margin.textChanged.connect(self.external_margin_write)
        self.input_tile_overlap.textChanged.connect(self.tile_overlap_write)

    # The following methods are invoked if a text field is changed by the user.
    def pixel_size_write(self):
        self.configuration_changed = True

    def pixel_horizontal_write(self):
        self.configuration_changed = True

    def pixel_vertical_write(self):
        self.configuration_changed = True

    def repetition_count_write(self):
        self.configuration_changed = True

    def external_margin_write(self):
        self.configuration_changed = True

    def tile_overlap_write(self):
        self.configuration_changed = True

    def accept(self):
        """
        This method is invoked when the OK button is pressed. If at least one parameter has been
        changed, all text fields are tested for valid input data. Valid data are stored in the
        configuration object. If a test fails, a dialog prompts the user for correction.
        
        :return: -
        """
        if self.configuration_changed:
            # Replace the original value with the corresponding entry in the gui text field.
            self.new_pixel_size = str(self.input_pixel_size.text())
            # Check if the float entered is within the given bounds [0., 0.02]. If the return value
            # is None, an error was detected. In this case give an example for a correct value.
            if Miscellaneous.testfloat(self.new_pixel_size, 0., 0.02) is None:
                Miscellaneous.show_input_error("Pixel size (mm)", "0.00375")
                return
            else:
                # Set the corresponding entry in the configuration object to the valuee ntered.
                self.c.conf.set(self.section_name, 'pixel size', self.new_pixel_size)

            # Repeat the same logic for all parameters.
            self.new_pixel_horizontal = str(self.input_pixel_horizontal.text())
            if Miscellaneous.testint(self.new_pixel_horizontal, 1, 20000) is None:
                Miscellaneous.show_input_error("Pixel count horizontal", "1280")
                return
            else:
                self.c.conf.set(self.section_name, 'pixel horizontal', self.new_pixel_horizontal)

            self.new_pixel_vertical = str(self.input_pixel_vertical.text())
            if Miscellaneous.testint(self.new_pixel_vertical, 1, 20000) is None:
                Miscellaneous.show_input_error("Pixel count vertical", "960")
                return
            else:
                self.c.conf.set(self.section_name, 'pixel vertical', self.new_pixel_vertical)

            self.new_repetition_count = str(self.input_repetition_count.text())
            if Miscellaneous.testint(self.new_repetition_count, 1, 10) is None:
                Miscellaneous.show_input_error("Repetition count", "3")
                return
            else:
                self.c.conf.set(self.section_name, 'repetition count', self.new_repetition_count)

            self.new_external_margin_pixel = str(self.input_external_margin.text())
            if Miscellaneous.testint(self.new_external_margin_pixel, 1, 10000) is None:
                Miscellaneous.show_input_error("External margin pixel", "300")
                return
            else:
                self.c.conf.set(self.section_name, 'external margin pixel',
                                self.new_external_margin_pixel)

            self.new_tile_overlap_pixel = str(self.input_tile_overlap.text())
            if Miscellaneous.testint(self.new_tile_overlap_pixel, 1, 5000) is None:
                Miscellaneous.show_input_error("Tile overlap pixels", "150")
                return
            else:
                self.c.conf.set(self.section_name, 'tile overlap pixel',
                                self.new_tile_overlap_pixel)

            # Copy all entries of the current camera model into the "Camera" section of the
            # configuration object. This section is displayed in the main configuration gui
            # under the heading "Camera".
            self.c.copy_camera_configuration(self.new_name)

        # Close the editing gui.
        self.close()

    def reject(self):
        # In case the Cancel button is pressed, discard all changes and close the gui.
        self.configuration_changed = False
        self.close()

    def closeEvent(self, evnt):
        self.close()
