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

import threading
import time
from datetime import datetime
from math import degrees, radians

import numpy
import pythoncom
import win32com.client


class OperateTelescope(threading.Thread):
    def __init__(self, configuration):
        threading.Thread.__init__(self)

        self.configuration = configuration
        self.lookup_wait_interval = (configuration.conf.getfloat(
            "ASCOM", "wait interval"))
        self.lookup_polling_interval = (configuration.conf.getfloat(
            "ASCOM", "polling interval"))
        self.polling_length = int(self.lookup_polling_interval * 1000.)
        self.lookup_guiding_interval = (configuration.conf.getfloat(
            "ASCOM", "guiding interval"))
        self.guiding_length = int(self.lookup_guiding_interval * 1000.)
        self.lookup_telescope_lookup_precision = (configuration.conf.getfloat(
            "ASCOM", "telescope lookup precision") / 3600.)
        self.instructions = []

        self.slew_to = {}
        self.slew_to['name'] = "slew to"

        self.lookup_tel_position = {}
        self.lookup_tel_position['name'] = "lookup tel position"

        self.calibrate = {}
        self.calibrate['name'] = "calibrate"

        self.start_guiding = {}
        self.start_guiding['name'] = "start guiding"

        self.continue_guiding = {}
        self.continue_guiding['name'] = "continue guiding"

        self.stop_guiding = {}
        self.stop_guiding['name'] = "stop guiding"

        self.start_moving_north = {}
        self.start_moving_north['name'] = "start moving north"
        self.stop_moving_north = {}
        self.stop_moving_north['name'] = "stop moving north"

        self.start_moving_south = {}
        self.start_moving_south['name'] = "start moving south"
        self.stop_moving_south = {}
        self.stop_moving_south['name'] = "stop moving south"

        self.start_moving_east = {}
        self.start_moving_east['name'] = "start moving east"
        self.stop_moving_east = {}
        self.stop_moving_east['name'] = "stop moving east"

        self.start_moving_west = {}
        self.start_moving_west['name'] = "start moving west"
        self.stop_moving_west = {}
        self.stop_moving_west['name'] = "stop moving west"

        self.pulse_correction = {}
        self.pulse_correction['name'] = "pulse correction"

        self.terminate = {}
        self.terminate['name'] = "terminate"

        self.direction_north = 0
        self.direction_south = 1
        self.direction_east = 2
        self.direction_west = 3

        # if self.configuration.protocol:
        #     print str(datetime.now())[11:21], \
        #         "OperateTelescope thread initialized"

    def run(self):
        pythoncom.CoInitialize()

        x = win32com.client.Dispatch(
            self.configuration.conf.get("ASCOM", "chooser"))
        x.DeviceType = 'Telescope'
        name = x.Choose(self.configuration.conf.get("ASCOM", "hub"))

        self.tel = win32com.client.Dispatch(name)

        if self.tel.Connected:
            if self.configuration.protocol:
                print str(datetime.now())[11:21], \
                    "->Telescope was already connected"
        else:
            self.tel.Connected = True
            if self.tel.Connected:
                if self.configuration.protocol:
                    print str(datetime.now())[11:21], \
                        "Connected to telescope now"
            else:
                print str(datetime.now())[11:21], \
                    "Unable to connect to telescope, expect exception"

        while True:
            if len(self.instructions) > 0:
                instruction = self.instructions.pop()
                # print >> sys.stderr, instruction['name']
                if instruction['name'] == "slew to":
                    if self.configuration.protocol:
                        print str(datetime.now())[11:21], \
                            "Slewing telescope to: RA: ", \
                            instruction['rect'] * 15., ", DE: ", \
                            instruction['decl']
                    self.tel.SlewToCoordinates(instruction['rect'],
                                               instruction['decl'])
                elif instruction['name'] == "lookup tel position":
                    rect = 25.
                    decl = 91.
                    iter_count = 0
                    while (abs(self.tel.RightAscension - rect) >
                                   self.lookup_telescope_lookup_precision / 15. or
                                   abs(self.tel.Declination - decl) >
                                   self.lookup_telescope_lookup_precision):
                        # if self.configuration.protocol:
                        #     print "diff(RA): ",\
                        #         abs(self.tel.RightAscension - rect) * 54000.,\
                        #         ", diff(DE): ",\
                        #         abs(self.tel.Declination - decl) * 3600.
                        rect = self.tel.RightAscension
                        decl = self.tel.Declination
                        iter_count += 1
                        time.sleep(self.lookup_wait_interval)
                    instruction['ra'] = radians(rect * 15.)
                    instruction['de'] = radians(decl)
                    instruction['finished'] = True
                    if self.configuration.protocol:
                        print str(datetime.now())[11:21], \
                            "Position look-up: RA: ", rect * 15., ", DE: ", \
                            decl, ", iterations: ", iter_count
                elif instruction['name'] == "calibrate":
                    ra_begin = self.tel.RightAscension
                    calibrate_pulse_length = instruction[
                        'calibrate_pulse_length']
                    self.tel.PulseGuide(2, calibrate_pulse_length)
                    time.sleep(calibrate_pulse_length / 500.)
                    ra_end = self.tel.RightAscension
                    if ra_end < ra_begin:
                        self.direction_east = 3
                        self.direction_west = 2
                    de_begin = self.tel.Declination
                    self.tel.PulseGuide(0, calibrate_pulse_length)
                    time.sleep(calibrate_pulse_length / 500.)
                    de_end = self.tel.Declination
                    if de_end < de_begin:
                        self.direction_north = 1
                        self.direction_south = 0
                    instruction['finished'] = True
                elif instruction['name'] == "start guiding":
                    rate_ra = instruction['rate_ra']
                    rate_de = instruction['rate_de']
                    start_time = time.mktime(datetime.now().timetuple())
                    start_ra = radians(self.tel.RightAscension * 15.)
                    start_de = radians(self.tel.Declination)
                    if numpy.sign(rate_ra) > 0:
                        direction_ra = self.direction_east
                    else:
                        direction_ra = self.direction_west
                    if numpy.sign(rate_de) > 0:
                        direction_de = self.direction_north
                    else:
                        direction_de = self.direction_south
                    continue_guiding_instruction = self.continue_guiding
                    self.instructions.insert(0, continue_guiding_instruction)
                elif instruction['name'] == "continue guiding":
                    # print "Executing continue guiding"
                    current_time = time.mktime(datetime.now().timetuple())
                    current_ra = radians(self.tel.RightAscension * 15.)
                    current_de = radians(self.tel.Declination)
                    target_ra = start_ra + rate_ra * (
                        current_time - start_time)
                    target_de = start_de + rate_de * (
                        current_time - start_time)
                    if abs(target_ra - start_ra) > abs(current_ra - start_ra):
                        print "Pulse guide in RA"
                        self.tel.PulseGuide(direction_ra, self.guiding_length)
                    if abs(target_de - start_de) > abs(current_de - start_de):
                        print "Pulse guide in DE"
                        self.tel.PulseGuide(direction_de, self.guiding_length)
                    self.instructions.insert(0, instruction)
                    time.sleep(self.lookup_guiding_interval)
                elif instruction['name'] == "stop guiding":
                    self.remove_instruction(self.continue_guiding)
                    instruction['finished'] = True
                elif instruction['name'] == "start moving north":
                    self.tel.PulseGuide(self.direction_north,
                                        self.polling_length)
                    self.instructions.insert(0, instruction)
                    time.sleep(self.lookup_polling_interval)
                elif instruction['name'] == "stop moving north":
                    self.remove_instruction(self.start_moving_north)
                    instruction['finished'] = True
                elif instruction['name'] == "start moving south":
                    self.tel.PulseGuide(self.direction_south,
                                        self.polling_length)
                    self.instructions.insert(0, instruction)
                    time.sleep(self.lookup_polling_interval)
                elif instruction['name'] == "stop moving south":
                    self.remove_instruction(self.start_moving_south)
                    instruction['finished'] = True
                elif instruction['name'] == "start moving east":
                    self.tel.PulseGuide(self.direction_east,
                                        self.polling_length)
                    self.instructions.insert(0, instruction)
                    time.sleep(self.lookup_polling_interval)
                elif instruction['name'] == "stop moving east":
                    self.remove_instruction(self.start_moving_east)
                    instruction['finished'] = True
                elif instruction['name'] == "start moving west":
                    self.tel.PulseGuide(self.direction_west,
                                        self.polling_length)
                    self.instructions.insert(0, instruction)
                    time.sleep(self.lookup_polling_interval)
                elif instruction['name'] == "stop moving west":
                    self.remove_instruction(self.start_moving_west)
                    instruction['finished'] = True
                elif instruction['name'] == "pulse correction":
                    direction = [self.direction_north, self.direction_south,
                                 self.direction_east, self.direction_west][
                        instruction['direction']]
                    pulse_length = instruction['pulse_length']
                    self.tel.PulseGuide(direction, pulse_length)
                    instruction['finished'] = True
                elif instruction['name'] == "terminate":
                    break
            else:
                time.sleep(self.lookup_polling_interval)

        pythoncom.CoUninitialize()
        if self.configuration.protocol:
            print str(datetime.now())[11:21], \
                "Ending OperateTelescope thread"

    def remove_instruction(self, instruction):
        for inst in self.instructions:
            if instruction['name'] == inst['name']:
                self.instructions.remove(inst)


class Telescope:
    def __init__(self, configuration):
        self.configuration = configuration
        self.lookup_wait_interval = (configuration.conf.getfloat(
            "ASCOM", "wait interval"))
        self.lookup_polling_interval = (configuration.conf.getfloat(
            "ASCOM", "polling interval"))
        self.optel = OperateTelescope(self.configuration)
        self.optel.start()
        self.pointing_correction_ra = 0.
        self.pointing_correction_de = 0.
        self.guiding_active = False

    def calibrate(self):
        self.calibrate_pulse_length = self.lookup_wait_interval * 1000
        if self.configuration.protocol:
            print str(datetime.now())[11:21], \
                "Calibrating guiding direction, time interval (ms): ", \
                self.calibrate_pulse_length
        calibrate_instruction = self.optel.calibrate
        calibrate_instruction[
            'calibrate_pulse_length'] = self.calibrate_pulse_length
        calibrate_instruction['finished'] = False
        self.optel.instructions.insert(0, calibrate_instruction)
        while not calibrate_instruction['finished']:
            time.sleep(self.lookup_polling_interval)
        if self.configuration.protocol:
            if self.optel.direction_east == 2:
                print "Direction for corrections in RA: normal"
            else:
                print "Direction for corrections in RA: reversed"
            if self.optel.direction_north == 0:
                print "Direction for corrections in DE: normal"
            else:
                print "Direction for corrections in DE: reversed"

    def slew_to(self, ra, de):
        rect = degrees(ra) / 15.
        decl = degrees(de)
        slew_to_instruction = self.optel.slew_to
        slew_to_instruction['rect'] = rect
        slew_to_instruction['decl'] = decl
        self.optel.instructions.insert(0, slew_to_instruction)
        (rect_lookup, decl_lookup) = self.lookup_tel_position_uncorrected()
        self.pointing_correction_ra = ra - rect_lookup
        self.pointing_correction_de = de - decl_lookup
        if self.configuration.protocol:
            print str(datetime.now())[11:21], \
                "New pointing correction computed (deg.): RA: ", \
                degrees(self.pointing_correction_ra), ", DE: ", \
                degrees(self.pointing_correction_de)

    def lookup_tel_position_uncorrected(self):
        lookup_tel_position_instruction = self.optel.lookup_tel_position
        lookup_tel_position_instruction['finished'] = False
        self.optel.instructions.insert(0, lookup_tel_position_instruction)
        while not lookup_tel_position_instruction['finished']:
            time.sleep(self.lookup_polling_interval)
        return (lookup_tel_position_instruction['ra'],
                lookup_tel_position_instruction['de'])

    def lookup_tel_position(self):
        (tel_ra_uncorrected,
         tel_de_uncorrected) = self.lookup_tel_position_uncorrected()
        return (tel_ra_uncorrected + self.pointing_correction_ra,
                tel_de_uncorrected + self.pointing_correction_de)

    def start_guiding(self, rate_ra, rate_de):
        start_guiding_instruction = self.optel.start_guiding
        start_guiding_instruction['rate_ra'] = rate_ra
        start_guiding_instruction['rate_de'] = rate_de
        if self.configuration.protocol:
            print str(datetime.now())[11:21], "Start guiding, Rate(RA): ", \
                degrees(start_guiding_instruction['rate_ra']) * 216000., \
                ", Rate(DE): ", \
                degrees(start_guiding_instruction['rate_de']) * 216000., \
                " (arc min. / hour)"
        self.optel.instructions.insert(0, start_guiding_instruction)
        self.guiding_active = True

    def stop_guiding(self):
        if self.configuration.protocol:
            print str(datetime.now())[11:21], "Stop guiding"
        stop_guiding_instruction = self.optel.stop_guiding
        stop_guiding_instruction['finished'] = False
        self.optel.instructions.insert(0, stop_guiding_instruction)
        while not stop_guiding_instruction['finished']:
            time.sleep(self.lookup_polling_interval)
        self.guiding_active = False

    def move_north(self):
        self.optel.instructions.insert(0, self.optel.start_moving_north)

    def stop_move_north(self):
        stop_moving_north_instruction = self.optel.stop_moving_north
        stop_moving_north_instruction['finished'] = False
        # self.optel.instructions.insert(0, stop_moving_north_instruction)
        self.optel.instructions.append(stop_moving_north_instruction)
        while not stop_moving_north_instruction['finished']:
            time.sleep(self.lookup_polling_interval)

    def move_south(self):
        self.optel.instructions.insert(0, self.optel.start_moving_south)

    def stop_move_south(self):
        stop_moving_south_instruction = self.optel.stop_moving_south
        stop_moving_south_instruction['finished'] = False
        # self.optel.instructions.insert(0, stop_moving_south_instruction)
        self.optel.instructions.append(stop_moving_south_instruction)
        while not stop_moving_south_instruction['finished']:
            time.sleep(self.lookup_polling_interval)

    def move_east(self):
        self.optel.instructions.insert(0, self.optel.start_moving_east)

    def stop_move_east(self):
        stop_moving_east_instruction = self.optel.stop_moving_east
        stop_moving_east_instruction['finished'] = False
        # self.optel.instructions.insert(0, stop_moving_east_instruction)
        self.optel.instructions.append(stop_moving_east_instruction)
        while not stop_moving_east_instruction['finished']:
            time.sleep(self.lookup_polling_interval)

    def move_west(self):
        self.optel.instructions.insert(0, self.optel.start_moving_west)

    def stop_move_west(self):
        stop_moving_west_instruction = self.optel.stop_moving_west
        stop_moving_west_instruction['finished'] = False
        # self.optel.instructions.insert(0, stop_moving_west_instruction)
        self.optel.instructions.append(stop_moving_west_instruction)
        while not stop_moving_west_instruction['finished']:
            time.sleep(self.lookup_polling_interval)

    def pulse_correction(self, direction, pulse_length):
        pulse_correction_instruction = self.optel.pulse_correction
        pulse_correction_instruction['direction'] = direction
        pulse_correction_instruction['pulse_length'] = pulse_length
        pulse_correction_instruction['finished'] = False
        self.optel.instructions.append(pulse_correction_instruction)
        while not pulse_correction_instruction['finished']:
            time.sleep(self.lookup_polling_interval)

    def terminate(self):
        if self.configuration.protocol:
            print str(datetime.now())[11:21], "Terminating telescope"
        self.optel.instructions.insert(0, self.optel.terminate)
        self.optel.join()
        if self.configuration.protocol:
            print str(datetime.now())[11:21], "Telescope terminated"
