# -*- coding: utf-8; -*-
"""
Copyright (c) 2016 Rolf Hempel, rolf6419@gmx.de
Adopted to INDI by Felix Huber

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
from math import radians
import sys

import numpy

from miscellaneous import Miscellaneous

import PyIndi


class IndiClient(PyIndi.BaseClient):
    def __init__(self):
        super(IndiClient, self).__init__()

    def newDevice(self, d):
        pass

    def newProperty(self, p):
        pass

    def removeProperty(self, p):
        pass

    def newBLOB(self, bp):
        pass

    def newSwitch(self, svp):
        pass

    def newNumber(self, nvp):
        pass

    def newText(self, tvp):
        pass

    def newLight(self, lvp):
        pass

    def newMessage(self, d, m):
        pass

    def serverConnected(self):
        pass

    def serverDisconnected(self, code):
        pass


class OperateTelescopeINDI(threading.Thread):
    """
    This module provides the low-level telescope interface
    to the INDI driver of the telescope mount. It keeps a queue of instructions which is handled by
    an independent thread.
        
    """

    def __init__(self, configuration):
        """
        Look up configuration parameters (section INDI), initialize the instruction queue and
        define instruction types.
        
        :param configuration: object containing parameters set by the user
        """

        threading.Thread.__init__(self)

        # Copy location of configuration object.
        self.configuration = configuration

        # Initialize an empty instruction queue.
        self.instructions = []

        # Define instruction types (as dictionaries). Every instruction has a "name" field
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

        # Initialize default directions for the indi guiderinterface
        self.direction_north = 0
        self.direction_south = 1
        self.direction_east = 2
        self.direction_west = 3

        self.device_telescope = None
        self.telescope_connect = None
        self.telescope_radec = None
        self.telescope_guideNS = None
        self.telescope_guideWE = None

        if self.configuration.protocol_level > 0:
            Miscellaneous.protocol("OperateTelescope thread initialized")

    def run(self):
        """
        Execute the thread which serves the telescope instruction queue.
        
        :return: -
        """

        # Connect to INDI
        self.indiclnt = IndiClient()
        self.indiclnt.setServer("localhost", 7624)
        if not (self.indiclnt.connectServer()):
            print("No indiserver running on " + self.indiclnt.getHost() + ":" + str(
                self.indiclnt.getPort()) + " - Try to run")
            print("  indiserver indi_simulator_telescope indi_simulator_ccd")
            sys.exit(1)

        # get the telescope device
        self.telescope = self.configuration.conf.get("INDI", "telescope driver")
        while not self.device_telescope:
            time.sleep(0.5)
            self.device_telescope = self.indiclnt.getDevice(self.telescope)

        # wait CONNECTION property be defined for telescope
        while not self.telescope_connect:
            print("Connect to %s" % self.telescope)
            time.sleep(0.5)
            self.telescope_connect = self.device_telescope.getSwitch("CONNECTION")

        # if the telescope device is not connected, we do connect it
        if not (self.device_telescope.isConnected()):
            # Property vectors are mapped to iterable Python objects
            # Hence we can access each element of the vector using Python indexing
            # each element of the "CONNECTION" vector is a ISwitch
            self.telescope_connect[0].s = PyIndi.ISS_ON  # the "CONNECT" switch
            self.telescope_connect[1].s = PyIndi.ISS_OFF  # the "DISCONNECT" switch
            self.indiclnt.sendNewSwitch(self.telescope_connect)  # send this new value to the device

        # We want to set the ON_COORD_SET switch to engage tracking after goto
        # device.getSwitch is a helper to retrieve a property vector
        self.telescope_on_coord_set = self.device_telescope.getSwitch("ON_COORD_SET")
        while not self.telescope_on_coord_set:
            time.sleep(0.5)
            self.telescope_on_coord_set = self.device_telescope.getSwitch("ON_COORD_SET")
        # # the order below is defined in the property vector, look at the standard Properties page
        #        # or enumerate them in the Python shell when you're developing your program
        #        self.telescope_on_coord_set[0].s=PyIndi.ISS_ON  # TRACK
        #        self.telescope_on_coord_set[1].s=PyIndi.ISS_OFF # SLEW
        #        self.telescope_on_coord_set[2].s=PyIndi.ISS_OFF # SYNC
        #        self.indiclnt.sendNewSwitch(self.telescope_on_coord_set)

        # get coordinate object
        while not self.telescope_radec:
            time.sleep(0.5)
            self.telescope_radec = self.device_telescope.getNumber("EQUATORIAL_EOD_COORD")
        if self.configuration.protocol_level > 1:
            Miscellaneous.protocol("Scope init done: RA: " +
                                   str(round(self.telescope_radec[0].value * 15., 5)) +
                                   ", DE: " + str(round(self.telescope_radec[1].value, 5)) +
                                   " (degrees)")
        # get pulse guide objects
        while not self.telescope_guideNS:
            time.sleep(0.5)
            self.telescope_guideNS = self.device_telescope.getNumber("TELESCOPE_TIMED_GUIDE_NS")
        while not self.telescope_guideWE:
            time.sleep(0.5)
            self.telescope_guideWE = self.device_telescope.getNumber("TELESCOPE_TIMED_GUIDE_WE")

        # Serve the instruction queue, until the "terminate" instruction is encountered.
        while True:
            if len(self.instructions) > 0:
                # Get the next instruction from the queue, look up its type (name), and execute it.
                instruction = self.instructions.pop()
                # Miscellaneous.protocol("Instruction: %s" % instruction)

                # Slew the telescope to a given (RA, DE) position.
                if instruction['name'] == "slew to":
                    if self.configuration.protocol_level > 1:
                        Miscellaneous.protocol("Slewing telescope to: RA: " + str(
                            round(instruction['rect'] * 15., 5)) + ", DE: " + str(
                            round(instruction['decl'], 5)) + " degrees")
                    # Instruct the INDI driver to execute the SlewToCoordinates instruction.
                    # Please note that coordinates are in hours (RA) and degrees (DE).
                    self.telescope_radec[0].value = instruction['rect']
                    self.telescope_radec[1].value = instruction['decl']
                    self.indiclnt.sendNewNumber(self.telescope_radec)

                # Wait until the mount is standing still, then look up the current mount position.
                elif instruction['name'] == "lookup tel position":
                    # wait until the scope has finished moving
                    while self.telescope_radec.s == PyIndi.IPS_BUSY:
                        if self.configuration.protocol_level > 2:
                            Miscellaneous.protocol("Scope Moving  RA: " +
                                                   str(round(self.telescope_radec[0].value * 15., 5)) +
                                                   ", DE: " + str(round(self.telescope_radec[1].value, 5)) +
                                                   " (degrees)")
                        time.sleep(self.configuration.conf.getfloat("INDI", "wait interval"))

                    # Stationary state reached, copy measured position (in radians) into dict.
                    instruction['ra'] = radians(self.telescope_radec[0].value)
                    instruction['de'] = radians(self.telescope_radec[1].value)
                    # Signal that the instruction is finished.
                    instruction['finished'] = True
                    if self.configuration.protocol_level > 2:
                        Miscellaneous.protocol(
                            "Position looked-up: RA: " + str(round(self.telescope_radec[0].value * 15., 5)) +
                            ", DE: " + str(round(self.telescope_radec[1].value, 5)) + " (degrees)")

                # Find out which mount directions correspond to directions in the sky.
                elif instruction['name'] == "calibrate":
                    Miscellaneous.protocol("start calibrate")
                    # Look up the current RA position of the mount.
                    ra_begin = self.telescope_radec[0].value * 15
                    # Look up the specified length of the test movements in RA, DE.
                    calibrate_pulse_length = instruction['calibrate_pulse_length']
                    # Issue an INDI "move east" instruction and wait a short time.
                    self.telescope_guideWE[0].value = 0
                    self.telescope_guideWE[1].value = calibrate_pulse_length
                    self.indiclnt.sendNewNumber(self.telescope_guideWE)
                    Miscellaneous.protocol("calibrate RA1 %s" % (self.telescope_radec[0].value * 15))
                    time.sleep(calibrate_pulse_length / 1000.)
                    Miscellaneous.protocol("calibrate RA2 %s" % (self.telescope_radec[0].value * 15))
                    time.sleep(calibrate_pulse_length / 1000.)
                    Miscellaneous.protocol("calibrate RA3 %s" % (self.telescope_radec[0].value * 15))
                    # Look up resulting mount position in the sky.
                    ra_end = self.telescope_radec[0].value * 15
                    if self.configuration.protocol_level > 2:
                        Miscellaneous.protocol("calibrate in RA %s" % (ra_end - ra_begin))

                    # The end point was west of the initial point. Flip the RA directions.
                    if ra_end < ra_begin:
                        self.direction_east = 3
                        self.direction_west = 2
                    # Do the same in declination.
                    de_begin = self.telescope_radec[1].value * 15
                    # Issue an INDI "move north" instruction and wait a short time.
                    self.telescope_guideNS[0].value = calibrate_pulse_length
                    self.telescope_guideNS[1].value = 0
                    self.indiclnt.sendNewNumber(self.telescope_guideNS)
                    time.sleep(calibrate_pulse_length / 500.)
                    de_end = self.telescope_radec[1].value * 15
                    if self.configuration.protocol_level > 2:
                        Miscellaneous.protocol("calibrate in DE %s" % (de_end - de_begin))
                    if de_end < de_begin:
                        self.direction_north = 1
                        self.direction_south = 0

                    time.sleep(calibrate_pulse_length / 500.)

                    self.telescope_on_coord_set[0].s = PyIndi.ISS_ON  # TRACK
                    self.telescope_on_coord_set[1].s = PyIndi.ISS_OFF  # SLEW
                    self.telescope_on_coord_set[2].s = PyIndi.ISS_OFF  # SYNC
                    self.indiclnt.sendNewSwitch(self.telescope_on_coord_set)

                    # Now the direction variables correspond to true coordinates in the sky.
                    instruction['finished'] = True

                # Start guiding the telescope with given rates in RA, DE. Guiding will continue
                # (even if other instructions are handled in the meantime) until a "stop guiding"
                # instruction is found in the queue.
                elif instruction['name'] == "start guiding":
                    # Look up the specified guide rates.
                    rate_ra = instruction['rate_ra']
                    rate_de = instruction['rate_de']
                    # Define the start point: time and position (RA,DE).
                    start_time = time.mktime(datetime.now().timetuple())
                    start_ra = radians(self.telescope_radec[0].value * 15.)
                    start_de = radians(self.telescope_radec[1].value)
                    # Set guiding directions in RA, DE.
                    if numpy.sign(rate_ra) > 0:
                        direction_ra = self.direction_east
                    else:
                        direction_ra = self.direction_west
                    if numpy.sign(rate_de) > 0:
                        direction_de = self.direction_north
                    else:
                        direction_de = self.direction_south
                    # The actual guiding is done in a chain of "continue_guiding" instructions.
                    continue_guiding_instruction = self.continue_guiding
                    # Insert the first instruction into the queue.
                    self.instructions.insert(0, continue_guiding_instruction)

                # This instruction checks if the telescope is ahead or behind the moving target.
                # If it is behind, a PulseGuide instruction of specified length is issued.
                # Otherwise nothing is done. The assumption is that many more instructions are
                # issued than PulseGuides are necessary. Therefore, it cannot happen that the
                # telescope lags behind permanently.
                elif instruction['name'] == "continue guiding":
                    # Look up the time and current pointing of the telescope.
                    current_time = time.mktime(datetime.now().timetuple())
                    current_ra = radians(self.telescope_radec[0].value * 15.)
                    current_de = radians(self.telescope_radec[1].value)
                    # Compute where the telescope should be aimed at this time.
                    target_ra = start_ra + rate_ra * (current_time - start_time)
                    target_de = start_de + rate_de * (current_time - start_time)

                    # The telescope has been moved too little in RA. Issue a PulseGuide.
                    if abs(target_ra - start_ra) > abs(current_ra - start_ra):
                        if self.configuration.protocol_level > 2:
                            Miscellaneous.protocol("Pulse guide in RA %s" % abs(target_ra - start_ra))
                        if direction_ra == 2:
                            self.telescope_guideWE[0].value = 0
                            self.telescope_guideWE[1].value = int(
                                self.configuration.conf.getfloat("INDI", "guiding interval") * 1000.)
                        else:
                            self.telescope_guideWE[0].value = int(
                                self.configuration.conf.getfloat("INDI", "guiding interval") * 1000.)
                            self.telescope_guideWE[1].value = 0
                        self.indiclnt.sendNewNumber(self.telescope_guideWE)

                    # The telescope has been moved too little in DE. Issue a PulseGuide.
                    if abs(target_de - start_de) > abs(current_de - start_de):
                        if self.configuration.protocol_level > 2:
                            Miscellaneous.protocol("Pulse guide in DE %s" % abs(target_de - start_de))
                        if direction_de == 1:
                            self.telescope_guideNS[0].value = 0
                            self.telescope_guideNS[1].value = int(
                                self.configuration.conf.getfloat("INDI", "guiding interval") * 1000.)
                        else:
                            self.telescope_guideNS[0].value = int(
                                self.configuration.conf.getfloat("INDI", "guiding interval") * 1000.)
                            self.telescope_guideNS[1].value = 0
                        self.indiclnt.sendNewNumber(self.telescope_guideNS)
                    # Re-insert this instruction into the queue.
                    self.instructions.insert(0, instruction)
                    time.sleep(self.configuration.conf.getfloat("INDI", "guiding interval"))

                # Stop guiding by removing all instructions of type "continue guiding" from the
                # queue.
                elif instruction['name'] == "stop guiding":
                    self.remove_instruction(self.continue_guiding)
                    instruction['finished'] = True

                # These instructions are used when the user presses one of the arrow keys.
                elif instruction['name'] == "start moving north":
                    if self.configuration.protocol_level > 2:
                        Miscellaneous.protocol("Start North")
                    # Issue a PulseGuide in the specified direction.
                    self.telescope_guideNS[0].value = self.configuration.conf.getfloat("INDI",
                                                                                       "polling interval") * 1000.
                    self.telescope_guideNS[1].value = 0
                    self.indiclnt.sendNewNumber(self.telescope_guideNS)
                    # Re-insert this instruction into the queue, and wait a short time.
                    self.instructions.insert(0, instruction)
                    time.sleep(self.configuration.conf.getfloat("INDI", "polling interval"))

                # This instruction is used when the "arrow up" key is released.
                elif instruction['name'] == "stop moving north":
                    if self.configuration.protocol_level > 2:
                        Miscellaneous.protocol("Stop North")
                    # Remove all "start moving north" instructions from the queue.
                    self.remove_instruction(self.start_moving_north)
                    instruction['finished'] = True

                # The following instructions are analog to the two above. They handle the three
                # other coordinate directions.
                elif instruction['name'] == "start moving south":
                    self.telescope_guideNS[0].value = 0
                    self.telescope_guideNS[1].value = self.configuration.conf.getfloat("INDI",
                                                                                       "polling interval") * 1000.
                    self.indiclnt.sendNewNumber(self.telescope_guideNS)
                    self.instructions.insert(0, instruction)
                    time.sleep(self.configuration.conf.getfloat("INDI", "polling interval"))

                elif instruction['name'] == "stop moving south":
                    self.remove_instruction(self.start_moving_south)
                    instruction['finished'] = True

                elif instruction['name'] == "start moving east":
                    self.telescope_guideWE[0].value = 0
                    self.telescope_guideWE[1].value = self.configuration.conf.getfloat("INDI",
                                                                                       "polling interval") * 1000.
                    self.indiclnt.sendNewNumber(self.telescope_guideWE)
                    self.instructions.insert(0, instruction)
                    time.sleep(self.configuration.conf.getfloat("INDI", "polling interval"))

                elif instruction['name'] == "stop moving east":
                    self.remove_instruction(self.start_moving_east)
                    instruction['finished'] = True

                elif instruction['name'] == "start moving west":
                    self.telescope_guideWE[0].value = self.configuration.conf.getfloat("INDI",
                                                                                       "polling interval") * 1000.
                    self.telescope_guideWE[1].value = 0
                    self.indiclnt.sendNewNumber(self.telescope_guideWE)
                    self.instructions.insert(0, instruction)
                    time.sleep(self.configuration.conf.getfloat("INDI", "polling interval"))

                elif instruction['name'] == "stop moving west":
                    self.remove_instruction(self.start_moving_west)
                    instruction['finished'] = True

                # Issue a PulseGuide instruction with given direction and length.
                elif instruction['name'] == "pulse correction":
                    # If a "calibrate" instruction was executed, correct the direction values
                    # (0,1,2,3) to reflect the real motion of the telescope.
                    direction = [self.direction_north, self.direction_south, self.direction_east,
                                 self.direction_west][instruction['direction']]
                    # The pulse_length is counted in milliseconds.
                    pulse_length = instruction['pulse_length']
                    if direction == 0:
                        self.telescope_guideNS[0].value = pulse_length
                        self.telescope_guideNS[1].value = 0
                        self.indiclnt.sendNewNumber(self.telescope_guideNS)
                    elif direction == 1:
                        self.telescope_guideNS[0].value = 0
                        self.telescope_guideNS[1].value = pulse_length
                        self.indiclnt.sendNewNumber(self.telescope_guideNS)
                    elif direction == 2:
                        self.telescope_guideWE[0].value = 0
                        self.telescope_guideWE[1].value = pulse_length
                        self.indiclnt.sendNewNumber(self.telescope_guideWE)
                    elif direction == 3:
                        self.telescope_guideWE[0].value = pulse_length
                        self.telescope_guideWE[1].value = 0
                        self.indiclnt.sendNewNumber(self.telescope_guideWE)
                    instruction['finished'] = True

                # If the "terminate" instruction is encountered, exit the loop
                elif instruction['name'] == "terminate":
                    break
            # If no instruction is in the queue, wait a short time.
            else:
                time.sleep(self.configuration.conf.getfloat("INDI", "polling interval"))

        if self.configuration.protocol_level > 0:
            Miscellaneous.protocol("Ending OperateTelescope thread")

    def remove_instruction(self, instruction):
        """
        Remove all instructions of type "instruction" from the queue.
        
        :param instruction: instruction object
        :return: -
        """

        # Loop over the entire instruction queue and remove instructions of given type.
        for inst in self.instructions:
            if instruction['name'] == inst['name']:
                self.instructions.remove(inst)

    def confgetfloat(self, keyword):
        """
        Get a hardware specific configuration value
        
        :param keyword: keyword in the section
        :return: float value of the keyword
        """

        return self.configuration.conf.getfloat("INDI", keyword)
