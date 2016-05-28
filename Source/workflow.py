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
import time
from datetime import datetime
from math import degrees

from PyQt4 import QtCore

from alignment import Alignment
from camera import Camera
from moon_ephem import MoonEphem
from telescope import Telescope


class Workflow(QtCore.QThread):
    camera_ready_signal = QtCore.pyqtSignal(float, float, float, float)
    alignment_ready_signal = QtCore.pyqtSignal()
    alignment_point_reached_signal = QtCore.pyqtSignal()
    alignment_performed_signal = QtCore.pyqtSignal()
    moon_limb_centered_signal = QtCore.pyqtSignal()
    focus_area_set_signal = QtCore.pyqtSignal()
    set_statusbar_signal = QtCore.pyqtSignal()
    reset_key_status_signal = QtCore.pyqtSignal()
    set_text_browser_signal = QtCore.pyqtSignal(QtCore.QString)

    def __init__(self, gui, parent=None):
        QtCore.QThread.__init__(self, parent)
        self.gui = gui
        self.run_loop_delay = float(self.gui.configuration.conf.get('ASCOM',
                                                                    'polling interval'))
        self.exiting = False

        self.set_session_output_flag = False
        self.camera_initialization_flag = False
        self.slew_to_alignment_point_flag = False
        self.perform_alignment_flag = False
        self.slew_to_moon_limb_flag = False
        self.set_focus_area_flag = False
        self.goto_focus_area_flag = False
        self.slew_to_tile_and_record_flag = False
        self.move_to_selected_tile_flag = False
        self.escape_pressed_flag = False

        self.stdout_saved = sys.stdout

        self.telescope = Telescope(self.gui.configuration)

        self.camera_connected = False

        self.start()

    def run(self):
        self.date_time = datetime.now()
        self.me = MoonEphem(self.gui.configuration, self.date_time)
        self.al = Alignment(self.gui.configuration, self.telescope, self.me)
        self.alignment_ready_signal.emit()

        while not self.exiting:
            if self.set_session_output_flag:
                self.set_session_output_flag = False
                if self.gui.configuration.conf.getboolean('Workflow',
                                                          'protocol to file'):
                    # print >> sys.stderr, "redirecting output to file"
                    try:
                        self.protocol_file = open(
                            self.gui.configuration.protocol_filename, 'a')
                    except IOError:
                        pass
                    sys.stdout = self.protocol_file
                else:
                    # print >> sys.stderr, "redirecting output to stdout"
                    sys.stdout = self.stdout_saved
                if self.gui.configuration.protocol:
                    print "\n----------------------------------------------------\n", \
                        str(datetime.now())[
                        :10], self.gui.configuration.version, "\n", \
                        "----------------------------------------------------"


            elif self.camera_initialization_flag:
                self.camera_initialization_flag = False
                if self.gui.camera_automation:
                    self.camera_trigger_delay = (
                        self.gui.configuration.conf.getfloat(
                            "Workflow", "camera trigger delay"))
                    if not self.camera_connected:
                        self.camera = Camera(self.gui.configuration,
                                             self.telescope,
                                             self.gui.mark_processed)
                        self.connect(self.camera, self.camera.signal,
                                     self.gui.signal_from_camera)
                        self.camera_connected = True
                        self.camera.start()
                self.al.is_landmark_offset_set = False
                self.active_tile_number = -1
                self.all_tiles_recorded = False

                self.date_time = datetime.now()
                self.me.update(self.date_time)

                de_center = self.me.de
                m_diameter = self.me.diameter
                phase_angle = self.me.phase_angle
                pos_angle = self.me.pos_angle_pole
                if self.gui.configuration.protocol:
                    print "\n", str(datetime.now())[11:21], \
                        "MoonPanoramaMaker (re)started, de_center:", \
                        degrees(de_center), ", m_diameter:", \
                        degrees(m_diameter), ", phase_angle:", degrees(
                        phase_angle), \
                        ", pos_angle:", degrees(pos_angle)

                self.camera_ready_signal.emit(de_center, m_diameter,
                                              phase_angle, pos_angle)

            elif self.slew_to_alignment_point_flag:
                self.slew_to_alignment_point_flag = False
                self.telescope.calibrate()
                (ra_landmark, de_landmark) = (
                    self.al.compute_telescope_coordinates_of_landmark())
                if self.gui.configuration.protocol:
                    print str(datetime.now())[11:21], \
                        "Slew to alignment point"
                self.telescope.slew_to(ra_landmark, de_landmark)
                self.alignment_point_reached_signal.emit()

            elif self.perform_alignment_flag:
                self.perform_alignment_flag = False
                if self.gui.configuration.protocol:
                    print str(datetime.now())[11:21], \
                        "Center landmark in camera live view"
                self.al.align()
                self.alignment_performed_signal.emit()

            elif self.slew_to_moon_limb_flag:
                self.slew_to_moon_limb_flag = False
                (ra, de) = self.al.center_offset_to_telescope_coordinates(
                    self.gui.tc.delta_ra_limb_center,
                    self.gui.tc.delta_de_limb_center)
                if self.gui.configuration.protocol:
                    print str(datetime.now())[11:21], "Slew to Moon limb"
                self.telescope.slew_to(ra, de)
                self.moon_limb_centered_signal.emit()

            elif self.set_focus_area_flag:
                self.set_focus_area_flag = False
                self.al.set_focus_area()
                self.focus_area_set_signal.emit()

            elif self.goto_focus_area_flag:
                self.goto_focus_area_flag = False
                (ra_focus, de_focus) = (
                    self.al.compute_telescope_coordinates_of_focus_area())
                self.telescope.slew_to(ra_focus, de_focus)

            elif self.slew_to_tile_and_record_flag:
                self.slew_to_tile_and_record_flag = False
                self.set_text_browser_signal.emit(
                    "Moving telescope to tile " + str(
                        self.active_tile_number) + ", please wait.")
                if self.gui.configuration.protocol:
                    print "Moving telescope to tile ", self.active_tile_number, \
                        ", RA offset: ", degrees(
                        self.gui.next_tile['delta_ra_center']), \
                        ", DE offset: ", degrees(
                        self.gui.next_tile['delta_de_center'])
                (ra, de) = self.al.tile_to_telescope_coordinates(
                    self.gui.next_tile)
                self.telescope.slew_to(ra, de)
                self.set_statusbar_signal.emit()
                guiding_rate_ra = self.me.rate_ra
                guiding_rate_de = self.me.rate_de
                if self.al.is_drift_set:
                    guiding_rate_ra += self.al.drift_ra
                    guiding_rate_de += self.al.drift_de
                self.telescope.start_guiding(guiding_rate_ra, guiding_rate_de)
                if self.gui.camera_automation:
                    time.sleep(self.camera_trigger_delay)
                    self.camera.active_tile_number = self.active_tile_number
                    self.camera.triggered = True
                    if self.gui.configuration.protocol:
                        print str(datetime.now())[11:21], \
                            "Exposure of tile ", self.active_tile_number, \
                            " started automatically."
                    if not self.escape_pressed_flag:
                        self.set_text_browser_signal.emit(
                            "Video started automatically. "
                            "Press 'Esc' to interrupt loop after current video.")
                else:
                    self.gui.gui_context = "start_continue_recording"
                    self.set_text_browser_signal.emit(
                        "Start video. After the video is finished, "
                        "confirm with 'enter'.")

            elif self.move_to_selected_tile_flag:
                self.move_to_selected_tile_flag = False
                (ra_selected_tile, de_selected_tile) = (
                    self.al.tile_to_telescope_coordinates(
                        self.gui.selected_tile))
                self.telescope.slew_to(ra_selected_tile, de_selected_tile)

            elif self.escape_pressed_flag:
                self.escape_pressed_flag = False
                if self.gui.camera_automation:
                    delay = float(self.gui.configuration.conf.get('ASCOM',
                                                                  'polling interval'))
                    while (self.camera.active):
                        time.sleep(delay)
                self.telescope.stop_guiding()
                self.set_text_browser_signal.emit("")
                self.reset_key_status_signal.emit()

            time.sleep(self.run_loop_delay)

        self.telescope.terminate()
        if self.camera_automation:
            self.camera.terminate = True
        time.sleep(self.run_loop_delay)
        try:
            self.protocol_file.close()
        except:
            pass
        sys.stdout = self.stdout_saved
