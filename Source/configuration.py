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
import os.path
import ConfigParser
from PyQt4 import QtGui
from configuration_editor import ConfigurationEditor


class Configuration:
    def __init__(self):
        self.version = "MoonPanoramaMaker 0.9.3"
        self.minimum_drift_seconds = 600.

        self.conf = ConfigParser.ConfigParser()

        self.protocol = True

        home = os.path.expanduser("~")
        self.config_filename = home + "\\.MoonPanoramaMaker.ini"
        self.protocol_filename = home + "\\MoonPanoramaMaker.log"
        if os.path.isfile(self.config_filename):
            self.conf.read(self.config_filename)
            self.configuration_read = True
        else:
            # Code to set config info
            self.configuration_read = False
            self.conf.add_section('Hidden Parameters')
            self.conf.set('Hidden Parameters', 'version ', self.version)
            self.conf.set('Hidden Parameters', 'main window x0', '350')
            self.conf.set('Hidden Parameters', 'main window y0', '50')
            self.conf.set('Hidden Parameters', 'tile window x0', '50')
            self.conf.set('Hidden Parameters', 'tile window y0', '50')

            self.conf.add_section('Geographical Position')
            self.conf.set('Geographical Position', 'longitude', '7.39720')
            self.conf.set('Geographical Position', 'latitude', '50.69190')
            self.conf.set('Geographical Position', 'elevation', '250')
            self.conf.set('Geographical Position', 'timezone', 'Europe/Berlin')

            self.conf.add_section('Camera')
            self.conf.set('Camera', 'name', 'ZWO ASI120MM-S')

            self.conf.add_section('Telescope')
            self.conf.set('Telescope', 'focal length', '2800.')

            self.conf.add_section('Tile Visualization')
            self.conf.set('Tile Visualization', 'figsize horizontal', '8.5')
            self.conf.set('Tile Visualization', 'figsize vertical', '8.5')
            self.conf.set('Tile Visualization', 'label fontsize', '11')
            self.conf.set('Tile Visualization', 'label shift', '0.8')

            self.conf.add_section('Workflow')
            self.conf.set('Workflow', 'protocol', 'True')
            self.conf.set('Workflow', 'protocol to file', 'True')
            self.conf.set('Workflow', 'camera automation', 'False')
            self.conf.set('Workflow', 'limb first', 'False')
            self.conf.set('Workflow', 'camera trigger delay', '3.')

            self.conf.add_section('ASCOM')
            self.conf.set('ASCOM', 'chooser', 'ASCOM.Utilities.Chooser')
            self.conf.set('ASCOM', 'hub', 'POTH.Telescope')
            self.conf.set('ASCOM', 'guiding interval', '0.2')
            self.conf.set('ASCOM', 'wait interval', '1.')
            self.conf.set('ASCOM', 'polling interval', '0.1')
            self.conf.set('ASCOM', 'telescope lookup precision', '0.5')

            self.conf.add_section('Camera ZWO ASI120MM-S')
            self.conf.set('Camera ZWO ASI120MM-S', 'name', 'ZWO ASI120MM-S')
            self.conf.set('Camera ZWO ASI120MM-S', 'pixel size', '0.00375')
            self.conf.set('Camera ZWO ASI120MM-S', 'pixel horizontal', '1280')
            self.conf.set('Camera ZWO ASI120MM-S', 'pixel vertical', '960')
            self.conf.set('Camera ZWO ASI120MM-S', 'external margin pixel', '300')
            self.conf.set('Camera ZWO ASI120MM-S', 'tile overlap pixel', '200')

            self.conf.add_section('Camera ZWO ASI174MC')
            self.conf.set('Camera ZWO ASI174MC', 'name', 'ZWO ASI174MC')
            self.conf.set('Camera ZWO ASI174MC', 'pixel size', '0.00586')
            self.conf.set('Camera ZWO ASI174MC', 'pixel horizontal', '1936')
            self.conf.set('Camera ZWO ASI174MC', 'pixel vertical', '1216')
            self.conf.set('Camera ZWO ASI174MC', 'external margin pixel', '200')
            self.conf.set('Camera ZWO ASI174MC', 'tile overlap pixel', '100')

            self.conf.add_section('Camera ZWO ASI178MC')
            self.conf.set('Camera ZWO ASI178MC', 'name', 'ZWO ASI178MC')
            self.conf.set('Camera ZWO ASI178MC', 'pixel size', '0.0024')
            self.conf.set('Camera ZWO ASI178MC', 'pixel horizontal', '3096')
            self.conf.set('Camera ZWO ASI178MC', 'pixel vertical', '2080')
            self.conf.set('Camera ZWO ASI178MC', 'external margin pixel', '550')
            self.conf.set('Camera ZWO ASI178MC', 'tile overlap pixel', '250')

            self.conf.add_section('Camera ZWO ASI185MC')
            self.conf.set('Camera ZWO ASI185MC', 'name', 'ZWO ASI185MC')
            self.conf.set('Camera ZWO ASI185MC', 'pixel size', '0.00375')
            self.conf.set('Camera ZWO ASI185MC', 'pixel horizontal', '1944')
            self.conf.set('Camera ZWO ASI185MC', 'pixel vertical', '1224')
            self.conf.set('Camera ZWO ASI185MC', 'external margin pixel', '300')
            self.conf.set('Camera ZWO ASI185MC', 'tile overlap pixel', '150')

            self.conf.add_section('Camera ZWO ASI224MC')
            self.conf.set('Camera ZWO ASI224MC', 'name', 'ZWO ASI224MC')
            self.conf.set('Camera ZWO ASI224MC', 'pixel size', '0.00375')
            self.conf.set('Camera ZWO ASI224MC', 'pixel horizontal', '1304')
            self.conf.set('Camera ZWO ASI224MC', 'pixel vertical', '976')
            self.conf.set('Camera ZWO ASI224MC', 'external margin pixel', '300')
            self.conf.set('Camera ZWO ASI224MC', 'tile overlap pixel', '150')

            self.conf.add_section('Camera Celestron Skyris 274C')
            self.conf.set('Camera Celestron Skyris 274C', 'name', 'Celestron Skyris 274C')
            self.conf.set('Camera Celestron Skyris 274C', 'pixel size', '0.0044')
            self.conf.set('Camera Celestron Skyris 274C', 'pixel horizontal', '1600')
            self.conf.set('Camera Celestron Skyris 274C', 'pixel vertical', '1200')
            self.conf.set('Camera Celestron Skyris 274C', 'external margin pixel', '250')
            self.conf.set('Camera Celestron Skyris 274C', 'tile overlap pixel', '150')

            self.conf.add_section('Camera Celestron Skyris 445M')
            self.conf.set('Camera Celestron Skyris 445M', 'name', 'Celestron Skyris 445M')
            self.conf.set('Camera Celestron Skyris 445M', 'pixel size', '0.00375')
            self.conf.set('Camera Celestron Skyris 445M', 'pixel horizontal', '1280')
            self.conf.set('Camera Celestron Skyris 445M', 'pixel vertical', '960')
            self.conf.set('Camera Celestron Skyris 445M', 'external margin pixel', '300')
            self.conf.set('Camera Celestron Skyris 445M', 'tile overlap pixel', '150')

            self.conf.add_section('Camera Celestron Skyris 618M')
            self.conf.set('Camera Celestron Skyris 618M', 'name', 'Celestron Skyris 618M')
            self.conf.set('Camera Celestron Skyris 618M', 'pixel size', '0.0056')
            self.conf.set('Camera Celestron Skyris 618M', 'pixel horizontal', '640')
            self.conf.set('Camera Celestron Skyris 618M', 'pixel vertical', '480')
            self.conf.set('Camera Celestron Skyris 618M', 'external margin pixel', '200')
            self.conf.set('Camera Celestron Skyris 618M', 'tile overlap pixel', '100')

            self.copy_camera_configuration(self.conf.get('Camera', 'name'))

    def set_protocol_flag(self):
        self.protocol = self.conf.getboolean('Workflow', 'protocol')

    def get_camera_list(self):
        camera_list = []
        for name in self.conf.sections():
            if name[:7] == 'Camera ':
                camera_list.append(name[7:])
        return camera_list

    def copy_camera_configuration(self, name):
        self.section_name = 'Camera ' + name
        self.conf.set('Camera', 'name', self.conf.get(self.section_name,
                                                      'name'))
        self.conf.set('Camera', 'pixel size',
                      self.conf.get(self.section_name, 'pixel size'))
        self.conf.set('Camera', 'pixel horizontal',
                      self.conf.get(self.section_name, 'pixel horizontal'))
        self.conf.set('Camera', 'pixel vertical',
                      self.conf.get(self.section_name, 'pixel vertical'))
        self.conf.set('Camera', 'external margin pixel',
                      self.conf.get(self.section_name,
                                    'external margin pixel'))
        self.conf.set('Camera', 'tile overlap pixel',
                      self.conf.get(self.section_name, 'tile overlap pixel'))

    def write_config(self):
        config_file = open(self.config_filename, 'w')
        self.conf.write(config_file)
        config_file.close()


if __name__ == "__main__":
    c = Configuration()
    camera_list = c.get_camera_list()
    app = QtGui.QApplication(sys.argv)
    editor = ConfigurationEditor(c)
    editor.show()
    app.exec_()

    longitude = c.conf.getfloat("Geographical Position", "longitude")
    print "longitude: ", longitude

    print "configuration changed: ", editor.configuration_changed
