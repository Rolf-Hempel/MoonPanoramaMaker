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
from math import degrees

from PyQt4 import QtCore, QtGui

from compute_drift_rate import ComputeDriftRate
from configuration import Configuration
from configuration_editor import ConfigurationEditor
from miscellaneous import Miscellaneous
from qtgui import Ui_MainWindow
from show_landmark import ShowLandmark
from tile_constructor import TileConstructor
from tile_number_input_dialog import Ui_TileNumberInputDialog
from tile_visualization import TileVisualization
from workflow import Workflow


class StartQT4(QtGui.QMainWindow):
    """
    This class is the main class of the MoonPanoramaMaker software. It implements the main gui and
    through it communicates with the user. It creates the workflow thread which asynchronously
    controls all program activities.

    """

    def __init__(self, parent=None):
        """
        Initialize the MoonPanoramaMaker environment.

        :param parent: None
        """

        # The (generated) QtGui class is contained in module qtgui.py.
        QtGui.QWidget.__init__(self, parent)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.setChildrenFocusPolicy(QtCore.Qt.NoFocus)

        # Build a list of gui buttons. It is used to control the de-activation and re-activation of
        # gui buttons at runtime. Also, connect gui events with method invocations.
        self.button_list = []
        self.ui.edit_configuration.clicked.connect(self.edit_configuration)
        self.button_list.append(self.ui.edit_configuration)
        self.ui.restart.clicked.connect(self.restart)
        self.button_list.append(self.ui.restart)
        self.ui.new_landmark_selection.clicked.connect(self.prompt_new_landmark_selection)
        self.button_list.append(self.ui.new_landmark_selection)
        self.ui.alignment.clicked.connect(self.prompt_alignment)
        self.button_list.append(self.ui.alignment)
        self.ui.configure_drift_correction.clicked.connect(self.configure_drift_correction)
        self.button_list.append(self.ui.configure_drift_correction)
        self.ui.rotate_camera.clicked.connect(self.prompt_rotate_camera)
        self.button_list.append(self.ui.rotate_camera)
        self.ui.set_focus_area.clicked.connect(self.set_focus_area)
        self.button_list.append(self.ui.set_focus_area)
        self.ui.goto_focus_area.clicked.connect(self.goto_focus_area)
        self.button_list.append(self.ui.goto_focus_area)
        self.ui.start_continue_recording.clicked.connect(self.start_continue_recording)
        self.button_list.append(self.ui.start_continue_recording)
        self.ui.select_tile.clicked.connect(self.select_tile)
        self.button_list.append(self.ui.select_tile)
        self.ui.move_to_selected_tile.clicked.connect(self.move_to_selected_tile)
        self.button_list.append(self.ui.move_to_selected_tile)
        self.ui.set_tile_unprocessed.clicked.connect(self.set_tile_unprocessed)
        self.button_list.append(self.ui.set_tile_unprocessed)
        self.ui.set_all_tiles_unprocessed.clicked.connect(self.set_all_tiles_unprocessed)
        self.button_list.append(self.ui.set_all_tiles_unprocessed)
        self.ui.set_all_tiles_processed.clicked.connect(self.set_all_tiles_processed)
        self.button_list.append(self.ui.set_all_tiles_processed)
        self.ui.show_landmark.clicked.connect(self.show_landmark)
        self.button_list.append(self.ui.show_landmark)
        self.ui.autoalignment.clicked.connect(self.prompt_autoalignment)
        self.button_list.append(self.ui.autoalignment)

        # The gui_context is used to know, at which point of program execution, for example, a
        # "Enter" key was pressed.
        self.gui_context = ""
        # Before gui buttons are de-activated, the activation status of all keys is saved for later
        # restoration. At the moment, no key status is saved.
        self.key_status_saved = False

        # Read in or (if no config file is found) create all configuration parameters.
        self.configuration = Configuration()
        # Set the button labels for focus area / focus star according to the configuration.
        self.set_focus_button_labels()

        # Start the workflow thread. It is executed asynchronously to keep the gui from freezing
        # during long-running tasks.
        self.workflow = Workflow(self)

        # The workflow thread sends signals when a task is finished. Connect those signals with
        # the appropriate gui activity.
        self.workflow.alignment_ready_signal.connect(self.start_workflow)
        self.workflow.camera_ready_signal.connect(self.camera_ready)
        self.workflow.alignment_point_reached_signal.connect(self.alignment_point_reached)
        self.workflow.alignment_performed_signal.connect(self.alignment_performed)
        self.workflow.autoalignment_point_reached_signal.connect(self.autoalignment_point_reached)
        self.workflow.autoalignment_performed_signal.connect(self.autoalignment_performed)
        self.workflow.autoalignment_reset_signal.connect(self.wait_for_autoalignment_off)
        self.workflow.moon_limb_centered_signal.connect(self.prompt_camera_rotated_acknowledged)
        self.workflow.focus_area_set_signal.connect(self.set_focus_area_finished)
        self.workflow.set_statusbar_signal.connect(self.set_statusbar)
        self.workflow.reset_key_status_signal.connect(self.reset_key_status)
        self.workflow.set_text_browser_signal.connect(self.set_text_browser)

        # Look up the location and size of the main gui. Replace the location parameters with those
        # stored in the configuration file when the gui was closed last time. This way, the gui
        # memorizes its location between MPM invocations.
        (x0, y0, width, height) = self.geometry().getRect()
        x0 = int(self.configuration.conf.get('Hidden Parameters', 'main window x0'))
        y0 = int(self.configuration.conf.get('Hidden Parameters', 'main window y0'))
        self.setGeometry(x0, y0, width, height)
        self.configuration.set_protocol_level()

        # Actions in the workflow thread are triggered by setting the corresponding flag in the gui
        # thread to True. Here, trigger redirecting stdout to a file if requested in configuration.
        self.workflow.set_session_output_flag = True

        # If the configuration was not read in from a previous run (i.e. only default values have
        # been set so far), open the configuration editor gui.
        if not self.configuration.configuration_read:
            editor = ConfigurationEditor(self.configuration)
            editor.exec_()
            # If the user made changes to the configuration, choices of writing a protocol,
            # of focussing on a star or surface area, and of re-directing it to a file might have
            # changed. Therefore, repeat the two above initializations.
            if editor.configuration_changed:
                self.configuration.set_protocol_level()
                self.set_focus_button_labels()
                self.workflow.set_session_output_flag = True

        # Write the program version into the window title.
        self.setWindowTitle(QtCore.QString(self.configuration.version))

    def setChildrenFocusPolicy(self, policy):
        """
        This method is needed so that arrow key events are associated with this object. The arrow
        keys are used to make pointing corrections to the telescope mount.

        :param policy: focus policy to be used
        :return: -
        """

        def recursiveSetChildFocusPolicy(parentQWidget):
            for childQWidget in parentQWidget.findChildren(QtGui.QWidget):
                childQWidget.setFocusPolicy(policy)
                recursiveSetChildFocusPolicy(childQWidget)

        recursiveSetChildFocusPolicy(self)

    def edit_configuration(self):
        """
        This method is invoked with the "configuration" gui button. Open the configuration editor.
        If the configuration is changed, close the tile visualization window and restart the
        workflow.

        :return: -
        """
        editor = ConfigurationEditor(self.configuration)
        editor.exec_()
        # print >> sys.stderr, "config changed:",
        # editor.configuration_changed, \
        #     ", config initialized: ", self.configuration_initialized
        if editor.configuration_changed:
            self.configuration.set_protocol_level()
            self.set_focus_button_labels()
            self.workflow.set_session_output_flag = True
            self.do_restart()

    def do_restart(self):
        """
        Do a program restart. First close the tile visualization window. Then restart the workflow.

        :return: -
        """

        try:
            self.tv.close_tile_visualization()
        except AttributeError:
            pass
        self.start_workflow()

    def restart(self):
        """
        This method is invoked with the "restart" gui button. Set the context and write a
        confirmation message to the text browser. If "Enter" is pressed (in this context), the
        do_restart method (above) is called.

        :return: -
        """
        self.gui_context = "restart"
        self.set_text_browser("Do you really want to restart? "
                              "Confirm with 'enter', otherwise press 'esc'.")

    def start_workflow(self):
        """
        Start the observation workflow. Disable all keys which at this point do not make sense yet.
        Then check if camera automation is selected in the configuration. If so, remind the user
        to start the FireCapture program. If camera automation is de-selected, skip this reminder,
        and proceed with method "camera_connect_request_answered".

        :return: -
        """

        # Just in case: reset autoalignment.
        self.reset_autoalignment()
        self.disable_keys(
            [self.ui.alignment, self.ui.configure_drift_correction, self.ui.rotate_camera,
             self.ui.set_focus_area, self.ui.goto_focus_area, self.ui.start_continue_recording,
             self.ui.select_tile, self.ui.move_to_selected_tile, self.ui.set_tile_unprocessed,
             self.ui.set_all_tiles_unprocessed, self.ui.set_all_tiles_processed,
             self.ui.show_landmark, self.ui.autoalignment])

        self.camera_automation = (
            self.configuration.conf.getboolean("Workflow", "camera automation"))
        if not self.camera_automation:
            # No camera automation: Go directly to "camera_connect_request_answered"
            self.camera_connect_request_answered()
        else:
            # Pressing the "Enter" key in this context will invoke method
            # "camera_connect_request_answered"
            self.gui_context = "camera connect request"
            self.set_text_browser("Make sure that FireCapture is started, and that "
                                  "'MoonPanoramaMaker' is selected in the PreProcessing section. "
                                  "Confirm with 'enter', otherwise press 'esc'.")

    def camera_connect_request_answered(self):
        """
        Start camera initialization in workflow thread, if camera automation is active. This method
        is either invoked directly from method "start_workflow", or by hitting the "Enter" key
        within the "camera connect request".

        :return: -
        """

        self.workflow.camera_initialization_flag = True

    def camera_ready(self, de_center, m_diameter, phase_angle, pos_angle):
        """
        This method is started by the workflow thread when camera initialization is finished.
        Set status flags and compute the optimal coverage of the sunlit part of the moon with
        camera tiles.

        :param de_center: declination of the moon center
        :param m_diameter: diameter (angle) of the moon
        :param phase_angle: phase angle of the sunlit moon phase. 0 corresponds to new moon, and
        pi to full moon.
        :param pos_angle: position angle of the "north pole" of the sunlit moon phase, counted
        counterclockwise.
        :return: -
        """

        # Set status flags.
        self.camera_rotated = False
        self.focus_area_set = False
        self.autoalign_enabled = False

        # Compute the tesselation of the sunlit moon phase.
        self.tc = TileConstructor(self.configuration, de_center, m_diameter, phase_angle, pos_angle)

        # Open the Matplotlib window which displays the tesselation.
        self.tv = TileVisualization(self.configuration, self.tc)

        # Initialization is complete, set the main gui status bar and proceed with landmark
        # selection.
        self.initialized = True
        self.set_statusbar()
        self.select_new_landmark()

    def prompt_new_landmark_selection(self):
        """
        This method is invoked by pressing the gui button "New Landmark Selection". Before doing
        so, ask the user for acknowledgement. Hitting "Enter" leads to method "select_new_landmark".

        :return: -
        """

        self.gui_context = "new_landmark_selection"
        self.set_text_browser("Do you really want to set a new landmark and re-align mount? "
                              "Confirm with 'enter', otherwise press 'esc'.")

    def select_new_landmark(self):
        """
        Discard any previously selected landmark. De-activate all keys further down in the
        observation workflow and ask the user to select a new landmark. When the selection is done,
        compute the offset of the landmark relative to the moon center and enable further gui
        activities.

        :return: -
        """

        self.set_text_browser("Select a landmark from the list. ")
        # Invoke "set_landmark" method of the alignment object. It offers the user a gui interface
        # for landmark selection. Based on the selection, the method computes the center offset.
        self.workflow.al.set_landmark()
        if self.workflow.al.is_landmark_offset_set:
            # Enable the "Show Landmark" button.
            self.ui.show_landmark.setEnabled(True)
            # If not in autoalignment mode: enable the button for manual alignment.
            if not self.workflow.al.autoalign_initialized:
                self.ui.alignment.setEnabled(True)
            # Proceed with slewing the telescope to the approximate alignment point in the sky.
            self.wait_for_alignment()

    def show_landmark(self):
        """
        Show the currently selected landmark. ShowLandmark implements the gui. It is passed the
        "LandmarkSelection" object which keeps the name of the landmark. The name is used to read
        the corresponding picture file from subdirectory "landmark_pictures".
        :return: -
        """

        myapp = ShowLandmark(self.workflow.al.ls)
        myapp.exec_()

    def prompt_alignment(self):
        """
        The "Alignment" gui button is pressed. Ask the user for acknowledgement before a new
        alignment is done.

        :return: -
        """

        self.gui_context = "alignment"
        self.set_text_browser("Do you really want to perform a new alignment? "
                              "Confirm with 'enter', otherwise press 'esc'.")

    def wait_for_alignment(self):
        """
        Either the "Enter" key is pressed for acknowledgement, or "select_new_landmark" has been
        executed. Slew the telescope to the expected position of the alignment point in the sky.

        :return: -
        """

        # Disable all keys while the telescope is moving.
        self.save_key_status()
        self.set_text_browser("Slewing telescope to alignment point, please wait.")
        # If a tile is currently active, change its appearance in the tile visualization window to
        # either processed or unprocessed. Mark no tile as active.
        self.reset_active_tile()
        # Update status bar to show that telescope is not aimed at any tile.
        self.set_statusbar()
        print ""
        if self.configuration.protocol_level > 0:
            Miscellaneous.protocol("Preparing for alignment.")
        # Trigger telescope slewing in workflow thread.
        self.workflow.slew_to_alignment_point_flag = True

    def alignment_point_reached(self):
        """
        The workflow thread has sent the "alignment_point_reached_signal". Prompt the user to center
        the landmark in the camera live view.

        :return: -
        """

        # self.reset_key_status()
        # The telescope was aligned before, only small corrections are expected.
        if self.workflow.al.is_aligned:
            self.set_text_browser("Center landmark in camera live view (with arrow keys or "
                                  "telescope hand controller). Confirm with 'enter'.")
        # First alignment: a greater offset is to be expected.
        else:
            self.set_text_browser("Move telescope to the Moon (with arrow keys or telescope hand"
                                  " controller), then center landmark in camera live view. "
                                  "Confirm with 'enter'.")
        # Set the context for "Enter" key.
        self.gui_context = "alignment_point_reached"

    def perform_alignment(self):
        """
        The user has centered the landmark. Now take the alignment point.

        :return: -
        """

        # Trigger the workflow thread to read out the current coordinates as an alignment point.
        self.workflow.perform_alignment_flag = True

    def alignment_performed(self):
        """
        Triggered by the workflow thread when the alignment point has been processed.

        :return: -
        """

        self.reset_key_status()
        # Activate the "Correct for Drift" gui button if enough alignment points are available.
        if self.workflow.al.drift_dialog_enabled:
            self.ui.configure_drift_correction.setEnabled(True)
        # At this point correcting the camera orientation makes sense. Enable the gui button.
        self.ui.rotate_camera.setEnabled(True)
        self.set_statusbar()
        # If the camera is properly oriented, prompt the user for proceeding with video recording.
        if self.camera_rotated:
            self.set_text_browser("Continue video recording using the record group buttons.")
        # Otherwise (i.e. after first alignment), proceed with rotating the camera.
        else:
            self.perform_camera_rotation()

    def reset_autoalignment(self):
        """
        When the auto-alignment button is toggled back and forth, it changes color and text. This
        auxiliary method resets the button to its original (not triggered) state and reconnects it
        with the method which is invoked to start autoalignment. Finally, flags which indicate
        autoalignment to be active are reset to their original state.

        :return: -
        """

        self.ui.autoalignment.setStyleSheet("background-color: light gray")
        self.ui.autoalignment.setFont(QtGui.QFont("MS Shell Dlg 2", weight=QtGui.QFont.Normal))
        self.ui.autoalignment.setText('Auto-Alignment on - B')
        self.ui.autoalignment.setShortcut("b")
        # Reconnect the auto-alignment button with autoalignment initialization.
        self.ui.autoalignment.clicked.connect(self.prompt_autoalignment)
        # Reset alignment mode to manual.
        self.autoalign_enabled = False
        # Mark autoalignment as not initialized.
        self.workflow.al.autoalign_initialized = False

    def prompt_autoalignment(self):
        """
        The auto-alignment button is pressed. Prompt the user for acknowledgement and set the
        context for the "Enter" key.

        :return: -
        """

        self.gui_context = "autoalignment"
        self.set_text_browser("Do you really want to switch on auto-alignment? "
                              "Confirm with 'enter', otherwise press 'esc'.")

    def wait_for_autoalignment(self):
        """
        The user has acknowledged that auto-alignment is to be switched on. Change the appearance of
        the gui button and slew to the alignment point.

        :return: -
        """

        # Disable the "Alignment" button for manual alignment, and de-activate all buttons while the
        # telescope slews to the alignment point.
        self.ui.alignment.setEnabled(False)
        self.save_key_status()
        # the "autoalign_enabled" flag tells the workflow thread, that this is no manual alignment.
        # In particular, when the point is reached, the workflow thread will emit the
        # "autoalignment_point_reached_signal".
        self.autoalign_enabled = True
        # Reconfigure the auto-alignment button.
        self.ui.autoalignment.clicked.connect(self.prompt_autoalignment_off)
        self.ui.autoalignment.setStyleSheet("background-color: red; color: white")
        self.ui.autoalignment.setFont(QtGui.QFont("MS Shell Dlg 2", weight=QtGui.QFont.Bold))
        self.ui.autoalignment.setText('Auto-Alignment off - B')
        self.ui.autoalignment.setShortcut("b")
        # Write a text message to the text browser, reset the active tile in the tile visualization
        # window, update the status bar and trigger the workflow thread to move the telescope.
        self.set_text_browser("Slewing telescope to alignment point, please wait.")
        self.reset_active_tile()
        self.set_statusbar()
        print ""
        if self.configuration.protocol_level > 0:
            Miscellaneous.protocol("Preparing for auto-alignment.")
        self.workflow.slew_to_alignment_point_flag = True

    def autoalignment_point_reached(self):
        """
        Triggered by the workflow thread when the telescope has reached the expected coordinates of
        the alignment point. In auto-alignment, the first alignment is done by the user manually.
        When the user has acknowledged that the landmark is properly centered, the reference frame
        still image is captured. In later alignment operations the shift relative to this reference
        frame is measured and used to determine the misalignment angles.

        :return: -
        """

        # self.reset_key_status()
        # Prompt the user to center the landmark and to confirm with pressing "Enter".
        self.set_text_browser("Center landmark in camera live view (with arrow keys or "
                              "telescope hand controller). Confirm with 'enter'.")
        self.gui_context = "autoalignment_point_reached"

    def perform_autoalignment(self):
        """
        The "Enter" key was pressed in context "autoalignment_point_reached". Trigger the workflow
        thread to initialize autoalignment.

        :return: -
        """

        self.set_text_browser("Initializing auto-alignment, please wait")
        # self.save_key_status()
        self.workflow.perform_autoalignment_flag = True

    def autoalignment_performed(self, success):
        """
        Triggered by the "autoalignment_performed_signal" in the workflow thread. Auto-alignment
        initialization might have failed, e.g. if the reference frame captured was too blurry. In
        this case de-activate auto-alignment and re-activate manual alignment.

        :param success: True if auto-alignment initialization was successful, False otherwise.
        :return: -
        """

        self.reset_key_status()
        # If auto-alignment has been initialized successfully, read configuration parameters and
        # prepare for video acquisition loop.
        if success:
            self.min_autoalign_interval = (
                self.configuration.conf.getfloat("Alignment", "min autoalign interval"))
            self.max_autoalign_interval = (
                self.configuration.conf.getfloat("Alignment", "max autoalign interval"))
            # The configuration parameter is in percent. In "workflow" it is compared to a value
            # between 0. and 1.
            self.max_alignment_error = (self.configuration.conf.getfloat("Alignment",
                                        "max alignment error")) / 100.
            # Initialize the maximum time between auto-aligns to the minimum acceptable value.
            # The interval will be increased at next auto-align if the correction is very small.
            self.max_seconds_between_autoaligns = self.min_autoalign_interval
            if self.workflow.al.drift_dialog_enabled:
                self.ui.configure_drift_correction.setEnabled(True)
            self.set_statusbar()
            self.set_text_browser("Continue video recording using the record group buttons.")
        # Auto-alignment initialization failed. Reset buttons to manual alignment and mark
        # auto-alignment as not enabled (same activity as if triggered by the user via gui).
        else:
            self.wait_for_autoalignment_off()

    def prompt_autoalignment_off(self):
        """
        Connected to the "Auto-Align off" gui button while auto-alignment is active. Ask the user
        before really switching back to manual alignment.

        :return: -
        """

        # Set the context for "Enter" detection and write prompt message to the text browser.
        self.gui_context = "autoalignment_off"
        self.set_text_browser("Do you really want to switch off auto-alignment? "
                              "Confirm with 'enter', otherwise press 'esc'.")

    def wait_for_autoalignment_off(self):
        """
        Invoked either automatically (auto-alignment failed) or by the user. Switch back to
        manual alignment and reset auto-alignment button.

        :return: -
        """

        self.reset_key_status()
        # Enable manual alignment, disable auto-alignment.
        self.ui.alignment.setEnabled(True)
        self.reset_autoalignment()
        # Control is given back to the user. Write protocol message and update the status bar.
        if self.configuration.protocol_level > 0:
            Miscellaneous.protocol("Auto-alignment has been disabled.")
        self.set_text_browser("Auto-alignment disabled, "
                              "continue video recording using the record group buttons.")
        self.set_statusbar()

    def configure_drift_correction(self):
        """
        The "Correct for Drift" button is pressed. Open a gui dialog for displaying available
        alignment points and selecting points used for drift determination.

        :return: -
        """

        drift_configuration_window = ComputeDriftRate(self.configuration, self.workflow.al)
        drift_configuration_window.exec_()
        self.set_statusbar()

    def prompt_rotate_camera(self):
        """
        The "Camera Orientation" button is pressed. Prompt the user for acknowledgement, because
        in the middle of video acquisition this operation has severe consequences.

        :return: -
        """

        # Set the context and display the prompt message.
        self.gui_context = "rotate_camera"
        self.set_text_browser("Do you really want to rotate camera? "
                              "All tiles will be marked as un-processed. "
                              "Confirm with 'enter', otherwise press 'esc'.")

    def perform_camera_rotation(self):
        """
        Invoked either automatically after first alignment (method "alignment_performed") or on
        user request.

        :return: -
        """

        # Switch back to manual alignment, if auto-alignment was active
        self.ui.alignment.setEnabled(True)
        self.reset_autoalignment()
        # Disable keys further down in observation workflow.
        self.disable_keys(
            [self.ui.set_focus_area, self.ui.goto_focus_area, self.ui.start_continue_recording,
             self.ui.select_tile, self.ui.move_to_selected_tile, self.ui.set_tile_unprocessed,
             self.ui.set_all_tiles_unprocessed, self.ui.set_all_tiles_processed,
             self.ui.autoalignment])
        # Display info for the user, and trigger workflow thread to move the telescope to the
        # center point of the sunlit moon limb.
        self.set_text_browser("Slewing telescope to Moon limb, please wait.")
        self.workflow.slew_to_moon_limb_flag = True

    def prompt_camera_rotated_acknowledged(self):
        """
        Triggered by the workflow thread ("moon_limb_centered_signal") when the telescope has
        reached the moon limb midpoint. Prompt the user to turn the camera properly.

        :return: -
        """

        # Set the context and display the prompt message.
        self.gui_context = "perform_camera_rotation"
        self.set_text_browser("Rotate camera until the moon limb at the center of the FOV is "
                              "oriented vertically. Confirm with 'enter'.")

    def finish_camera_rotation(self):
        """
        The user has rotated the camera and acknowledged by pressing "Enter". The system is now
        ready for video acquisition. Activate the buttons of the record group and display an
        info message in the text browser.

        :return: -
        """

        self.camera_rotated = True
        if self.configuration.protocol_level > 0:
            Miscellaneous.protocol("Camera rotation finished")
        # Activate gui buttons. Auto-alignment is possible only when camera_automation is active.
        self.enable_keys([self.ui.set_focus_area, self.ui.start_continue_recording,
                          self.ui.select_tile, self.ui.set_tile_unprocessed,
                          self.ui.set_all_tiles_unprocessed, self.ui.set_all_tiles_processed])
        self.ui.autoalignment.setEnabled(self.camera_automation)
        # When the camera orientation has changed, all tiles are marked "unprocessed"
        self.tv.mark_all_unprocessed()
        self.workflow.active_tile_number = -1
        # Update the status bar and display message.
        self.set_statusbar()
        if self.configuration.conf.getboolean("Workflow", "focus on star"):
            self.set_text_browser("Start video recording using the record group buttons, "
                                  "or select the focus star.")
        else:
            self.set_text_browser("Start video recording using the record group buttons, "
                                  "or select the focus area.")

    def set_focus_area(self):
        """
        Triggered by the "Select Focus Area" gui button. The user is requested to move the telescope
        manually to an appropriate location for focus checking, and to confirm the position with
        pressing "Enter". This position is stored. The telescope can be moved back to this point
        later by pressing "Goto Focus Area".

        :return: -
        """

        # Write the user prompt to the text browser.
        if self.configuration.conf.getboolean("Workflow", "focus on star"):
            self.set_text_browser("Move telescope to focus star. Confirm with 'enter', otherwise "
                                  "press 'esc'.")
        else:
            self.set_text_browser("Move telescope to focus area. Confirm with 'enter', otherwise "
                                  "press 'esc'.")
        # If the telescope was aimed at a tile, reset its "active" status, update the status bar,
        # and set the context for the "Enter" key.
        self.reset_active_tile()
        self.set_statusbar()
        self.gui_context = "set_focus_area"

    def finish_set_focus_area(self):
        """
        The user has acknowledged the position of the focus area. Trigger the workflow thread to
        capture the position.

        :return: -
        """

        if self.configuration.protocol_level > 0:
            if self.configuration.conf.getboolean("Workflow", "focus on star"):
                Miscellaneous.protocol("The user has selected a new focus star")
            else:
                Miscellaneous.protocol("The user has selected a new focus area")
        self.workflow.set_focus_area_flag = True

    def set_focus_area_finished(self):
        """
        Triggered by the "focus_area_set_signal" from the workflow thread. The focus area position
        is captured. Now the user may proceed with video acquisition.

        :return: -
        """

        # Mark the focus area as being recorded, update status bar, and display message.
        self.focus_area_set = True
        self.set_statusbar()
        self.set_text_browser("Start / continue video recording using the record group buttons.")
        # Enable the gui button "Goto Focus Area"
        self.ui.goto_focus_area.setEnabled(True)

    def goto_focus_area(self):
        """
        Triggered by pressing the "Goto Focus Area" button. Move the telescope to the recorded
        position where camera focus can be checked.

        :return: -
        """

        if self.configuration.protocol_level > 0:
            Miscellaneous.protocol("Goto focus area")
        # If the telescope was aimed at a tile, reset its "active" status, update the status bar,
        # display a message and trigger the workflow thread to move the telescope.
        self.reset_active_tile()
        self.set_statusbar()
        self.set_text_browser("After focusing, continue video recording using the record "
                              "group buttons.")
        self.workflow.goto_focus_area_flag = True

    def set_focus_button_labels(self):
        """
        The user can choose to focus on a star or on a surface feature. Set the button labels
        accordingly.

        :return: -
        """

        if self.configuration.conf.getboolean("Workflow", "focus on star"):
            self.ui.set_focus_area.setText('Select Focus Star - F')
            self.ui.set_focus_area.setShortcut("f")
            self.ui.goto_focus_area.setText('GoTo Focus Star - G')
            self.ui.goto_focus_area.setShortcut("g")
        else:
            self.ui.set_focus_area.setText('Select Focus Area - F')
            self.ui.set_focus_area.setShortcut("f")
            self.ui.goto_focus_area.setText('GoTo Focus Area - G')
            self.ui.goto_focus_area.setShortcut("g")

    def start_continue_recording(self):
        """
        Record the next video. Identify the next tile to be recorded. If there is one left,
        trigger the workflow thread to move the telescope to the tile's location and record the
        video.

        This method is invoked from three places:
        - Manually by pressing the gui button "Start / Continue Recording"
        - In manual camera mode, by pressing the enter key when the user has taken a video.
        - In automatic camera mode, when the "signal_from_camera" method is executed.

        :return: -
        """

        # Disable the "Move to Selected Tile" button, because after this operation no selection is
        # active any more.
        self.ui.move_to_selected_tile.setEnabled(False)
        # De-activate all keys while the operation is in progress.
        self.save_key_status()
        if self.configuration.protocol_level > 0:
            Miscellaneous.protocol("Start/continue recording.")
        # If guiding was active (from last video recording), stop it now.
        if self.workflow.telescope.guiding_active:
            self.workflow.telescope.stop_guiding()
        # Check if the currently active tile is marked "processed", change its display in the
        # tile visualization window accordingly. It will not be marked as "active" any more.
        if self.tc.list_of_tiles_sorted[self.workflow.active_tile_number]['processed']:
            self.mark_processed()
        # Look for the next unprocessed tile.
        (self.next_tile, next_tile_index) = self.find_next_unprocessed_tile()

        # There is no unprocessed tile left, set the "all_tiles_recorded" flag, display a message,
        # re-activate gui keys and exit the viceo acquisition loop
        if self.next_tile is None:
            self.all_tiles_recorded = True
            self.ui.move_to_selected_tile.setEnabled(False)
            self.set_statusbar()
            self.set_text_browser("All tiles have been recorded.")
            if self.configuration.protocol_level > 0:
                Miscellaneous.protocol("All tiles have been recorded.")
            self.reset_key_status()
        # There is at least one tile left. Set "active_tile_number" and change its display in the
        # tile visualization window. Initialize the "camera_interrupted" flag. (The user may set
        # it to True during video acquisition.) Finally, trigger the workflow thread to record the
        # video.
        else:
            self.workflow.active_tile_number = next_tile_index
            self.tv.mark_active(self.workflow.active_tile_number)
            if self.camera_automation:
                self.camera_interrupted = False
            self.workflow.slew_to_tile_and_record_flag = True

    def find_next_unprocessed_tile(self):
        """
        Find the next tile to be recorded, i.e. which is not marked as "processed". Start searching
        with the index following the current "active_tile_number".

        A special case is when an auto-alignment error is too large. Then the videos taken since
        the previous auto-alignment are discarded and have to be repeated. In this case, go back to
        the first of these tiles and continue from there.

        :return: (next tile, index of next tile), or (None, -1) if no "unprocessed" tile is left.
        """

        # Initialize an index vector, starting with 0. Its length is the total number of tiles.
        indices = range(len(self.tc.list_of_tiles_sorted))

        # After failure in auto-alignment, let the index vector start with index "repeat_from_here",
        # and wrap around.
        if self.workflow.repeat_from_here != -1:
            indices_shifted = indices[self.workflow.repeat_from_here:] + indices[
                                        0:self.workflow.repeat_from_here]
            self.workflow.repeat_from_here = -1
        # Let the index vector start with index "active_tile_number", and wrap around.
        elif self.workflow.active_tile_number != -1:
            indices_shifted = indices[self.workflow.active_tile_number:] + indices[
                                        0:self.workflow.active_tile_number]
        # No "repeat from here" and no "active_tile_number" set: Keep the tiles in original order.
        else:
            indices_shifted = indices

        # Look for first "unprocessed" tile in shifted order. Leave the loop when the first is
        # found.
        next_tile = None
        next_tile_index = -1
        for i in indices_shifted:
            tile = self.tc.list_of_tiles_sorted[i]
            if not tile['processed']:
                next_tile = tile
                next_tile_index = i
                break

        return (next_tile, next_tile_index)

    def mark_processed(self):
        """
        Change the color of the currently "active_tile_number" in the tile visualization window to
        indicate that it is "processed". If auto-alignment is active, keep a list of tiles processed
        since last alignment point (for later rollback).

        :return: -
        """

        self.tv.mark_processed([self.workflow.active_tile_number])
        # After successful exposure, put active tile on list of tiles processed since last
        # auto-align. This list will be reset to unprocessed later if the error in the next
        # auto-align is too large.
        if self.workflow.al.autoalign_initialized:
            self.workflow.tile_indices_since_last_autoalign.append(self.workflow.active_tile_number)

    def select_tile(self):
        """
        Triggered by pressing the "Select Tile" bui button. Open a gui for selecting a tile index.
        Then enable the "Move to Selected Tile" button which can be used to drive the mount to the
        tile's position.

        :return: -
        """

        if self.workflow.active_tile_number > -1:
            # There is an active tile. If it is still unprocessed, mark it as such in the tile
            # visualization window.
            if (self.tc.list_of_tiles_sorted[self.workflow.active_tile_number][
                    'processed'] == False):
                self.tv.mark_unprocessed([self.workflow.active_tile_number])
        # Open the dialog for selecting a tile number. Class TileNumberInput (in this module, see
        # below) extends the TileNumberInputDialog in module tile_number_input_dialog. Set the
        # context to "workflow", so that on dialog closing the selected value will be stored in
        # "active_tile_number" of the workflow object.
        self.tni = TileNumberInput(self.workflow.active_tile_number, self.workflow)
        self.tni.exec_()
        if self.configuration.protocol_level > 1:
            Miscellaneous.protocol("Tile number " + str(self.workflow.active_tile_number) +
                                   " was selected.")
        self.ui.move_to_selected_tile.setEnabled(True)
        # Clear the text browser.
        self.set_text_browser("")

    def set_tile_unprocessed(self):
        """
        Tiles can be selected either done by drawing a rectangle in the tile visualization
        window, or by the variable "active_tile_number" of the workflow object not being set to -1.
        First, check if one mechanism results in an non-empty list. If so, present the list to the
        user and ask for acknowledgement that these tiles should be marked as unprocessed.

        :return: -
        """

        # Initialize the list with (potentially) selected tiles in visualization window.
        self.selected_tile_numbers = self.tv.get_selected_tile_numbers()
        # If empty, check if there is a non-trivial active_tile_number.
        if len(self.selected_tile_numbers) == 0 and self.workflow.active_tile_number != -1:
            self.selected_tile_numbers.append(self.workflow.active_tile_number)
        # If one of the mechanisms produced a non-empty list, set the gui context and ask the
        # user to confirm the operation.
        if len(self.selected_tile_numbers) > 0:
            self.selected_tile_numbers_string = str(self.selected_tile_numbers)[1:-1]
            self.gui_context = "set_tile_unprocessed"
            self.set_text_browser(
                "Do you want to mark tile(s) " + self.selected_tile_numbers_string + " as "
                "un-processed? Confirm with 'enter', otherwise press 'esc'.")

    def mark_unprocessed(self):
        """
        The user has confirmed that the selected tile numbers should be marked unprocessed. Method
        "mark_unprocessed" in class "TileVisualization" both sets the corresponding flags and
        changes the color of the tiles in the visualization window.

        :return: -
        """

        # The action is performed in class TileVisualization.
        self.tv.mark_unprocessed(self.selected_tile_numbers)
        if self.configuration.protocol_level > 0:
            Miscellaneous.protocol("Tile(s) " + self.selected_tile_numbers_string +
                                   " are marked unprocessed.")
        # Since at least one tile is unprocessed now, reset the "all_tiles_recorded" flag.
        self.all_tiles_recorded = False
        self.set_text_browser("")
        self.set_statusbar()

    def set_all_tiles_unprocessed(self):
        """
        Triggered by pressing the "Set All Tiles Unprocessed" button. Set the context for the
        "Enter" key and ask the user for confirmation.

        :return: -
        """

        self.gui_context = "set_all_tiles_unprocessed"
        self.set_text_browser("Do you want to mark all tiles "
                              "as un-processed? Confirm with 'enter', "
                              "otherwise press 'esc'.")

    def mark_all_tiles_unprocessed(self):
        """
        The user has confirmed that all tiles should be set unprocessed by pressing the "Enter" key.
        Method "mark_all_unprocessed" in class "TileVisualization" both sets the corresponding flags
        and changes the color of the tiles in the visualization window.

        :return: -
        """

        # Perform the task in class TileVisualization.
        self.tv.mark_all_unprocessed()
        self.all_tiles_recorded = False
        # Reset the active tile number. Processing will start from the beginning.
        self.workflow.active_tile_number = -1
        self.set_text_browser("")
        if self.configuration.protocol_level > 0:
            Miscellaneous.protocol("All tiles are marked as unprocessed.")

    def set_all_tiles_processed(self):
        """
        Triggered by pressing the "Set All Tiles Processed" button. Set the context for the
        "Enter" key and ask the user for confirmation.

        :return: -
        """

        self.gui_context = "set_all_tiles_processed"
        self.set_text_browser("Do you want to mark all tiles "
                              "as processed? Confirm with 'enter', "
                              "otherwise press 'esc'.")

    def mark_all_tiles_processed(self):
        """
        The user has confirmed that all tiles should be set processed by pressing the "Enter" key.
        Method "mark_all_processed" in class "TileVisualization" both sets the corresponding flags
        and changes the color of the tiles in the visualization window.

        :return: -
        """

        self.tv.mark_all_processed()
        # Mark the recording process as finished. No more tiles to record.
        self.all_tiles_recorded = True
        self.workflow.active_tile_number = -1
        self.set_text_browser("All tiles are marked as processed.")
        if self.configuration.protocol_level > 0:
            Miscellaneous.protocol("All tiles are marked as processed.")

    def move_to_selected_tile(self):
        """
        Triggered by the gui button "Move to Selected Tile". Mark the tile active in the tile
        visualization window and trigger the workflow thread to move the telescope to the tile.

        :return: -
        """

        # Get the tile object from the list kept by the TileConstructor object.
        self.selected_tile = self.tc.list_of_tiles_sorted[self.workflow.active_tile_number]
        if self.configuration.protocol_level > 0:
            Miscellaneous.protocol("Goto selected tile number " +
                                   str(self.workflow.active_tile_number))
        # Mark the tile active in the tile visualization window, refresh the status bar.
        self.tv.mark_active(self.workflow.active_tile_number)
        self.set_statusbar()
        # Clear the text browser and instruct the workflow thread to move the mount.
        self.set_text_browser("")
        self.workflow.move_to_selected_tile_flag = True

    def reset_active_tile(self):
        """
        If a tile has been selected as active, but then it is not processed, it can be reset with
        this method. It is marked as unprocessed in the TileConstructor object and in the tile
        visualization window, and the currently "active_tile_number" is reset to -1.

        :return: -
        """

        # There is a selected active tile.
        if self.workflow.active_tile_number > -1:
            if (self.tc.list_of_tiles_sorted[self.workflow.active_tile_number][
                    'processed'] == False):
                self.tv.mark_unprocessed([self.workflow.active_tile_number])
            else:
                self.mark_processed()
        self.workflow.active_tile_number = -1

    def save_key_status(self):
        """
        For all buttons of the main gui: save the current state (enabled / disabled), then disable
        all buttons. The saved state is restored with method "reset_key_status".

        :return: -
        """

        # Initialize the status list.
        self.saved_key_status = []
        # For each button store a boolean indicating its being enabled / disabled.
        for button in self.button_list:
            self.saved_key_status.append(button.isEnabled())
            # Disable the button.
            button.setEnabled(False)
        # Set a flag indicating that the key status has been saved.
        self.key_status_saved = True

    def change_saved_key_status(self, button, new_status):
        """
        During a long-running process the gui buttons are disabled by a call of "save_key_status".
        This method is used if in such a situation the saved status of a button must be changed. At
        the next call of "reset_key_status" this button will then be changed to this new status
        insted to the one saved originally.

        :param button: button object in self.button_list
        :param new_status: new saved status of this button. True if "isEnabled", otherwise False.
        :return: -
        """

        button_index = self.button_list.index(button)
        self.saved_key_status[button_index] = new_status

    def reset_key_status(self):
        """
        Reverse operation to save_key_status: Restore the status of all gui buttons and reset the
        flag "key_status_saved" to False.

        :return: -
        """

        if self.key_status_saved:
            map(lambda x, y: x.setEnabled(y), self.button_list, self.saved_key_status)
            self.key_status_saved = False

    def disable_keys(self, button_list):
        """
        Disable a specific list of gui buttons.

        :param button_list: list with selected gui buttons
        :return: -
        """

        for item in button_list:
            item.setEnabled(False)

    def enable_keys(self, button_list):
        """
        Enable a specific list of gui buttons.

        :param button_list: list with selected gui buttons
        :return: -
        """

        for item in button_list:
            item.setEnabled(True)

    def signal_from_camera(self):
        """
        In "camera automation" mode, the camera has emitted its signal "signal" when video
        acquisition is finished. (The signal is connected with this method in the workflow thread.)
        If in the meantime the "Esc" key was pressed, stop the video acquisition loop. Otherwise
        continue with method "start_continue_recording".

        :return:
        """

        if self.camera_interrupted:
            self.camera_interrupted = False
        else:
            self.reset_key_status()
            self.start_continue_recording()

    def keyPressEvent(self, event):
        """
        Define activities to be performed when specific keyboard keys are pressed. This method
        overrides the standard activity of the main window class.

        :param event: event object
        :return: -
        """

        # To keep apart the various activities which are specified by pressing "Enter", the
        # gui_context variable carries the context where the program waits for the "Enter" event.
        # The context variable is reset and a specific action is triggered.
        if type(event) == QtGui.QKeyEvent and event.isAutoRepeat() == False:
            if event.key() == 16777220:  # Enter key
                if self.gui_context == "restart":
                    self.gui_context = ""
                    self.do_restart()
                elif self.gui_context == "camera connect request":
                    self.gui_context = ""
                    self.camera_connect_request_answered()
                elif self.gui_context == "new_landmark_selection":
                    self.gui_context = ""
                    self.select_new_landmark()
                elif self.gui_context == "alignment":
                    self.gui_context = ""
                    self.wait_for_alignment()
                elif self.gui_context == "alignment_point_reached":
                    self.gui_context = ""
                    self.perform_alignment()
                elif self.gui_context == "autoalignment":
                    self.gui_context = ""
                    self.wait_for_autoalignment()
                elif self.gui_context == "autoalignment_point_reached":
                    self.gui_context = ""
                    self.perform_autoalignment()
                elif self.gui_context == "autoalignment_off":
                    self.gui_context = ""
                    self.wait_for_autoalignment_off()
                elif self.gui_context == "rotate_camera":
                    self.gui_context = ""
                    self.perform_camera_rotation()
                elif self.gui_context == "perform_camera_rotation":
                    self.gui_context = ""
                    self.finish_camera_rotation()
                elif self.gui_context == "set_focus_area":
                    self.gui_context = ""
                    self.finish_set_focus_area()
                elif self.gui_context == "start_continue_recording":
                    self.reset_key_status()
                    self.gui_context = ""
                    self.mark_processed()
                    self.start_continue_recording()
                elif self.gui_context == "set_tile_unprocessed":
                    self.gui_context = ""
                    self.mark_unprocessed()
                elif self.gui_context == "set_all_tiles_unprocessed":
                    self.gui_context = ""
                    self.mark_all_tiles_unprocessed()
                elif self.gui_context == "set_all_tiles_processed":
                    self.gui_context = ""
                    self.mark_all_tiles_processed()

            # Escape key:
            elif event.key() == QtCore.Qt.Key_Escape:
                # If "key_status_saved" is True, keys are disabled because an operation
                # is going on.
                if self.key_status_saved:
                    # Tell the user to be patient (no immediate action)
                    self.set_text_browser("Please wait")
                    if self.configuration.protocol_level > 0:
                        Miscellaneous.protocol("The user has interrupted the workflow.")
                    self.gui_context = ""
                    # Tell the workflow thread that the recording loop is to be interrupted.
                    self.workflow.escape_pressed_flag = True
                    # By setting this flag, the automatic exposure loop is interrupted in
                    # method "signal_from_camera".
                    self.camera_interrupted = True
                else:
                    self.set_text_browser("")
                    self.gui_context = ""

            # The arrow keys start moving the telescope in the direction indicated.
            elif event.key() == QtCore.Qt.Key_Down:
                self.workflow.telescope.move_south()
            elif event.key() == QtCore.Qt.Key_Up:
                self.workflow.telescope.move_north()
            elif event.key() == QtCore.Qt.Key_Left:
                self.workflow.telescope.move_east()
            elif event.key() == QtCore.Qt.Key_Right:
                self.workflow.telescope.move_west()

    def keyReleaseEvent(self, event):
        """
        The telescope moves as long as an arrow key is pressed. When it is released, tell the
        telescope thread to stop the motion.

        :param event: event object
        :return: -
        """
        if type(event) == QtGui.QKeyEvent and event.isAutoRepeat() == False:
            if event.key() == QtCore.Qt.Key_Down:
                self.workflow.telescope.stop_move_south()
            if event.key() == QtCore.Qt.Key_Up:
                self.workflow.telescope.stop_move_north()
            if event.key() == QtCore.Qt.Key_Left:
                self.workflow.telescope.stop_move_east()
            if event.key() == QtCore.Qt.Key_Right:
                self.workflow.telescope.stop_move_west()

    def set_text_browser(self, text):
        """
        Display a text in the text browser field of the main gui. This is used for messages to the
        user and for prompts for user actions.

        :param text: string to be displayed in the text browser
        :return: -
        """

        self.ui.prompt_text_browser.setText(text)

    def set_statusbar(self):
        """
        The status bar at the bottom of the main gui summarizes various infos on the process status.
        Depending of the situation within the observation process, specific information may or may
        not be available. Read out flags to decide which infos to present. The status information
        is concatenated into a single "status_text" which eventually is written into the main gui
        status bar.

        :return: -
        """

        # Show if the process is initialized or not.
        if self.initialized:
            status_text = "Initialized"
        else:
            status_text = ""
        # Show name of selected landmark.
        if self.workflow.al.is_landmark_offset_set:
            status_text += ", landmark %s selected" % self.workflow.al.ls.selected_landmark
        # Display current alignment corrections in RA, DE (in arc minutes)
        if self.workflow.al.is_aligned:
            align_ra = degrees(self.workflow.al.ra_correction) * 60.
            align_de = degrees(self.workflow.al.de_correction) * 60.
            status_text += (
                ", mount alignment: (" + '%3.1f' % align_ra + "'," + '%3.1f' % align_de + "')")
        # If auto-alignment is active, add a note on that.
        if self.autoalign_enabled:
            status_text += ", auto-align on"
        # Show drift rates in arc minutes per hour.
        if self.workflow.al.is_drift_set:
            drift_ra = degrees(self.workflow.al.drift_ra) * 216000.
            drift_de = degrees(self.workflow.al.drift_de) * 216000.
            status_text += (
                ", drift rate: (" + '%4.2f' % drift_ra + "'/h, " + '%4.2f' % drift_de + "'/h)")
        # Tell if camera is properly oriented.
        if self.camera_rotated:
            status_text += ", camera rotated"
        # Tell if a focus area has been selected.
        if self.focus_area_set:
            if self.configuration.conf.getboolean("Workflow", "focus on star"):
                status_text += ", focus star selected"
            else:
                status_text += ", focus area selected"
        # Tell at which tile the telescope is currently pointing.
        if self.workflow.active_tile_number >= 0:
            status_text += ", aimed at tile " + str(self.workflow.active_tile_number)
        # Tell if all tiles have been recorded.
        if self.workflow.all_tiles_recorded:
            status_text += ", all tiles recorded"
        # Write the complete message to the status bar.
        self.ui.statusbar.showMessage(status_text)

    def closeEvent(self, evnt):
        """
        When the user asks to close the main gui, a dialog is presented asking for confirmation.
        In case the user confirms, do cleanup activities before closing the main gui.

        :param evnt: event object
        :return: -
        """

        # Ask the user for confirmation.
        quit_msg = "Are you sure you want to exit the MoonPanoramaMaker " \
                   "program?"
        reply = QtGui.QMessageBox.question(self, 'Message', quit_msg, QtGui.QMessageBox.Yes,
                                           QtGui.QMessageBox.No)
        # Positive reply: Do it.
        if reply == QtGui.QMessageBox.Yes:
            evnt.accept()

            # Store the geometry of main window, so it is placed the same at next program start.
            (x0, y0, width, height) = self.geometry().getRect()
            self.configuration.conf.set('Hidden Parameters', 'main window x0', str(x0))
            self.configuration.conf.set('Hidden Parameters', 'main window y0', str(y0))
            try:
                # The tile visualization window geometry is saved as well before closing the window.
                self.tv.close_tile_visualization()
            except AttributeError:
                pass
            # Write the whole configuration back to disk.
            self.configuration.write_config()
            # Stop the workflow thread. This will terminate the camera thread and close the protocol
            # file.
            self.workflow.exiting = True
            time.sleep(4. * self.workflow.run_loop_delay)
        else:
            # No confirmation by the user: Don't stop program execution.
            evnt.ignore()


class TileNumberInput(QtGui.QDialog, Ui_TileNumberInputDialog):
    """
    This class extends the (generated) class Ui_TileNumberInputDialog. Methods __init__ and accept
    override their parent versions.

    """

    def __init__(self, start_value, value_context, parent=None):
        """
        Initialization of the TileNumberInputDialog.

        :param start_value: the spinBox is preset at this particular start value.
        :param value_context: name of an object where the entered spinBox value is to be stored.
        """
        self.value_context = value_context
        QtGui.QDialog.__init__(self, parent)
        self.setupUi(self)
        self.spinBox.setFocus()
        # Initialize spinBox to current tile number
        self.spinBox.setValue(start_value)

    def accept(self):
        """
        On exit from the dialog, save the selected tile number.

        :return: -
        """

        # Store the tile number in instance variable "active_tile_number" in the object
        # "value_context", and close the window.
        self.value_context.active_tile_number = self.spinBox.value()
        self.close()


if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    myapp = StartQT4()
    myapp.show()
    sys.exit(app.exec_())
