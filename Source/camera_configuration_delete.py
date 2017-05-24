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

from PyQt4 import QtGui

from camera_delete_dialog import Ui_Dialog


class CameraConfigurationDelete(QtGui.QDialog, Ui_Dialog):
    """
    This class implements the activities executed when a camera configuration is to be deleted
    from the list of available models. In particular, the configuration is to be marked as changed.
    
    """

    def __init__(self, parent=None):
        QtGui.QDialog.__init__(self, parent)
        self.setupUi(self)
        self.configuration_changed = False

    def accept(self):
        self.configuration_changed = True
        self.close()

    def reject(self):
        self.configuration_changed = False
        self.close()

    def closeEvent(self, evnt):
        self.close()
