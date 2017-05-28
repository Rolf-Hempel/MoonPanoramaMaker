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
from math import degrees, sqrt

import numpy as np
from PyQt4 import QtGui

import configuration
import moon_ephem
import telescope
from image_shift import ImageShift
from landmark_selection import LandmarkSelection
from miscellaneous import Miscellaneous


class Alignment:
    """
    This class deals with the correction of the misalignment of the telescope mounting. The
    alignment error is determined either with the help of the user or automatically (auto-
    alignment). The change of the alignment error, called drift rate, is computed as soon as
    enough alignment measurements are available.
    
    Additionally, class Alignment provides methods for transformations between various coordinate
    systems
    
    """
    def __init__(self, configuration, telescope, moon_ephem, debug=False):
        """
        Initialization of instance variables
        
        :param configuration: object containing parameters set by the user
        :param telescope: encapsulates telescope control via ASCOM
        :param moon_ephem: object with positions of the sun and moon, including libration info
        :param debug: if set to True, display keypoints and shifts during auto-alignment
        """

        self.debug = debug
        self.configuration = configuration
        self.wait_interval = (self.configuration.conf.getfloat(
            "ASCOM", "wait interval"))
        self.tel = telescope
        self.me = moon_ephem
        self.ls = LandmarkSelection(self.me, self.configuration)
        self.is_landmark_offset_set = False
        self.is_aligned = False
        # Initialization of alignments performed during an observing session.
        self.alignment_points = []
        # Auto-alignment is not initialized. Initialization will include a reference image with
        # which later alignments will be compared.
        self.autoalign_initialized = False
        self.aligment_reference_captured = False
        # In auto-alignment initialization the telescope mount is moved to two locations near
        # the alignment landmark position. The image shifts are measured using camera still images
        # and compared with the expected shifts, based on the mount displacements. These
        # measurements are used to determine whether or not the camera is oriented upright /
        # upside-down or if it is mirror-inverted. if the absolute value of the shifts deviates
        # from the expected value by more tnan 30%, auto-alignment is deemed unsuccessful.
        self.max_autoalign_error = 0.3

        # Initialize drift correction
        self.drift_disabled = False
        self.drift_dialog_enabled = False
        self.is_drift_set = False
        # By default, use the first alignment point as the begin and the last alignment point as
        # the end of the time interval for drift determination.
        self.default_first_drift = True
        self.default_last_drift = True
        self.first_index = 0
        self.last_index = 0

        # Initialize current corrections in RA and DE (telescope - celestial coordinates)
        self.ra_correction = 0.
        self.de_correction = 0.

    def set_landmark(self):
        """
        Let the user select the landmark used for telescope alignment and compute its offset
        from the moon center, including libration and topocentric parallax.
        
        :return: -
        """

        # Open a gui where the user can select among a collection of landmarks on the moon
        offsets = self.ls.select_landmark(datetime.now())
        # A landmark has been selected, store and print coordinate offsets.
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
        """
        Determine the current error in telescope pointing, either with the help of the user
        (manual mode) or automatically (auto-alignment).
        
        :param alignment_manual: True if the telescope has been aimed at landmark by the user
        :return: In case alignment_manual=False (auto-alignment), return the relative alignment
                 error. The deviation of the current positioning as compared to the expected
                 position, based on the previous alignment, is determined. The quotient of this
                 deviation and the width of the overlap between tiles is returned. If it is too
                 large, a complete panorama coverage cannot be guaranteed. In case of
                 manual_alignment=True, return None.
        """

        # Alignment is only possible after a landmark has been selected.
        if not self.is_landmark_offset_set:
            print "Error: Landmark offset not set"
            raise RuntimeError("Error: Landmark offset not set")

        # Manual alignment: The telescope is aimed at the current location of the landmark. Look
        # up its position and proceed to alignment computation.
        if alignment_manual:
            # The telescope position is delivered by ASCOM driver of mounting
            (ra_landmark, de_landmark) = self.tel.lookup_tel_position()
            relative_alignment_error = None

        # Auto-alignment: No assumption on the current telescope pointing can be made.
        else:
            # Automatic alignment: check if auto-alignment has been initialized
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
            global_shift = sqrt(x_shift**2+y_shift**2)
            relative_alignment_error = global_shift/self.shift_angle
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
            if self.configuration.protocol:
                print str(datetime.now())[11:21], \
                    "Rotated to RA/DE: RA_shift: ", \
                    ra_shift / self.im_shift.pixel_angle, \
                    ", DE_shift: ", de_shift / self.im_shift.pixel_angle,\
                    " (pixels)"
            # The shift is computed as "current frame - reference". Add
            # coordinate shifts to current mount position to get mount
            # setting where landmark is located as on reference frame.
            ra_landmark += ra_shift
            de_landmark += de_shift

        # From here on, manual and auto-alignment can be treated the same. The current mount
        # position is given by(ra_landmark, de_landmark).
        current_time = datetime.now()
        # Set the time of the alignment point with an accuracy better than a second.
        self.alignment_time = self.current_time_seconds(current_time)

        # Update ephemeris of moon and sun
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

        # Store a new alignment point
        alignment_point = {}
        alignment_point['time_string'] = str(current_time)[11:19]
        alignment_point['time_seconds'] = self.alignment_time
        alignment_point['ra_correction'] = self.ra_correction
        alignment_point['de_correction'] = self.de_correction
        self.alignment_points.append(alignment_point)

        self.is_aligned = True

        # If more than one alignment point is stored, enable drift dialog and compute drift rate
        # of telescope mount.
        if len(self.alignment_points) > 1:
            self.drift_dialog_enabled = True
            if self.default_last_drift:
                self.last_index = len(self.alignment_points) - 1
                self.compute_drift_rate()
        return relative_alignment_error

    def initialize_auto_align(self, camera_socket):
        """
        Establish the relation between the directions of (x,y) coordinates in an idealized pixel
        image of the Moon (x positive to the east, y positive southwards) and the (x,y) coordinates
        of the normalized plane in which the tile construction is done (x positive to the right,
        y positive upwards). Take into account potential mirror inversion in the optical system.
        
        :param camera_socket: interface to the camera to capture videos and still images
        :return: fraction of alignment error as compared to width of overlap between tiles
        """

        self.autoalign_initialized = False

        # Capture an alignment reference frame
        self.im_shift = ImageShift(self.configuration, camera_socket,
                                   debug=self.debug)
        if self.configuration.protocol_level > 1:
            Miscellaneous.protocol("Alignment reference frame captured.")

        # The shift_angle is the overlap width between panorama tiles.
        self.shift_angle = self.im_shift.ol_angle
        # Three positions in the sky are defined: right shift in x direction, zero shift, and
        # downward shift in y direction. (x,y) are the pixel coordinates in the still images
        # captured with the video camera. All shifts are relative to the current coordinates of
        # the landmark.
        shift_vectors = [[self.shift_angle, 0.], [0., 0.], [0., self.shift_angle]]
        xy_shifts = []
        for shift in shift_vectors:
            # Compute current coordinates of landmark, including corrections for alignment and drift
            (ra_landmark, de_landmark) = (
                self.compute_telescope_coordinates_of_landmark())
            # Transform (x,y) coordinates into (ra,de) coordinates.
            # The y-flip has to be set to -1. because the rotate function
            # assumes the y coordinate to point up, whereas the y pixel
            # coordinate is pointing down (see comment in method align.
            (shift_angle_ra, shift_angle_de) = Miscellaneous.rotate(
                self.me.pos_angle_pole, self.me.de, 1., 1., -1.,
                shift[0], shift[1])
            # Drive the telescope to the computed position in the sky.
            self.tel.slew_to(ra_landmark + shift_angle_ra,
                             de_landmark + shift_angle_de)
            # Wait until the telescope orientation has stabilized.
            time.sleep(self.wait_interval)
            try:
                # Capture a still image of the area around landmark and determine the shift versus
                # the reference frame.
                (x_shift, y_shift, in_cluster, outliers) = \
                    self.im_shift.shift_vs_reference()
            # If the image was not good enough for automatic shift determination, disable auto-
            # alignment.
            except RuntimeError as e:
                if self.configuration.protocol_level > 2:
                    Miscellaneous.protocol(str(e))
                raise RuntimeError
            if self.configuration.protocol:
                if self.configuration.protocol_level > 2:
                    Miscellaneous.protocol("Frame captured for autoalignment, x_shift: " +
                                           str(x_shift / self.im_shift.pixel_angle) +
                                           ", y_shift: " + str(y_shift / self.im_shift.pixel_angle)+
                                           " (pixels), consistent shifts: " + str(in_cluster) +
                                           ", outliers: " + str(outliers))
            xy_shifts.append([x_shift, y_shift])
        # Subtract second position from first and third position
        shift_vector_0_measured = [xy_shifts[0][0] - xy_shifts[1][0],
                                   xy_shifts[0][1] - xy_shifts[1][1]]
        shift_vector_2_measured = [xy_shifts[2][0] - xy_shifts[1][0],
                                   xy_shifts[2][1] - xy_shifts[1][1]]

        # Compare measured shifts in x and y with the expected directions to find out if images
        # are mirror-inverted in x or y.
        self.flip_x = np.sign(shift_vector_0_measured[0])
        self.flip_y = np.sign(shift_vector_2_measured[1])
        if self.configuration.protocol_level > 2:
            Miscellaneous.protocol("Autoalign, mirroring detected in x: " + str(self.flip_x) +
                                   ", in y: " + str(self.flip_y))
        # Determine how much the measured shifts deviate from the expected shifts in the focal
        # plane. If the difference is too large, auto-alignment initialization is interpreted as
        # not successful.
        error_x = abs(
            abs(shift_vector_0_measured[0]) - self.shift_angle) / self.shift_angle
        error_y = abs(
            abs(shift_vector_2_measured[1]) - self.shift_angle) / self.shift_angle
        error = max(error_x, error_y)
        if error > self.max_autoalign_error:
            if self.configuration.protocol_level > 0:
                Miscellaneous.protocol("Autoalign initialization failed, error in x: " +
                    str(error_x * 100.) + ", in y: " + str(error_y * 100.) + " (percent)")
            raise RuntimeError
        else:
            if self.configuration.protocol_level > 0:
                Miscellaneous.protocol("Autoalign successful, error in x: " +
                    str(error_x * 100.) + ", in y: " + str(error_y * 100.) + " (percent)")
        self.autoalign_initialized = True
        # Return the relative error as compared with tile overlap width.
        return error

    def compute_drift_rate(self):
        """
        Compute the drift rate of the telescope mount, based on two alignment points. By default,
        the first and last alignment point are used. Other indices may have been selected by the
        user.
        
        :return: -
        """

        self.is_drift_set = False
        if self.drift_disabled:
            return
        time_diff = (self.alignment_points[self.last_index]['time_seconds'] -
                     self.alignment_points[self.first_index]['time_seconds'])
        # Drift is only computed if the time difference of the alignment points is large enough.
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
        if self.configuration.protocol_level > 1:
            Miscellaneous.protocol("Drift rate based on alignment points " + str(self.first_index) +
                                   " and " + str(self.last_index) + ": Drift in Ra = " +
                                   str(degrees(self.drift_ra) * 216000.) + ", drift in De = " +
                                   str(degrees(self.drift_de) * 216000.) + " (in arc min/hour)")
        # Set flag to true to indicate that a valid drift rate has been determined.
        self.is_drift_set = True

    def set_focus_area(self):
        """
        The user may select a place on the moon where lighting conditions are optimal for setting
        the focus. This method stores the current location, so the telescope can be moved to it
        later to update the focus setting.
        
        :return: -
        """

        if not self.is_aligned:
            if self.configuration.protocol_level > 0:
                Miscellaneous.protocol("Internal error: Attempt to set focus area without alignment")
            raise RuntimeError("Cannot set focus area without alignment")
        # Look up the current position of the telescope mount.
        (ra_focus, de_focus) = self.tel.lookup_tel_position()
        # Translate telescope position into true (RA,DE) coordinates
        (ra_ephem_focus, de_ephem_focus) = (
            self.telescope_to_ephemeris_coordinates(ra_focus, de_focus))
        # Compute current moon position and displacement of telescope position relative to moon
        # center.
        self.me.update(datetime.now())
        self.ra_offset_focus_area = ra_ephem_focus - self.me.ra
        self.de_offset_focus_area = de_ephem_focus - self.me.de

    def compute_coordinate_correction(self):
        """
        Compute the current difference between telescope and celestial coordinates, including
        alignment and (if available) drift rate.
        
        :return: telescope - celestial coordinates: (Offset in RA, Offset in DE) 
        """

        # If an alignment has been performed, compute offsets in RA and DE.
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
                # Compute time in seconds since last alignment.
                time_diff = (time.mktime(now.timetuple()) + fract
                             - self.alignment_time)
                ra_offset += time_diff * self.drift_ra
                de_offset += time_diff * self.drift_de
        # Before the first alignment, set offsets to zero and print a warning to stdout.
        else:
            if self.configuration.protocol_level > 2:
                Miscellaneous.protocol("Info: I will apply zero coordinate correction before " \
                                        "alignment.")
            ra_offset = 0.
            de_offset = 0.
        return (ra_offset, de_offset)

    def ephemeris_to_telescope_coordinates(self, ra, de):
        """
        Translate celestial equatorial coordinates into coordinates of telescope mount.
        
        :param ra: Celestial right ascension
        :param de: Celestial declination
        :return: Equatorial mount coordinates (RA, DE)
        """

        correction = self.compute_coordinate_correction()
        # Add corrections to ephemeris position to get telescope coordinates
        telescope_ra = ra + correction[0]
        telescope_de = de + correction[1]
        if self.configuration.protocol_level > 2:
            Miscellaneous.protocol("Translating equatorial to telescope coordinates, " \
                                   "correction in RA: " + str(degrees(correction[0])) +
                                   ", in DE: " + str(degrees(correction[1])) + ", Telescope RA: " +
                                   str(degrees(telescope_ra)) + ", Telescope DE: " +
                                   str(degrees(telescope_de)) + " (all in degrees)")
        return (telescope_ra, telescope_de)

    def telescope_to_ephemeris_coordinates(self, ra, de):
        """
        Translate coordinates of telescope mount into celestial equatorial coordinates (inverse
        operation to ephemeris_to_telescope_coordinates).
        
        :param ra: RA of telescope mount
        :param de: DE of telescope mount
        :return: Celestial coordinates (ra, de)
        """

        correction = self.compute_coordinate_correction()
        # Subtract corrections from telescope coordinates to get true
        # coordinates
        return (ra - correction[0], de - correction[1])

    def center_offset_to_telescope_coordinates(self, delta_ra, delta_de):
        """
        Translate offset angles relative to moon center into equatorial coordinates (RA, DE) in
        the coordinate system of the telescope mount.
        
        :param delta_ra: Center offset angle in ra
        :param delta_de: Center offset angle in de
        :return: Equatorial telescope mount coordinates (RA, DE)
        """

        # Compute current position of the moon.
        self.me.update(datetime.now())
        if self.configuration.protocol_level > 2:
            Miscellaneous.protocol("Translating center offset to equatorial coordinates, " \
                                    "center offsets: RA: " + str(degrees(delta_ra)) +
                                    ", DE: " + str(degrees(delta_de)) +
                                    ", moon position (center): RA: " + str(degrees(self.me.ra)) +
                                    ", DE: " + str(degrees(self.me.de)) + " (all in degrees)")
        # Add the offset to moon center coordinates.
        ra = self.me.ra + delta_ra
        de = self.me.de + delta_de
        # Translate coordinates into telescope system
        return self.ephemeris_to_telescope_coordinates(ra, de)

    def compute_telescope_coordinates_of_landmark(self):
        """
        Compute the current position of the landmark in the equatorial mount coordinate system.
        
        :return: Equatorial telescope mount coordinates (RA, DE) of landmark.
        """

        return self.center_offset_to_telescope_coordinates(
            self.ra_offset_landmark, self.de_offset_landmark)

    def compute_telescope_coordinates_of_focus_area(self):
        """
        Compute the current position of the focus area in the equatorial mount coordinate system.
        
        :return: Equatorial telescope mount coordinates (RA, DE) of the focus area.
        """

        return self.center_offset_to_telescope_coordinates(
            self.ra_offset_focus_area, self.de_offset_focus_area)

    def tile_to_telescope_coordinates(self, tile):
        """
        Compute the current position of the center of a panorama tile in the equatorial mount
        coordinate system.
        
        :param tile: Index of panorama tile
        :return: Equatorial telescope mount coordinates (RA, DE) of the tile center.
        """

        return self.center_offset_to_telescope_coordinates(
            tile['delta_ra_center'], tile['delta_de_center'])

    def current_time_seconds(self, current_time):
        """
        Compute the current time (in consecutive seconds), including fractional part.
        
        :param current_time: Datetime object
        :return: time measured in consecutive seconds
        """

        try:
            fract = float(str(current_time)[19:24])
        except:
            fract = 0.
        return time.mktime(current_time.timetuple()) + fract

    def seconds_since_last_alignment(self):
        """
        Compute time (in seconds) since last alignment.
        
        :return: time measured in consecutive seconds
        """

        current_time = datetime.now()
        return self.current_time_seconds(current_time) - self.alignment_time


if __name__ == "__main__":
    from socket_client import SocketClient, SocketClientDebug

    app = QtGui.QApplication(sys.argv)
    c = configuration.Configuration()

    tel = telescope.Telescope(c)

    host = 'localhost'
    port = 9820

    if c.camera_debug:
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

    me = moon_ephem.MoonEphem(c, date_time, debug=c.ephemeris_debug)

    al = Alignment(c, tel, me, debug=c.alignment_debug)
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
