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

from PyQt5 import QtWidgets
from pytz import all_timezones

from camera_configuration_delete import CameraConfigurationDelete
from camera_configuration_editor import CameraConfigurationEditor
from camera_configuration_input import CameraConfigurationInput
from configuration_dialog import Ui_ConfigurationDialog
from miscellaneous import Miscellaneous

basePath = os.path.dirname(os.path.abspath(sys.argv[0]))
sys.path.insert(0, basePath)


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
        # These flags indicate which part of the initialization have to be repeated.
        self.output_channel_changed = False
        self.telescope_changed = False
        self.camera_automation_changed = False
        self.tesselation_changed = False
        # Remember if the ASCOM or INDI configuration editor was called. Changes made by this
        # editor are only applied in the end if the user accepts the changes in the main window.
        self.ascomeditor = None
        self.ascomeditor_called = False
        self.indieditor = None
        self.indieditor_called = False

        # Start filling the text fields of the GUI.
        self.input_longitude.setText(self.c.conf.get("Geographical Position", "longitude"))
        self.input_latitude.setText(self.c.conf.get("Geographical Position", "latitude"))
        self.input_elevation.setText(self.c.conf.get("Geographical Position", "elevation"))
        self.timezone_chooser.addItems(all_timezones)
        self.timezone_chooser.setCurrentIndex(
            all_timezones.index(self.c.conf.get("Geographical Position", "timezone")))

        # Special treatment of available camera models: populate the camera_chooser with list.
        camlist = self.c.get_camera_list()
        self.camera_chooser.addItems(camlist)
        self.camera_chooser.setCurrentIndex(camlist.index(self.c.conf.get("Camera", "name")))

        self.input_ip_address.setText(self.c.conf.get("Camera", "ip address"))

        self.input_focal_length.setText(self.c.conf.get("Telescope", "focal length"))
        # Prepare for alternative telescope interfaces (e.g. INDI).
        interface_list = ["ASCOM", "INDI"]
        self.mount_interface_chooser.addItems(interface_list)
        self.mount_interface_chooser.setCurrentIndex(
            interface_list.index(self.c.conf.get("Telescope", "interface type")))

        protocol_levels = ['0', '1', '2', '3']
        self.protocol_level_chooser.addItems(protocol_levels)
        self.protocol_level_chooser.setCurrentIndex(
            protocol_levels.index(self.c.conf.get("Workflow", "protocol level")))
        self.protocol_to_file_chooser.addItems(
            ["Write the protocol to a file", 'Write the protocol to standard output'])
        self.protocol_to_file_chooser.setCurrentIndex(
            ['True', 'False'].index(self.c.conf.get("Workflow", "protocol to file")))
        self.focus_on_star_chooser.addItems(
            ['Select a star for adjusting the focus', 'Select an area on the moon for focussing'])
        self.focus_on_star_chooser.setCurrentIndex(
            ['True', 'False'].index(self.c.conf.get("Workflow", "focus on star")))
        self.limb_first_chooser.addItems(
            ['Begin at the bright moon limb', 'Begin at the terminator'])
        self.limb_first_chooser.setCurrentIndex(
            ['True', 'False'].index(self.c.conf.get("Workflow", "limb first")))
        self.camera_automation_chooser.addItems(
            ['Trigger FireCapture automatically', 'Trigger the camera manually'])
        self.camera_automation_chooser.setCurrentIndex(
            ['True', 'False'].index(self.c.conf.get("Workflow", "camera automation")))
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

        self.new_ascom_driver_name = self.c.conf.get('ASCOM', 'telescope driver')
        self.new_ascom_guiding_interval = self.c.conf.get('ASCOM', 'guiding interval')
        self.new_ascom_wait_interval = self.c.conf.get('ASCOM', 'wait interval')
        self.new_ascom_pulse_guide_speed_ra = self.c.conf.get('ASCOM', 'pulse guide speed RA')
        self.new_ascom_pulse_guide_speed_de = self.c.conf.get('ASCOM', 'pulse guide speed DE')
        self.new_ascom_telescope_lookup_precision = self.c.conf.get('ASCOM',
                                                                    'telescope lookup precision')

        self.new_indi_server_url = self.c.conf.get('INDI', 'server url')
        self.new_indi_pulse_guide_speed_index = self.c.conf.get('INDI', 'pulse guide speed index')
        self.new_indi_guiding_interval = self.c.conf.get('INDI', 'guiding interval')
        self.new_indi_wait_interval = self.c.conf.get('INDI', 'wait interval')
        self.new_indi_telescope_lookup_precision = self.c.conf.get('INDI',
                                                                   'telescope lookup precision')

        # Connect textChanged signals with methods to update the corresponding parameters.
        self.input_longitude.textChanged.connect(self.longitude_write)
        self.input_latitude.textChanged.connect(self.latitude_write)
        self.input_elevation.textChanged.connect(self.elevation_write)
        self.timezone_chooser.currentIndexChanged.connect(self.timezone_write)

        self.camera_chooser.currentIndexChanged.connect(self.camera_changed)
        self.edit_camera.clicked.connect(self.start_edit_camera_dialog)
        self.new_camera.clicked.connect(self.start_new_camera_dialog)
        self.delete_camera.clicked.connect(self.start_delete_camera_dialog)

        self.input_ip_address.textChanged.connect(self.ip_address_write)

        self.input_focal_length.textChanged.connect(self.focal_length_write)
        self.mount_interface_chooser.currentIndexChanged.connect(self.mount_interface_changed)
        if str(self.mount_interface_chooser.currentText()) == "ASCOM":
            self.configure_mount_interface.clicked.connect(self.start_ascom_dialog)
        elif str(self.mount_interface_chooser.currentText()) == "INDI":
            self.configure_mount_interface.clicked.connect(self.start_indi_dialog)

        self.protocol_level_chooser.currentIndexChanged.connect(self.protocol_level_write)
        self.protocol_to_file_chooser.currentIndexChanged.connect(self.protocol_to_file_write)
        self.focus_on_star_chooser.currentIndexChanged.connect(self.focus_on_star_write)
        self.limb_first_chooser.currentIndexChanged.connect(self.limb_first_write)
        self.camera_automation_chooser.currentIndexChanged.connect(self.camera_automation_write)
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
        editor = CameraConfigurationEditor(self.c, camera_name)
        editor.exec_()
        if editor.configuration_changed:
            self.tesselation_changed = True
            self.configuration_changed = True

    def start_new_camera_dialog(self):
        """
        The "Input camera" button is clicked: Open the input camera dialog.

        :return: -
        """

        inputeditor = CameraConfigurationInput(self.c)
        # Start the input GUI.
        inputeditor.exec_()
        # Check if new parameters have been entered.
        if inputeditor.configuration_changed:
            # Mark the configuration object as changed.
            self.configuration_changed = True
            # Update the list of available cameras
            camlist = self.c.get_camera_list()
            # Update the camera chooser to contain the extended list of camera names.
            self.camera_chooser.clear()
            self.camera_chooser.addItems(camlist)
            # Set the current chooser entry to the new camera model.
            self.camera_chooser.setCurrentIndex(camlist.index(self.c.conf.get("Camera", "name")))

    def start_delete_camera_dialog(self):
        """
        The "Delete camera" button has been clicked: Open the delete camera dialog.

        :return: -
        """

        deleteeditor = CameraConfigurationDelete()
        # Start the GUI.
        deleteeditor.exec_()
        # Check if the selected camera is really deleted.
        if deleteeditor.configuration_changed:
            # Mark the configuration object as changed.
            self.configuration_changed = True
            # Remove the section with parameters of the deleted camera model from configuration
            # object.
            self.c.conf.remove_section('Camera ' + str(self.camera_chooser.currentText()))
            # Update the list of available cameras
            camlist = self.c.get_camera_list()
            # Update the camera chooser to contain the extended list of camera names.
            self.camera_chooser.clear()
            self.camera_chooser.addItems(camlist)
            # The current camera is deleted, set the index of the chooser to 0 (default).
            self.camera_chooser.setCurrentIndex(0)

    def ip_address_write(self):
        """
        If the parameter has been changed, set the appropriate configuration change flags
        to True.

        :return: -
        """

        self.camera_automation_changed = True
        self.configuration_changed = True

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
            try:
                self.configure_mount_interface.clicked.disconnect()
            except:
                pass
            self.configure_mount_interface.clicked.connect(self.start_ascom_dialog)
        elif str(self.mount_interface_chooser.currentText()) == "INDI":
            try:
                self.configure_mount_interface.clicked.disconnect()
            except:
                pass
            self.configure_mount_interface.clicked.connect(self.start_indi_dialog)

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
                                                      "Most likely the ASCOM platform is not "
                                                      "installed on this computer.\n\nIf this is "
                                                      "a Linux system, "
                                                      "there might be an INDI client available. "
                                                      "In this case, try to use 'INDI' instead of "
                                                      "'ASCOM'.")
            return

        self.ascomeditor = AscomConfigurationEditor(self.c, self.new_ascom_driver_name,
                                                    self.new_ascom_guiding_interval,
                                                    self.new_ascom_wait_interval,
                                                    self.new_ascom_pulse_guide_speed_ra,
                                                    self.new_ascom_pulse_guide_speed_de,
                                                    self.new_ascom_telescope_lookup_precision)
        # Start the GUI.
        self.ascomeditor.exec_()

        # Remember that the AscomConfigurationEditor was invoked.
        self.ascomeditor_called = True
        # Check if the configuration has changed.
        if self.ascomeditor.configuration_changed:
            # Mark the configuration object as changed.
            self.configuration_changed = True
            # Copy back the current gui values.
            self.new_ascom_driver_name = self.ascomeditor.new_driver_name
            self.new_ascom_guiding_interval = str(self.ascomeditor.input_guiding_interval.text())
            self.new_ascom_wait_interval = str(self.ascomeditor.input_wait_interval.text())
            self.new_ascom_pulse_guide_speed_ra = str(
                self.ascomeditor.input_pulse_guide_speed_ra.text())
            self.new_ascom_pulse_guide_speed_de = str(
                self.ascomeditor.input_pulse_guide_speed_de.text())
            self.new_ascom_telescope_lookup_precision = str(
                self.ascomeditor.input_telescope_lookup_precision.text())
        if self.ascomeditor.telescope_changed:
            # Mark the telescope driver as changed.
            self.telescope_changed = True

    def start_indi_dialog(self):
        """
        The "configure" button has been clicked for the INDI telescope interface:
        Open the INDI dialog.

        :return: -
        """

        try:
            # PyIndi is only available on Linux and MacOS. On Windows systems, do nothing.
            import PyIndi
        except ImportError:
            Miscellaneous.show_detailed_error_message("The INDI interface does not seem to work.",
                                                      "Most likely PyIndi is not installed on "
                                                      "this computer.\n\nIf this is a Windows "
                                                      "system, "
                                                      "there might be an ASCOM client available. "
                                                      "In this case, try to use 'ASCOM' instead "
                                                      "of 'INDI'.")
            return

        from indi_configuration_editor import IndiConfigurationEditor

        self.indieditor = IndiConfigurationEditor(self.c, self.new_indi_server_url,
                                                  self.new_indi_pulse_guide_speed_index,
                                                  self.new_indi_guiding_interval,
                                                  self.new_indi_wait_interval,
                                                  self.new_indi_telescope_lookup_precision)
        # Start the GUI.
        self.indieditor.exec_()

        # Remember that the INDIConfigurationEditor was invoked.
        self.indieditor_called = True
        # Check if the configuration has changed.
        if self.indieditor.configuration_changed:
            # Mark the configuration object as changed.
            self.configuration_changed = True
            # Copy back the current gui values.
            self.new_indi_server_url = str(self.indieditor.input_indi_server_url.text())
            self.new_indi_pulse_guide_speed_index = str(
                self.indieditor.pulse_guide_speed_chooser.currentIndex())
            self.new_indi_guiding_interval = str(self.indieditor.input_guiding_interval.text())
            self.new_indi_wait_interval = str(self.indieditor.input_wait_interval.text())
            self.new_indi_telescope_lookup_precision = str(
                self.indieditor.input_telescope_lookup_precision.text())
        if self.indieditor.telescope_changed:
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

            self.c.conf.set("Geographical Position", "timezone",
                            self.timezone_chooser.currentText())

            input_string = str(self.input_ip_address.text())
            if Miscellaneous.testipaddress(input_string):
                self.c.conf.set("Camera", "ip address", input_string)
            else:
                Miscellaneous.show_input_error("IP address to access FireCapture", "192.168.0.34")
                return

            input_string = str(self.input_focal_length.text())
            if Miscellaneous.testfloat(input_string, 0., 100000.):
                self.c.conf.set("Telescope", "focal length", input_string)
            else:
                Miscellaneous.show_input_error("Focal length", "4670.")
                return

            self.c.conf.set("Telescope", "interface type",
                            str(self.mount_interface_chooser.currentText()))
            self.c.conf.set("Workflow", "protocol level", self.protocol_level_chooser.currentText())
            self.c.set_protocol_level()
            self.c.conf.set("Workflow", "protocol to file",
                            ['True', 'False'][self.protocol_to_file_chooser.currentIndex()])
            self.c.conf.set("Workflow", "focus on star",
                            ['True', 'False'][self.focus_on_star_chooser.currentIndex()])
            self.c.conf.set("Workflow", "limb first",
                            ['True', 'False'][self.limb_first_chooser.currentIndex()])
            self.c.conf.set("Workflow", "camera automation",
                            ['True', 'False'][self.camera_automation_chooser.currentIndex()])

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
                self.c.conf.set("ASCOM", "guiding interval", self.new_ascom_guiding_interval)
                self.c.conf.set("ASCOM", "wait interval", self.new_ascom_wait_interval)
                self.c.conf.set("ASCOM", "pulse guide speed RA",
                                self.new_ascom_pulse_guide_speed_ra)
                self.c.conf.set("ASCOM", "pulse guide speed DE",
                                self.new_ascom_pulse_guide_speed_de)
                self.c.conf.set("ASCOM", "telescope lookup precision",
                                self.new_ascom_telescope_lookup_precision)
                self.c.conf.set('ASCOM', 'telescope driver', self.ascomeditor.new_driver_name)

            if self.indieditor_called:
                # If the IndiEditor was called, copy back the current new values.
                self.c.conf.set("INDI", "server url", self.new_indi_server_url)
                self.c.conf.set("INDI", "pulse guide speed index",
                                self.new_indi_pulse_guide_speed_index)
                self.c.conf.set("INDI", "guiding interval", self.new_indi_guiding_interval)
                self.c.conf.set("INDI", "wait interval", self.new_indi_wait_interval)
                self.c.conf.set("INDI", "telescope lookup precision",
                                self.new_indi_telescope_lookup_precision)

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
