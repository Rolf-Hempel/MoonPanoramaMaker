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

import numpy as np
from PyQt4 import QtGui

import configuration
import moon_ephem
import telescope
from image_shift import ImageShift
from landmark_selection import LandmarkSelection
from miscellaneous import Miscellaneous


class Alignment:
    def __init__(self, configuration, telescope, moon_ephem, debug=False):
        self.debug = debug
        self.configuration = configuration
        self.wait_interval = (self.configuration.conf.getfloat(
            "ASCOM", "wait interval"))
        self.tel = telescope
        self.me = moon_ephem
        self.ls = LandmarkSelection(self.me, self.configuration)
        self.is_landmark_offset_set = False
        self.is_aligned = False
        self.alignment_points = []
        self.autoalign_initialized = False
        self.aligment_reference_captured = False
        self.max_autoalign_error = 0.3

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

    def align(self, alignment_manual=True):
        if not self.is_landmark_offset_set:
            print "Error: Landmark offset not set"
            raise RuntimeError("Error: Landmark offset not set")

        if alignment_manual:
            # The telescope position is delivered by ASCOM driver of mounting
            (ra_landmark, de_landmark) = self.tel.lookup_tel_position()

        else:
            # Automatic alignment, derive coordinates of landmark from
            if not self.autoalign_initialized:
                raise RuntimeError(
                    "Error: Attempt to do autoalign before initialization")
            # Move telescope to expected coordinates of alignment point
            (ra_landmark, de_landmark) = (
                self.compute_telescope_coordinates_of_landmark())
            self.tel.slew_to(ra_landmark, de_landmark)
            time.sleep(self.wait_interval)
            try:
                # Measure shift against reference frame
                (x_shift, y_shift, in_cluster, outliers) = \
                    self.im_shift.shift_vs_reference()
                if self.configuration.protocol:
                    print str(datetime.now())[11:21], \
                        "New alignment frame captured, x_shift: ", \
                        x_shift / self.im_shift.pixel_angle, \
                        ", y_shift: ", y_shift / self.im_shift.pixel_angle,\
                        " (pixels), consistent shifts: ", \
                        in_cluster, ", outliers: ", outliers
            except RuntimeError as e:
                if self.configuration.protocol:
                    print str(datetime.now())[11:21], str(e)
                raise RuntimeError(str(e))
            # Translate shifts measured in camera image into equatorial
            # coordinates
            scale_factor = 1.
            # In tile construction (where the rotate function had been
            # designed for) x is pointing right and y upwards. Here, x is
            # pointing right and y downwards. Therefore, the y flip has to
            # be reversed.
            (ra_shift, de_shift) = Miscellaneous.rotate(self.me.pos_angle_pole,
                                                        self.me.de,
                                                        scale_factor,
                                                        self.flip_x,
                                                        -1. * self.flip_y,
                                                        x_shift, y_shift)
            # The shift is computed as "current frame - reference". Add
            # coordinate shifts to current mount position to get mount
            # setting where landmark is located as on reference frame.
            ra_landmark += ra_shift
            de_landmark += de_shift

        current_time = datetime.now()
        try:
            fract = float(str(current_time)[19:24])
        except:
            fract = 0.
        self.alignment_time = time.mktime(current_time.timetuple()) + fract

        self.me.update(current_time)
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
                degrees(de_landmark), ", RA correction ('): ", \
                degrees(self.ra_correction) * 60., ", DE correction ('): ", \
                degrees(self.de_correction) * 60.

        alignment_point = {}
        alignment_point['time_string'] = str(current_time)[11:19]
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
        return

    def initialize_auto_align(self, camera_socket):
        # Establish the relation between the directions of (x,y) coordinates
        # in an idealized pixel image of the Moon (x positive to the east, y
        # positive southwards) and the (x,y) coordinates of the normalized
        # plane in which the tile construction is done (x positive to the
        # right, y positive upwards). Take into account potential mirroring in
        # the optical system.
        #
        self.autoalign_initialized = False

        # Capture an alignment reference frame
        self.im_shift = ImageShift(self.configuration, camera_socket,
                                   debug=self.debug)
        if self.configuration.protocol:
            print str(datetime.now())[11:21], \
                "Alignment reference frame captured"

        shift_angle = self.im_shift.ol_angle
        shift_vectors = [[shift_angle, 0.], [0., 0.], [0., shift_angle]]
        xy_shifts = []
        for shift in shift_vectors:
            (ra_landmark, de_landmark) = (
                self.compute_telescope_coordinates_of_landmark())
            # The y-flip has to be set to -1. because the rotate function
            # assumes the y coordinate to point up, whereas the y pixel
            # coordinate is pointing down (see comment in method align.
            (shift_angle_ra, shift_angle_de) = Miscellaneous.rotate(
                self.me.pos_angle_pole, self.me.de, 1., 1., -1.,
                shift[0], shift[1])
            self.tel.slew_to(ra_landmark + shift_angle_ra,
                             de_landmark + shift_angle_de)
            time.sleep(self.wait_interval)
            try:
                (x_shift, y_shift, in_cluster, outliers) = \
                    self.im_shift.shift_vs_reference()
            except RuntimeError as e:
                print str(datetime.now())[11:21], str(e)
                raise RuntimeError
            if self.configuration.protocol:
                print str(datetime.now())[11:21], \
                    "Frame captured for autoalignment, x_shift: ", x_shift / self.im_shift.pixel_angle, \
                    ", y_shift: ", y_shift / self.im_shift.pixel_angle, " (pixels), consistent shifts: ", \
                    in_cluster, ", outliers: ", outliers
            xy_shifts.append([x_shift, y_shift])
        shift_vector_0_measured = [xy_shifts[0][0] - xy_shifts[1][0],
                                   xy_shifts[0][1] - xy_shifts[1][1]]
        shift_vector_2_measured = [xy_shifts[2][0] - xy_shifts[1][0],
                                   xy_shifts[2][1] - xy_shifts[1][1]]

        self.flip_x = np.sign(shift_vector_0_measured[0])
        self.flip_y = np.sign(shift_vector_2_measured[1])
        if self.configuration.protocol:
            print str(datetime.now())[11:21], \
                "Autoalign, mirroring in x: ", self.flip_x, ", in y: ", self.flip_y
        error_x = abs(
            abs(shift_vector_0_measured[0]) - shift_angle) / shift_angle
        error_y = abs(
            abs(shift_vector_2_measured[1]) - shift_angle) / shift_angle
        error = max(error_x, error_y)
        if error > self.max_autoalign_error:
            if self.configuration.protocol:
                print "Autoalign initialization failed, error in x: ", \
                    error_x * 100., ", in y: ", error_y * 100., " (percent)"
            raise RuntimeError
        else:
            if self.configuration.protocol:
                print "Autoalign successful, error in x: ", \
                    error_x * 100., ", in y: ", error_y * 100., " (percent)"
        self.autoalign_initialized = True
        return error

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
            raise RuntimeError("Cannot set focus area without alignment")
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
    from socket_client import SocketClient, SocketClientDebug

    app = QtGui.QApplication(sys.argv)
    c = configuration.Configuration()

    tel = telescope.Telescope(c)

    host = 'localhost'
    port = 9820

    debug = True

    if debug:
        mysocket = SocketClientDebug(host, port)
    else:
        try:
            mysocket = SocketClient(host, port)
        except:
            print "Camera: Connection to FireCapture failed, expect exception"
            exit()

    # date_time = '2015/05/18 15:20:30'
    date_time = datetime(2015, 10, 26, 21, 55, 00)

    # date_time = datetime.now()

    me = moon_ephem.MoonEphem(c, date_time, debug=True)

    al = Alignment(c, tel, me, debug=debug)
    al.set_landmark()

    print "ra_offset_landmark (s): ", 240 * degrees(al.ra_offset_landmark)
    print "de_offset_landmark ('): ", 60 * degrees(al.de_offset_landmark)

    (ra_landmark, de_landmark) = al.compute_telescope_coordinates_of_landmark()
    tel.slew_to(ra_landmark, de_landmark)

    answer = input("Center Landmark in telescope, enter '1' when ready\n")
    if answer != 1:
        exit
    al.align(alignment_manual=True)

    print datetime.now()
    print "ra correction (s): ", 240 * degrees(al.ra_correction)
    print "de correction ('): ", 60 * degrees(al.de_correction)

    al.initialize_auto_align(mysocket)

    for alignment_count in range(2):
        print " "
        print "Perform an autoalignment"
        al.align(alignment_manual=False)

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
    mysocket.close()
    tel.terminate()
    app.closeAllWindows()
