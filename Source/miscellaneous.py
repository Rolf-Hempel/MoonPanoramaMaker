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

from math import sin, cos
from show_input_error import ShowInputError


class Miscellaneous():
    @staticmethod
    def testfloat(string, lower_bound, upper_bound):
        try:
            fl = float(string)
            if lower_bound <= fl <= upper_bound:
                return fl
        except:
            pass
        return None

    @staticmethod
    def testint(string, lower_bound, upper_bound):
        try:
            i = int(string)
            if lower_bound <= i <= upper_bound:
                return i
        except:
            pass
        return None

    @staticmethod
    def testbool(string):
        if "True" in string:
            return True
        elif "False" in string:
            return False
        else:
            return None

    @staticmethod
    def show_input_error(parameter_string, example_string):
        inputerror = ShowInputError(parameter_string, example_string)
        inputerror.exec_()

    @staticmethod
    def rotate(pos_angle, de_center, scale_factor, flip_x, flip_y, x, y):
        dx = x*scale_factor*flip_x
        dy = y*scale_factor*flip_y
        delta_ra_rot = ((dy * sin(pos_angle) - dx * cos(pos_angle)) /
                        cos(de_center))
        delta_de_rot = (dx * sin(pos_angle) + dy * cos(pos_angle))
        return [delta_ra_rot, delta_de_rot]


if __name__ == "__main__":
    s = '    False   '
    result = Miscellaneous.testfloat(s, 0., 50.)
    print "string = ", s, ", testfloat: ", result
    if result is None:
        print "wrong input"
    else:
        print "correct input"
    result = Miscellaneous.testint(s, 0, 100)
    print "string = ", s, ", testint: ", result
    if result is None:
        print "wrong input"
    else:
        print "correct input"
    result = Miscellaneous.testbool(s)
    print "string = ", s, ", testbool: ", result
    if result is None:
        print "wrong input"
    else:
        print "correct input"
