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

import socket
import time
from os import listdir

import Image
import numpy as np


class SocketClient:
    def __init__(self, host, port):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((host, port))

    def mysend(self, msg):
        sent = self.sock.send(msg)
        if sent == 0:
            raise RuntimeError("Send: socket connection broken")

    def myreceive(self, recv_count):
        data = self.sock.recv(recv_count)
        if data == 0:
            return None
        total_rx = len(data)
        rcvd = data
        while total_rx < recv_count:
            data = self.sock.recv(recv_count - total_rx)
            if data == 0:
                return None
            total_rx += len(data)
            rcvd = rcvd + data
        if rcvd == '':
            raise RuntimeError("Recv: socket connection broken")
        return rcvd

    def myreceive_int(self, length):
        message = self.myreceive(length)
        values = map(ord, message)
        value = 0
        for i in range(length):
            value += values[i] * 256 ** (length - 1 - i)
        return value

    def acquire_video(self, file_name_appendix):
        self.mysend(file_name_appendix)
        ack = self.sock.recv(1)
        return ack

    def acquire_still_image(self, compression_factor):
        self.mysend("still_pic")
        self.mysend("%02d" % compression_factor)
        width = self.myreceive_int(4)
        height = self.myreceive_int(4)
        dynamic = self.myreceive_int(4)
        values = map(ord, self.myreceive(width * height * dynamic))
        image_array = np.empty((height, width), dtype=np.uint8)
        pos = 0
        if dynamic == 1:
            for j in range(height):
                for i in range(width):
                    image_array[j, i] = values[pos]
                    pos += 1
        elif dynamic == 2:
            for j in range(height):
                for i in range(width):
                    image_array[j, i] = (values[pos] << 8) + values[pos + 1]
                    pos += 2
        else:
            return None
        return (image_array, width, height, dynamic)

    def close(self):
        self.sock.close()


class SocketClientDebug:
    """
    This class mirrors the behaviour of class SocketClient if there is no
    access to a real camera via a socket connection to FireCapture. Instead,
    still images are read from a directory in consecutive order. They are
    returned to the calling program in the same format as the still images
    from the camera.
    """

    def __init__(self, host, port):
        self.image_directory = "alignment_test_images"
        self.image_counter = 0
        self.image_file_list = listdir(self.image_directory)

    def mysend(self, text):
        pass

    def acquire_video(self, text):
        return "a"

    def acquire_still_image(self, compression_factor):
        if self.image_counter >= len(self.image_file_list):
            raise RuntimeError("still image counter out of range")
        still_image_file = self.image_file_list[self.image_counter]
        still_image = Image.open(
            self.image_directory + "/" + still_image_file).convert('L')
        (width, height) = still_image.size
        new_width = width / compression_factor
        new_height = height / compression_factor
        still_image = still_image.resize((new_width, new_height),
                                         Image.ANTIALIAS)
        still_image_array = np.asarray(still_image)
        dynamic = 1
        self.image_counter += 1
        return (still_image_array, new_width, new_height, dynamic)

    def close(self):
        pass


if __name__ == "__main__":
    host = 'localhost'
    port = 9820
    mysocket = SocketClientDebug(host, port)
    # mysocket = SocketClientDebug(host, port)
    print "Client: socket connected"
    time.sleep(1.)
    try:
        # Acquire Video
        print "Client: Acquire video file"
        print "Client: acknowledgement from Server = ", \
            mysocket.acquire_video("_tile_001")
        time.sleep(2.)
        # Acquire still picture:
        print "Client: Acquire still picture"
        compression_factor = 1
        (image_array, width, height, dynamic) = mysocket.acquire_still_image(
            compression_factor)
        print "Client: acknowledgement from Server = ", width, ", ", height, \
            ", dynamic: ", dynamic
        time.sleep(2.)
        img = Image.fromarray(image_array, 'L')
        img.show()
    except Exception as e:
        print "Client, ", str(e)
    mysocket.mysend("terminate")
    print "Client: termination message sent"
    mysocket.close()
    time.sleep(1.)
