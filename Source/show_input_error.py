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

from input_error_dialog import Ui_InputErrorDialog


class ShowInputError(QtWidgets.QDialog, Ui_InputErrorDialog):
    """
    This class implements an InputErrorDialog window. It prompts the user to correct the input
    of a parameter and gives a correctly formatted example.
    
    """

    def __init__(self, parameter_string, example_string, parent=None):
        """
        Open the window and show the message.
        
        :param parameter_string: string representation of the parameter
        :param example_string: example for a correctly formatted parameter
        """

        QtWidgets.QDialog.__init__(self, parent)
        self.setupUi(self)
        self.message.setText(
            "Invalid input for parameter: \n" + parameter_string + "\n\nValid input example: \n"
            + example_string)
        self.okbutton.clicked.connect(self.accept)

    def accept(self):
        self.close()

    def closeEvent(self, evnt):
        self.close()
