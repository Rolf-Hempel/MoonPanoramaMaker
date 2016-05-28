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

from PyQt4 import QtGui

import configuration
import moon_ephem
import telescope
from landmark_selection import LandmarkSelection


class Alignment:
    def __init__(self, configuration, telescope, moon_ephem):
        self.configuration = configuration
        self.tel = telescope
        self.me = moon_ephem
        self.ls = LandmarkSelection(self.me, self.configuration)
        self.is_landmark_offset_set = False
        self.is_aligned = False
        self.alignment_points = []

        self.drift_disabled = False
        self.drift_dialog_enabled = False
        self.is_drift_set = False
        self.default_first_drift = True
        self.default_last_drift = True
        self.first_index = 0
        self.last_index = 0

        self.ra_correction = 0.
        self.de_correction = 0.

    def set_landmark(self):
        offsets = self.ls.select_landmark(datetime.now())
        if self.ls.landmark_selected:
            (self.ra_offset_landmark, self.de_offset_landmark) = offsets
            if self.configuration.protocol:
                print str(datetime.now())[11:21], \
                    "Landmark offset (RA): ", \
                    degrees(self.ra_offset_landmark) * 60., \
                    ", landmark offset (DE): ", \
                    degrees(self.de_offset_landmark) * 60.
            self.is_landmark_offset_set = True
        else:
            self.is_landmark_offset_set = False

    def align(self):
        if self.is_landmark_offset_set:
            # The telescope position is delivered by ASCOM driver of mounting
            (ra_landmark, de_landmark) = self.tel.lookup_tel_position()
        else:
            print "Error: Landmark offset not set"
            exit()

        actual_time = datetime.now()
        try:
            fract = float(str(actual_time)[19:24])
        except:
            fract = 0.
        self.alignment_time = time.mktime(actual_time.timetuple()) + fract

        self.me.update(actual_time)
        if self.configuration.protocol:
            print str(datetime.now())[11:21], \
                "Computing new alignment, moon position: RA: ", \
                degrees(self.me.ra), ", DE: ", degrees(self.me.de)

        # Correction = telescope position minus updated ephemeris position of
        # landmark
        self.ra_correction = ra_landmark - (self.me.ra +
                                            self.ra_offset_landmark)
        self.de_correction = de_landmark - (self.me.de +
                                            self.de_offset_landmark)
        if self.configuration.protocol:
            print "RA(landmark): ", degrees(ra_landmark), ", DE(landmark): ", \
                degrees(de_landmark), ", RA correction: ", \
                degrees(self.ra_correction) * 60., ", DE correction: ", \
                degrees(self.de_correction) * 60.

        alignment_point = {}
        alignment_point['time_string'] = str(actual_time)[11:19]
        alignment_point['time_seconds'] = self.alignment_time
        alignment_point['ra_correction'] = self.ra_correction
        alignment_point['de_correction'] = self.de_correction
        self.alignment_points.append(alignment_point)

        self.is_aligned = True

        if len(self.alignment_points) > 1:
            self.drift_dialog_enabled = True
            if self.default_last_drift:
                self.last_index = len(self.alignment_points) - 1
                self.compute_drift_rate()

    def compute_drift_rate(self):
        self.is_drift_set = False
        if self.drift_disabled:
            return
        time_diff = (self.alignment_points[self.last_index]['time_seconds'] -
                     self.alignment_points[self.first_index]['time_seconds'])
        if time_diff < self.configuration.minimum_drift_seconds:
            return
        self.drift_ra = (
            (self.alignment_points[self.last_index]['ra_correction'] -
             self.alignment_points[self.first_index][
                 'ra_correction']) / time_diff)
        self.drift_de = (
            (self.alignment_points[self.last_index]['de_correction'] -
             self.alignment_points[self.first_index][
                 'de_correction']) / time_diff)
        if self.configuration.protocol:
            print "Computing drift rate using alignment points ", \
                self.first_index, " and ", self.last_index, \
                ". Drift in Ra: ", degrees(self.drift_ra) * 216000., \
                ", drift in De: ", degrees(self.drift_de) * 216000.
        self.is_drift_set = True

    def set_focus_area(self):
        if not self.is_aligned:
            print "Cannot set focus area without alignment"
            exit
        (ra_focus, de_focus) = self.tel.lookup_tel_position()
        # Translate telescope position into true (RA,DE) coordinates
        (ra_ephem_focus, de_ephem_focus) = (
            self.telescope_to_ephemeris_coordinates(ra_focus, de_focus))
        self.me.update(datetime.now())
        self.ra_offset_focus_area = ra_ephem_focus - self.me.ra
        self.de_offset_focus_area = de_ephem_focus - self.me.de

    def compute_coordinate_correction(self):
        if self.is_aligned:
            # Set correction to static value from last alignment
            ra_offset = self.ra_correction
            de_offset = self.de_correction
            # In case drift has been determined, add time-dependent correction
            # term
            if self.is_drift_set:
                now = datetime.now()
                try:
                    fract = float(str(now)[19:24])
                except:
                    fract = 0.
                time_diff = (time.mktime(now.timetuple()) + fract
                             - self.alignment_time)
                ra_offset += time_diff * self.drift_ra
                de_offset += time_diff * self.drift_de
        else:
            if self.configuration.protocol:
                print str(datetime.now())[11:21], \
                    "Info: I will apply zero coordinate correction before " \
                    "alignment."
            ra_offset = 0.
            de_offset = 0.
        return (ra_offset, de_offset)

    def ephemeris_to_telescope_coordinates(self, ra, de):
        correction = self.compute_coordinate_correction()
        # Add corrections to ephemeris position to get telescope coordinates
        return (ra + correction[0], de + correction[1])

    def telescope_to_ephemeris_coordinates(self, ra, de):
        correction = self.compute_coordinate_correction()
        # Subtract corrections from telescope coordinates to get true
        # coordinates
        return (ra - correction[0], de - correction[1])

    def center_offset_to_telescope_coordinates(self, delta_ra, delta_de):
        # Compute current ephermis position of focus area
        self.me.update(datetime.now())
        if self.configuration.protocol:
            print str(datetime.now())[11:21], \
                "Translating center offset to telescope coordinates, " \
                "moon position: RA: ", \
                degrees(self.me.ra), ", DE: ", degrees(self.me.de)
        ra = self.me.ra + delta_ra
        de = self.me.de + delta_de
        # Translate coordinates into telescope system
        return self.ephemeris_to_telescope_coordinates(ra, de)

    def compute_telescope_coordinates_of_landmark(self):
        return self.center_offset_to_telescope_coordinates(
            self.ra_offset_landmark, self.de_offset_landmark)

    def compute_telescope_coordinates_of_focus_area(self):
        return self.center_offset_to_telescope_coordinates(
            self.ra_offset_focus_area, self.de_offset_focus_area)

    def tile_to_telescope_coordinates(self, tile):
        return self.center_offset_to_telescope_coordinates(
            tile['delta_ra_center'], tile['delta_de_center'])


if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    c = configuration.Configuration()

    tel = telescope.Telescope(c)

    # date_time = '2015/05/18 15:20:30'
    date_time = datetime(2015, 7, 26, 16, 50, 32)

    # date_time = datetime.datetime.now()

    me = moon_ephem.MoonEphem(c, date_time)

    al = Alignment(c, tel, me)

    al.set_landmark()

    print "ra_offset_landmark (s): ", 240 * degrees(al.ra_offset_landmark)
    print "de_offset_landmark ('): ", 60 * degrees(al.de_offset_landmark)

    answer = input("Center Landmark in telescope, enter '1' when ready\n")
    if answer != 1:
        exit
    al.align()

    print datetime.now()
    print "ra correction (s): ", 240 * degrees(al.ra_correction)
    print "de correction ('): ", 60 * degrees(al.de_correction)

    answer = input("Center Landmark in telescope, enter '1' when ready\n")
    if answer != 1:
        exit
    al.align()

    print datetime.now()
    print "ra correction (s): ", 240 * degrees(al.ra_correction)
    print "de correction ('): ", 60 * degrees(al.de_correction)

    if al.is_drift_set:
        print "ra drift (s/sec): ", 240 * degrees(al.drift_ra)
        print "de drift ('/sec): ", 60 * degrees(al.drift_de)

        for i in range(3):
            time.sleep(60)
            (ra_d, de_d) = al.compute_coordinate_correction()
            print "Ra coord. correction (s): ", 240 * degrees(ra_d)
            print "De coord. correction ('): ", 60 * degrees(de_d)
