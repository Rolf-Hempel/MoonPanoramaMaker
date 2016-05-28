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
from datetime import datetime
from math import degrees, radians
from math import sin, cos

from PyQt4 import QtGui

import configuration
from edit_landmarks import EditLandmarks
from moon_ephem import MoonEphem


class LandmarkSelection:
    def __init__(self, me, configuration):
        self.landmarks = {
            'Aristarchus': [-47.49, 23.73],
            'Copernicus': [-20.08, 9.62],
            'Hansen': [72.54, 14.04],
            'Krafft': [-72.72, 16.56],
            'Langrenus': [61.04, -8.86],
            'Proclus': [46.8, 16.1],
            'Moon Center': [0., 0.],
            'Theophilus': [26.25, -11.48],
            'Ulugh Beigh': [-81.96, 32.67]
        }
        self.me = me
        self.configuration = configuration
        self.selected_landmark = ""

    def select_landmark(self, date_time):
        self.me.update(date_time)
        self.me.compute_libration()
        myapp = EditLandmarks(self.selected_landmark, self.landmarks,
                              self.me.colong)
        myapp.exec_()
        if myapp.selected_landmark != "":
            self.selected_landmark = myapp.selected_landmark
            self.landmark_selected = True
            return self.compute_landmark_offsets(self.selected_landmark)
        else:
            self.landmark_selected = False
            return (1., 1.)

    def compute_landmark_offsets(self, landmark):
        try:
            long = radians(self.landmarks[landmark][0])
            lat = radians(self.landmarks[landmark][1])
            if self.configuration.protocol:
                print str(datetime.now())[11:21], \
                    "New Landmark selected: ", landmark, \
                    ", longitude: ", degrees(long), ", latitude: ", degrees(
                    lat)
            return self.coord_translation(long, lat)
        except:
            print >> sys.stderr, "Error in landmark_selection: unknown landmark"
            return (0., 0.)

    def coord_translation(self, long, lat):
        da_prime = -sin(long - self.me.topocentric_lib_long) * cos(
            lat) * self.me.radius
        y = -cos(long - self.me.topocentric_lib_long) * cos(
            lat) * self.me.radius
        z = sin(lat) * self.me.radius
        y_prime = y * cos(self.me.topocentric_lib_lat) - z * sin(
            self.me.topocentric_lib_lat)
        dd_prime = y * sin(self.me.topocentric_lib_lat) + z * cos(
            self.me.topocentric_lib_lat)
        offset_ra = (da_prime * cos(self.me.pos_rot_north) + dd_prime * sin(
            self.me.pos_rot_north)) / cos(self.me.de)
        offset_de = -da_prime * sin(self.me.pos_rot_north) + dd_prime * cos(
            self.me.pos_rot_north)
        return (offset_ra, offset_de)


if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    c = configuration.Configuration()
    date_time = datetime(2016, 3, 18, 9, 0, 0)
    me = MoonEphem(c, date_time)
    ls = LandmarkSelection(me, c)

    offsets = ls.select_landmark(date_time)

    if ls.landmark_selected:
        print 'Time (UT): ', me.location_time.date
        print 'Moon RA: %s, DE: %s, Diameter: %s' % (me.ra, me.de,
                                                     degrees(
                                                         me.diameter))
        print 'Libration in Latitude: ', degrees(me.topocentric_lib_lat)
        print 'Libration in Longitude: ', degrees(me.topocentric_lib_long)
        print 'Pos. angle North Pole: ', degrees(me.pos_rot_north)
        print 'Selenographic Co-Longitude: ', me.colong
        print 'Sun RA: %s, DE: %s' % (me.sun_ra, me.sun_de)
        print 'Elongation: %s' % (degrees(me.elongation))
        print 'Phase angle: %s' % (degrees(me.phase_angle))
        print 'Sun direction: %s' % (degrees(me.pos_angle_sun))
        print ('Pos. angle Pole (bright limb to the right): %s' %
               (degrees(me.pos_angle_pole)))
        print "Landmark: ", ls.selected_landmark, ", Offset RA ('): ", degrees(
            offsets[0]) * 60., ", Offset DE ('): ", degrees(offsets[1]) * 60.
    else:
        print "No landmark selected, Offset RA (Rad): ", offsets[
            0], ", Offset DE (Rad): ", offsets[1]
