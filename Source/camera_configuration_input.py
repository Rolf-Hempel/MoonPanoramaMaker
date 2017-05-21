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

from PyQt4 import QtGui

from camera_dialog import Ui_CameraDialog
from miscellaneous import Miscellaneous


class CameraConfigurationInput(QtGui.QDialog, Ui_CameraDialog):
    def __init__(self, configuration, parent=None):
        QtGui.QDialog.__init__(self, parent)
        self.setupUi(self)
        self.c = configuration
        self.camlist = self.c.get_camera_list()

        self.configuration_changed = False

        self.input_camera_name.textChanged.connect(self.camera_name_write)
        self.input_pixel_size.textChanged.connect(self.pixel_size_write)
        self.input_pixel_horizontal.textChanged.connect(
            self.pixel_horizontal_write)
        self.input_pixel_vertical.textChanged.connect(
            self.pixel_vertical_write)
        self.input_repetition_count.textChanged.connect(
            self.repetition_count_write)
        self.input_external_margin.textChanged.connect(
            self.external_margin_write)
        self.input_tile_overlap.textChanged.connect(self.tile_overlap_write)

    def camera_name_write(self):
        self.configuration_changed = True

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
        if self.configuration_changed:
            self.new_name = str(self.input_camera_name.text())
            if self.new_name in self.camlist:
                Miscellaneous.show_input_error(
                    "Brand / Name (duplicate)", "Name not in list")
                return
            elif self.new_name == '':
                Miscellaneous.show_input_error(
                    "Brand / Name", "ZWO ASI120MM-S")
                return

            self.new_pixel_size = str(self.input_pixel_size.text())
            if Miscellaneous.testfloat(
                    self.new_pixel_size, 0., 0.02) is None:
                Miscellaneous.show_input_error(
                    "Pixel size (mm)", "0.00375")
                return

            self.new_pixel_horizontal = str(
                self.input_pixel_horizontal.text())
            if Miscellaneous.testint(
                    self.new_pixel_horizontal, 1, 20000) is None:
                Miscellaneous.show_input_error(
                    "Pixel count horizontal", "1280")
                return

            self.new_pixel_vertical = str(self.input_pixel_vertical.text())
            if Miscellaneous.testint(
                    self.new_pixel_vertical, 1, 20000) is None:
                Miscellaneous.show_input_error(
                    "Pixel count vertical", "960")
                return

            self.new_repetition_count = str(self.input_repetition_count.text())
            if Miscellaneous.testint(self.new_repetition_count, 1, 10) is None:
                Miscellaneous.show_input_error("Repetition count", "3")
                return

            self.new_external_margin_pixel = str(
                self.input_external_margin.text())
            if Miscellaneous.testint(
                    self.new_external_margin_pixel, 1, 10000) is None:
                Miscellaneous.show_input_error(
                    "External margin pixel", "300")
                return

            self.new_tile_overlap_pixel = str(
                self.input_tile_overlap.text())
            if Miscellaneous.testint(
                    self.new_tile_overlap_pixel, 1, 5000) is None:
                Miscellaneous.show_input_error(
                    "Tile overlap pixels", "150")
                return

            self.section_name = 'Camera ' + self.new_name
            self.c.conf.add_section(self.section_name)
            self.c.conf.set(self.section_name, 'name',
                            self.new_name)
            self.c.conf.set(self.section_name, 'pixel size',
                            self.new_pixel_size)
            self.c.conf.set(self.section_name, 'pixel horizontal',
                            self.new_pixel_horizontal)
            self.c.conf.set(self.section_name, 'pixel vertical',
                            self.new_pixel_vertical)
            self.c.conf.set(self.section_name, 'repetition count',
                            self.new_repetition_count)
            self.c.conf.set(self.section_name, 'external margin pixel',
                            self.new_external_margin_pixel)
            self.c.conf.set(self.section_name, 'tile overlap pixel',
                            self.new_tile_overlap_pixel)

            self.c.copy_camera_configuration(self.new_name)

        self.close()

    def reject(self):
        self.configuration_changed = False
        self.close()

    def closeEvent(self, evnt):
        self.close()
