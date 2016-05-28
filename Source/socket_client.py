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


class SocketClient:
    def __init__(self, host, port):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((host, port))

    def mysend(self, msg):
        sent = self.sock.send(msg)
        if sent == 0:
            raise RuntimeError("socket connection broken")

    def myreceive(self):
        rcvd = self.sock.recv(1)
        if rcvd == '':
            raise RuntimeError("socket connection broken")
        return rcvd

    def close(self):
        self.sock.close()


if __name__ == "__main__":
    host = 'localhost'
    port = 9820
    mysocket = SocketClient(host, port)
    print "Client: socket connected"
    for i in range(4):
        print "Client: Send message to Server"
        try:
            msg = "_Tile-" + "{0:0>3}".format(i)
            mysocket.mysend(msg)
        except Exception as e:
            print "Client, ", str(e)
        try:
            ack = mysocket.myreceive()
        except Exception as e:
            print "Client, ", str(e)
        print "Client: acknowledgement from Server = ", ack

    mysocket.close()
    time.sleep(2.)
