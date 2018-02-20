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

import sys
from math import sin, cos
from datetime import datetime
from PyQt5 import QtWidgets

from show_input_error import ShowInputError


class Miscellaneous():
    """
    This class provides static methods for various auxiliary purposes.
    
    """

    @staticmethod
    def protocol(string):
        print(str(datetime.now())[11:21], string)
        sys.stdout.flush()

    @staticmethod
    def testfloat(string, lower_bound, upper_bound):
        """
        Test if a floating point parameter is within given bounds.
        
        :param string: string representation of the parameter
        :param lower_bound: lower bound of allowed interval
        :param upper_bound: upper bound of allowed interval
        :return: the parameter converted to float, if okay. Else return None.
        """

        try:
            fl = float(string)
            if lower_bound <= fl <= upper_bound:
                return fl
        except:
            pass
        return None

    @staticmethod
    def testint(string, lower_bound, upper_bound):
        """
        Test if an integer parameter is within given bounds.

        :param string: string representation of the parameter
        :param lower_bound: lower bound of allowed interval
        :param upper_bound: upper bound of allowed interval
        :return: the parameter converted to int, if okay. Else return None.
        """

        try:
            i = int(string)
            if lower_bound <= i <= upper_bound:
                return i
        except:
            pass
        return None

    @staticmethod
    def testbool(string):
        """
        Test if the string repreentation of a boolean parameter contains "True" or "False".

        :param string: string representation of the parameter
        :return: the parameter converted to boolean, if okay. Else return None.
        """

        if "True" in string:
            return True
        elif "False" in string:
            return False
        else:
            return None

    @staticmethod
    def show_input_error(parameter_string, example_string):
        """
        Open a window which shows an invalid input parameter together with a valid example.
        
        :param parameter_string: string representation of the invalid parameter
        :param example_string: example string showing a valid value for this parameter
        :return: -
        """

        inputerror = ShowInputError(parameter_string, example_string)
        inputerror.exec_()

    @staticmethod
    def show_detailed_error_message(message, details):
        msg = QtWidgets.QMessageBox()
        msg.setIcon(QtWidgets.QMessageBox.Warning)
        msg.setText(message)
        msg.setWindowTitle(" ")
        msg.setDetailedText(details)
        msg.setStandardButtons(QtWidgets.QMessageBox.Ok)
        msg.exec_()

    @staticmethod
    def rotate(pos_angle, de_center, scale_factor, flip_x, flip_y, x, y):
        """
        Rotate scale and mirror-reverse vector (x,y) into (diff_RA, diff_DE). The x axis is assumed
        to point to the right, the y axis upwards (as used in class TileConstructor). If the x / and
        y axes are oriented differently, set parameters flip_x, flip_y accordingly.
        
        :param pos_angle: angle between origin and target coordinate systems (counterclockwise)
        :param de_center: declination (used for approximate correction of RA displacement)
        :param scale_factor: scale factor between origin and target coordinate systems
        :param flip_x: +1. if x axis is pointing to the right, -1. otherwise
        :param flip_y: +1. if y axis is pointing to the right, -1. otherwise
        :param x: input coordinate x
        :param y: input coordinate y
        :return: tuple with equatorial displacements (diff_RA, diff_DE)
        """

        # Scale and flip x,y coordinates.
        dx = x * scale_factor * flip_x
        dy = y * scale_factor * flip_y
        # Perform the rotation by angle pos_angle, correct diff_RA for declination angle.
        delta_ra_rot = ((dy * sin(pos_angle) - dx * cos(pos_angle)) / cos(de_center))
        delta_de_rot = (dx * sin(pos_angle) + dy * cos(pos_angle))
        return [delta_ra_rot, delta_de_rot]


if __name__ == "__main__":
    s = '    False   '
    result = Miscellaneous.testfloat(s, 0., 50.)
    print("string = ", s, ", testfloat: ", result)
    if result is None:
        print("wrong input")
    else:
        print("correct input")
    result = Miscellaneous.testint(s, 0, 100)
    print("string = ", s, ", testint: ", result)
    if result is None:
        print("wrong input")
    else:
        print("correct input")
    result = Miscellaneous.testbool(s)
    print("string = ", s, ", testbool: ", result)
    if result is None:
        print("wrong input")
    else:
        print("correct input")
