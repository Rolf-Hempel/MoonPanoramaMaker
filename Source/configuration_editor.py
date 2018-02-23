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

from PyQt5 import QtWidgets
from pytz import timezone
from configuration_dialog import Ui_ConfigurationDialog
from camera_configuration_editor import CameraConfigurationEditor
from camera_configuration_input import CameraConfigurationInput
from camera_configuration_delete import CameraConfigurationDelete
from exceptions import ASCOMException
from miscellaneous import Miscellaneous


class ConfigurationEditor(QtWidgets.QDialog, Ui_ConfigurationDialog):
    """
    Update the parameters used by MoonPanoramaMaker which are stored in the configuration object.
    The interaction with the user is through the ConfigurationDialog class.
    
    """

    def __init__(self, configuration, parent=None):
        """
        Initialize the text fields in the GUI based on the configuration object, and connect
        gui signals with methods to update the configuration object entries.
        
        :param configuration: object containing parameters set by the user
        :param parent: 
        """

        QtWidgets.QDialog.__init__(self, parent)
        self.setupUi(self)
        # Configuration object c
        self.c = configuration
        # Set the flag indicating if the configuration was changed to False.
        self.configuration_changed = False
        self.output_channel_changed = False
        self.telescope_changed = False
        self.camera_automation_changed = False
        self.tesselation_changed = False
        # Remember if the ASCOM configuration editor was called. Changes made by this editor are
        # only applied in the end if the user accepts the changes in the main window.
        self.ascomeditor_called = False

        # Start filling the text fields of the GUI.
        self.input_longitude.setText(self.c.conf.get("Geographical Position", "longitude"))
        self.input_latitude.setText(self.c.conf.get("Geographical Position", "latitude"))
        self.input_elevation.setText(self.c.conf.get("Geographical Position", "elevation"))
        self.input_timezone.setText(self.c.conf.get("Geographical Position", "timezone"))

        # Special treatment of available camera models: populate the camera_chooser with list.
        self.camlist = self.c.get_camera_list()
        self.camera_chooser.addItems(self.camlist)
        self.camera_chooser.setCurrentIndex(self.camlist.index(self.c.conf.get("Camera", "name")))

        self.input_focal_length.setText(self.c.conf.get("Telescope", "focal length"))
        # Prepare for alternative telescope interfaces (e.g. INDI).
        self.interface_list = ["ASCOM", "INDI"]
        # self.interface_list = ["ASCOM"]
        self.mount_interface_chooser.addItems(self.interface_list)
        self.mount_interface_chooser.setCurrentIndex(
            self.interface_list.index(self.c.conf.get("Telescope", "interface type")))

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
        self.mount_interface_chooser.currentIndexChanged.connect(self.mount_interface_changed)
        if str(self.mount_interface_chooser.currentText()) == "ASCOM":
            self.configure_mount_interface.clicked.connect(self.start_ascom_dialog)
        elif str(self.mount_interface_chooser.currentText()) == "INDI":
            # INDI is not implemented yet. Insert the connection to the INDI configuration editor.
            pass

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

        self.input_min_autoalign_interval.textChanged.connect(self.min_autoalign_interval_write)
        self.input_max_autoalign_interval.textChanged.connect(self.max_autoalign_interval_write)
        self.input_max_alignment_error.textChanged.connect(self.max_alignment_error_write)

    def longitude_write(self):
        """
        If the parameter has been changed, set the appropriate configuration change flags to True.
        
        :return: -
        """

        self.tesselation_changed = True
        self.configuration_changed = True

    def latitude_write(self):
        """
        If the parameter has been changed, set the appropriate configuration change flags to True.

        :return: -
        """

        self.tesselation_changed = True
        self.configuration_changed = True

    def elevation_write(self):
        """
        If the parameter has been changed, set the appropriate configuration change flags to True.

        :return: -
        """

        self.tesselation_changed = True
        self.configuration_changed = True

    def timezone_write(self):
        """
        If the parameter has been changed, set the appropriate configuration change flags to True.

        :return: -
        """

        self.tesselation_changed = True
        self.configuration_changed = True

    def camera_changed(self):
        """
        First check if the camera name is valid (i.e. not blank). Then copy all parameters of the
        choosen camera into the "Camera" section of the configuration object. Finally, set the
        appropriate configuration change flags to True.

        :return: -
        """

        if str(self.camera_chooser.currentText()) != "":
            self.c.copy_camera_configuration(str(self.camera_chooser.currentText()))
            self.tesselation_changed = True
            self.configuration_changed = True

    def start_edit_camera_dialog(self):
        """
        The "Edit camera" button is clicked: start the camera configuration GUI and populate the
        text fields with the parameters of the currently chosen camera. Start the editor GUI. When
        it closes, check if parameters have changed. If so, If the parameter has been changed, set
        the appropriate configuration change flags to True.

        :return: -
        """

        camera_name = str(self.camera_chooser.currentText())
        self.editor = CameraConfigurationEditor(self.c, camera_name)
        self.editor.exec_()
        if self.editor.configuration_changed:
            self.tesselation_changed = True
            self.configuration_changed = True

    def start_new_camera_dialog(self):
        """
        The "Input camera" button is clicked: Open the input camera dialog.

        :return: -
        """

        self.inputeditor = CameraConfigurationInput(self.c)
        # Start the input GUI.
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
        # Start the GUI.
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
        If the parameter has been changed, set the appropriate configuration change flags to True.

        :return: -
        """

        self.tesselation_changed = True
        self.configuration_changed = True

    def mount_interface_changed(self):
        """
        If the mount interface type has changed, set the appropriate configuration change flags to
        True.

        :return: -
        """

        if str(self.mount_interface_chooser.currentText()) == "ASCOM":
            self.configure_mount_interface.clicked.connect(self.start_ascom_dialog)
        elif str(self.mount_interface_chooser.currentText()) == "INDI":
            self.configure_mount_interface.clicked.disconnect()

        self.telescope_changed = True
        self.configuration_changed = True

    def start_ascom_dialog(self):
        """
        The "configure" button has been clicked for the ASCOM telescope interface:
        Open the ASCOM dialog.

        :return: -
        """

        try:
            # ASCON is only available on Windows. On Linux systems, do nothing.
            from ascom_configuration_editor import AscomConfigurationEditor
        except ImportError:
            Miscellaneous.show_detailed_error_message("The ASCOM interface does not seem to work.",
                    "Most likely the ASCOM platform is not installed on this computer.\n\nIf this is a Linux system, "
                    "there might be an INDI client available. In this case, try to use 'INDI' instead of 'ASCOM'")
            return

        self.ascomeditor = AscomConfigurationEditor(self.c)
        # Start the GUI.
        self.ascomeditor.exec_()

        # Remember that the AscomConfigurationEditor was invoked.
        self.ascomeditor_called = True
        # Check if the configuration has changed.
        if self.ascomeditor.configuration_changed:
            # Mark the configuration object as changed.
            self.configuration_changed = True
        if self.ascomeditor.telescope_changed:
            # Mark the telescope driver as changed.
            self.telescope_changed = True

    def protocol_level_write(self):
        """
        If the parameter has been changed, set the appropriate configuration change flags to True.

        :return: -
        """

        self.configuration_changed = True

    def protocol_to_file_write(self):
        """
        If the parameter has been changed, set the appropriate configuration change flags to True.

        :return: -
        """

        self.output_channel_changed = True
        self.configuration_changed = True

    def focus_on_star_write(self):
        """
        If the parameter has been changed, set the appropriate configuration change flags to True.

        :return: -
        """

        self.configuration_changed = True

    def limb_first_write(self):
        """
        If the parameter has been changed, set the appropriate configuration change flags to True.

        :return: -
        """

        self.tesselation_changed = True
        self.configuration_changed = True

    def camera_automation_write(self):
        """
        If the parameter has been changed, set the appropriate configuration change flags to True.

        :return: -
        """

        self.camera_automation_changed = True
        self.configuration_changed = True

    def camera_trigger_delay_write(self):
        """
        If the parameter has been changed, set the appropriate configuration change flags to True.

        :return: -
        """

        self.configuration_changed = True

    def fig_size_horizontal_write(self):
        """
        If the parameter has been changed, set the appropriate configuration change flags to True.

        :return: -
        """

        self.tesselation_changed = True
        self.configuration_changed = True

    def fig_size_vertical_write(self):
        """
        If the parameter has been changed, set the appropriate configuration change flags to True.

        :return: -
        """

        self.tesselation_changed = True
        self.configuration_changed = True

    def label_font_size_write(self):
        """
        If the parameter has been changed, set the appropriate configuration change flags to True.

        :return: -
        """

        self.tesselation_changed = True
        self.configuration_changed = True

    def label_shift_write(self):
        """
        If the parameter has been changed, set the appropriate configuration change flags to True.

        :return: -
        """

        self.tesselation_changed = True
        self.configuration_changed = True

    def min_autoalign_interval_write(self):
        """
        If the parameter has been changed, set the appropriate configuration change flags to True.

        :return: -
        """

        self.configuration_changed = True

    def max_autoalign_interval_write(self):
        """
        If the parameter has been changed, set the appropriate configuration change flags to True.

        :return: -
        """

        self.configuration_changed = True

    def max_alignment_error_write(self):
        """
        If the parameter has been changed, set the appropriate configuration change flags to True.

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
            # If the tesselation is changed, most of the work done so far has to be repeated.
            # Ask the user if this is really what he/she wants to do.
            if self.tesselation_changed:
                # Ask the user for confirmation.
                quit_msg = "The configuration change will invalidate the videos recorded so far. " \
                           "Do you really want to restart the recording workflow?"
                reply = QtWidgets.QMessageBox.question(self, 'Message', quit_msg,
                                                       QtWidgets.QMessageBox.Yes,
                                                       QtWidgets.QMessageBox.No)
                # Negative reply: Ignore changed inputs and close the editor.
                if reply == QtWidgets.QMessageBox.No:
                    self.reject()

            # Get the input string from the GUI text field.
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

            self.c.conf.set("Telescope", "interface type",
                            str(self.mount_interface_chooser.currentText()))

            input_string = str(self.input_protocol_level.text())
            if Miscellaneous.testint(input_string, 0, 3) is not None:
                self.c.conf.set("Workflow", "protocol level", str(self.input_protocol_level.text()))
                self.c.set_protocol_level()
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
                self.c.conf.set("Workflow", "focus on star", str(self.input_focus_on_star.text()))
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

            if self.ascomeditor_called:
                # If the AscomEditor was called, new parameters are already checked for validity.
                self.c.conf.set("ASCOM", "guiding interval", self.ascomeditor.new_guiding_interval)
                self.c.conf.set("ASCOM", "wait interval", self.ascomeditor.new_wait_interval)
                self.c.conf.set("ASCOM", "pulse guide speed RA",
                                self.ascomeditor.new_pulse_guide_speed_ra)
                self.c.conf.set("ASCOM", "pulse guide speed DE",
                                self.ascomeditor.new_pulse_guide_speed_de)
                self.c.conf.set("ASCOM", "telescope lookup precision",
                                self.ascomeditor.new_telescope_lookup_precision)
                self.c.conf.set('ASCOM', 'telescope driver', self.ascomeditor.new_driver_name)

        # All tests passed successfully, and all parameters have been written to the
        # configuration object. Close the GUI window.
        self.close()

    def reject(self):
        """
        The Cancel button is pressed, discard the changes and close the GUI window.
        :return: -
        """

        self.configuration_changed = False
        self.output_channel_changed = False
        self.telescope_changed = False
        self.camera_automation_changed = False
        self.tesselation_changed = False
        self.close()

    def closeEvent(self, event):
        self.close()
