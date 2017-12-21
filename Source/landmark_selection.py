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

from PyQt5 import QtWidgets

import configuration
from edit_landmarks import EditLandmarks
from miscellaneous import Miscellaneous
from moon_ephem import MoonEphem


class LandmarkSelection:
    """
    This class keeps a list of landmark features on the moon and provides methods for selecting
    a specific landmark as well as coordinate transformations which eventually give the offsets in
    RA and DE relative to the moon center.
    
    """
    def __init__(self, me, configuration):
        """
        Initialization of the landmark list. For each landmark there must be a file "landmark.png"
        in the subdirectory "landmark_pictures". This picture shows a section of the moon with
        arrows pointing at the selected landmark.
        
        :param me: object with positions of the sun and moon, including libration info
        :param configuration: object containing parameters set by the user
        """

        # Dictionary with selenographic [longitude, latitude] for each available landmark.
        self.landmarks = {
            'Hansen': [72.54, 14.04],
            'Langrenus': [61.04, -8.86],
            'Proclus': [46.8, 16.1],
            'Roemer': [36.41, 25.43],
            'Posidonius-A': [29.52, 31.69],
            'Theophilus': [26.25, -11.48],
            'Eudoxus': [16.23, 44.27],
            'Aristillus': [1.21, 33.88],
            'Moon Center': [0., 0.],
            'Alpetragius': [-4.51, -16.05],
            'Tycho': [-11.22, -43.30],
            'Eratosthenes': [-11.32, 14.47],
            'Copernicus': [-20.08, 9.62],
            'Kepler': [-38.01, 8.12],
            'Aristarchus': [-47.49, 23.73],
            'Krafft': [-72.72, 16.56],
            'Ulugh Beigh': [-81.96, 32.67]
        }
        self.me = me
        self.configuration = configuration
        # Initialize the selected landmark as empty string.
        self.selected_landmark = ""

    def select_landmark(self, date_time):
        """
        Update ephemeris and libration data for the moon, then open a gui window for landmark
        selection. If the user has selected a landmark, compute true topocentric offset angles in
        (RA, DE) for the landmark relative to the moon center and set the "landmark_selected" flag
        to True. If no landmark is selected, set the flag to False.
        
        :param date_time: Datetime object with current time information
        :return: Offsets in (RA, DE) of landmark relative to the center of the moon
        """
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
        """
        Compute offsets in (RA, DE) relative to the moon center for the landmark feature. Take into
        account topocentric parallax and libration.
        
        :param landmark: name of the landmark (String)
        :return: offset (radians) in (RA, DE) of landmark relative to moon center
        """

        try:
            # Get selenographic longitude and latitude of landmark.
            longitude = radians(self.landmarks[landmark][0])
            latitude = radians(self.landmarks[landmark][1])
            if self.configuration.protocol_level > 0:
                Miscellaneous.protocol("New Landmark selected: " + landmark +
                    ", selenographic longitude: " + str(degrees(longitude)) + ", latitude: " +
                    str(degrees(latitude)))
            # Perform the coordinate transformation and return the offsets (in radians)
            return self.coord_translation(longitude, latitude)
        except:
            # This is an internal error and should not occur.
            print("Error in landmark_selection: unknown landmark", file=sys.stderr)
            return (0., 0.)

    def coord_translation(self, longitude, latitude):
        """
        Translate selenographic coordinates on the moon into true topocentric displacements in
        (RA, DE).
        
        :param longitude: selenographic longitude of landmark
        :param latitude: selenographic latitude of landmark
        :return: offset (radians) in (RA, DE) of landmark relative to moon center
        """

        # Look at the user's guide for algorithmic details. (da_prime, dd_prime) are the
        # displacements (radians) on the moon's disk, oriented with lunar north up.
        da_prime = -sin(longitude - self.me.topocentric_lib_long) * cos(
            latitude) * self.me.radius
        y = -cos(longitude - self.me.topocentric_lib_long) * cos(
            latitude) * self.me.radius
        z = sin(latitude) * self.me.radius
        y_prime = y * cos(self.me.topocentric_lib_lat) - z * sin(
            self.me.topocentric_lib_lat)
        dd_prime = y * sin(self.me.topocentric_lib_lat) + z * cos(
            self.me.topocentric_lib_lat)
        # Rotate for position angle of the moon's rotational axis. Apply approximate correction
        # to RA offset for the moon's declination angle.
        offset_ra = (da_prime * cos(self.me.pos_rot_north) + dd_prime * sin(
            self.me.pos_rot_north)) / cos(self.me.de)
        offset_de = -da_prime * sin(self.me.pos_rot_north) + dd_prime * cos(
            self.me.pos_rot_north)
        return (offset_ra, offset_de)


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    c = configuration.Configuration()
    date_time = datetime(2016, 3, 18, 9, 0, 0)
    me = MoonEphem(c, date_time)
    ls = LandmarkSelection(me, c)

    offsets = ls.select_landmark(date_time)

    if ls.landmark_selected:
        print('Time (UT): ', me.location_time.date)
        print('Moon RA: %s, DE: %s, Diameter: %s' % (me.ra, me.de,
                                                     degrees(
                                                         me.diameter)))
        print('Libration in Latitude: ', degrees(me.topocentric_lib_lat))
        print('Libration in Longitude: ', degrees(me.topocentric_lib_long))
        print('Pos. angle North Pole: ', degrees(me.pos_rot_north))
        print('Selenographic Co-Longitude: ', me.colong)
        print('Sun RA: %s, DE: %s' % (me.sun_ra, me.sun_de))
        print('Elongation: %s' % (degrees(me.elongation)))
        print('Phase angle: %s' % (degrees(me.phase_angle)))
        print('Sun direction: %s' % (degrees(me.pos_angle_sun)))
        print(('Pos. angle Pole (bright limb to the right): %s' %
               (degrees(me.pos_angle_pole))))
        print("Landmark: ", ls.selected_landmark, ", Offset RA ('): ", degrees(
            offsets[0]) * 60., ", Offset DE ('): ", degrees(offsets[1]) * 60.)
    else:
        print("No landmark selected, Offset RA (Rad): ", offsets[
            0], ", Offset DE (Rad): ", offsets[1])
