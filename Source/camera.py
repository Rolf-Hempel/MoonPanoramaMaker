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

from socket_client import SocketClient, SocketClientDebug


class Camera(QtCore.QThread):
    def __init__(self, configuration, telescope, mark_processed, debug=False):
        QtCore.QThread.__init__(self)
        self.signal = QtCore.SIGNAL("signal")

        self.configuration = configuration
        self.telescope = telescope

        # Register method in StartQT4 (module moon_panorama_maker) for marking tile as processed.
        self.mark_processed = mark_processed

        self.lookup_polling_interval = (self.configuration.conf.getfloat(
            "ASCOM", "polling interval"))
        # Enable consecutive acquisition of more than one video (e.g. for exposures with different
        # filters.
        self.repetition_count = self.configuration.conf.getint("Camera", "repetition count")
        # The "triggered" flag is set to True in "workflow" to start an exposure.
        self.triggered = False
        # The "active" flag is looked up in "workflow" to find out if a video is being acquired.
        self.active = False
        self.terminate = False
        self.active_tile_number = -1

        self.host = 'localhost'
        self.port = 9820
        # For debugging purposes, the connection to FireCapture can be replaced with a mockup class
        # which reads still images from files. These can be used to test the autoaligh mechanism.
        if debug:
            self.mysocket = SocketClientDebug(self.host, self.port)
            if self.configuration.protocol:
                print "Camera: Debug mode, still camera emulated"
                print "Camera: OperateCamera thread initialized"
        else:
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
                self.triggered = False
                self.active = True
                # Acquire "repetition_count" videos by triggering FireCapture through the socket.
                for video_number in range(self.repetition_count):
                    if self.configuration.protocol:
                        print "Camera: Send trigger to FireCapture, tile: ",\
                            self.active_tile_number, ", repetition number: ", video_number
                    try:
                        # The tile number is encoded in the message. The FireCapture plugin appends
                        # this message to the video file names (to keep the files apart later).
                        msg = "_Tile-" + "{0:0>3}".format(self.active_tile_number)
                        self.mysocket.mysend(msg)
                    except Exception as e:
                        print "Camera, Error message in trigger: ", str(e)
                    if self.configuration.protocol:
                        print "Camera: Wait for FireCapture to finish exposure"
                    try:
                        # Wait for FireCapture to finish the exposure.
                        ack_length = 1
                        ack = self.mysocket.myreceive(ack_length)
                    except Exception as e:
                        print "Camera, Error message in ack: ", str(e)
                    if self.configuration.protocol:
                        print "Camera: acknowledgement from FireCapture = ", ack

                # All videos for this tile are acquired, mark tile as processed.
                self.mark_processed()
                self.emit(self.signal, "hi from camera")
                if self.configuration.protocol:
                    print "Camera, all videos for tile ", self.active_tile_number,\
                        " captured, signal (tile processed) emitted"
                self.active = False

            time.sleep(self.lookup_polling_interval)

        self.mysocket.close()
        if self.configuration.protocol:
            print "Camera: Connection to FireCapture program closed"