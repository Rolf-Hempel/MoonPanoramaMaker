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

import win32com.client
from PyQt5 import QtWidgets
from ascom_dialog import Ui_AscomDialog
from miscellaneous import Miscellaneous


class AscomConfigurationEditor(QtWidgets.QDialog, Ui_AscomDialog):
    """
    Update the telescope driver info in the configuration object. The interaction with the user is
    through the ascom_dialog.ui gui.

    """

    def __init__(self, configuration, new_ascom_driver_name, new_ascom_guiding_interval,
                 new_ascom_wait_interval, new_ascom_pulse_guide_speed_ra,
                 new_ascom_pulse_guide_speed_de, new_ascom_telescope_lookup_precision, parent=None):
        """
        Read the current camera information from the configuration object and populate the text
        fields of the editor gui.

        :param configuration: object containing parameters set by the user
        :param new_ascom_driver_name: name of the ASCOM telescope driver
        :param new_ascom_guiding_interval: duration of guiding pulses (sec.)
        :param new_ascom_wait_interval: time between tests for current telescope pointing (sec.)
        :param new_ascom_pulse_guide_speed_ra: pulse guide speed in RA (in deg./sec.)
        :param new_ascom_pulse_guide_speed_de: pulse guide speed in DE (in deg./sec.)
        :param new_ascom_telescope_lookup_precision: maximum difference (arc sec.) between two
                                                    consecutive position lookups after a "slew to"
        :param parent: parent class
        """

        QtWidgets.QDialog.__init__(self, parent)
        self.setupUi(self)
        self.c = configuration

        # Special case driver_name: copy input value in instance variables, to be used by method
        # "open_ascom_chooser".
        self.new_driver_name = self.old_driver_name = new_ascom_driver_name
        # Fill the gui text fields with the current parameters
        self.input_guiding_interval.setText(new_ascom_guiding_interval)
        self.input_wait_interval.setText(new_ascom_wait_interval)
        self.input_pulse_guide_speed_ra.setText(new_ascom_pulse_guide_speed_ra)
        self.input_pulse_guide_speed_de.setText(new_ascom_pulse_guide_speed_de)
        self.input_telescope_lookup_precision.setText(new_ascom_telescope_lookup_precision)

        # The configuration_changed flag indicates if at least one parameter has been changed by
        # the user. If the telescope driver is changed, driver initialization has to be repeated.
        # In this case the "telescope_changed" flag will be set to True. Initialize both flags to
        # False.
        self.configuration_changed = False
        self.telescope_changed = False

        # Connect changes to the gui text fields with the methods below.
        self.select_driver.clicked.connect(self.open_ascom_chooser)
        self.input_guiding_interval.textChanged.connect(self.guiding_interval_write)
        self.input_wait_interval.textChanged.connect(self.wait_interval_write)
        self.input_pulse_guide_speed_ra.textChanged.connect(self.pulse_guide_speed_ra_write)
        self.input_pulse_guide_speed_de.textChanged.connect(self.pulse_guide_speed_de_write)
        self.input_telescope_lookup_precision.textChanged.connect(
            self.telescope_lookup_precision_write)

    def open_ascom_chooser(self):
        try:
            x = win32com.client.Dispatch("ASCOM.Utilities.Chooser")
            x.DeviceType = 'Telescope'
            driver_name = x.Choose(self.new_driver_name)
            if driver_name != "":
                self.new_driver_name = driver_name
        except:
            if self.c.protocol_level > 0:
                Miscellaneous.protocol("Unable to access the ASCOM telescope chooser. Please check"
                                       " the ASCOM platform installation.")
            Miscellaneous.show_detailed_error_message("Unable to access the ASCOM telescope "
                                                      "chooser", "Is the ASCOM Platform "
                                                                 "installed on this "
                                                                 "computer? Please check the "
                                                                 "installation.")

    # The following methods are invoked if a text field is changed by the user.
    def guiding_interval_write(self):
        """
        If the parameter has been changed, set the appropriate configuration change flags to True.

        :return: -
        """

        self.configuration_changed = True

    def wait_interval_write(self):
        """
        If the parameter has been changed, set the appropriate configuration change flags to True.

        :return: -
        """

        self.configuration_changed = True

    def pulse_guide_speed_ra_write(self):
        """
        If the parameter has been changed, set the appropriate configuration change flags to True.

        :return: -
        """

        self.telescope_changed = True
        self.configuration_changed = True

    def pulse_guide_speed_de_write(self):
        """
        If the parameter has been changed, set the appropriate configuration change flags to True.

        :return: -
        """

        self.telescope_changed = True
        self.configuration_changed = True

    def telescope_lookup_precision_write(self):
        """
        If the parameter has been changed, set the appropriate configuration change flags to True.

        :return: -
        """

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
            new_guiding_interval = str(self.input_guiding_interval.text())
            # Check if the float entered is within the given bounds [0., 3.]. If the return value
            # is None, an error was detected. In this case give an example for a correct value.
            if not Miscellaneous.testfloat(new_guiding_interval, 0., 3.):
                Miscellaneous.show_input_error("Guiding interval", "0.2")
                return

            # Repeat the same logic for all parameters.
            new_wait_interval = str(self.input_wait_interval.text())
            if not Miscellaneous.testfloat(new_wait_interval, 0., 20.):
                Miscellaneous.show_input_error("Wait interval", "1.")
                return

            new_pulse_guide_speed_ra = str(self.input_pulse_guide_speed_ra.text())
            if not Miscellaneous.testfloat(new_pulse_guide_speed_ra, 0., 0.1):
                Miscellaneous.show_input_error("Pulse guide speed", "0.001")
                return

            new_pulse_guide_speed_de = str(self.input_pulse_guide_speed_de.text())
            if not Miscellaneous.testfloat(new_pulse_guide_speed_de, 0., 0.1):
                Miscellaneous.show_input_error("Pulse guide speed", "0.001")
                return

            new_telescope_lookup_precision = str(self.input_telescope_lookup_precision.text())
            if not Miscellaneous.testfloat(new_telescope_lookup_precision, 0.1, 10.):
                Miscellaneous.show_input_error("Telescope position lookup precision", "0.5")
                return

        # Special case driver_name: This one is handled by a gui of the ASCOM platform.
        if self.new_driver_name != self.old_driver_name:
            self.configuration_changed = True
            self.telescope_changed = True

        # Close the editing gui.
        self.close()

    def reject(self):
        # In case the Cancel button is pressed, discard all changes and close the gui.
        # Reject the change to the driver name.
        self.new_driver_name = self.old_driver_name
        self.configuration_changed = False
        self.telescope_changed = False
        self.close()

    def closeEvent(self, evnt):
        self.close()
