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

basePath = os.path.dirname(os.path.abspath(sys.argv[0]))
sys.path.insert(0, basePath)

from PyQt4 import QtGui
from pytz import timezone
from configuration_dialog import Ui_ConfigurationDialog
from camera_configuration_editor import CameraConfigurationEditor
from camera_configuration_input import CameraConfigurationInput
from camera_configuration_delete import CameraConfigurationDelete
from miscellaneous import Miscellaneous


class ConfigurationEditor(QtGui.QDialog, Ui_ConfigurationDialog):
    """
    Update the parameters used by MoonPanoramaMaker which are stored in the configuration object.
    The interaction with the user is through the ConfigurationDialog class.
    
    """

    def __init__(self, configuration, parent=None):
        """
        Initialize the text fields in the gui based on the configuration object, and connect
        gui signals with methods to update the configuration object entries.
        
        :param configuration: object containing parameters set by the user
        :param parent: 
        """

        QtGui.QDialog.__init__(self, parent)
        self.setupUi(self)
        # Configuration object c
        self.c = configuration
        # Set the flag indicating if the configuration was changed to False.
        self.configuration_changed = False

        # Start filling the text fields of the gui.
        self.input_longitude.setText(self.c.conf.get("Geographical Position", "longitude"))
        self.input_latitude.setText(self.c.conf.get("Geographical Position", "latitude"))
        self.input_elevation.setText(self.c.conf.get("Geographical Position", "elevation"))
        self.input_timezone.setText(self.c.conf.get("Geographical Position", "timezone"))

        # Special treatment of available camera models: populate the camera_chooser with list.
        self.camlist = self.c.get_camera_list()
        self.camera_chooser.addItems(self.camlist)
        self.camera_chooser.setCurrentIndex(self.camlist.index(self.c.conf.get("Camera", "name")))

        self.input_focal_length.setText(self.c.conf.get("Telescope", "focal length"))

        self.input_protocol_level.setText(self.c.conf.get("Workflow", "protocol level"))
        self.input_protocol_to_file.setText(self.c.conf.get("Workflow", "protocol to file"))
        self.input_focus_on_star.setText(self.c.conf.get("Workflow", "focus on star"))
        self.input_limb_first.setText(self.c.conf.get("Workflow", "limb first"))
        self.input_camera_automation.setText(self.c.conf.get("Workflow", "camera automation"))
        self.input_camera_trigger_delay.setText(self.c.conf.get("Workflow", "camera trigger delay"))

        self.input_fig_size_horizontal.setText(
            self.c.conf.get("Tile Visualization", "figsize horizontal"))
        self.input_fig_size_vertical.setText(
            self.c.conf.get("Tile Visualization", "figsize vertical"))
        self.input_label_font_size.setText(self.c.conf.get("Tile Visualization", "label fontsize"))
        self.input_label_shift.setText(self.c.conf.get("Tile Visualization", "label shift"))

        self.input_chooser.setText(self.c.conf.get("ASCOM", "chooser"))
        self.input_hub.setText(self.c.conf.get("ASCOM", "hub"))
        self.input_guiding_interval.setText(self.c.conf.get("ASCOM", "guiding interval"))
        self.input_wait_interval.setText(self.c.conf.get("ASCOM", "wait interval"))
        self.input_polling_interval.setText(self.c.conf.get("ASCOM", "polling interval"))
        self.input_telescope_lookup_precision.setText(
            self.c.conf.get("ASCOM", "telescope lookup precision"))

        self.input_min_autoalign_interval.setText(
            self.c.conf.get("Alignment", "min autoalign interval"))
        self.input_max_autoalign_interval.setText(
            self.c.conf.get("Alignment", "max autoalign interval"))
        self.input_max_alignment_error.setText(self.c.conf.get("Alignment", "max alignment error"))

        # Connect textChanged signals with methods to update the corresponding parameters.
        self.input_longitude.textChanged.connect(self.longitude_write)
        self.input_latitude.textChanged.connect(self.latitude_write)
        self.input_elevation.textChanged.connect(self.elevation_write)
        self.input_timezone.textChanged.connect(self.timezone_write)

        self.camera_chooser.currentIndexChanged.connect(self.camera_changed)
        self.edit_camera.clicked.connect(self.start_edit_camera_dialog)
        self.new_camera.clicked.connect(self.start_new_camera_dialog)
        self.delete_camera.clicked.connect(self.start_delete_camera_dialog)

        self.input_focal_length.textChanged.connect(self.focal_length_write)

        self.input_protocol_level.textChanged.connect(self.protocol_level_write)
        self.input_protocol_to_file.textChanged.connect(self.protocol_to_file_write)
        self.input_focus_on_star.textChanged.connect(self.focus_on_star_write)
        self.input_limb_first.textChanged.connect(self.limb_first_write)
        self.input_camera_automation.textChanged.connect(self.camera_automation_write)
        self.input_camera_trigger_delay.textChanged.connect(self.camera_trigger_delay_write)
        self.input_fig_size_horizontal.textChanged.connect(self.fig_size_horizontal_write)
        self.input_fig_size_vertical.textChanged.connect(self.fig_size_vertical_write)
        self.input_label_font_size.textChanged.connect(self.label_font_size_write)
        self.input_label_shift.textChanged.connect(self.label_shift_write)

        self.input_chooser.textChanged.connect(self.chooser_write)
        self.input_hub.textChanged.connect(self.hub_write)
        self.input_guiding_interval.textChanged.connect(self.guiding_interval_write)
        self.input_wait_interval.textChanged.connect(self.wait_interval_write)
        self.input_polling_interval.textChanged.connect(self.polling_interval_write)
        self.input_telescope_lookup_precision.textChanged.connect(
            self.telescope_lookup_precision_write)

        self.input_min_autoalign_interval.textChanged.connect(self.min_autoalign_interval_write)
        self.input_max_autoalign_interval.textChanged.connect(self.max_autoalign_interval_write)
        self.input_max_alignment_error.textChanged.connect(self.max_alignment_error_write)

    def longitude_write(self):
        """
        If the parameter has been changed, set the configuration_changed flag to True.
        
        :return: -
        """

        self.configuration_changed = True

    def latitude_write(self):
        """
        If the parameter has been changed, set the configuration_changed flag to True.

        :return: -
        """

        self.configuration_changed = True

    def elevation_write(self):
        """
        If the parameter has been changed, set the configuration_changed flag to True.

        :return: -
        """

        self.configuration_changed = True

    def timezone_write(self):
        """
        If the parameter has been changed, set the configuration_changed flag to True.

        :return: -
        """

        self.configuration_changed = True

    def camera_changed(self):
        """
        First check if the camera name is valid (i.e. not blank). Then copy all parameters of the
        choosen camera into the "Camera" section of the configuration object. Finally, set the
        configuration_changed flag to True.

        :return: -
        """

        if str(self.camera_chooser.currentText()) != "":
            self.c.copy_camera_configuration(str(self.camera_chooser.currentText()))
            self.configuration_changed = True

    def start_edit_camera_dialog(self):
        """
        The "Edit camera" button is clicked: start the camera configuration gui and populate the
        text fields with the parameters of the currently chosen camera. Start the editor gui. When
        it closes, check if parameters have changed. If so, set the configuration_changed flag
        to True.

        :return: -
        """

        camera_name = str(self.camera_chooser.currentText())
        self.editor = CameraConfigurationEditor(self.c, camera_name)
        self.editor.exec_()
        if self.editor.configuration_changed:
            self.configuration_changed = True

    def start_new_camera_dialog(self):
        """
        The "Input camera" button is clicked: Open the input camera dialog.

        :return: -
        """

        self.inputeditor = CameraConfigurationInput(self.c)
        # Start the input gui.
        self.inputeditor.exec_()
        # Check if new parameters have been entered.
        if self.inputeditor.configuration_changed:
            # Mark the configuration object as changed.
            self.configuration_changed = True
            # Update the list of available cameras
            self.camlist = self.c.get_camera_list()
            # Update the camera chooser to contain the extended list of camera names.
            self.camera_chooser.clear()
            self.camera_chooser.addItems(self.camlist)
            # Set the current chooser entry to the new camera model.
            self.camera_chooser.setCurrentIndex(
                self.camlist.index(self.c.conf.get("Camera", "name")))

    def start_delete_camera_dialog(self):
        """
        The "Delete camera" button has been clicked: Open the delete camera dialog.

        :return: -
        """

        self.deleteeditor = CameraConfigurationDelete()
        # Start the gui.
        self.deleteeditor.exec_()
        # Check if the selected camera is really deleted.
        if self.deleteeditor.configuration_changed:
            # Mark the configuration object as changed.
            self.configuration_changed = True
            # Remove the section with parameters of the deleted camera model from configuration
            # object.
            self.c.conf.remove_section('Camera ' + str(self.camera_chooser.currentText()))
            # Update the list of available cameras
            self.camlist = self.c.get_camera_list()
            # Update the camera chooser to contain the extended list of camera names.
            self.camera_chooser.clear()
            self.camera_chooser.addItems(self.camlist)
            # The current camera is deleted, set the index of the chooser to 0 (default).
            self.camera_chooser.setCurrentIndex(0)

    def focal_length_write(self):
        """
        If the parameter has been changed, set the configuration_changed flag to True.

        :return: -
        """

        self.configuration_changed = True

    def protocol_level_write(self):
        """
        If the parameter has been changed, set the configuration_changed flag to True.

        :return: -
        """

        self.configuration_changed = True

    def protocol_to_file_write(self):
        """
        If the parameter has been changed, set the configuration_changed flag to True.

        :return: -
        """

        self.configuration_changed = True

    def focus_on_star_write(self):
        """
        If the parameter has been changed, set the configuration_changed flag to True.

        :return: -
        """

        self.configuration_changed = True

    def limb_first_write(self):
        """
        If the parameter has been changed, set the configuration_changed flag to True.

        :return: -
        """

        self.configuration_changed = True

    def camera_automation_write(self):
        """
        If the parameter has been changed, set the configuration_changed flag to True.

        :return: -
        """

        self.configuration_changed = True

    def camera_trigger_delay_write(self):
        """
        If the parameter has been changed, set the configuration_changed flag to True.

        :return: -
        """

        self.configuration_changed = True

    def fig_size_horizontal_write(self):
        """
        If the parameter has been changed, set the configuration_changed flag to True.

        :return: -
        """

        self.configuration_changed = True

    def fig_size_vertical_write(self):
        """
        If the parameter has been changed, set the configuration_changed flag to True.

        :return: -
        """

        self.configuration_changed = True

    def label_font_size_write(self):
        """
        If the parameter has been changed, set the configuration_changed flag to True.

        :return: -
        """

        self.configuration_changed = True

    def label_shift_write(self):
        """
        If the parameter has been changed, set the configuration_changed flag to True.

        :return: -
        """

        self.configuration_changed = True

    def chooser_write(self):
        """
        Special case for the ASCOM chooser: No check for validity of the input string.
        If the parameter has been changed, set the configuration_changed flag to True.

        :return: -
        """

        self.c.conf.set("ASCOM", "chooser", str(self.input_chooser.text()))
        self.configuration_changed = True

    def hub_write(self):
        """
        Special case for the ASCOM hub: No check for validity of the input string.
        If the parameter has been changed, set the configuration_changed flag to True.

        :return: -
        """

        self.c.conf.set("ASCOM", "hub", str(self.input_hub.text()))
        self.configuration_changed = True

    def guiding_interval_write(self):
        """
        If the parameter has been changed, set the configuration_changed flag to True.

        :return: -
        """

        self.configuration_changed = True

    def wait_interval_write(self):
        """
        If the parameter has been changed, set the configuration_changed flag to True.

        :return: -
        """

        self.configuration_changed = True

    def polling_interval_write(self):
        """
        If the parameter has been changed, set the configuration_changed flag to True.

        :return: -
        """

        self.configuration_changed = True

    def telescope_lookup_precision_write(self):
        """
        If the parameter has been changed, set the configuration_changed flag to True.

        :return: -
        """

        self.configuration_changed = True

    def min_autoalign_interval_write(self):
        """
        If the parameter has been changed, set the configuration_changed flag to True.

        :return: -
        """

        self.configuration_changed = True

    def max_autoalign_interval_write(self):
        """
        If the parameter has been changed, set the configuration_changed flag to True.

        :return: -
        """

        self.configuration_changed = True

    def max_alignment_error_write(self):
        """
        If the parameter has been changed, set the configuration_changed flag to True.

        :return: -
        """

        self.configuration_changed = True

    def accept(self):
        """
        If the OK button is clicked and the configuration has been changed, test all parameters for
        validity. In case an out-of-bound value is entered, open an error correction dialog window.
        
        :return: -
        """

        if self.configuration_changed:
            # Get the input string from the gui text field.
            input_string = str(self.input_longitude.text())
            # Test the input value if it is within the allowed interval (here [-360., +360.])
            if Miscellaneous.testfloat(input_string, -360., 360.):
                self.c.conf.set("Geographical Position", "longitude", input_string)
            else:
                # The value entered is out of bound, show a valid input value example.
                Miscellaneous.show_input_error("Longitude", "7.39720")
                return

            # Repeat the same logic for the other input fields.
            input_string = str(self.input_latitude.text())
            if Miscellaneous.testfloat(input_string, -90., 90.):
                self.c.conf.set("Geographical Position", "latitude", input_string)
            else:
                Miscellaneous.show_input_error("Latitude", "50.69190")
                return

            input_string = str(self.input_elevation.text())
            if Miscellaneous.testint(input_string, -100, 9000):
                self.c.conf.set("Geographical Position", "elevation", input_string)
            else:
                Miscellaneous.show_input_error("Elevation", "250")
                return

            # Special case time zone: Take the time zone string entered and try to convert it using
            # the timezone method of pytz. If an error is raised, the input string was invalid.
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

            input_string = str(self.input_protocol_level.text())
            if Miscellaneous.testint(input_string, 0, 3) is not None:
                self.c.conf.set("Workflow", "protocol level", str(self.input_protocol_level.text()))
            else:
                Miscellaneous.show_input_error("Session protocol level", "2")
                return

            input_string = str(self.input_protocol_to_file.text())
            if Miscellaneous.testbool(input_string) is not None:
                self.c.conf.set("Workflow", "protocol to file",
                                str(self.input_protocol_to_file.text()))
            else:
                Miscellaneous.show_input_error("Write protocol to file", "True")
                return

            input_string = str(self.input_focus_on_star.text())
            if Miscellaneous.testbool(input_string) is not None:
                self.c.conf.set("Workflow", "focus on star",
                                str(self.input_focus_on_star.text()))
            else:
                Miscellaneous.show_input_error("Focus on star", "False")
                return

            input_string = str(self.input_limb_first.text())
            if Miscellaneous.testbool(input_string) is not None:
                self.c.conf.set("Workflow", "limb first", str(self.input_limb_first.text()))
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
                self.c.conf.set("Workflow", "camera trigger delay", input_string)
            else:
                Miscellaneous.show_input_error("Camera trigger delay", "10.")
                return

            input_string = str(self.input_fig_size_horizontal.text())
            if Miscellaneous.testfloat(input_string, 0., 25.):
                self.c.conf.set("Tile Visualization", "figsize horizontal", input_string)
            else:
                Miscellaneous.show_input_error("Figure size horizontal", "10.")
                return

            input_string = str(self.input_fig_size_vertical.text())
            if Miscellaneous.testfloat(input_string, 0., 25.):
                self.c.conf.set("Tile Visualization", "figsize vertical", input_string)
            else:
                Miscellaneous.show_input_error("Figure size vertical", "10.")
                return

            input_string = str(self.input_label_font_size.text())
            if Miscellaneous.testint(input_string, 6, 16):
                self.c.conf.set("Tile Visualization", "label fontsize", input_string)
            else:
                Miscellaneous.show_input_error("Font size for labels", "11")
                return

            input_string = str(self.input_label_shift.text())
            if Miscellaneous.testfloat(input_string, 0., 1.):
                self.c.conf.set("Tile Visualization", "label shift", input_string)
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
                self.c.conf.set("ASCOM", "telescope lookup precision", input_string)
            else:
                Miscellaneous.show_input_error("Telescope position lookup precision", "0.5")
                return

            input_string = str(self.input_min_autoalign_interval.text())
            if Miscellaneous.testfloat(input_string, 20., 1800.):
                self.c.conf.set("Alignment", "min autoalign interval", input_string)
            else:
                Miscellaneous.show_input_error("Minimum auto-alignment interval", "120.")
                return

            input_string = str(self.input_max_autoalign_interval.text())
            if Miscellaneous.testfloat(input_string, 30., 3600.):
                self.c.conf.set("Alignment", "max autoalign interval", input_string)
            else:
                Miscellaneous.show_input_error("Maximum auto-alignment interval", "900.")
                return

            input_string = str(self.input_max_alignment_error.text())
            if Miscellaneous.testfloat(input_string, 10., 60.):
                self.c.conf.set("Alignment", "max alignment error", input_string)
            else:
                Miscellaneous.show_input_error("Max alignment error", "30.")
                return

        # All tests passed successfully, and all parameters have been written to the
        # configuration object. Close the gui window.
        self.close()

    def reject(self):
        """
        The Cancel button is pressed, discard the changes and close the gui window.
        :return: -
        """

        self.configuration_changed = False
        self.close()

    def closeEvent(self, evnt):
        self.close()
