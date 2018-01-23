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

from PyQt5 import QtCore

from alignment import Alignment
from camera import Camera
from miscellaneous import Miscellaneous
from moon_ephem import MoonEphem
from telescope import Telescope
from tile_constructor import TileConstructor


class Workflow(QtCore.QThread):
    """
    The Workflow class creates a thread which runs in parallel to the main gui. Communication
    between the main gui and the workflow thread is realized as follows: Actions in this
    thread are triggered by flags set in the main gui thread. In the reverse direction, this
    thread emits signals which are connected with methods in the main gui.
    
    """

    # Define the list of signals with which this thread communicates with the main gui.
    output_channel_initialized_signal = QtCore.pyqtSignal()
    telescope_initialized_signal = QtCore.pyqtSignal()
    camera_initialized_signal = QtCore.pyqtSignal()
    tesselation_initialized_signal = QtCore.pyqtSignal()
    alignment_point_reached_signal = QtCore.pyqtSignal()
    autoalignment_point_reached_signal = QtCore.pyqtSignal()
    alignment_performed_signal = QtCore.pyqtSignal()
    autoalignment_performed_signal = QtCore.pyqtSignal(bool)
    autoalignment_reset_signal = QtCore.pyqtSignal()
    moon_limb_centered_signal = QtCore.pyqtSignal()
    focus_area_set_signal = QtCore.pyqtSignal()
    set_statusbar_signal = QtCore.pyqtSignal()
    reset_key_status_signal = QtCore.pyqtSignal()
    set_text_browser_signal = QtCore.pyqtSignal(str)

    def __init__(self, gui, parent=None):
        """
        Establish the connection with the main gui, set some instance variables and initialize all
        flags to False.
        
        :param gui: main gui object
        """

        QtCore.QThread.__init__(self, parent)
        self.gui = gui

        # Create the alignment object. Alignment points are kept throughout the whole program
        # execution, even if the telescope driver or other configuration parameters are changed.
        self.al = Alignment(self.gui.configuration, debug=self.gui.configuration.alignment_debug)

        self.exiting = False

        self.output_channel_initialization_flag = False
        self.telescope_initialization_flag = False
        self.camera_initialization_flag = False
        self.new_tesselation_flag = False
        self.slew_to_alignment_point_flag = False
        self.perform_alignment_flag = False
        self.perform_autoalignment_flag = False
        self.slew_to_moon_limb_flag = False
        self.set_focus_area_flag = False
        self.goto_focus_area_flag = False
        self.slew_to_tile_and_record_flag = False
        self.move_to_selected_tile_flag = False
        self.escape_pressed_flag = False

        # Save the descriptor of standard output. Stdout might be redirected to a file and back
        # later.
        self.stdout_saved = sys.stdout

        # Initialize status variables.
        self.output_redirected = False
        self.telescope_connected = False
        self.camera_connected = False
        self.tesselation_created = False

        self.start()

    def run(self):
        """
        Execute the workflow thread. Its main part is a permanent loop which looks for activity
        flags set by the main gui. When a flag is true, the corresponding action is performed.
        On completion, a signal is emitted.
        
        :return: -
        """

        # Main workflow loop.
        while not self.exiting:

            # Re-direct stdout to a file if requested in configuration.
            if self.output_channel_initialization_flag:
                self.output_channel_initialization_flag = False
                # Action required if configuration value does not match current redirection status.
                if self.gui.configuration.conf.getboolean('Workflow', 'protocol to file') != self.output_redirected:
                    # Output currently redirected. Reset to stdout.
                    if self.output_redirected:
                        sys.stdout = self.stdout_saved
                        self.output_redirected = False
                    # Currently set to stdout, redirect to file now.
                    else:
                        try:
                            self.protocol_file = open(self.gui.configuration.protocol_filename, 'a')
                            sys.stdout = self.protocol_file
                            self.output_redirected = True
                        except IOError:
                            pass
                print ("Signal the main GUI that the output channel is initialized.")
                # Signal the main GUI that the output channel is initialized.
                self.output_channel_initialized_signal.emit()

            # Initialize the telescope object.
            elif self.telescope_initialization_flag:
                self.telescope_initialization_flag = False
                # If a telescope driver is active, first terminate it:
                if self.telescope_connected:
                    self.telescope.terminate()
                    time.sleep(4. * float(self.gui.configuration.conf.get('ASCOM', 'polling interval')))
                    self.telescope_connected = False
                # Connect the telescope driver specified in configuration.
                try:
                    self.telescope = Telescope(self.gui.configuration)
                    # Register new telescope object with the alignment object.
                    self.al.set_telescope(self.telescope)
                    self.telescope_connected = True
                except Exception:
                    if self.gui.configuration.protocol_level > 0:
                        Miscellaneous.protocol("Telescope initialization failed.")
                print ("Signal the main GUI that the telescope driver is initialized.")
                # Signal the main GUI that the telescope driver is initialized.
                self.telescope_initialized_signal.emit()

            # Initialize the camera object.
            elif self.camera_initialization_flag:
                self.camera_initialization_flag = False
                # If the camera is connected, disconnect it now.
                if self.camera_connected:
                    self.camera.terminate = True
                    time.sleep(4. * float(self.gui.configuration.conf.get('ASCOM', 'polling interval')))
                    self.camera_connected = False
                # If camera automation is on, create a Camera object and connect the camera.
                if self.gui.configuration.conf.getboolean("Workflow", "camera automation"):
                    try:
                        self.camera = Camera(self.gui.configuration, self.gui.mark_processed,
                                             debug=self.gui.configuration.camera_debug)
                        self.camera.start()
                        self.camera_connected = True
                    except Exception:
                        if self.gui.configuration.protocol_level > 0:
                            Miscellaneous.protocol("Camera initialization failed.")
                print ("Signal the main GUI that the camera is initialized.")
                # Signal the main GUI that the camera is initialized.
                self.camera_initialized_signal.emit()

            # Initialize a new tesselation of the current moon phase and create the tile
            # visualization window.
            elif self.new_tesselation_flag:
                self.new_tesselation_flag = False

                # Initialize some instance variables.
                self.active_tile_number = -1
                self.repeat_from_here = -1
                self.all_tiles_recorded = False

                # Set the time to current time and create a new moon ephemeris object.
                self.date_time = datetime.now()
                self.me = MoonEphem(self.gui.configuration, self.date_time,
                                    debug=self.gui.configuration.ephemeris_debug)
                # Register the new ephemeris object with the alignment object.
                self.al.set_moon_ephem(self.me)

                de_center = self.me.de
                m_diameter = self.me.diameter
                phase_angle = self.me.phase_angle
                pos_angle = self.me.pos_angle_pole
                # Compute the tesselation of the sunlit moon phase.
                self.tc = TileConstructor(self.gui.configuration, de_center, m_diameter, phase_angle,
                                          pos_angle)

                # Write the initialization message to stdout / file:
                if self.gui.configuration.protocol:
                    if self.gui.configuration.protocol_level > 0:
                        print("")
                        Miscellaneous.protocol("MoonPanoramaMaker (re)started"
                            "\n           ----------------------------------------------------\n" +
                            "           " + str(datetime.now())[:10] + " " +
                            self.gui.configuration.version + "\n" +
                            "           ----------------------------------------------------")
                        Miscellaneous.protocol("Moon center RA: " +
                                        str(round(degrees(self.me.ra), 5)) + ", DE: " +
                                        str(round(degrees(self.me.de), 5)) + " (degrees), " +
                                        "diameter: " + str(round(degrees(m_diameter)*60., 3)) +
                                        " ('), phase_angle: " + str(round(degrees(phase_angle), 2)) +
                                        ", pos_angle: " + str(round(degrees(pos_angle), 2)) +
                                        " (degrees)")
                        Miscellaneous.protocol("Moon speed (arc min./hour), RA: " +
                                    str(round(degrees(self.me.rate_ra) * 216000., 3)) + ", DE: " +
                                    str(round(degrees(self.me.rate_de) * 216000., 3)))

                self.tesselation_created = True
                print ("Signal the main GUI that the tesselation is initialized.")
                # Signal the main GUI that the tesselation is initialized.
                self.tesselation_initialized_signal.emit()

            # Slew the telescope to the coordinates of the alignment point.
            elif self.slew_to_alignment_point_flag:
                self.slew_to_alignment_point_flag = False
                # First calibrate the north/south/east/west directions of the mount
                # This would not be necessary every time!
                self.telescope.calibrate()
                # Compute alignment point coordinates and instruct telescope to move there.
                (ra_landmark, de_landmark) = (self.al.compute_telescope_coordinates_of_landmark())
                if self.gui.configuration.protocol_level > 0:
                    Miscellaneous.protocol("Moving telescope to alignment point.")
                self.telescope.slew_to(ra_landmark, de_landmark)
                # Depending on the context where this activity was triggered emit different signals.
                if self.gui.autoalign_enabled:
                    # In auto-alignment mode: Trigger method "autoalignment_point_reached" in gui.
                    self.autoalignment_point_reached_signal.emit()
                else:
                    # In manual alignment mode: Trigger method "alignment_point_reached" in gui.
                    self.alignment_point_reached_signal.emit()

            # The mount has been aimed manually at the exact landmark location. Define an alignment
            # point.
            elif self.perform_alignment_flag:
                self.perform_alignment_flag = False
                if self.gui.configuration.protocol_level > 0:
                    print("")
                    Miscellaneous.protocol("Performing manual alignment.")
                self.al.align(alignment_manual=True)
                # Trigger method "alignment_performed" in gui.
                self.alignment_performed_signal.emit()

            # The mount has been aimed manually at the exact landmark location. Initialize
            # auto-alignment by taking a reference frame with the camera. This operation may fail
            # (e.g. if reference frame shows too little detail). Inform gui about success via a
            # signal argument.
            elif self.perform_autoalignment_flag:
                self.perform_autoalignment_flag = False
                if self.gui.configuration.protocol_level > 0:
                    print("")
                    Miscellaneous.protocol("Trying to initialize auto-alignment.")
                # Try to initialize auto-alignment. Signal (caught in moon_panorama_maker in
                # method "autoalignment_performed" carries info on success / failure as boolean.
                try:
                    self.al.initialize_auto_align(self.camera.mysocket)
                    # Initialize list of tiles captured from now on. If at the next auto-alignment
                    # the pointing precision is too low, they have to be repeated.
                    self.tile_indices_since_last_autoalign = []
                    # Signal success to gui, start method "autoalign_performed" there.
                    self.autoalignment_performed_signal.emit(True)
                    if self.gui.configuration.protocol_level > 0:
                        Miscellaneous.protocol("Auto-alignment initialization successful.")
                except RuntimeError:
                    # Signal failure to gui, start method "autoalign_performed" there.
                    self.autoalignment_performed_signal.emit(False)
                    if self.gui.configuration.protocol_level > 0:
                        Miscellaneous.protocol("Auto-alignment initialization failed.")

            # Slew the telescope to the moon's limb midpoint. Triggered by "perform_camera_rotation"
            # in gui.
            elif self.slew_to_moon_limb_flag:
                self.slew_to_moon_limb_flag = False
                # Compute coordinates of limb center point and slew telescope there.
                (ra, de) = self.al.center_offset_to_telescope_coordinates(
                    self.tc.delta_ra_limb_center, self.tc.delta_de_limb_center)
                if self.gui.configuration.protocol_level > 0:
                    Miscellaneous.protocol("Moving telescope to Moon limb.")
                self.telescope.slew_to(ra, de)
                # Signal success to gui, start method "prompt_camera_rotated_acknowledged" in gui.
                self.moon_limb_centered_signal.emit()

            # Memorize the current telescope location as focus area. Triggered by method
            # "finish_set_focus_area" in gui.
            elif self.set_focus_area_flag:
                self.set_focus_area_flag = False
                self.al.set_focus_area()
                if self.gui.configuration.protocol_level > 1:
                    if self.gui.configuration.conf.getboolean("Workflow", "focus on star"):
                        Miscellaneous.protocol("Location of focus star saved, RA: " + str(
                            round(degrees(self.al.true_ra_focus), 5)) + ", DE: " + str(
                            round(degrees(self.al.true_de_focus), 5)) + " (all in degrees)")
                    else:
                        Miscellaneous.protocol(
                            "Location of focus area saved, offset from center RA ('): " + str(
                                round(degrees(self.al.ra_offset_focus_area) * 60.,
                                      3)) + ", DE ('): " + str(
                                round(degrees(self.al.de_offset_focus_area) * 60., 3)))
                # Start method "set_focus_area_finished" in gui.
                self.focus_area_set_signal.emit()

            # Move telescope to the focus area. Triggered by method "goto_focus_area" in gui.
            elif self.goto_focus_area_flag:
                self.goto_focus_area_flag = False
                (ra_focus, de_focus) = (self.al.compute_telescope_coordinates_of_focus_area())
                if self.gui.configuration.protocol_level > 0:
                    print("")
                    if self.gui.configuration.conf.getboolean("Workflow", "focus on star"):
                        Miscellaneous.protocol("Moving telescope to focus star.")
                    else:
                        Miscellaneous.protocol("Moving telescope to focus area.")
                self.telescope.slew_to(ra_focus, de_focus)

            # This is the most complicated activity of this thread. It is triggered in three
            # different situations (see method "start_continue_recording" in gui).
            elif self.slew_to_tile_and_record_flag:
                self.slew_to_tile_and_record_flag = False
                # Maximum time between auto-alignments has passed, do a new alignment
                if self.al.autoalign_initialized and self.al.seconds_since_last_alignment() > \
                        self.gui.max_seconds_between_autoaligns:
                    if self.gui.configuration.protocol_level > 0:
                        print("")
                        Miscellaneous.protocol("Trying to perform auto-alignment.")
                    self.set_text_browser_signal.emit("Trying to perform auto-alignment.")
                    # For test puuposes only! Repeat alignments several times. In production mode
                    # set repetition count to 1 (in configuration).
                    auto_alignment_disabled = False
                    for repetition_index in range(self.gui.configuration.align_repetition_count):
                        try:
                            # Perform an auto-alignment. Return value gives size of correction
                            # relative to width of overlap between tiles (between 0. and 1.).
                            relative_alignment_error = self.al.align(alignment_manual=False)
                            # If enough alignment points are set, enable drift correction dialog
                            # button.
                            if self.al.drift_dialog_enabled:
                                self.gui.change_saved_key_status(
                                    self.gui.ui.configure_drift_correction, True)
                            # On first iteration only: check if time between alignments is to be
                            # adjusted.
                            if repetition_index == 0:
                                # If error too large, reduce time between auto-alignments (within bounds
                                # given by parameters "min_autoalign_interval" and
                                # "max_autoalign_interval".
                                if relative_alignment_error > self.gui.max_alignment_error:
                                    self.gui.max_seconds_between_autoaligns = max((
                                        self.gui.max_seconds_between_autoaligns /
                                        self.gui.configuration.align_interval_change_factor),
                                        self.gui.min_autoalign_interval)
                                    if self.gui.configuration.protocol_level > 0:
                                        Miscellaneous.protocol(
                                            "Auto-alignment inaccurate: Error is " + str(round(
                                                relative_alignment_error / self.gui.max_alignment_error,
                                                2)) + " times the maximum allowed, roll back to last "
                                                      "" + "alignment point. New time between "
                                                           "alignments: " + str(
                                                self.gui.max_seconds_between_autoaligns) + " seconds.")
                                    # Videos since last auto-alignment have to be repeated.
                                    if len(self.tile_indices_since_last_autoalign) > 0:
                                        self.tv.mark_unprocessed(
                                            self.tile_indices_since_last_autoalign)
                                        # Reset list of tiles since last auto-align (a fresh
                                        # auto-align has been just performed). Save the lowest index of
                                        # the invalidated tiles. When the gui method
                                        # "find_next_unprocessed_tile" will look for the
                                        # next unprocessed tile, it will start with this one.
                                        self.repeat_from_here = min(self.tile_indices_since_last_autoalign)
                                        # Reset list of tiles to be repeated.
                                        self.tile_indices_since_last_autoalign = []
                                    else:
                                        self.repeat_from_here = -1
                                else:
                                    # Auto-alignment is accurate enough. Reset list of tiles since last
                                    # successful alignment.
                                    self.tile_indices_since_last_autoalign = []
                                    if self.gui.configuration.protocol_level > 0:
                                        Miscellaneous.protocol(
                                            "Auto-alignment accurate: Error is " + str(round(
                                                relative_alignment_error / self.gui.max_alignment_error,
                                                2)) + " times the maximum allowed.")
                                # If the alignment error was very low, increase time between
                                # auto-alignments (within bounds).
                                if relative_alignment_error < self.gui.max_alignment_error / \
                                        self.gui.configuration.align_very_precise_factor:
                                    self.gui.max_seconds_between_autoaligns = min((
                                        self.gui.max_seconds_between_autoaligns *
                                        self.gui.configuration.align_interval_change_factor),
                                        self.gui.max_autoalign_interval)
                                    if self.gui.configuration.protocol_level > 0:
                                        Miscellaneous.protocol("Relative alignment error very small, "
                                                               "new time between alignments: " + str(
                                            self.gui.max_seconds_between_autoaligns) + " seconds.")
                            if self.gui.configuration.protocol_level > 0:
                                Miscellaneous.protocol("Auto-alignment successful")
                        # Auto-alignment was not successful, continue in moon_panorama_maker with
                        # method "wait_for_autoalignment_off" (reset auto-alignment, including gui
                        # button, enable manual alignment button, and prompt user to continue
                        # manually.)
                        except RuntimeError as e:
                            self.autoalignment_reset_signal.emit()
                            if self.gui.configuration.protocol_level > 0:
                                Miscellaneous.protocol("Auto-alignment failed, revert to manual mode.")
                            # No video acquisition because of missing alignment.
                            auto_alignment_disabled = True
                            break
                    if auto_alignment_disabled:
                        continue

                # Alignment is up-to-date, move telescoppe to active tile for video acquisition.
                self.set_text_browser_signal.emit(
                    "Moving telescope to tile " + str(self.active_tile_number) + ", please wait.")
                if self.gui.configuration.protocol_level > 0:
                    print("")
                    Miscellaneous.protocol("Moving telescope to tile " +
                                           str(self.active_tile_number))
                if self.gui.configuration.protocol_level > 2:
                    Miscellaneous.protocol("RA offset ('): " +
                                str(round(degrees(self.gui.next_tile['delta_ra_center'])*60., 3)) +
                                ", DE offset ('): " +
                                str(round(degrees(self.gui.next_tile['delta_de_center'])*60., 3)))
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
                if self.gui.configuration.conf.getboolean("Workflow", "camera automation"):
                    # Wait a little until telescope pointing has stabilized.
                    time.sleep(self.gui.configuration.conf.getfloat("Workflow", "camera trigger delay"))
                    # Send tile number to camera (for inclusion in video file name) and start
                    # camera.
                    self.camera.active_tile_number = self.active_tile_number
                    self.camera.triggered = True
                    if self.gui.configuration.protocol_level > 1:
                        Miscellaneous.protocol("Exposure of tile " + str(self.active_tile_number) +
                                               " started automatically.")
                    # If meanwhile the Esc key has been pressed, do not ask for pressing it again.
                    # Otherwise tell the user that he/she can interrupt by pressing 'Exc'.
                    if not self.escape_pressed_flag:
                        self.set_text_browser_signal.emit("Video(s) started automatically. "
                                                          "Press 'Esc' to interrupt loop after "
                                                          "video(s) for current tile.")
                else:
                    # Manual exposure: Set the context in moon_panorama_maker for Enter key.
                    # Pressing it will continue workflow.
                    self.gui.gui_context = "start_continue_recording"
                    self.set_text_browser_signal.emit("Start video(s). After all videos for this "
                        " tile are finished, confirm with 'enter'. Press 'Esc' to interrupt the "
                        " recording workflow.")

            # Triggered by method "move_to_selected_tile" in moon_panorama_maker.
            elif self.move_to_selected_tile_flag:
                self.move_to_selected_tile_flag = False
                # First translate tile number into telescope coordinates.
                (ra_selected_tile, de_selected_tile) = (
                    self.al.tile_to_telescope_coordinates(self.gui.selected_tile))
                # Move telescope to aim point. (This is a blocking operation.)
                self.telescope.slew_to(ra_selected_tile, de_selected_tile)
                self.set_text_browser_signal.emit("")
                # Start method "reset_key_status" in gui to re-activate gui buttons.
                self.reset_key_status_signal.emit()

            # The escape key has been pressed during video workflow. Wait until running activities
            # are safe to be interrupted. Then give control back to gui.
            elif self.escape_pressed_flag:
                self.escape_pressed_flag = False
                # Wait while camera is active.
                if self.gui.configuration.conf.getboolean("Workflow", "camera automation"):
                    delay = float(self.gui.configuration.conf.get('ASCOM', 'polling interval'))
                    while (self.camera.active):
                        time.sleep(delay)
                # After video(s) are finished, stop telescope guiding, blank out text browser and
                # give key control back to the user.
                self.telescope.stop_guiding()
                self.set_text_browser_signal.emit("")
                # Start method "reset_key_status" in gui to re-activate gui buttons.
                self.reset_key_status_signal.emit()

            # Sleep time inserted to limit CPU consumption by idle looping.
            time.sleep(float(self.gui.configuration.conf.get('ASCOM', 'polling interval')))
            # print ("End of main loop")

        # The "exiting" flag is set (by gui method "CloseEvent"). Terminate the telescope first.
        self.telescope.terminate()
        # If camera automation is active, set termination flag in camera and wait a short while.
        if self.gui.configuration.conf.getboolean("Workflow", "camera automation"):
            self.camera.terminate = True
        time.sleep(self.gui.configuration.conf.get('ASCOM', 'polling interval'))
        # If stdout was re-directed to a file: Close the file and reset stdout to original value.
        if self.gui.configuration.conf.getboolean('Workflow', 'protocol to file'):
            try:
                self.protocol_file.close()
                # Set standard output back to the value before it was re-routed to protocol file.
                sys.stdout = self.stdout_saved
            except:
                pass
