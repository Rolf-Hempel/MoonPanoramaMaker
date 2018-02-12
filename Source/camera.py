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

from miscellaneous import Miscellaneous
from socket_client import SocketClient, SocketClientDebug


class Camera(QtCore.QThread):
    """
    This class provides an asynchronous interface to the video camera for the acquisition of videos.
    A separate thread waits for triggers from the workflow object to start the camera. It then
    sends a request to the MoonPanoramaMaker plugin in FireCapture via the socket_client, and waits
    for the acknowledgement message which confirms that the video has been captured.

    Please note that the socket interface to FireCapture is also used in synchronous mode for still
    picture capturing used by the autoalignment mechanism.

    """

    def __init__(self, configuration, telescope, mark_processed, debug=False):
        """
        Initialize the camera object.

        :param configuration: object containing parameters set by the user
        :param telescope: encapsulates telescope control via ASCOM
        :param mark_processed: a method in moon_panorama_maker which marks tiles as processed
        :param debug: if True, the socket_client (FireCapture connection) is replaced with a
        mockup object with the same interface. It does not capture videos, but returns the
        acknowledgement as the real object does.

        """
        QtCore.QThread.__init__(self)
        # During camera initialization (in class "workflow") the signal is connected with method
        # "signal_from_camera" in moon_panormaa_maker.
        self.signal = QtCore.SIGNAL("signal")

        self.configuration = configuration
        self.telescope = telescope

        # Register method in StartQT4 (module moon_panorama_maker) for marking tile as processed.
        self.mark_processed = mark_processed

        # Avoid too much compute power consumption due to idle looping
        self.lookup_polling_interval = (
        self.configuration.conf.getfloat("ASCOM", "polling interval"))
        # The "triggered" flag is set to True in "workflow" to start an exposure.
        self.triggered = False
        # The "active" flag is looked up in "workflow" to find out if a video is being acquired.
        self.active = False
        self.terminate = False
        self.active_tile_number = -1

        # The socket connection is hardwired. It could be made flexible to allow FireCapture
        # and MoonPanoramaMaker to run on different computers.
        self.host = 'localhost'
        self.port = 9820
        # For debugging purposes, the connection to FireCapture can be replaced with a mockup class
        # which reads still images from files. These can be used to test the autoaligh mechanism.
        if debug:
            self.mysocket = SocketClientDebug(self.host, self.port, self.configuration.camera_delay)
            if self.configuration.protocol_level > 0:
                Miscellaneous.protocol("Camera in debug mode, still camera emulated.")
        else:
            try:
                self.mysocket = SocketClient(self.host, self.port)
            except:
                if self.configuration.protocol_level > 0:
                    Miscellaneous.protocol(
                        "Camera connection to FireCapture failed, expect exception")
                return
            if self.configuration.protocol:
                if self.configuration.protocol_level > 0:
                    Miscellaneous.protocol("Camera: Connection to FireCapture program established")

    def run(self):
        while True:
            if self.terminate:
                break
            elif self.triggered:
                self.triggered = False
                self.active = True
                # Acquire "repetition_count" videos by triggering FireCapture through the socket.
                # Setting a repetition count > 1 allows the consecutive acquisition of more than
                # one video (e.g. for exposures with different filters.
                repetition_count = self.configuration.conf.getint("Camera", "repetition count")
                for video_number in range(repetition_count):
                    if video_number > 0:
                        # If more than one video per tile is to be recorded, insert a short wait
                        # time. Otherwise FireCapture might get stuck.
                        time.sleep(self.configuration.camera_time_between_multiple_exposures)
                    if self.configuration.protocol_level > 0:
                        Miscellaneous.protocol("Camera: Send trigger to FireCapture, tile: " +
                            str(self.active_tile_number) + ", repetition number: " +
                            str(video_number))
                    try:
                        # The tile number is encoded in the message. The FireCapture plugin appends
                        # this message to the video file names (to keep the files apart later).
                        msg = "_Tile-{0:0>3}".format(self.active_tile_number)
                        self.mysocket.mysend(msg)
                    except Exception as e:
                        if self.configuration.protocol_level > 0:
                            Miscellaneous.protocol("Camera, Error message in trigger: " + str(e))
                    if self.configuration.protocol_level > 2:
                        Miscellaneous.protocol("Camera: Wait for FireCapture to finish exposure")
                    try:
                        # Wait for FireCapture to finish the exposure.
                        ack_length = 1
                        ack = self.mysocket.myreceive(ack_length)
                    except Exception as e:
                        if self.configuration.protocol_level > 0:
                            Miscellaneous.protocol("Camera, Error message in ack: " + str(e))
                    if self.configuration.protocol_level > 2:
                        Miscellaneous.protocol("Camera: acknowledgement from FireCapture = " + ack)

                # All videos for this tile are acquired, mark tile as processed.
                self.mark_processed()
                # Trigger method "signal_from_camera" in moon_panorama_maker
                self.emit(self.signal, "hi from camera")
                if self.configuration.protocol_level > 0:
                    Miscellaneous.protocol("Camera, all videos for tile " +
                                           str(self.active_tile_number) +
                                           " captured, signal (tile processed) emitted")
                self.active = False

            time.sleep(self.lookup_polling_interval)

        self.mysocket.close()
        if self.configuration.protocol_level > 0:
            Miscellaneous.protocol("Camera: Connection to FireCapture program closed")
