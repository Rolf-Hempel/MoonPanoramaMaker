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

from ascom_dialog import Ui_AscomDialog
from miscellaneous import Miscellaneous


class AscomConfigurationEditor(QtWidgets.QDialog, Ui_AscomDialog):
    """
    Update the telescope driver info in the configuration object. The interaction with the user is
    through the ascom_dialog.ui gui.

    """

    def __init__(self, configuration, parent=None):
        """
        Read the current camera information from the configuration object and populate the text
        fields of the editor gui.

        :param configuration: object containing parameters set by the user
        """
        QtWidgets.QDialog.__init__(self, parent)
        self.setupUi(self)
        self.c = configuration

        # Read the current ASCOM parameters from the configuration object
        self.new_driver_name = self.c.conf.get('ASCOM', 'telescope driver')
        self.new_guiding_interval = self.c.conf.get('ASCOM', 'guiding interval')
        self.new_wait_interval = self.c.conf.get('ASCOM', 'wait interval')
        self.new_pulse_guide_speed = self.c.conf.get('ASCOM', 'pulse guide speed')
        self.new_telescope_lookup_precision = self.c.conf.get('ASCOM', 'telescope lookup precision')

        # Fill the gui text fields with the current parameters
        self.input_guiding_interval.setText(self.new_guiding_interval)
        self.input_wait_interval.setText(self.new_wait_interval)
        self.input_pulse_guide_speed.setText(self.new_pulse_guide_speed)
        self.input_telescope_lookup_precision.setText(self.new_telescope_lookup_precision)

        # The configuration_changed flag indicates if at least one parameter has been changed by
        # the user. If the telescope driver is changed, driver initialization has to be repeated.
        # In this case the "telescope_changed" flag will be set to True. Initialize both flags to
        # False.
        self.configuration_changed = False
        self.telescope_changed = False

        # Connect changes to the gui text fields with the methods below.
        self.input_guiding_interval.textChanged.connect(self.guiding_interval_write)
        self.input_wait_interval.textChanged.connect(self.wait_interval_write)
        self.input_pulse_guide_speed.textChanged.connect(self.pulse_guide_speed_write)
        self.input_telescope_lookup_precision.textChanged.connect(self.telescope_lookup_precision_write)


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

    def pulse_guide_speed_write(self):
        """
        If the parameter has been changed, set the appropriate configuration change flags to True.

        :return: -
        """

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
            self.new_guiding_interval = str(self.input_guiding_interval.text())
            # Check if the float entered is within the given bounds [0., 3.]. If the return value
            # is None, an error was detected. In this case give an example for a correct value.
            if Miscellaneous.testfloat(self.new_guiding_interval, 0., 3.):
                self.c.conf.set("ASCOM", "guiding interval", self.new_guiding_interval)
            else:
                Miscellaneous.show_input_error("Guiding interval", "0.2")
                return

            # Repeat the same logic for all parameters.
            self.new_wait_interval = str(self.input_wait_interval.text())
            if Miscellaneous.testfloat(self.new_wait_interval, 0., 20.):
                self.c.conf.set("ASCOM", "wait interval", self.new_wait_interval)
            else:
                Miscellaneous.show_input_error("Wait interval", "1.")
                return

            self.input_pulse_guide_speed = str(self.input_pulse_guide_speed.text())
            if Miscellaneous.testfloat(self.input_pulse_guide_speed, 0., 1.):
                self.c.conf.set("ASCOM", "pulse guide speed", self.input_pulse_guide_speed)
            else:
                Miscellaneous.show_input_error("Pulse guide speed", "0.01")
                return

            input_string = str(self.input_telescope_lookup_precision.text())
            if Miscellaneous.testfloat(input_string, 0.1, 10.):
                self.c.conf.set("ASCOM", "telescope lookup precision", input_string)
            else:
                Miscellaneous.show_input_error("Telescope position lookup precision", "0.5")
                return

        # Close the editing gui.
        self.close()

    def reject(self):
        # In case the Cancel button is pressed, discard all changes and close the gui.
        self.configuration_changed = False
        self.close()

    def closeEvent(self, evnt):
        self.close()
