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

import time

from PyQt4 import QtCore

from socket_client import SocketClient


class Camera(QtCore.QThread):
    def __init__(self, configuration, telescope, mark_processed):
        QtCore.QThread.__init__(self)
        self.signal = QtCore.SIGNAL("signal")

        self.configuration = configuration
        self.telescope = telescope
        self.mark_processed = mark_processed

        self.lookup_polling_interval = (self.configuration.conf.getfloat(
            "ASCOM", "polling interval"))
        self.triggered = False
        self.active = False
        self.terminate = False
        self.active_tile_number = -1

        self.host = 'localhost'
        self.port = 9820
        try:
            self.mysocket = SocketClient(self.host, self.port)
        except:
            print "Camera: Connection to FireCapture failed, expect exception"
            return
        if self.configuration.protocol:
            print "Camera: Connection to FireCapture program established"
            print "Camera: OperateCamera thread initialized"

    def run(self):
        while True:
            if self.terminate:
                break
            elif self.triggered:
                if self.configuration.protocol:
                    print "Camera: Send trigger to FireCapture"
                try:
                    msg = "_Tile-" + "{0:0>3}".format(self.active_tile_number)
                    self.mysocket.mysend(msg)
                except Exception as e:
                    print "Camera, Error message in trigger: ", str(e)
                self.triggered = False
                self.active = True
            elif self.active:
                if self.configuration.protocol:
                    print "Camera: Wait for FireCapture to finish exposure"
                try:
                    ack = self.mysocket.myreceive()
                except Exception as e:
                    print "Camera, Error message in ack: ", str(e)
                if self.configuration.protocol:
                    print "Camera: acknowledgement from FireCapture = ", ack
                self.active = False
                self.mark_processed()

                self.emit(self.signal, "hi from camera")
                if self.configuration.protocol:
                    print "in Camera, signal emitted"

            time.sleep(self.lookup_polling_interval)

        self.mysocket.close()
        if self.configuration.protocol:
            print "Camera: Connection to FireCapture program closed"


# class TriggerCameraGui(QtGui.QDialog, Ui_TriggerCameraDialog):
#     def __init__(self, configuration, parent=None):
#         QtGui.QDialog.__init__(self, parent)
#
#         print "starting GUI"
#         self.ui = Ui_TriggerCameraDialog()
#         self.ui.setupUi(self)
#         self.ui.startNext.clicked.connect(self.start_cont_exposures)
#
#         self.configuration = configuration
#         self.camera_automation = (self.configuration.conf.getboolean(
#             "Workflow", "camera automation"))
#         print "camera automation: ", self.camera_automation
#
#         if self.camera_automation:
#             self.camera = Camera(self.configuration, self.mark_processed)
#             self.connect(self.camera, self.camera.signal,
#                          self.start_cont_exposures)
#             self.camera.start()
#
#         self.active_tile_number = -1
#         self.list_of_tiles = []
#         for i in range(5):
#             self.list_of_tiles.append(False)
#
#     def start_cont_exposures(self):
#         print "start / continue exposures"
#         print self.find_next_unprocessed_tile()
#         if self.active_tile_number == -2:
#             if self.camera_automation:
#                 self.camera.interrupted = True
#                 print "Setting exposure loop idle"
#             else:
#                 print "All tiles exposed"
#         elif self.camera_automation:
#             self.camera.triggered = True
#             print ("Exposure of tile ", self.active_tile_number,
#                    " started automatically.")
#         else:
#             print ("Start exposure of tile ", self.active_tile_number,
#                    " manually and press enter.")
#
#     def find_next_unprocessed_tile(self):
#         if self.active_tile_number == -1:
#             self.active_tile_number = 0
#         try:
#             self.active_tile_number = self.list_of_tiles.index(False)
#             self.list_of_tiles[self.active_tile_number] = True
#         except:
#             self.active_tile_number = -2
#         return self.active_tile_number
#
#     def mark_processed(self):
#         print "mark processed tile number ", self.active_tile_number
#
#     def keyPressEvent(self, event):
#         if type(event) == QtGui.QKeyEvent:
#             print "key pressed: ", event.key()
#             if event.key() == QtCore.Qt.Key_Escape:
#                 print "interrupt exposure loop"
#                 if self.camera_automation:
#                     self.camera.interrupted = True
#             elif event.key() == 16777220:  # Enter key
#                 print "enter key pressed"
#                 self.start_cont_exposures()
#

# if __name__ == "__main__":
#     app = QtGui.QApplication(sys.argv)
#     configuration = Configuration()
#     myapp = TriggerCameraGui(configuration)
#     myapp.show()
#     sys.exit(app.exec_())
