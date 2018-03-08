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
from indi_dialog import Ui_INDIDialog
from miscellaneous import Miscellaneous
import os
import webbrowser


class IndiConfigurationEditor(QtWidgets.QDialog, Ui_INDIDialog):
    """
    Update the telescope driver info in the configuration object. The interaction with the user is
    through the ascom_dialog.ui gui.

    """

    def __init__(self, configuration, new_indi_server_url, new_indi_pulse_guide_speed_index,
                 new_indi_guiding_interval, new_indi_wait_interval,
                 new_indi_telescope_lookup_precision, parent=None):
        """
        Read the current camera information from the configuration object and populate the text
        fields of the editor gui.

        :param configuration: object containing parameters set by the user
        :param new_indi_server_url: URL of the INDI server process
        :param new_indi_pulse_guide_speed_index: index of the pulse guide speed chooser combobox
        :param new_indi_guiding_interval: duration of guiding pulses (sec.)
        :param new_indi_wait_interval: time between tests for current telescope pointing (sec.)
        :param new_indi_telescope_lookup_precision: maximum difference (arc sec.) between two
                                                    consecutive position lookups after a "slew to"
        :param parent: parent class
        """

        QtWidgets.QDialog.__init__(self, parent)
        self.setupUi(self)
        self.c = configuration

        # Fill the gui text fields with the current parameters
        self.input_indi_server_url.setText(new_indi_server_url)
        guide_speeds = ["SLEW_GUIDE", "SLEW_CENTERING", "SLEW_FIND", "SLEW_MAX"]
        self.pulse_guide_speed_chooser.addItems(guide_speeds)
        self.pulse_guide_speed_chooser.setCurrentIndex(int(new_indi_pulse_guide_speed_index))
        self.input_guiding_interval.setText(new_indi_guiding_interval)
        self.input_wait_interval.setText(new_indi_wait_interval)
        self.input_telescope_lookup_precision.setText(new_indi_telescope_lookup_precision)

        # The configuration_changed flag indicates if at least one parameter has been changed by
        # the user. If the telescope driver is changed, driver initialization has to be repeated.
        # In this case the "telescope_changed" flag will be set to True. Initialize both flags to
        # False.
        self.configuration_changed = False
        self.telescope_changed = False

        # Connect changes to the gui text fields with the methods below.
        self.configure_server.clicked.connect(self.open_indi_manager)
        self.input_indi_server_url.textChanged.connect(self.indi_server_url_write)
        self.pulse_guide_speed_chooser.currentIndexChanged.connect(self.pulse_guide_speed_write)
        self.input_guiding_interval.textChanged.connect(self.guiding_interval_write)
        self.input_wait_interval.textChanged.connect(self.wait_interval_write)
        self.input_telescope_lookup_precision.textChanged.connect(
            self.telescope_lookup_precision_write)

    def open_indi_manager(self):
        # This must be extended for the case that the indi-web server does not run on 'localhost'.
        try:
            os.system('pgrep indi-web > /dev/null || ( indi-web & )')
        except:
            if self.c.protocol_level > 0:
                Miscellaneous.protocol("Unable to start the indi-web manager. Please check"
                                       " the INDI installation.")

        # Check if the given URL of the INDI server is valid.
        if Miscellaneous.testipaddress(str(self.input_indi_server_url.text())):
            try:
                webbrowser.open("http://" + str(self.input_indi_server_url.text()) + ":8624")
            except:
                if self.c.protocol_level > 0:
                    Miscellaneous.protocol("Unable to access the indi-web manager. Please check"
                                           " the INDI installation.")
            self.configuration_changed = True
            self.telescope_changed = True
        else:
            Miscellaneous.show_detailed_error_message("Invalid URL entered.",
                                                      "The URL of the INDI server is not correct. "
                                                      "It must be eigher 'localhost' or the IP number "
                                                      "of the system where the INDI "
                                                      "server is executed. (e.g. '192.168.0.2') ")

    # The following methods are invoked if a text field is changed by the user.
    def indi_server_url_write(self):
        """
        If the parameter has been changed, set the appropriate configuration change flags to True.

        :return: -
        """

        self.telescope_changed = True
        self.configuration_changed = True

    def pulse_guide_speed_write(self):
        """
        If the parameter has been changed, set the appropriate configuration change flags to True.

        :return: -
        """

        self.telescope_changed = True
        self.configuration_changed = True

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
            # Check if the URL entered is valid. If it is not, give an example of a valid URL.
            # The URL has been copied to "self.new_indi_server_url" in method "indi_server_url_write"
            # already because it might have been needed by "open_indi_manager".
            if not Miscellaneous.testipaddress(str(self.input_indi_server_url.text())):
                Miscellaneous.show_input_error("URL of the INDI server", "'localhost'")
                return

            # Check if the float entered is within the given bounds [0., 3.]. If the return value
            # is None, an error was detected. In this case give an example for a correct value.
            if not Miscellaneous.testfloat(str(self.input_guiding_interval.text()), 0., 3.):
                Miscellaneous.show_input_error("Guide pulse duration", "0.5")
                return

            # Repeat the same logic for "Wait interval".
            if not Miscellaneous.testfloat(str(self.input_wait_interval.text()), 0., 20.):
                Miscellaneous.show_input_error("Wait interval", "1.")
                return

            if not Miscellaneous.testfloat(str(self.input_telescope_lookup_precision.text()), 0.1,
                                           10.):
                Miscellaneous.show_input_error("Telescope position lookup precision", "0.5")
                return

        # Close the editing gui.
        self.close()

    def reject(self):
        # In case the Cancel button is pressed, discard all changes and close the gui.
        self.configuration_changed = False
        self.telescope_changed = False
        self.close()

    def closeEvent(self, evnt):
        self.close()
