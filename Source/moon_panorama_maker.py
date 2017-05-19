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

from PyQt4 import QtCore, QtGui

from compute_drift_rate import ComputeDriftRate
from configuration import Configuration
from configuration_editor import ConfigurationEditor
from qtgui import Ui_MainWindow
from show_landmark import ShowLandmark
from tile_constructor import TileConstructor
from tile_number_input_dialog import Ui_TileNumberInputDialog
from tile_visualization import TileVisualization
from workflow import Workflow


class TileNumberInput(QtGui.QDialog, Ui_TileNumberInputDialog):
    def __init__(self, start_value, value_context, parent=None):
        self.value_context = value_context
        QtGui.QDialog.__init__(self, parent)
        self.setupUi(self)
        self.spinBox.setFocus()
        self.spinBox.setValue(start_value)

    def accept(self):
        self.value_context.active_tile_number = self.spinBox.value()
        self.close()


class StartQT4(QtGui.QMainWindow):
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.setChildrenFocusPolicy(QtCore.Qt.NoFocus)

        self.button_list = []
        self.ui.edit_configuration.clicked.connect(self.edit_configuration)
        self.button_list.append(self.ui.edit_configuration)
        self.ui.restart.clicked.connect(self.restart)
        self.button_list.append(self.ui.restart)
        self.ui.new_landmark_selection.clicked.connect(
            self.prompt_new_landmark_selection)
        self.button_list.append(self.ui.new_landmark_selection)
        self.ui.alignment.clicked.connect(self.prompt_alignment)
        self.button_list.append(self.ui.alignment)
        self.ui.configure_drift_correction.clicked.connect(
            self.configure_drift_correction)
        self.button_list.append(self.ui.configure_drift_correction)
        self.ui.rotate_camera.clicked.connect(self.prompt_rotate_camera)
        self.button_list.append(self.ui.rotate_camera)
        self.ui.set_focus_area.clicked.connect(self.set_focus_area)
        self.button_list.append(self.ui.set_focus_area)
        self.ui.goto_focus_area.clicked.connect(self.goto_focus_area)
        self.button_list.append(self.ui.goto_focus_area)
        self.ui.start_continue_recording.clicked.connect(
            self.start_continue_recording)
        self.button_list.append(self.ui.start_continue_recording)
        self.ui.select_tile.clicked.connect(self.select_tile)
        self.button_list.append(self.ui.select_tile)
        self.ui.move_to_selected_tile.clicked.connect(
            self.move_to_selected_tile)
        self.button_list.append(self.ui.move_to_selected_tile)
        self.ui.set_tile_unprocessed.clicked.connect(self.set_tile_unprocessed)
        self.button_list.append(self.ui.set_tile_unprocessed)
        self.ui.set_all_tiles_unprocessed.clicked.connect(
            self.set_all_tiles_unprocessed)
        self.button_list.append(self.ui.set_all_tiles_unprocessed)
        self.ui.set_all_tiles_processed.clicked.connect(
            self.set_all_tiles_processed)
        self.button_list.append(self.ui.set_all_tiles_processed)
        self.ui.show_landmark.clicked.connect(
            self.show_landmark)
        self.button_list.append(self.ui.show_landmark)
        self.ui.autoalignment.clicked.connect(
            self.prompt_autoalignment)
        self.button_list.append(self.ui.autoalignment)

        self.gui_context = ""
        self.key_status_saved = False

        self.configuration = Configuration()

        self.workflow = Workflow(self)

        self.workflow.camera_ready_signal.connect(self.camera_ready)
        self.workflow.alignment_ready_signal.connect(self.start_workflow)
        self.workflow.alignment_point_reached_signal.connect(
            self.alignment_point_reached)
        self.workflow.alignment_performed_signal.connect(
            self.alignment_performed)
        self.workflow.moon_limb_centered_signal.connect(
            self.prompt_camera_rotated_acknowledged)
        self.workflow.focus_area_set_signal.connect(
            self.set_focus_area_finished)
        self.workflow.set_statusbar_signal.connect(
            self.set_statusbar)
        self.workflow.reset_key_status_signal.connect(
            self.reset_key_status)
        self.workflow.set_text_browser_signal.connect(self.set_text_browser)

        (x0, y0, width, height) = self.geometry().getRect()
        x0 = int(
            self.configuration.conf.get('Hidden Parameters', 'main window x0'))
        y0 = int(
            self.configuration.conf.get('Hidden Parameters', 'main window y0'))
        self.setGeometry(x0, y0, width, height)
        self.configuration.set_protocol_flag()
        self.workflow.set_session_output_flag = True
        if not self.configuration.configuration_read:
            editor = ConfigurationEditor(self.configuration)
            editor.exec_()
            if editor.configuration_changed:
                self.configuration.set_protocol_flag()
                self.workflow.set_session_output_flag = True

        self.setWindowTitle(QtCore.QString(self.configuration.version))

    def setChildrenFocusPolicy(self, policy):
        def recursiveSetChildFocusPolicy(parentQWidget):
            for childQWidget in parentQWidget.findChildren(QtGui.QWidget):
                childQWidget.setFocusPolicy(policy)
                recursiveSetChildFocusPolicy(childQWidget)

        recursiveSetChildFocusPolicy(self)

    def edit_configuration(self):
        editor = ConfigurationEditor(self.configuration)
        editor.exec_()
        # print >> sys.stderr, "config changed:", editor.configuration_changed, \
        #     ", config initialized: ", self.configuration_initialized
        if editor.configuration_changed:
            self.workflow.set_session_output_flag = True
            try:
                self.tv.close_tile_visualization()
            except AttributeError:
                pass
            self.start_workflow()

    def restart(self):
        self.gui_context = "restart"
        self.set_text_browser(
            "Do you really want to restart? "
            "Confirm with 'enter', otherwise press 'esc'.")

    def start_workflow(self):
        self.disable_keys([3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15])

        self.camera_automation = (self.configuration.conf.getboolean(
            "Workflow", "camera automation"))
        if not self.camera_automation:
            self.camera_connect_request_answered()
        else:
            self.gui_context = "camera connect request"
            self.set_text_browser(
                "Make sure that FireCapture is started, and that "
                "'MoonPanoramaMaker' is selected in the PreProcessing section. "
                "Confirm with 'enter', otherwise press 'esc'.")

    def camera_connect_request_answered(self):
        self.workflow.camera_initialization_flag = True

    def camera_ready(self, de_center, m_diameter, phase_angle, pos_angle):

        self.camera_rotated = False
        self.focus_area_set = False
        self.autoalign_enabled = False

        self.tc = TileConstructor(self.configuration, de_center, m_diameter,
                                  phase_angle, pos_angle)

        self.tv = TileVisualization(self.configuration, self.tc)

        self.initialized = True
        self.set_statusbar()
        self.select_new_landmark()

    def prompt_new_landmark_selection(self):
        self.gui_context = "new_landmark_selection"
        self.set_text_browser(
            "Do you really want to set a new landmark and re-align mount? "
            "Confirm with 'enter', otherwise press 'esc'.")

    def select_new_landmark(self):
        self.disable_keys([3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15])
        self.camera_rotated = False
        self.set_text_browser(
            "Select a landmark from the list. ")
        if self.configuration.protocol:
            print str(datetime.now())[11:21], \
                "Select a new landmark from the list."
        self.workflow.al.set_landmark()
        if self.workflow.al.is_landmark_offset_set:
            self.ui.show_landmark.setEnabled(True)
            self.ui.alignment.setEnabled(True)
            self.wait_for_alignment()

    def show_landmark(self):
        myapp = ShowLandmark(self.workflow.al.ls)
        myapp.exec_()

    def prompt_alignment(self):
        self.gui_context = "alignment"
        self.set_text_browser(
            "Do you really want to perform a new alignment? "
            "Confirm with 'enter', otherwise press 'esc'.")

    def wait_for_alignment(self):
        self.save_key_status()
        self.set_text_browser(
            "Slewing telescope to alignment point, please wait.")
        self.reset_active_tile()
        self.set_statusbar()
        self.workflow.slew_to_alignment_point_flag = True

    def alignment_point_reached(self):
        self.reset_key_status()
        if self.workflow.al.is_aligned:
            self.set_text_browser(
                "Center landmark in camera live view (with arrow keys or "
                "telescope hand controller). Confirm with 'enter'.")
        else:
            self.set_text_browser(
                "Move telescope to the Moon (with arrow keys or telescope hand"
                " controller), then center landmark in camera live view. "
                "Confirm with 'enter'.")
        self.gui_context = "alignment_point_reached"

    def perform_alignment(self):
        self.workflow.perform_alignment_flag = True

    def alignment_performed(self):
        if self.workflow.al.drift_dialog_enabled:
            self.ui.configure_drift_correction.setEnabled(True)
        self.ui.rotate_camera.setEnabled(True)
        self.set_statusbar()
        if self.camera_rotated:
            self.set_text_browser(
                "Continue video recording using the record group buttons.")
        else:
            self.perform_camera_rotation()

    def prompt_autoalignment(self):
        self.gui_context = "autoalignment"
        self.set_text_browser(
            "Do you really want to switch on auto-alignment? "
            "Confirm with 'enter', otherwise press 'esc'.")

    def wait_for_autoalignment(self):
        self.ui.alignment.setEnabled(False)
        self.save_key_status()
        self.autoalign_enabled = True
        self.ui.autoalignment.clicked.connect(
            self.prompt_autoalignment_off)
        self.ui.autoalignment.setShortcut("B")
        self.ui.autoalignment.setStyleSheet("background-color: red")
        self.ui.autoalignment.setText('Auto-Align off - B')
        self.set_text_browser(
            "Slewing telescope to alignment point, please wait.")
        self.reset_active_tile()
        self.set_statusbar()
        self.workflow.slew_to_alignment_point_flag = True

    def autoalignment_point_reached(self):
        self.reset_key_status()
        self.set_text_browser(
            "Center landmark in camera live view (with arrow keys or "
            "telescope hand controller). Confirm with 'enter'.")
        self.gui_context = "autoalignment_point_reached"

    def perform_autoalignment(self):
        self.workflow.perform_autoalignment_flag = True

    def prompt_autoalignment_off(self):
        self.gui_context = "autoalignment_off"
        self.set_text_browser(
            "Do you really want to switch off auto-alignment? "
            "Confirm with 'enter', otherwise press 'esc'.")

    def wait_for_autoalignment_off(self):
        self.ui.alignment.setEnabled(True)
        self.autoalign_enabled = False
        self.ui.autoalignment.clicked.connect(
            self.prompt_autoalignment)
        self.ui.autoalignment.setShortcut("B")
        self.ui.autoalignment.setStyleSheet("background-color: light gray")
        self.ui.autoalignment.setText('Auto-Align on - B')
        self.set_text_browser("")
        self.set_statusbar()

    def configure_drift_correction(self):
        drift_configuration_window = ComputeDriftRate(self.configuration,
                                                      self.workflow.al)
        drift_configuration_window.exec_()
        self.set_statusbar()

    def prompt_rotate_camera(self):
        self.gui_context = "rotate_camera"
        self.set_text_browser(
            "Do you really want to rotate camera? "
            "All tiles will be marked as un-processed. "
            "Confirm with 'enter', otherwise press 'esc'.")

    def perform_camera_rotation(self):
        self.disable_keys([6, 7, 8, 9, 10, 11, 12, 13])
        self.set_text_browser("Slewing telescope to Moon limb, please wait.")
        self.workflow.slew_to_moon_limb_flag = True

    def prompt_camera_rotated_acknowledged(self):
        self.gui_context = "perform_camera_rotation"
        self.set_text_browser(
            "Rotate camera until the moon limb at the center of the FOV is "
            "oriented vertically. Confirm with 'enter'.")

    def finish_camera_rotation(self):
        self.ui.autoalignment.setEnabled(True)
        self.ui.set_focus_area.setEnabled(True)
        self.ui.start_continue_recording.setEnabled(True)
        self.ui.select_tile.setEnabled(True)
        self.ui.set_tile_unprocessed.setEnabled(True)
        self.ui.set_all_tiles_unprocessed.setEnabled(True)
        self.ui.set_all_tiles_processed.setEnabled(True)
        self.tv.mark_all_unprocessed()
        self.workflow.active_tile_number = -1
        self.camera_rotated = True
        self.set_statusbar()
        self.set_text_browser(
            "Start video recording using the record group buttons, "
            "or select the focus area.")

    def set_focus_area(self):
        if self.configuration.protocol:
            print str(datetime.now())[11:21], "Select focus area"
        self.set_text_browser(
            "Move telescope to focus area. Confirm with 'enter', otherwise press 'esc'.")
        self.reset_active_tile()
        self.set_statusbar()
        self.gui_context = "set_focus_area"

    def finish_set_focus_area(self):
        self.workflow.set_focus_area_flag = True

    def set_focus_area_finished(self):
        self.focus_area_set = True
        self.set_statusbar()
        self.set_text_browser(
            "Start / continue video recording using the record group buttons.")
        self.ui.goto_focus_area.setEnabled(True)

    def goto_focus_area(self):
        if self.configuration.protocol:
            print str(datetime.now())[11:21], "Goto focus area"
        self.reset_active_tile()
        self.set_statusbar()
        self.set_text_browser(
            "After focussing, continue video recording using the record "
            "group buttons.")
        self.workflow.goto_focus_area_flag = True

    def start_continue_recording(self):
        self.ui.move_to_selected_tile.setEnabled(False)
        self.save_key_status()
        if self.configuration.protocol:
            print str(datetime.now())[11:21], "Start/continue recording"
        if self.workflow.telescope.guiding_active:
            self.workflow.telescope.stop_guiding()
        if self.tc.list_of_tiles_sorted[self.workflow.active_tile_number][
            'processed']:
            self.mark_processed()
        (self.next_tile, next_tile_index) = self.find_next_unprocessed_tile()

        if self.next_tile is None:
            self.all_tiles_recorded = True
            self.ui.move_to_selected_tile.setEnabled(False)
            self.set_statusbar()
            self.set_text_browser(
                "All tiles have been recorded.")
            if self.configuration.protocol:
                print str(datetime.now())[11:21], \
                    "All tiles have been recorded."
            self.reset_key_status()
        else:
            self.workflow.active_tile_number = next_tile_index
            self.tv.mark_active(self.workflow.active_tile_number)
            if self.camera_automation:
                self.camera_interrupted = False
            self.workflow.slew_to_tile_and_record_flag = True

    def find_next_unprocessed_tile(self):
        indices = range(len(self.tc.list_of_tiles_sorted))
        if self.workflow.active_tile_number == -1:
            indices_shifted = indices
        else:
            indices_shifted = indices[
                              self.workflow.active_tile_number:] + indices[
                                                                   0:self.workflow.active_tile_number]
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
        self.tv.mark_processed([self.workflow.active_tile_number])

    def select_tile(self):
        if self.workflow.active_tile_number > -1:
            if (self.tc.list_of_tiles_sorted[self.workflow.active_tile_number]
                ['processed'] == False):
                self.tv.mark_unprocessed([self.workflow.active_tile_number])
        self.tni = TileNumberInput(self.workflow.active_tile_number,
                                   self.workflow)
        self.tni.exec_()
        if self.configuration.protocol:
            print str(datetime.now())[11:21], "Tile number ", \
                self.workflow.active_tile_number, " selected"
        self.ui.move_to_selected_tile.setEnabled(True)
        self.set_text_browser("")

    def set_tile_unprocessed(self):
        self.selected_tile_numbers = self.tv.get_selected_tile_numbers()
        if len(
                self.selected_tile_numbers) == 0 and self.workflow.active_tile_number != -1:
            self.selected_tile_numbers.append(self.workflow.active_tile_number)
        if len(self.selected_tile_numbers) > 0:
            self.selected_tile_numbers_string = str(
                self.selected_tile_numbers)[1:-1]
            self.gui_context = "set_tile_unprocessed"
            self.set_text_browser(
                "Do you want to mark tile(s) " + self.selected_tile_numbers_string +
                " as un-processed? Confirm with 'enter', "
                "otherwise press 'esc'.")

    def mark_unprocessed(self):
        self.tv.mark_unprocessed(self.selected_tile_numbers)
        if self.configuration.protocol:
            print str(datetime.now())[11:21], \
                "Tile(s) " + self.selected_tile_numbers_string + " marked unprocessed."
        self.all_tiles_recorded = False
        self.set_text_browser("")
        self.set_statusbar()

    def set_all_tiles_unprocessed(self):
        self.gui_context = "set_all_tiles_unprocessed"
        self.set_text_browser(
            "Do you want to mark all tiles "
            "as un-processed? Confirm with 'enter', "
            "otherwise press 'esc'.")

    def mark_all_tiles_unprocessed(self):
        self.tv.mark_all_unprocessed()
        self.all_tiles_recorded = False
        self.workflow.active_tile_number = -1
        self.set_text_browser("")
        if self.configuration.protocol:
            print str(datetime.now())[11:21], \
                "All tiles are marked as unprocessed."

    def set_all_tiles_processed(self):
        self.gui_context = "set_all_tiles_processed"
        self.set_text_browser(
            "Do you want to mark all tiles "
            "as processed? Confirm with 'enter', "
            "otherwise press 'esc'.")

    def mark_all_tiles_processed(self):
        self.tv.mark_all_processed()
        self.all_tiles_recorded = True
        self.workflow.active_tile_number = -1
        self.set_text_browser(
            "All tiles are marked as processed.")
        if self.configuration.protocol:
            print str(datetime.now())[11:21], \
                "All tiles are marked as processed."

    def move_to_selected_tile(self):
        self.selected_tile = self.tc.list_of_tiles_sorted[
            self.workflow.active_tile_number]
        if self.configuration.protocol:
            print str(datetime.now())[11:21], "Goto selected tile number ", \
                self.workflow.active_tile_number
        self.tv.mark_active(self.workflow.active_tile_number)
        self.set_statusbar()
        self.set_text_browser("")
        self.workflow.move_to_selected_tile_flag = True

    def reset_active_tile(self):
        if self.workflow.active_tile_number > -1:
            if (self.tc.list_of_tiles_sorted[self.workflow.active_tile_number]
                ['processed'] == False):
                self.tv.mark_unprocessed([self.workflow.active_tile_number])
            else:
                self.mark_processed()
        self.workflow.active_tile_number = -1

    def save_key_status(self):
        self.saved_key_status = []
        for button in self.button_list:
            self.saved_key_status.append(button.isEnabled())
            button.setEnabled(False)
        self.key_status_saved = True

    def reset_key_status(self):
        if self.key_status_saved:
            map(lambda x, y: x.setEnabled(y), self.button_list,
                self.saved_key_status)
            self.key_status_saved = False

    def disable_keys(self, index_list):
        for index in index_list:
            self.button_list[index].setEnabled(False)

    def signal_from_camera(self):
        if self.camera_interrupted:
            self.camera_interrupted = False
        else:
            self.reset_key_status()
            self.start_continue_recording()

    def keyPressEvent(self, event):
        if type(event) == QtGui.QKeyEvent and event.isAutoRepeat() == False:
            if event.key() == 16777220:  # Enter key
                if self.gui_context == "restart":
                    self.gui_context = ""
                    try:
                        self.tv.close_tile_visualization()
                    except AttributeError:
                        pass
                    self.start_workflow()
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


            elif event.key() == QtCore.Qt.Key_Escape:
                if self.key_status_saved:
                    self.set_text_browser("Please wait")
                    self.gui_context = ""
                    self.workflow.escape_pressed_flag = True
                    self.camera_interrupted = True
                else:
                    self.set_text_browser("")
                    self.gui_context = ""

            elif event.key() == QtCore.Qt.Key_Down:
                self.workflow.telescope.move_south()
            elif event.key() == QtCore.Qt.Key_Up:
                self.workflow.telescope.move_north()
            elif event.key() == QtCore.Qt.Key_Left:
                self.workflow.telescope.move_east()
            elif event.key() == QtCore.Qt.Key_Right:
                self.workflow.telescope.move_west()

    def keyReleaseEvent(self, event):
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
        self.ui.prompt_text_browser.setText(text)

    def set_statusbar(self):
        if self.initialized:
            status_text = "Initialized"
        else:
            status_text = ""
        if self.workflow.al.is_landmark_offset_set:
            status_text += ", landmark %s selected" % self.workflow.al.ls.selected_landmark
        if self.workflow.al.is_aligned:
            align_ra = degrees(self.workflow.al.ra_correction) * 60.
            align_de = degrees(self.workflow.al.de_correction) * 60.
            status_text += (", mount alignment: (" + '%3.1f' % align_ra +
                            "'," + '%3.1f' % align_de + "')")
        if self.autoalign_enabled:
            status_text += ", auto-align on"
        if self.workflow.al.is_drift_set:
            drift_ra = degrees(self.workflow.al.drift_ra) * 216000.
            drift_de = degrees(self.workflow.al.drift_de) * 216000.
            status_text += (", drift rate: (" + '%4.2f' % drift_ra + "'/h, " +
                            '%4.2f' % drift_de + "'/h)")
        if self.camera_rotated:
            status_text += ", camera rotated"
        if self.focus_area_set:
            status_text += ", focus area selected"
        if self.workflow.active_tile_number >= 0:
            status_text += ", aimed at tile " + str(
                self.workflow.active_tile_number)
        if self.workflow.all_tiles_recorded:
            status_text += ", all tiles recorded"
        self.ui.statusbar.showMessage(status_text)

    def closeEvent(self, evnt):
        quit_msg = "Are you sure you want to exit the MoonPanoramaMaker program?"
        reply = QtGui.QMessageBox.question(self, 'Message',
                                           quit_msg, QtGui.QMessageBox.Yes,
                                           QtGui.QMessageBox.No)
        if reply == QtGui.QMessageBox.Yes:
            evnt.accept()

            (x0, y0, width, height) = self.geometry().getRect()
            self.configuration.conf.set('Hidden Parameters', 'main window x0',
                                        str(x0))
            self.configuration.conf.set('Hidden Parameters', 'main window y0',
                                        str(y0))
            try:
                self.tv.close_tile_visualization()
            except AttributeError:
                pass
            self.configuration.write_config()
            self.workflow.exiting = True
            time.sleep(2. * self.workflow.run_loop_delay)
        else:
            evnt.ignore()


if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    myapp = StartQT4()
    myapp.show()
    sys.exit(app.exec_())
