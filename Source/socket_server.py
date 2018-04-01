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
import socket


class SocketServer:
    """
    This class is obsolete code. It was used to test the communication between MoonPanoramaMaker
    and FireCapture. The SocketServer is a stand-alone application which emulates the MPM plugin
    in FireCapture. It takes reqests to start video capturing and sends faked acknowledgements back
    to MPM.

    The class is obsolete because it does not implement the still image capturing required by
    auto-alignment. Today MPM can be tested without the SocketServer by seeting the "camera_debug"
    flag in configuration.py to True. Then, on the client side, the video and still-image requests
    are handled by mockup class SocketClientDebug which does not communicate with FireCapture.

    """

    def __init__(self, host, port):

        # Create an INET, STREAMing socket
        self.serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # Bind the socket to localhost and port 1234
        self.serversocket.bind((host, port))
        # Become a server socket
        self.serversocket.listen(1)
        print("Server started")

    @staticmethod
    def mysend(sock, msg):
        sent = sock.send(msg)
        if sent == 0:
            raise RuntimeError("Socket connection broken.")

    @staticmethod
    def myreceive(sock):
        try:
            rcvd = sock.recv(9)
        except:
            raise RuntimeError("Socket connection terminated.")
        if rcvd == '':
            raise RuntimeError("Socket connection broken.")
        return rcvd


if __name__ == "__main__":
    host = 'localhost'
    port = 9820
    myserver = SocketServer(host, port)

    while True:
        # accept connection from outside and create a clientsocket
        (clientsocket, address) = myserver.serversocket.accept()
        print("")
        print("Server: connection with client established")

        # now wait for message through via the clientsocket
        while True:
            try:
                msg_read = myserver.myreceive(clientsocket)
            except Exception as e:
                print("Server: ", str(e))
                break
            print("Server: msg received: ", msg_read)
            print("-------------------------------")
            print("Take an exposure in FireCapture")
            print("-------------------------------")

            # Replace the sleep function with the camera exposure.
            time.sleep(4.)

            try:
                myserver.mysend(clientsocket, "a")
            except Exception as e:
                print("Server: ", str(e))
                break
            print("Server, ackn sent")

        time.sleep(2.)
