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
import sys

basePath = os.path.dirname( os.path.abspath( sys.argv[0] ) )
sys.path.insert( 0, basePath )

from PyQt4 import QtGui
from pytz import timezone
from configuration_dialog import Ui_ConfigurationDialog
from camera_configuration_editor import CameraConfigurationEditor
from camera_configuration_input import CameraConfigurationInput
from camera_configuration_delete import CameraConfigurationDelete
from miscellaneous import Miscellaneous


class ConfigurationEditor(QtGui.QDialog, Ui_ConfigurationDialog):
    def __init__(self, configuration, parent=None):
        QtGui.QDialog.__init__(self, parent)
        self.setupUi(self)
        self.c = configuration
        self.configuration_changed = False
        self.input_longitude.setText(
            self.c.conf.get("Geographical Position", "longitude"))
        self.input_latitude.setText(
            self.c.conf.get("Geographical Position", "latitude"))
        self.input_elevation.setText(
            self.c.conf.get("Geographical Position", "elevation"))
        self.input_timezone.setText(
            self.c.conf.get("Geographical Position", "timezone"))

        self.camlist = self.c.get_camera_list()
        self.camera_chooser.addItems(self.camlist)
        self.camera_chooser.setCurrentIndex(
            self.camlist.index(self.c.conf.get("Camera", "name")))

        self.input_focal_length.setText(
            self.c.conf.get("Telescope", "focal length"))

        self.input_protocol.setText(
            self.c.conf.get("Workflow", "protocol"))
        self.input_protocol_to_file.setText(
            self.c.conf.get("Workflow", "protocol to file"))
        self.input_limb_first.setText(
            self.c.conf.get("Workflow", "limb first"))
        self.input_camera_automation.setText(
            self.c.conf.get("Workflow", "camera automation"))
        self.input_camera_trigger_delay.setText(
            self.c.conf.get("Workflow", "camera trigger delay"))

        self.input_fig_size_horizontal.setText(
            self.c.conf.get("Tile Visualization", "figsize horizontal"))
        self.input_fig_size_vertical.setText(
            self.c.conf.get("Tile Visualization", "figsize vertical"))
        self.input_label_font_size.setText(
            self.c.conf.get("Tile Visualization", "label fontsize"))
        self.input_label_shift.setText(
            self.c.conf.get("Tile Visualization", "label shift"))

        self.input_chooser.setText(
            self.c.conf.get("ASCOM", "chooser"))
        self.input_hub.setText(
            self.c.conf.get("ASCOM", "hub"))
        self.input_guiding_interval.setText(
            self.c.conf.get("ASCOM", "guiding interval"))
        self.input_wait_interval.setText(
            self.c.conf.get("ASCOM", "wait interval"))
        self.input_polling_interval.setText(
            self.c.conf.get("ASCOM", "polling interval"))
        self.input_telescope_lookup_precision.setText(
            self.c.conf.get("ASCOM", "telescope lookup precision"))

        self.input_longitude.textChanged.connect(self.longitude_write)
        self.input_latitude.textChanged.connect(self.latitude_write)
        self.input_elevation.textChanged.connect(self.elevation_write)
        self.input_timezone.textChanged.connect(self.timezone_write)

        self.camera_chooser.currentIndexChanged.connect(self.camera_changed)
        self.edit_camera.clicked.connect(self.start_edit_camera_dialog)
        self.new_camera.clicked.connect(self.start_new_camera_dialog)
        self.delete_camera.clicked.connect(self.start_delete_camera_dialog)

        self.input_focal_length.textChanged.connect(self.focal_length_write)

        self.input_protocol.textChanged.connect(self.protocol_write)
        self.input_protocol_to_file.textChanged.connect(
            self.protocol_to_file_write)
        self.input_limb_first.textChanged.connect(self.limb_first_write)
        self.input_camera_automation.textChanged.connect(
            self.camera_automation_write)
        self.input_camera_trigger_delay.textChanged.connect(
            self.camera_trigger_delay_write)
        self.input_fig_size_horizontal.textChanged.connect(
            self.fig_size_horizontal_write)
        self.input_fig_size_vertical.textChanged.connect(
            self.fig_size_vertical_write)
        self.input_label_font_size.textChanged.connect(
            self.label_font_size_write)
        self.input_label_shift.textChanged.connect(self.label_shift_write)

        self.input_chooser.textChanged.connect(self.chooser_write)
        self.input_hub.textChanged.connect(self.hub_write)
        self.input_guiding_interval.textChanged.connect(
            self.guiding_interval_write)
        self.input_wait_interval.textChanged.connect(self.wait_interval_write)
        self.input_polling_interval.textChanged.connect(
            self.polling_interval_write)
        self.input_telescope_lookup_precision.textChanged.connect(
            self.telescope_lookup_precision_write)

    def longitude_write(self):
        self.configuration_changed = True

    def latitude_write(self):
        self.configuration_changed = True

    def elevation_write(self):
        self.configuration_changed = True

    def timezone_write(self):
        self.configuration_changed = True

    def camera_changed(self):
        if str(self.camera_chooser.currentText()) != "":
            self.c.copy_camera_configuration(
                str(self.camera_chooser.currentText()))
            self.configuration_changed = True

    def start_edit_camera_dialog(self):
        camera_name = str(self.camera_chooser.currentText())
        self.editor = CameraConfigurationEditor(self.c, camera_name)
        self.editor.exec_()
        if self.editor.configuration_changed:
            self.configuration_changed = True

    def start_new_camera_dialog(self):
        self.inputeditor = CameraConfigurationInput(self.c)
        self.inputeditor.exec_()
        if self.inputeditor.configuration_changed:
            self.configuration_changed = True
            self.camlist = self.c.get_camera_list()
            self.camera_chooser.clear()
            self.camera_chooser.addItems(self.camlist)
            self.camera_chooser.setCurrentIndex(
                self.camlist.index(self.c.conf.get("Camera", "name")))

    def start_delete_camera_dialog(self):
        self.deleteeditor = CameraConfigurationDelete()
        self.deleteeditor.exec_()
        if self.deleteeditor.configuration_changed:
            self.configuration_changed = True
            self.c.conf.remove_section(
                'Camera ' + str(self.camera_chooser.currentText()))
            self.camlist = self.c.get_camera_list()
            self.camera_chooser.clear()
            self.camera_chooser.addItems(self.camlist)
            self.camera_chooser.setCurrentIndex(0)

    def focal_length_write(self):
        self.configuration_changed = True

    def protocol_write(self):
        self.configuration_changed = True

    def protocol_to_file_write(self):
        self.configuration_changed = True

    def limb_first_write(self):
        self.configuration_changed = True

    def camera_automation_write(self):
        self.configuration_changed = True

    def camera_trigger_delay_write(self):
        self.configuration_changed = True

    def fig_size_horizontal_write(self):
        self.configuration_changed = True

    def fig_size_vertical_write(self):
        self.configuration_changed = True

    def label_font_size_write(self):
        self.configuration_changed = True

    def label_shift_write(self):
        self.configuration_changed = True

    def chooser_write(self):
        self.c.conf.set("ASCOM", "chooser",
                        str(self.input_chooser.text()))
        self.configuration_changed = True

    def hub_write(self):
        self.c.conf.set("ASCOM", "hub",
                        str(self.input_hub.text()))
        self.configuration_changed = True

    def guiding_interval_write(self):
        self.configuration_changed = True

    def wait_interval_write(self):
        self.configuration_changed = True

    def polling_interval_write(self):
        self.configuration_changed = True

    def telescope_lookup_precision_write(self):
        self.configuration_changed = True

    def accept(self):
        if self.configuration_changed:
            input_string = str(self.input_longitude.text())
            if Miscellaneous.testfloat(input_string, -360., 360.):
                self.c.conf.set("Geographical Position", "longitude",
                                input_string)
            else:
                Miscellaneous.show_input_error("Longitude", "7.39720")
                return

            input_string = str(self.input_latitude.text())
            if Miscellaneous.testfloat(input_string, -90., 90.):
                self.c.conf.set("Geographical Position", "latitude",
                                input_string)
            else:
                Miscellaneous.show_input_error("Latitude", "50.69190")
                return

            input_string = str(self.input_elevation.text())
            if Miscellaneous.testint(input_string, -100, 9000):
                self.c.conf.set("Geographical Position", "elevation",
                                input_string)
            else:
                Miscellaneous.show_input_error("Elevation", "250")
                return

            try:
                timezone(str(self.input_timezone.text()))
                self.c.conf.set("Geographical Position", "timezone",
                                str(self.input_timezone.text()))
            except:
                Miscellaneous.show_input_error("Timezone", "Europe/Berlin")
                return

            input_string = str(self.input_focal_length.text())
            if Miscellaneous.testfloat(input_string, 0., 100000.):
                self.c.conf.set("Telescope", "focal length", input_string)
            else:
                Miscellaneous.show_input_error("Focal length", "4670.")
                return

            input_string = str(self.input_protocol.text())
            if Miscellaneous.testbool(input_string) is not None:
                self.c.conf.set("Workflow", "protocol",
                                str(self.input_protocol.text()))
            else:
                Miscellaneous.show_input_error("Write session protocol",
                                               "True")
                return

            input_string = str(self.input_protocol_to_file.text())
            if Miscellaneous.testbool(input_string) is not None:
                self.c.conf.set("Workflow", "protocol to file",
                                str(self.input_protocol_to_file.text()))
            else:
                Miscellaneous.show_input_error("Write protocol to file",
                                               "True")
                return

            input_string = str(self.input_limb_first.text())
            if Miscellaneous.testbool(input_string) is not None:
                self.c.conf.set("Workflow", "limb first",
                                str(self.input_limb_first.text()))
            else:
                Miscellaneous.show_input_error("Limb first", "True")
                return

            input_string = str(self.input_camera_automation.text())
            if Miscellaneous.testbool(input_string) is not None:
                self.c.conf.set("Workflow", "camera automation",
                                str(self.input_camera_automation.text()))
            else:
                Miscellaneous.show_input_error("Camera automation", "True")
                return

            input_string = str(self.input_camera_trigger_delay.text())
            if Miscellaneous.testfloat(input_string, 0., 60.):
                self.c.conf.set("Workflow", "camera trigger delay",
                                input_string)
            else:
                Miscellaneous.show_input_error("Camera trigger delay", "10.")
                return

            input_string = str(self.input_fig_size_horizontal.text())
            if Miscellaneous.testfloat(input_string, 0., 25.):
                self.c.conf.set("Tile Visualization", "figsize horizontal",
                                input_string)
            else:
                Miscellaneous.show_input_error("Figure size horizontal", "10.")
                return

            input_string = str(self.input_fig_size_vertical.text())
            if Miscellaneous.testfloat(input_string, 0., 25.):
                self.c.conf.set("Tile Visualization", "figsize vertical",
                                input_string)
            else:
                Miscellaneous.show_input_error("Figure size vertical", "10.")
                return

            input_string = str(self.input_label_font_size.text())
            if Miscellaneous.testint(input_string, 6, 16):
                self.c.conf.set("Tile Visualization", "label fontsize",
                                input_string)
            else:
                Miscellaneous.show_input_error("Font size for labels", "11")
                return

            input_string = str(self.input_label_shift.text())
            if Miscellaneous.testfloat(input_string, 0., 1.):
                self.c.conf.set("Tile Visualization", "label shift",
                                input_string)
            else:
                Miscellaneous.show_input_error("Label shift parameter", "0.8")
                return

            input_string = str(self.input_guiding_interval.text())
            if Miscellaneous.testfloat(input_string, 0., 3.):
                self.c.conf.set("ASCOM", "guiding interval", input_string)
            else:
                Miscellaneous.show_input_error("Guide pulse duration", "0.2")
                return

            input_string = str(self.input_wait_interval.text())
            if Miscellaneous.testfloat(input_string, 0., 20.):
                self.c.conf.set("ASCOM", "wait interval", input_string)
            else:
                Miscellaneous.show_input_error("Wait interval", "1.")
                return

            input_string = str(self.input_polling_interval.text())
            if Miscellaneous.testfloat(input_string, 0., 1.):
                self.c.conf.set("ASCOM", "polling interval", input_string)
            else:
                Miscellaneous.show_input_error("Polling interval", "0.1")
                return

            input_string = str(self.input_telescope_lookup_precision.text())
            if Miscellaneous.testfloat(input_string, 0.1, 10.):
                self.c.conf.set("ASCOM", "telescope lookup precision",
                                input_string)
            else:
                Miscellaneous.show_input_error("Polling interval", "0.1")
                return

        self.close()

    def reject(self):
        self.configuration_changed = False
        self.close()

    def closeEvent(self, evnt):
        self.close()
