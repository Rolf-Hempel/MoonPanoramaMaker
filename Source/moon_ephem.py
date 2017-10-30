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

import datetime
import time
from math import asin, atan2, sin, cos, acos, pi, sqrt, radians, degrees

import ephem
import pytz

import configuration


class MoonEphem:
    """
    The MoonEphem class computes the positions of the sun and the moon in the sky, the position
    angles of the sunlit phase and of the rotational axis, and the topocentric libration angles in
    longitude and latitude. For algorithmic details refer to the user's manual.
    
    """

    def __init__(self, configuration, date_time, debug=False):
        """
        Initialize the MoonEphem object.
        
        :param configuration: object containing parameters set by the user
        :param date_time: datetime object of the time for which coordinates are to be computed
        :param debug: if debug=True, the value of date_time is ignored and a fixed time
        (26 Oct. 2015, 21:55 CET) is used instead.
        """

        self.configuration = configuration
        # Look up geographical position of observer (for parallax computations) and time zone
        self.location_time = ephem.Observer()
        self.location_time.lon = (
            radians(self.configuration.conf.getfloat("Geographical Position", "longitude")))
        self.location_time.lat = (
            radians(self.configuration.conf.getfloat("Geographical Position", "latitude")))
        self.location_time.elevation = (
            self.configuration.conf.getfloat("Geographical Position", "elevation"))
        self.tz = (pytz.timezone(self.configuration.conf.get("Geographical Position", "timezone")))
        self.debug = debug
        self.utc = pytz.utc
        # So far no position has been calculated. From the next call on, the previous position
        # will be used to compute the speed of the moon in (RA,DE) (finite difference).
        self.position_stored = False
        # Set rates for the moon's motion per second in (RA,DE) to average values.
        self.rate_ra = radians(38. / 60.) / 3600.
        self.rate_de = 0.
        # Compute the coordinates for date_time.
        self.update(date_time)

    def sun_direction(self):
        """
        Compute the angle at the moon's center between equatorial North and the sun. The angle is
        counted counterclockwise.
        
        :return: the sun's position angle (radians)
        """

        sinsd = (sin(self.sun_ra - self.ra) * cos(self.sun_de) / sin(self.elongation))
        cossd = (sin(self.sun_de) * cos(self.de) - cos(self.sun_de) * sin(self.de) * cos(
            self.sun_ra - self.ra)) / sin(self.elongation)
        return atan2(sinsd, cossd)

    def local_time_to_utc(self, date_time):
        """
        Convert local time to UTC.
        
        :param date_time: local datetime object 
        :return: UTC datetime object
        """
        loc_dt = self.tz.localize(date_time)
        return loc_dt.astimezone(self.utc)

    def update(self, date_time):
        """
        Compute accurate topocentric positions of sun and moon, the moon's phase angle and the
        position angle of its sunlit phase. If a previous position was stored for a time within the
        last two hours, the speed of the moon in (RA,DE) is computed as finite difference values.
        
        :param date_time: datetime object of current time
        :return: -
        """

        # Translate time stamp into UTC. In debug mode compute the moon position for a fixed time
        # (as defined in configuration.py).
        if self.debug:
            # Alternative date, used for first tests of auto-alignment:
            t = self.configuration.ephemeris_fixed_datetime
            dt = datetime.datetime(t[0], t[1], t[2], t[3], t[4], t[5])
            self.location_time.date = self.local_time_to_utc(dt)
        else:
            self.location_time.date = self.local_time_to_utc(date_time)

        # Compute the ephemeris using PyEphem.
        self.moon = ephem.Moon(self.location_time)
        s = ephem.Sun(self.location_time)
        self.ra = self.moon.ra
        self.de = self.moon.dec
        self.radius = self.moon.radius
        self.diameter = self.moon.radius * 2.
        self.sun_ra = s.ra
        self.sun_de = s.dec
        # Compute the distance between sun and moon in the sky.
        self.elongation = acos(
            sin(self.de) * sin(self.sun_de) + cos(self.de) * cos(self.sun_de) * cos(
                self.sun_ra - self.ra))
        # Compute the position angles of the point on the moon limb pointing at the sun,
        # and of the North pole of the sunlit moon phase.
        self.pos_angle_sun = self.sun_direction()
        self.pos_angle_pole = self.pos_angle_sun + pi / 2.

        c = sqrt(
            s.earth_distance ** 2 + self.moon.earth_distance ** 2 - 2. * s.earth_distance *
            self.moon.earth_distance * cos(
                self.elongation))
        sina = s.earth_distance * sin(self.elongation) / c
        cosa = ((s.earth_distance ** 2 - c ** 2 - self.moon.earth_distance ** 2) / (
            2. * c * self.moon.earth_distance))
        # Compute the phase angle of the sunlit moon phase.
        self.phase_angle = atan2(sina, cosa)

        # For the computation of the moon speed, the time in consecutive seconds must be known to
        # better than a second. Therefore, add the fractional part and store the result in
        # "current_time".
        try:
            fract = float(str(date_time)[19:24])
        except:
            fract = 0.
        current_time = time.mktime(date_time.timetuple()) + fract

        # If a previous position was stored, check if it's in the valid time range.
        # The two times must be at least one second apart (for stability), and at most two hours.
        if self.position_stored:
            if 1. < abs(current_time - self.stored_time) < 7200.:
                self.rate_ra = (self.ra - self.stored_ra) / (current_time - self.stored_time)
                self.rate_de = (self.de - self.stored_de) / (current_time - self.stored_time)
                # Replace the stored time stamp and coordinates with the current values.
                self.stored_time = current_time
                self.stored_ra = self.ra
                self.stored_de = self.de
        # There is no previous data point, store the current one.
        else:
            self.stored_ra = self.ra
            self.stored_de = self.de
            self.stored_time = current_time
            self.position_stored = True

    def compute_libration(self):
        """
        Compute topocentric libration angles and the position angle of the moon's rotational axis.
        
        :return: -
        """

        # Astrometric libration angles and the selenographic co-longitude of the sun are provided
        # by PyEphem.
        self.astrometric_lib_lat = self.moon.libration_lat
        self.astrometric_lib_long = self.moon.libration_long
        self.colong = self.moon.colong

        # Compute topocentric libration values. For algorithmic details, refer to the user's guide.
        j2000 = ephem.Date(datetime.datetime(2000, 1, 1, 12, 0))
        t = (ephem.Date(self.location_time.date) - j2000) / 36525.
        epsilon = radians(23.439281 - 0.013002575 * t)
        ma = ephem.Equatorial(self.ra, self.de, epoch=ephem.Date(self.location_time.date))
        me = ephem.Ecliptic(ma)
        cap_i = radians(1.54266)
        omega = radians(125.044555 - 1934.13626194 * t)
        lm = radians(218.31664563 + 481267.88119575 * t - 0.00146638 * t ** 2)
        i = acos(cos(cap_i) * cos(epsilon) + sin(cap_i) * sin(epsilon) * cos(omega))
        omega_prime = atan2(-sin(cap_i) * sin(omega) / sin(i), (
            cos(cap_i) * sin(epsilon) - sin(cap_i) * cos(epsilon) * cos(omega)) / sin(i))

        self.pos_rot_north = atan2(-sin(i) * cos(omega_prime - self.ra),
                                   cos(self.de) * cos(i) - sin(self.de) * sin(i) * sin(
                                       omega_prime - self.ra))
        self.topocentric_lib_lat = asin(
            -sin(cap_i) * cos(me.lat) * sin(me.lon - omega) - cos(cap_i) * sin(me.lat))
        self.topocentric_lib_long = (atan2(
            cos(cap_i) * cos(me.lat) * sin(me.lon - omega) - sin(cap_i) * sin(me.lat),
            cos(me.lat) * cos(me.lon - omega)) - lm + omega) % (2. * pi)
        if self.topocentric_lib_long > 1.:
            self.topocentric_lib_long -= 2. * pi
        elif self.topocentric_lib_long < -1.:
            self.topocentric_lib_long += 2. * pi


if __name__ == "__main__":
    c = configuration.Configuration()

    #    date_time = datetime.datetime(2015,06,21, 17,20,30)
    #    date_time = datetime.datetime.now()

    #    date_time = datetime.datetime(2015,8,14, 16,53,22)

    #    geographical_position = {}
    #    geographical_position['longitude'] = '7.39720'
    #    geographical_position['latitude'] = '50.69190'
    #    geographical_position['elevation'] = 250

    # date_time = datetime.datetime(2015, 10, 1, 21, 55, 00)
    # me = MoonEphem(c, date_time)
    # ra_start = me.ra
    # de_start = me.de
    # for length in [1, 5, 10, 20]:
    #     end_time = datetime.datetime(2015, 10, 1, 21, 55, 0 + length)
    #     me.update(end_time)
    #     ra_end = me.ra
    #     de_end = me.de
    #     rate_ra = degrees((ra_end - ra_start) / (length) * 3600.) * 60.
    #     rate_de = degrees((de_end - de_start) / (length) * 3600.) * 60.  #
    #     print "length: ", length, ", rate_ra: ", rate_ra, ", rate_de: ", rate_de
    #     print "Values computed in MoonEphem, rate_ra: ", degrees(
    #         me.rate_ra) * 60., ", rate_de: ", degrees(me.rate_de) * 60.

    for i in range(30):
        date_time = datetime.datetime(2015, 10, 1 + i, 21, 55, 00)
        # date_time = datetime.datetime(2011, 6, 1 + i, 2, 0, 0)
        me = MoonEphem(c, date_time, debug=False)
        me.compute_libration()
        end_time = date_time + datetime.timedelta(seconds=10)

        print 'Time (UT): ', me.location_time.date
        print 'Moon RA: %s, DE: %s, Diameter: %s' % (me.ra, me.de, ephem.degrees(me.diameter))
        print 'Astrometric libration in Latitude: ', me.astrometric_lib_lat, ", in longitude: ", \
            me.astrometric_lib_long
        print "Topocentric libration in latitude: ", degrees(
            me.topocentric_lib_lat), ", in longitude: ", degrees(me.topocentric_lib_long)
        print "Position angle of North Pole: ", degrees(me.pos_rot_north)
        print 'Selenographic Co-Longitude: ', me.colong
        print 'Sunlit geographic longitudes between ', degrees(-me.colong), " and ", degrees(
            -me.colong) + 180.
        # print 'Sun RA: %s, DE: %s' % (me.sun_ra, me.sun_de)
        print 'Elongation: %s' % (ephem.degrees(me.elongation))
        print 'Phase angle: %s' % (ephem.degrees(me.phase_angle))
        print 'Sun direction: %s' % (ephem.degrees(me.pos_angle_sun))
        print (
            'Pos. angle pole (bright limb to the right): %s' % (ephem.degrees(me.pos_angle_pole)))

        length = 10
        ra_start = me.ra
        de_start = me.de
        end_time = date_time + datetime.timedelta(seconds=length)
        me.update(end_time)
        ra_end = me.ra
        de_end = me.de
        rate_ra = degrees((ra_end - ra_start) / (length) * 3600.) * 60.
        rate_de = degrees((de_end - de_start) / (length) * 3600.) * 60.  #
        print "rate_ra: ", rate_ra, ", rate_de: ", rate_de
        print ""
