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
    autoalignment_point_reached_signal = QtCore.pyqtSignal()
    autoalignment_performed_signal = QtCore.pyqtSignal(bool)
    autoalignment_reset_signal = QtCore.pyqtSignal()
    moon_limb_centered_signal = QtCore.pyqtSignal()
    focus_area_set_signal = QtCore.pyqtSignal()
    set_statusbar_signal = QtCore.pyqtSignal()
    reset_key_status_signal = QtCore.pyqtSignal()
    set_text_browser_signal = QtCore.pyqtSignal(QtCore.QString)

    def __init__(self, gui, parent=None):
        QtCore.QThread.__init__(self, parent)
        self.gui = gui

        self.run_loop_delay = float(self.gui.configuration.conf.get('ASCOM', 'polling interval'))
        self.exiting = False

        self.set_session_output_flag = False
        self.camera_initialization_flag = False
        self.slew_to_alignment_point_flag = False
        self.perform_alignment_flag = False
        self.perform_autoalignment_flag = False
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
        self.me = MoonEphem(self.gui.configuration, self.date_time, debug=self.gui.configuration.ephemeris_debug)
        self.al = Alignment(self.gui.configuration, self.telescope, self.me, debug=self.gui.configuration.alignment_debug)
        self.alignment_ready_signal.emit()

        while not self.exiting:
            if self.set_session_output_flag:
                self.set_session_output_flag = False
                if self.gui.configuration.conf.getboolean('Workflow', 'protocol to file'):
                    # print >> sys.stderr, "redirecting output to file"
                    try:
                        self.protocol_file = open(self.gui.configuration.protocol_filename, 'a')
                    except IOError:
                        pass
                    sys.stdout = self.protocol_file
                else:
                    # print >> sys.stderr, "redirecting output to stdout"
                    sys.stdout = self.stdout_saved
                if self.gui.configuration.protocol:
                    print "\n----------------------------------------------------\n", str(
                        datetime.now())[
                                                                                      :10], \
                        self.gui.configuration.version, "\n", \
                        "----------------------------------------------------"


            elif self.camera_initialization_flag:
                self.camera_initialization_flag = False
                if self.gui.camera_automation:
                    self.camera_trigger_delay = (
                        self.gui.configuration.conf.getfloat("Workflow", "camera trigger delay"))
                    if not self.camera_connected:
                        self.camera = Camera(self.gui.configuration, self.telescope,
                            self.gui.mark_processed, debug=self.gui.configuration.camera_debug)
                        self.connect(self.camera, self.camera.signal, self.gui.signal_from_camera)
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
                    print "\n", str(datetime.now())[
                                11:21], "MoonPanoramaMaker (re)started, de_center:", degrees(
                        de_center), ", m_diameter:", degrees(m_diameter), ", phase_angle:", degrees(
                        phase_angle), ", pos_angle:", degrees(pos_angle)

                self.camera_ready_signal.emit(de_center, m_diameter, phase_angle, pos_angle)

            elif self.slew_to_alignment_point_flag:
                self.slew_to_alignment_point_flag = False
                self.telescope.calibrate()
                (ra_landmark, de_landmark) = (self.al.compute_telescope_coordinates_of_landmark())
                if self.gui.configuration.protocol:
                    print str(datetime.now())[11:21], "Slew to alignment point"
                self.telescope.slew_to(ra_landmark, de_landmark)
                if self.gui.autoalign_enabled:
                    self.autoalignment_point_reached_signal.emit()
                else:
                    self.alignment_point_reached_signal.emit()

            elif self.perform_alignment_flag:
                self.perform_alignment_flag = False
                if self.gui.configuration.protocol:
                    print str(datetime.now())[11:21], "Center landmark in camera live view"
                self.al.align(alignment_manual=True)
                self.alignment_performed_signal.emit()

            elif self.perform_autoalignment_flag:
                self.perform_autoalignment_flag = False
                if self.gui.configuration.protocol:
                    print str(datetime.now())[11:21], "Try to initialize auto-alignment"
                # Try to initialize auto-alignment. Signal (caught in moon_panorama_maker in
                # method "autoalignment_performed" carries info on success / failure as boolean.
                try:
                    self.al.initialize_auto_align(self.camera.mysocket)
                    # Initialize list of tiles captured from now on. If at the next auto-alignment
                    # the pointing precision is too low, they have to be repeated.
                    self.tiles_since_last_autoalign = []
                    self.autoalignment_performed_signal.emit(True)
                    if self.gui.configuration.protocol:
                        print str(datetime.now())[11:21], "Auto-alignment initialization successful"
                except RuntimeError:
                    self.autoalignment_performed_signal.emit(False)
                    if self.gui.configuration.protocol:
                        print str(datetime.now())[11:21], "Auto-alignment initialization failed"

            elif self.slew_to_moon_limb_flag:
                self.slew_to_moon_limb_flag = False
                (ra, de) = self.al.center_offset_to_telescope_coordinates(
                    self.gui.tc.delta_ra_limb_center, self.gui.tc.delta_de_limb_center)
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
                (ra_focus, de_focus) = (self.al.compute_telescope_coordinates_of_focus_area())
                self.telescope.slew_to(ra_focus, de_focus)

            elif self.slew_to_tile_and_record_flag:
                self.slew_to_tile_and_record_flag = False
                # Maximum time between auto-alignments has passed, do a new alignment
                if self.al.autoalign_initialized and self.al.seconds_since_last_alignment() > \
                        self.gui.max_seconds_between_autoaligns:
                    if self.gui.configuration.protocol:
                        print str(datetime.now())[11:21], "Try to perform auto-alignment"
                    try:
                        # Perform an auto-alignment. Return value gives size of correction relative
                        # to width of overlap between tiles (between 0. and 1.).
                        relative_alignment_error = self.al.align(alignment_manual=False)
                        # If error too large, reduce time between auto-alignments (within bounds
                        # given by parameters "min_autoalign_interval" and "max_autoalign_interval".
                        if relative_alignment_error > self.gui.max_alignment_error:
                            self.gui.max_seconds_between_autoaligns = max(
                                (self.gui.max_seconds_between_autoaligns / 1.5),
                                self.gui.min_autoalign_interval)
                            # Videos since last auto-alignment have to be repeated.
                            if len(self.tiles_since_last_autoalign) > 0:
                                self.gui.tv.mark_unprocessed(self.tiles_since_last_autoalign)
                            # Reset list of tiles since last auto-align (a fresh auto-align has
                            # been just performed).
                            self.tiles_since_last_autoalign = []
                        # If the alignment error was very low, increase time between auto-alignments
                        # (within bounds).
                        elif relative_alignment_error < self.gui.min_alignment_error:
                            self.gui.max_seconds_between_autoaligns = min(
                                (self.gui.max_seconds_between_autoaligns * 1.5),
                                self.gui.max_autoalign_interval)
                        if self.gui.configuration.protocol:
                            print str(datetime.now())[11:21], "Auto-alignment successful"
                    # Auto-alignment was not successful, continue in moon_panorama_maker with
                    # method "wait_for_autoalignment_off" (reset auto-alignment, including gui
                    # button, enable manual alignment button, and prompt user to continue manually.)
                    except RuntimeError:
                        self.autoalignment_reset_signal.emit()
                        print str(datetime.now())[11:21], "Auto-alignment failed"
                        # No video acquisition because of missing alignment.
                        continue

                # Alignment is up-to-date, move telescoppe to active tile for video acquisition.
                self.set_text_browser_signal.emit(
                    "Moving telescope to tile " + str(self.active_tile_number) + ", please wait.")
                if self.gui.configuration.protocol:
                    print "Moving telescope to tile ", self.active_tile_number, ", RA offset: ", \
                        degrees(
                        self.gui.next_tile['delta_ra_center']), ", DE offset: ", degrees(
                        self.gui.next_tile['delta_de_center'])
                (ra, de) = self.al.tile_to_telescope_coordinates(self.gui.next_tile)
                self.telescope.slew_to(ra, de)
                self.set_statusbar_signal.emit()
                # During video acquisition, guide the telescope to follow the moon among stars.
                guiding_rate_ra = self.me.rate_ra
                guiding_rate_de = self.me.rate_de
                # If drift has been determined, include it in guidance rates.
                if self.al.is_drift_set:
                    guiding_rate_ra += self.al.drift_ra
                    guiding_rate_de += self.al.drift_de
                self.telescope.start_guiding(guiding_rate_ra, guiding_rate_de)
                if self.gui.camera_automation:
                    # Wait a little until telescope pointing has stabilized.
                    time.sleep(self.camera_trigger_delay)
                    # Send tile number to camera (for inclusion in video file name) and start camera.
                    self.camera.active_tile_number = self.active_tile_number
                    self.camera.triggered = True
                    if self.gui.configuration.protocol:
                        print str(datetime.now())[
                              11:21], "Exposure of tile ", self.active_tile_number, " started " \
                                                                                    "automatically."
                    # If meanwhile the Esc key has been pressed, do not ask for pressing it again.
                    if not self.escape_pressed_flag:
                        self.set_text_browser_signal.emit("Video started automatically. "
                                                          "Press 'Esc' to interrupt loop after "
                                                          "current video.")
                else:
                    # Manual exposure: Set the context in moon_panorama_maker for Enter key.
                    # Pressing it will continue workflow.
                    self.gui.gui_context = "start_continue_recording"
                    self.set_text_browser_signal.emit("Start video. After the video is finished, "
                                                      "confirm with 'enter'.")

            elif self.move_to_selected_tile_flag:
                self.move_to_selected_tile_flag = False
                # Triggered by method "move_to_selected_tile" in moon_panorama_maker. First
                # translate tile number into telescope coordinates.
                (ra_selected_tile, de_selected_tile) = (
                    self.al.tile_to_telescope_coordinates(self.gui.selected_tile))
                # Move telescope to aim point.
                self.telescope.slew_to(ra_selected_tile, de_selected_tile)

            elif self.escape_pressed_flag:
                self.escape_pressed_flag = False
                # The escape key has been pressed during video workflow. Wait while camera is
                # active.
                if self.gui.camera_automation:
                    delay = float(self.gui.configuration.conf.get('ASCOM', 'polling interval'))
                    while (self.camera.active):
                        time.sleep(delay)
                # After video(s) are finished, stop telescope guiding, blank out text browser and
                # give key control back to the user.
                self.telescope.stop_guiding()
                self.set_text_browser_signal.emit("")
                self.reset_key_status_signal.emit()

            time.sleep(self.run_loop_delay)

        self.telescope.terminate()
        # If camera automation is active, set termination flag in camera and wait a short while.
        if self.camera_automation:
            self.camera.terminate = True
        time.sleep(self.run_loop_delay)
        try:
            self.protocol_file.close()
        except:
            pass
        # Set standard output back to the value before it was re-routed to protocol file.
        sys.stdout = self.stdout_saved