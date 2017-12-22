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

import configparser
import os.path
import sys

from PyQt5 import QtWidgets

from configuration_editor import ConfigurationEditor


class Configuration:
    """
    The Configuration class is used to manage all parameters which can be changed or set by the
    user. This includes input / output to file for persistent storage.
    
    """

    def __init__(self):
        """
        Initialize the configuration object.
        
        """

        # The version number is displayed on the MPM main gui title line.
        self.version = "MoonPanoramaMaker 0.9.5"

        ############################################################################################
        # Switch on/off debug modes:
        #
        # Debug mode for camera emulation: In the socket client, the interface to FireCapture is
        # emulated. FireCapture does not need to be started. No videos are captured, though.
        self.camera_debug = False
        # If camera is emulated, insert a delay (in seconds) before sending the acknowledgement
        # message (to emulate exposure time).
        self.camera_delay = 2.
        #
        # Debug mode for auto-alignment visualization:
        self.alignment_debug = False
        # Please note: Since the alignment_debug option uses a MatPlotLib window which interferes
        # with the tile configuration window of MoonPanoramaMaker, this debug option can only be
        # used in unit testing (i.e. using the main program in module image_shift).
        #
        # Another parameter used for alignment debugging is "align_repetition_count". If set to a
        # value > 1, several auto-alignment operations are repeated in direct succession. This way
        # errors in the auto-alignment operation can be distinguished from other alignment errors
        # that build up in between alignments. This debugging feature is independent of the
        # alignment_debug flag and is used with the full MoonPanoramaMaker software.
        self.align_repetition_count = 1
        #
        # Debug mode for ephemeris computations: Perform ephemeris computations for a fixed date and
        # time, thus switching off temporal changes of feature positions.
        self.ephemeris_debug = False
        # If ephemeris_debug is set to True, set the fixed date and time in terms of the selected
        # time zone [year, month, day, hour, minute, second].
        self.ephemeris_fixed_datetime = [2017, 10, 15, 5, 30, 0]
        ############################################################################################

        # Set internal parameters which cannot be changed by the user.

        # If multiple exposures of a tile are to be made in succession, insert a short wait time
        # in between exposures. Otherwise FireCapture might get stuck.
        self.camera_time_between_multiple_exposures = 1.

        # Minimum length of time interval for drift computation:
        self.minimum_drift_seconds = 600.   # 10 minutes

        # Resolution (in pixels) of overlap width in still pictures for shift determination:
        self.pixels_in_overlap_width = 40   # 40 pixels

        # Parameters used in auto-alignment:
        # In auto-alignment initialization the telescope mount is moved to two locations near
        # the alignment landmark position. The image shifts are measured using camera still images
        # and compared with the expected shifts, based on the mount displacements. These
        # measurements are used to determine whether or not the camera is oriented upright /
        # upside-down or if it is mirror-inverted. if the absolute value of the shifts deviates
        # from the expected value by more than the given fraction, auto-alignment is deemed
        # unsuccessful.
        self.align_max_autoalign_error = 0.3
        # Factor by which the interval between auto-alignments is changed:
        self.align_interval_change_factor = 1.5
        # Criterion for very precise alignment:
        self.align_very_precise_factor = 4.

        # Parameters in CLAHE image normalization:
        # Clip limit:
        self.clahe_clip_limit = 2.
        # Tile grid size:
        self.clahe_tile_grid_size = 8

        # Parameters for ORB keypoint detection:
        # WTA_K parameter:
        self.orb_wta_k = 4              # originally: 3, optimized: 4
        # Number of features:
        self.orb_nfeatures = 50
        # Edge threshold:
        self.orb_edge_threshold = 0     # originally: 30, optimized: 0
        # Patch size:
        self.orb_patch_size = 31
        # Scale factor:
        self.orb_scale_factor = 1.2
        # Number of levels:
        self.orb_n_levels = 8

        # Parameters in shift cluster detection:
        # Cluster radius in pixels:
        self.dbscan_cluster_radius = 3.
        # Minimum sample size:
        self.dbscan_minimum_sample = 5      # originally: 10, optimized: 5
        # Minimum of measurements in cluster:
        self.dbscan_minimum_in_cluster = 5  # originally: 10, optimized: 5

        # Initialize the protocol flag
        self.protocol = True

        # The config file for persistent parameter storage is located in the user's home
        # directory, as is the detailed MoonPanoramaMaker logfile.
        home = os.path.expanduser("~")
        self.config_filename = home + "\\.MoonPanoramaMaker.ini"
        self.protocol_filename = home + "\\MoonPanoramaMaker.log"

        self.config_file_exists = os.path.isfile(self.config_filename)
        self.config_up_to_date = False
        # If an existing config file is found, read it in.
        if self.config_file_exists:
            self.conf = configparser.ConfigParser()
            self.conf.read(self.config_filename)
            # Check if the file is for the current MPM version, otherwise try to update it.
            # If not successful, do not use the old config file.
            self.config_up_to_date = self.check_for_compatibility()
            if self.config_up_to_date:
                # The configuration was read from the parameter file or made compatible.
                self.configuration_read = True

        if not self.config_file_exists or not self.config_up_to_date:
            # Code to set standard config info. The "Hidden Parameters" are not displayed in the
            # configuration gui. Most of them are for placing gui windows where they had been at
            # the previous session.
            self.configuration_read = False
            self.conf = configparser.ConfigParser()
            self.conf.add_section('Hidden Parameters')
            self.conf.set('Hidden Parameters', 'version', self.version)
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
            self.conf.set('Tile Visualization', 'figsize horizontal', '7.')
            self.conf.set('Tile Visualization', 'figsize vertical', '7.')
            self.conf.set('Tile Visualization', 'label fontsize', '9')
            self.conf.set('Tile Visualization', 'label shift', '0.8')

            self.conf.add_section('Workflow')
            self.conf.set('Workflow', 'protocol level', '2')
            self.conf.set('Workflow', 'protocol to file', 'True')
            self.conf.set('Workflow', 'camera automation', 'False')
            self.conf.set('Workflow', 'focus on star', 'False')
            self.conf.set('Workflow', 'limb first', 'False')
            self.conf.set('Workflow', 'camera trigger delay', '3.')

            self.conf.add_section('ASCOM')
            self.conf.set('ASCOM', 'chooser', 'ASCOM.Utilities.Chooser')
            self.conf.set('ASCOM', 'hub', 'POTH.Telescope')
            self.conf.set('ASCOM', 'guiding interval', '0.2')
            self.conf.set('ASCOM', 'wait interval', '1.')
            self.conf.set('ASCOM', 'polling interval', '0.1')
            self.conf.set('ASCOM', 'telescope lookup precision', '0.5')

            self.conf.add_section('Alignment')
            self.conf.set('Alignment', 'min autoalign interval', '30.')
            self.conf.set('Alignment', 'max autoalign interval', '300.')
            self.conf.set('Alignment', 'max alignment error', '50.')

            self.conf.add_section('Camera ZWO ASI120MM-S')
            self.conf.set('Camera ZWO ASI120MM-S', 'name', 'ZWO ASI120MM-S')
            self.conf.set('Camera ZWO ASI120MM-S', 'pixel size', '0.00375')
            self.conf.set('Camera ZWO ASI120MM-S', 'pixel horizontal', '1280')
            self.conf.set('Camera ZWO ASI120MM-S', 'pixel vertical', '960')
            self.conf.set('Camera ZWO ASI120MM-S', 'repetition count', '1')
            self.conf.set('Camera ZWO ASI120MM-S', 'external margin pixel', '300')
            self.conf.set('Camera ZWO ASI120MM-S', 'tile overlap pixel', '200')

            self.conf.add_section('Camera ZWO ASI174MC')
            self.conf.set('Camera ZWO ASI174MC', 'name', 'ZWO ASI174MC')
            self.conf.set('Camera ZWO ASI174MC', 'pixel size', '0.00586')
            self.conf.set('Camera ZWO ASI174MC', 'pixel horizontal', '1936')
            self.conf.set('Camera ZWO ASI174MC', 'pixel vertical', '1216')
            self.conf.set('Camera ZWO ASI174MC', 'repetition count', '1')
            self.conf.set('Camera ZWO ASI174MC', 'external margin pixel', '200')
            self.conf.set('Camera ZWO ASI174MC', 'tile overlap pixel', '100')

            self.conf.add_section('Camera ZWO ASI178MC')
            self.conf.set('Camera ZWO ASI178MC', 'name', 'ZWO ASI178MC')
            self.conf.set('Camera ZWO ASI178MC', 'pixel size', '0.0024')
            self.conf.set('Camera ZWO ASI178MC', 'pixel horizontal', '3096')
            self.conf.set('Camera ZWO ASI178MC', 'pixel vertical', '2080')
            self.conf.set('Camera ZWO ASI178MC', 'repetition count', '1')
            self.conf.set('Camera ZWO ASI178MC', 'external margin pixel', '550')
            self.conf.set('Camera ZWO ASI178MC', 'tile overlap pixel', '250')

            self.conf.add_section('Camera ZWO ASI185MC')
            self.conf.set('Camera ZWO ASI185MC', 'name', 'ZWO ASI185MC')
            self.conf.set('Camera ZWO ASI185MC', 'pixel size', '0.00375')
            self.conf.set('Camera ZWO ASI185MC', 'pixel horizontal', '1944')
            self.conf.set('Camera ZWO ASI185MC', 'pixel vertical', '1224')
            self.conf.set('Camera ZWO ASI185MC', 'repetition count', '1')
            self.conf.set('Camera ZWO ASI185MC', 'external margin pixel', '300')
            self.conf.set('Camera ZWO ASI185MC', 'tile overlap pixel', '150')

            self.conf.add_section('Camera ZWO ASI224MC')
            self.conf.set('Camera ZWO ASI224MC', 'name', 'ZWO ASI224MC')
            self.conf.set('Camera ZWO ASI224MC', 'pixel size', '0.00375')
            self.conf.set('Camera ZWO ASI224MC', 'pixel horizontal', '1304')
            self.conf.set('Camera ZWO ASI224MC', 'pixel vertical', '976')
            self.conf.set('Camera ZWO ASI224MC', 'repetition count', '1')
            self.conf.set('Camera ZWO ASI224MC', 'external margin pixel', '300')
            self.conf.set('Camera ZWO ASI224MC', 'tile overlap pixel', '150')

            self.conf.add_section('Camera Celestron Skyris 274C')
            self.conf.set('Camera Celestron Skyris 274C', 'name', 'Celestron Skyris 274C')
            self.conf.set('Camera Celestron Skyris 274C', 'pixel size', '0.0044')
            self.conf.set('Camera Celestron Skyris 274C', 'pixel horizontal', '1600')
            self.conf.set('Camera Celestron Skyris 274C', 'pixel vertical', '1200')
            self.conf.set('Camera Celestron Skyris 274C', 'repetition count', '1')
            self.conf.set('Camera Celestron Skyris 274C', 'external margin pixel', '250')
            self.conf.set('Camera Celestron Skyris 274C', 'tile overlap pixel', '150')

            self.conf.add_section('Camera Celestron Skyris 445M')
            self.conf.set('Camera Celestron Skyris 445M', 'name', 'Celestron Skyris 445M')
            self.conf.set('Camera Celestron Skyris 445M', 'pixel size', '0.00375')
            self.conf.set('Camera Celestron Skyris 445M', 'pixel horizontal', '1280')
            self.conf.set('Camera Celestron Skyris 445M', 'pixel vertical', '960')
            self.conf.set('Camera Celestron Skyris 445M', 'repetition count', '1')
            self.conf.set('Camera Celestron Skyris 445M', 'external margin pixel', '300')
            self.conf.set('Camera Celestron Skyris 445M', 'tile overlap pixel', '150')

            self.conf.add_section('Camera Celestron Skyris 618M')
            self.conf.set('Camera Celestron Skyris 618M', 'name', 'Celestron Skyris 618M')
            self.conf.set('Camera Celestron Skyris 618M', 'pixel size', '0.0056')
            self.conf.set('Camera Celestron Skyris 618M', 'pixel horizontal', '640')
            self.conf.set('Camera Celestron Skyris 618M', 'pixel vertical', '480')
            self.conf.set('Camera Celestron Skyris 618M', 'repetition count', '1')
            self.conf.set('Camera Celestron Skyris 618M', 'external margin pixel', '200')
            self.conf.set('Camera Celestron Skyris 618M', 'tile overlap pixel', '100')

            # Fill the entries of section "Camera" by copying the entries from the chosen
            # camera model.
            self.copy_camera_configuration(self.conf.get('Camera', 'name'))

        # Set the "protocol_level" variable. This will control the amount of protocol output.
        self.set_protocol_level()

    def check_for_compatibility(self):
        """
        Test if the MoonPanoramaMaker version number in the parameter file read differs from the
        current version. If so, change / add parameters to make them compatible with the current
        version. At program termination the new parameter set will be written, so next time the
        parameters will be consistent.
        
        :return: True, if the data read from the file could be made compatible with the current
                  version. Otherwise return False.
        """

        file_is_compatible = False
        version_read = self.conf.get('Hidden Parameters', 'version')
        if version_read == self.version:
            # Configuration file matches current format. Nothing to be done.
            file_is_compatible = True
        elif version_read == "MoonPanoramaMaker 0.9.3":
            # The update support starts for version 0.9.3. Before that one, not many users had
            # installed MoonPanoramaMaker. Update the version number.
            self.conf.set('Hidden Parameters', 'version', self.version)
            # The handling of session protocol changed.
            wp = self.conf.getboolean('Workflow', 'protocol')
            if wp:
                self.conf.set('Workflow', 'protocol level', '2')
            else:
                self.conf.set('Workflow', 'protocol level', '0')
            self.conf.remove_option('Workflow', 'protocol')
            # Add the parameter "focus on star" which was introduced with version 0.9.5.
            self.conf.set('Workflow', 'focus on star', 'False')
            # Add the "Alignment" section which was introduced with version 0.9.5.
            self.conf.add_section('Alignment')
            self.conf.set('Alignment', 'min autoalign interval', '30.')
            self.conf.set('Alignment', 'max autoalign interval', '300.')
            self.conf.set('Alignment', 'max alignment error', '50.')
            # Set the repetition count parameter for each camera. This camera parameter was
            # introduced with version 0.9.5., too. The parameter is in section "Camera" as well
            # as in all parameter sets of supported camera models.
            self.conf.set('Camera', 'repetition count', '1')
            camlist = self.get_camera_list()
            for cam in camlist:
                self.conf.set('Camera ' + cam, 'repetition count', '1')
        else:
            # Parameter file cannot be made compatible.
            file_is_compatible = False
        return file_is_compatible

    def set_protocol_level(self):
        """
        Read from the configuration object the level of detail for the session protocol. The
        follwoing levels are supported:
        0:  No session protocol
        1:  Minimal protocol, only high-level activities, e.g. alignments, video aquisitions,
            no details
        2:  Quantitative information on high-level activities
        3:  Detailed information also on low-level activities (only for debugging)
        
        :return: -
        """

        self.protocol_level = self.conf.getint('Workflow', 'protocol level')

    def get_camera_list(self):
        """
        Look up all camera models, for which parameters are stored in the configuration object.
        
        :return: list of all available camera names (strings)
        """

        camera_list = []
        for name in self.conf.sections():
            if name[:7] == 'Camera ':
                camera_list.append(name[7:])
        return camera_list

    def copy_camera_configuration(self, name):
        """
        Copy the parameters stored for a given camera model into the section "Camera" of the
        configuration object. The parameters in this section are used by MoonPanoramaMaker's
        computations.
        
        :param name: Name (string) of the selected camera model
        :return: -
        """

        self.section_name = 'Camera ' + name
        self.conf.set('Camera', 'name', self.conf.get(self.section_name, 'name'))
        self.conf.set('Camera', 'pixel size', self.conf.get(self.section_name, 'pixel size'))
        self.conf.set('Camera', 'pixel horizontal',
                      self.conf.get(self.section_name, 'pixel horizontal'))
        self.conf.set('Camera', 'pixel vertical',
                      self.conf.get(self.section_name, 'pixel vertical'))
        self.conf.set('Camera', 'repetition count',
                      self.conf.get(self.section_name, 'repetition count'))
        self.conf.set('Camera', 'external margin pixel',
                      self.conf.get(self.section_name, 'external margin pixel'))
        self.conf.set('Camera', 'tile overlap pixel',
                      self.conf.get(self.section_name, 'tile overlap pixel'))

    def write_config(self):
        """
        Write the contentes of the configuration object back to the configuration file in the
        user's home directory.
        
        :return: -
        """

        config_file = open(self.config_filename, 'w')
        self.conf.write(config_file)
        config_file.close()


if __name__ == "__main__":
    c = Configuration()
    camera_list = c.get_camera_list()
    app = QtWidgets.QApplication(sys.argv)
    editor = ConfigurationEditor(c)
    editor.show()
    app.exec_()

    print("Current version: ", c.version)
    longitude = c.conf.getfloat("Geographical Position", "longitude")
    print("longitude: ", longitude)

    if not c.configuration_read or editor.configuration_changed:
        print("configuration has changed, write back config file: ")
        c.write_config()
