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

class TelescopeException(Exception):
    """
    Base exception for errors associated with the telescope interface.
    """
    pass


class ASCOMException(TelescopeException):
    """
    Base exception for errors associated with accessing the telescope driver via ASCOM.
    """
    pass


class ASCOMConnectException(ASCOMException):
    """
    Exception raised while connecting to the ASCOM telescope driver.
    """
    pass


class ASCOMPropertyException(ASCOMException):
    """
    Exception raised because the ASCOM telescope driver misses at least one required property.
    Look at the returned message string for details.
    """
    pass
