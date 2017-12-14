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
import warnings
from os import listdir
from struct import unpack

import PIL.Image as Image
import matplotlib.pyplot as plt
import numpy as np
from skimage import img_as_ubyte


class SocketClient:
    """
    The SocketClient class implements the communication endpoint on MoonPanoramaMaker's side for
    video and still image acquisition through FireCapture. For video acquisition the blocking method
    acquire_video is provided. Non-blocking video acquisition may be coded by using the lower-level
    send and receive methods directly.

    """

    def __init__(self, host, port):
        """
        Initialization: create a socket connection to the socket server in the MoonPanoramaMaker
        plugin in FireCapture.

        :param host: host id for the socket connection
        :param port: port id on which the socket server is listening
        """

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((host, port))

    def mysend(self, msg):
        """
        Send a string over the socket connection. If a failure occurs, a RuntimeError exception is
        raised.

        :param msg: message to be sent (string)
        :return: number of bytes sent
        """

        sent = self.sock.send(msg.encode())
        if sent == 0:
            raise RuntimeError("Send: socket connection broken")

    def myreceive(self, recv_count):
        """
        Receive a message (byte) through the socket connection. If the socket connection is
        interrupted during the operation, a RuntimeException is raised. Please note that this
        method blocks if less bytes than recv_count are to be received.

        :param recv_count: number of bytes to be received
        :return: message (bytes) received
        """

        # Recieve the first chunk of data.
        data = self.sock.recv(recv_count)
        if len(data) == 0:
            raise RuntimeError("Recv: socket connection broken")
        # if data == 0:
        #     return None
        total_rx = len(data)
        rcvd = data
        # Append more chunks until the expected number of characters are received.
        while total_rx < recv_count:
            data = self.sock.recv(recv_count - total_rx)
            if len(data) == 0:
                raise RuntimeError("Recv: socket connection broken")
            # if data == 0:
            #     return None
            total_rx += len(data)
            rcvd = rcvd + data

        # The expected number of bytes have been received.
        return rcvd

    def myreceive_int(self, length):
        """
        Receive an integer value through the socket.

        :param length: length of the integer to be received (in bytes, either 1, 2, 4, or 8)
        :return: the value (int) of the integer received
        """

        # Communication over the net is big-endian.
        if length == 4:
            return unpack('!l', self.myreceive(4))[0]
        elif length == 2:
            return unpack('!h', self.myreceive(2))[0]
        elif length == 1:
            return unpack('!b', self.myreceive(1))[0]
        elif length == 8:
            return unpack('!q', self.myreceive(8))[0]
        else:
            raise Exception("Error in myreceive_int: unsupported int length " + str(length))

    def acquire_video(self, file_name_appendix):
        """
        Trigger the acquisition of a video in FireCapture and wait for the acknowledgement. The
        character string File_name_appendix is used to encode detailed info (e.g. MPM tile numbers)
        into the names of the video files. It is appended to the file name by FireCapture. The
        string must be 9 characters long and can be anything except "terminate" or "still_pic".

        :param file_name_appendix: character string to be appended to the filename by FireCapture
        :return: character returned by FireCapture as acknowledgement
        """

        self.mysend(file_name_appendix)
        ack = self.sock.recv(1).decode()
        return ack

    def acquire_still_image(self, compression_factor, reduce_to_8bit=True):
        """
        Trigger the acquisition of a monochrome still picture by FireCapture. The dynamic range of
        the image can be either 8 or 16 bit. The full-scale camera image is reduced in size both
        in x and y by parameter "compression_factor" (max. 2 digits). The size reduction is done on
        the FireCapture side to reduce network traffic.

        :param compression_factor: factor by which pixel counts are to be reduced in both x and y
        :param reduce_to_8bit: if True, reduce image_array to 8bit values even if the image was
        received as 16bit. If False, return image_array at full dynamic range.
        :return: tuple with four items: the image_array (numpy style), the width and height of the
        image in pixels, and the dynamic depth of the image (1 for 8bit, 2 for 16bit).
        """

        # Trigger still picture acquisition. Append the two digit compression factor.
        self.mysend("still_pic")
        self.mysend("%02d" % compression_factor)
        # Receive pixel sizes and info on dynamic depth of the image.
        width = self.myreceive_int(4)
        height = self.myreceive_int(4)
        dynamic = self.myreceive_int(4)
        # Receive the image as a byte string and convert it into int values.
        bytebuffer = self.myreceive(width * height * dynamic)
        if dynamic == 1:
            image_array = np.frombuffer(bytebuffer, dtype=np.uint8).reshape((height, width))
        elif dynamic == 2:
            if reduce_to_8bit:
                with warnings.catch_warnings():
                    warnings.simplefilter("ignore")
                    image_array = img_as_ubyte(
                        np.frombuffer(bytebuffer, dtype=np.dtype('<u2')).reshape((height, width)))
            else:
                image_array = np.frombuffer(bytebuffer, dtype=np.dtype('<u2')).reshape(
                    (height, width))
        else:
            return None
        return (image_array, width, height, dynamic)

    def close(self):
        """
        Close the socket connection.

        :return: -
        """

        self.sock.close()


class SocketClientDebug:
    """
    This class mirrors the behaviour of class SocketClient if there is no
    access to a real camera via a socket connection to FireCapture. Instead,
    still images are read from a directory in consecutive order. They are
    returned to the calling program in the same format as the still images
    from the camera.
    """

    def __init__(self, host, port, delay):
        """
        Initialization: set the name of the local directory from which the still images are to be
        read. Since there will be no socket communication, parameters host and port are not used.
        Instead of using the camera to capture still images, images are read from a local
        subdirectory.

        :param host: host id for the socket connection (ignored)
        :param port: port id on which the socket server is listening (ignored)
        :param delay: delay (seconds) before acknowledgement message is sent
                      (to emulate video exposure time)
        """

        self.image_directory = "alignment_test_images"
        # Initialize the counter for still images acquired.
        self.image_counter = 0
        # Create list of images stored in the image_directory.
        self.image_file_list = listdir(self.image_directory)
        # Set the delay for exposure time emulation.
        self.camera_delay = delay

    def mysend(self, text):
        """
        Dummy method: do not do anything.

        :param text: text of the message (ignored)
        :return: -
        """

        pass

    def myreceive(self, recv_count):
        """
        Dummy method: no receive operation is performed. A faked message of the expected length is
        returned.

        :param recv_count: number of bytes to be received
        :return: message (string) received (faked) of length recv_count
        """

        # Insert a delay to emulate the time needed to record the video.
        time.sleep(self.camera_delay)
        return "a" * recv_count

    def acquire_video(self, file_name_appendix):
        """
        Dummy method: no video acquisition is triggered. Just return the acknowledgement character.

        :param file_name_appendix: character string to be appended to the filename (ignored)
        :return: character "a" as acknowledgement
        """

        # Insert a delay to emulate the time needed to record the video.
        time.sleep(self.camera_delay)
        return "a"

    def acquire_still_image(self, compression_factor):
        """
        Emulate still image acquisition by reading them from a local directory. The image can
        be reduced in size by specifying a "comression_factor" > 1. Make sure not to call this
        method more often than there are images in the directory. Otherwise a RuntimeExecption is
        raised.

        :param compression_factor: factor by which pixel counts are to be reduced in both x and y
        :return: tuple with four items: the image_array (numpy style), the width and height of the
        image in pixels, and the dynamic depth of the image (1 for 8bit).
        """

        # Test if there is an unread image left in the local directory.
        if self.image_counter >= len(self.image_file_list):
            raise RuntimeError("still image counter out of range")
        # Read the image from the file, and extract the luminance channel.
        still_image_file = self.image_file_list[self.image_counter]
        still_image = Image.open(self.image_directory + "/" + still_image_file).convert('L')
        # Look up size info and compute new size after compression.
        (width, height) = still_image.size
        new_width = width / compression_factor
        new_height = height / compression_factor
        # If compression is active, resize the image.
        if compression_factor != 1:
            still_image = still_image.resize((new_width, new_height), Image.ANTIALIAS)
        # Convert the image into an numpy array
        still_image_array = np.asarray(still_image)
        dynamic = 1
        self.image_counter += 1
        # Return the image in the same format as the real socket client would do.
        return (still_image_array, new_width, new_height, dynamic)

    def close(self):
        """
        Dummy method for closing the socket.

        :return: -
        """

        pass


if __name__ == "__main__":
    host = 'localhost'
    port = 9820
    # mysocket = SocketClient(host, port)
    mysocket = SocketClientDebug(host, port, 1.)
    print("Client: socket connected")
    time.sleep(1.)
    try:
        # Acquire Video
        print("Client: Acquire video file")
        print("Client: acknowledgement from Server = ", mysocket.acquire_video("_tile_001"))
        time.sleep(2.)
        # Acquire still picture:
        print("Client: Acquire still picture")
        compression_factor = 1
        (image_array, width, height, dynamic) = mysocket.acquire_still_image(compression_factor)
        print("Client: acknowledgement from Server = ", width, ", ", height, ", dynamic: ", dynamic)
        time.sleep(2.)
        plt.imshow(image_array)
        plt.show()
    except Exception as e:
        print("Client, ", str(e))
    mysocket.mysend("terminate")
    print("Client: termination message sent")
    mysocket.close()
    time.sleep(1.)
