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

from miscellaneous import Miscellaneous


class OperateTelescope(threading.Thread):
    """
    This module contains two classes: This class "OperateTelescope" provides the low-level interface
    to the ASCOM driver of the telescope mount. It keeps a queue of instructions which is handled by
    an independent thread.

    Class Telescope provides the interface to the outside world. Its methods put instructions into
    the OperateTelescope queue. Some of its methods block until the OperateTelescope thread has
    acknowledged completion. Others are non-blocking.

    """

    def __init__(self, configuration):
        """
        Look up configuration parameters (section ASCOM), initialize the instruction queue and
        define instruction types.

        :param configuration: object containing parameters set by the user
        """

        threading.Thread.__init__(self)

        # Look up configuration parameters.
        self.configuration = configuration
        self.lookup_wait_interval = (configuration.conf.getfloat("ASCOM", "wait interval"))
        self.lookup_polling_interval = (configuration.conf.getfloat("ASCOM", "polling interval"))
        self.polling_length = int(self.lookup_polling_interval * 1000.)
        self.lookup_guiding_interval = (configuration.conf.getfloat("ASCOM", "guiding interval"))
        self.guiding_length = int(self.lookup_guiding_interval * 1000.)
        self.lookup_telescope_lookup_precision = (
        configuration.conf.getfloat("ASCOM", "telescope lookup precision") / 3600.)

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

        # Initialize default directions for the ASCOM instruction "PulseGuide"
        self.direction_north = 0
        self.direction_south = 1
        self.direction_east = 2
        self.direction_west = 3

        if self.configuration.protocol_level > 0:
            Miscellaneous.protocol("OperateTelescope thread initialized")

    def run(self):
        """
        Execute the thread which serves the telescope instruction queue.

        :return: -
        """

        # This is necessary because Windows COM objects are shared between threads.
        pythoncom.CoInitialize()

        # Initialize the ASCOM chooser and open a window where the telescope hub can be selected.
        x = win32com.client.Dispatch(self.configuration.conf.get("ASCOM", "chooser"))
        x.DeviceType = 'Telescope'
        # Set the comboBox in the chooser to the hub specified in the configuration.
        name = x.Choose(self.configuration.conf.get("ASCOM", "hub"))

        # Connect to the ASCOM hub.
        self.tel = win32com.client.Dispatch(name)

        # Check if the telescope was already connected to the hub. If not, establish the connection.
        if self.tel.Connected:
            if self.configuration.protocol_level > 1:
                Miscellaneous.protocol("The Telescope was already connected to the hub")
        else:
            self.tel.Connected = True
            if self.tel.Connected:
                if self.configuration.protocol_level > 1:
                    Miscellaneous.protocol("Telescope and hub are connected now.")
            else:
                if self.configuration.protocol_level > 0:
                    Miscellaneous.protocol("Unable to connect hub and telescope, expect exception")

        # Serve the instruction queue, until the "terminate" instruction is encountered.
        while True:
            if len(self.instructions) > 0:
                # Get the next instruction from the queue, look up its type (name), and execute it.
                instruction = self.instructions.pop()

                # Slew the telescope to a given (RA, DE) position.
                if instruction['name'] == "slew to":
                    if self.configuration.protocol_level > 1:
                        Miscellaneous.protocol("Slewing telescope to: RA: " + str(round(instruction[
                                            'rect'] * 15., 5)) + ", DE: " + str(round(instruction[
                                            'decl'], 5)) + " degrees")
                    # Instruct the ASCOM driver to execute the SlewToCoordinates instruction.
                    # Please note that coordinates are in hours (RA) and degrees (DE).
                    self.tel.SlewToCoordinates(instruction['rect'], instruction['decl'])

                # Wait until the mount is standing still, then look up the current mount position.
                elif instruction['name'] == "lookup tel position":
                    # Initialize (rect, decl) with impossible coordinates, and iteration count to 0.
                    rect = 25.
                    decl = 91.
                    iter_count = 0
                    # Idle loop until changes in RA,DE are smaller than specified threshold.
                    while (abs(self.tel.RightAscension - rect) >
                                   self.lookup_telescope_lookup_precision / 15. or
                            abs(self.tel.Declination - decl) >
                                   self.lookup_telescope_lookup_precision):
                        rect = self.tel.RightAscension
                        decl = self.tel.Declination
                        iter_count += 1
                        time.sleep(self.lookup_wait_interval)
                    # Stationary state reached, copy measured position (in radians) into dict.
                    instruction['ra'] = radians(rect * 15.)
                    instruction['de'] = radians(decl)
                    # Signal that the instruction is finished.
                    instruction['finished'] = True
                    if self.configuration.protocol_level > 2:
                        Miscellaneous.protocol("Position looked-up: RA: " +
                                               str(round(rect * 15., 5)) +
                                               ", DE: " + str(round(decl, 5)) +
                                               " (degrees), iterations: " + str(iter_count))

                # Find out which ASCOM directions correspond to directions in the sky.
                elif instruction['name'] == "calibrate":
                    # Look up the current RA position of the mount.
                    ra_begin = self.tel.RightAscension
                    # Look up the specified length of the test movements in RA, DE.
                    calibrate_pulse_length = instruction['calibrate_pulse_length']
                    # Issue an ASCOM "move east" instruction and wait a short time.
                    self.tel.PulseGuide(2, calibrate_pulse_length)
                    time.sleep(calibrate_pulse_length / 500.)
                    # Look up resulting mount position in the sky.
                    ra_end = self.tel.RightAscension
                    # The end point was west of the initial point. Flip the RA directions.
                    if ra_end < ra_begin:
                        self.direction_east = 3
                        self.direction_west = 2
                    # Do the same in declination.
                    de_begin = self.tel.Declination
                    self.tel.PulseGuide(0, calibrate_pulse_length)
                    time.sleep(calibrate_pulse_length / 500.)
                    de_end = self.tel.Declination
                    if de_end < de_begin:
                        self.direction_north = 1
                        self.direction_south = 0
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
                    start_ra = radians(self.tel.RightAscension * 15.)
                    start_de = radians(self.tel.Declination)
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
                # If it is behind, an ASCOM PulseGuide instruction of specified length is issued.
                # Otherwise nothing is done. The assumption is that many more instructions are
                # issued than PulseGuides are necessary. Therefore, it cannot happen that the
                # telescope lags behind permanently.
                elif instruction['name'] == "continue guiding":
                    # Look up the time and current pointing of the telescope.
                    current_time = time.mktime(datetime.now().timetuple())
                    current_ra = radians(self.tel.RightAscension * 15.)
                    current_de = radians(self.tel.Declination)
                    # Compute where the telescope should be aimed at this time.
                    target_ra = start_ra + rate_ra * (current_time - start_time)
                    target_de = start_de + rate_de * (current_time - start_time)
                    # The telescope has been moved too little in RA. Issue a PulseGuide.
                    if abs(target_ra - start_ra) > abs(current_ra - start_ra):
                        if self.configuration.protocol_level > 2:
                            Miscellaneous.protocol("Pulse guide in RA")
                        self.tel.PulseGuide(direction_ra, self.guiding_length)
                    # The telescope has been moved too little in DE. Issue a PulseGuide.
                    if abs(target_de - start_de) > abs(current_de - start_de):
                        if self.configuration.protocol_level > 2:
                            Miscellaneous.protocol("Pulse guide in DE")
                        self.tel.PulseGuide(direction_de, self.guiding_length)
                    # Re-insert this instruction into the queue.
                    self.instructions.insert(0, instruction)
                    time.sleep(self.lookup_guiding_interval)

                # Stop guiding by removing all instructions of type "continue guiding" from the
                # queue.
                elif instruction['name'] == "stop guiding":
                    self.remove_instruction(self.continue_guiding)
                    instruction['finished'] = True

                # These instructions are used when the user presses one of the arrow keys.
                elif instruction['name'] == "start moving north":
                    # Issue a PulseGuide in the specified direction.
                    self.tel.PulseGuide(self.direction_north, self.polling_length)
                    # Re-insert this instruction into the queue, and wait a short time.
                    self.instructions.insert(0, instruction)
                    time.sleep(self.lookup_polling_interval)

                # This instruction is used when the "arrow up" key is released.
                elif instruction['name'] == "stop moving north":
                    # Remove all "start moving north" instructions from the queue.
                    self.remove_instruction(self.start_moving_north)
                    instruction['finished'] = True

                # The following instructions are analog to the two above. They handle the three
                # other coordinate directions.
                elif instruction['name'] == "start moving south":
                    self.tel.PulseGuide(self.direction_south, self.polling_length)
                    self.instructions.insert(0, instruction)
                    time.sleep(self.lookup_polling_interval)

                elif instruction['name'] == "stop moving south":
                    self.remove_instruction(self.start_moving_south)
                    instruction['finished'] = True

                elif instruction['name'] == "start moving east":
                    self.tel.PulseGuide(self.direction_east, self.polling_length)
                    self.instructions.insert(0, instruction)
                    time.sleep(self.lookup_polling_interval)

                elif instruction['name'] == "stop moving east":
                    self.remove_instruction(self.start_moving_east)
                    instruction['finished'] = True

                elif instruction['name'] == "start moving west":
                    self.tel.PulseGuide(self.direction_west, self.polling_length)
                    self.instructions.insert(0, instruction)
                    time.sleep(self.lookup_polling_interval)

                elif instruction['name'] == "stop moving west":
                    self.remove_instruction(self.start_moving_west)
                    instruction['finished'] = True

                # Issue an ASCOM PulseGuide instruction with given direction and length.
                elif instruction['name'] == "pulse correction":
                    # If a "calibrate" instruction was executed, correct the ASCOM direction values
                    # (0,1,2,3) to reflect the real motion of the telescope.
                    direction = [self.direction_north, self.direction_south, self.direction_east,
                                 self.direction_west][instruction['direction']]
                    # The pulse_length is counted in milliseconds.
                    pulse_length = instruction['pulse_length']
                    # Perform the ASCOM PulseGuide instruction.
                    self.tel.PulseGuide(direction, pulse_length)
                    instruction['finished'] = True

                # If the "terminate" instruction is encountered, exit the loop
                elif instruction['name'] == "terminate":
                    break
            # If no instruction is in the queue, wait a short time.
            else:
                time.sleep(self.lookup_polling_interval)

        # See comment at the beginning of this method.
        pythoncom.CoUninitialize()
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


class Telescope:
    """
    This class provides the interface to the low-level class "OperateTelescope". The methods of
    class "Telescope" are used by MoonPanoramaMaker to handle telescope operations.

    """

    def __init__(self, configuration):
        """
        Look up configuration parameters and initialize some instance variables.

        :param configuration: object containing parameters set by the user
        """

        self.configuration = configuration
        self.lookup_wait_interval = (configuration.conf.getfloat("ASCOM", "wait interval"))
        self.lookup_polling_interval = (configuration.conf.getfloat("ASCOM", "polling interval"))

        # Instantiate the OperateTelescope object and start the thread.
        self.optel = OperateTelescope(self.configuration)
        self.optel.start()

        self.readout_correction_ra = 0.
        self.readout_correction_de = 0.
        self.guiding_active = False

    def calibrate(self):
        """
        Check if movements in RA,DE are mirror-reversed. Directions will be corrected in future
        instructions. This method blocks until the low-level instruction is finished.

        :return: -
        """

        # Set the pulse length for test movements. Make sure that "lookup_wait_interval" is not
        # too large, otherwise this operation will take too long.
        self.calibrate_pulse_length = self.lookup_wait_interval * 1000
        if self.configuration.protocol_level > 2:
            Miscellaneous.protocol("Calibrating guiding direction, time interval (ms): " +
                str(self.calibrate_pulse_length))
        # Choose the instruction, and set the pulse length.
        calibrate_instruction = self.optel.calibrate
        calibrate_instruction['calibrate_pulse_length'] = self.calibrate_pulse_length
        # Initialize the "finished" field to False, and insert the instruction into the queue.
        calibrate_instruction['finished'] = False
        self.optel.instructions.insert(0, calibrate_instruction)
        # Idle loop until the calibration is finished. Write out the results.
        while not calibrate_instruction['finished']:
            time.sleep(self.lookup_polling_interval)
        if self.configuration.protocol_level > 2:
            if self.optel.direction_east == 2:
                Miscellaneous.protocol("Direction for corrections in RA: normal")
            else:
                Miscellaneous.protocol("Direction for corrections in RA: reversed")
            if self.optel.direction_north == 0:
                Miscellaneous.protocol("Direction for corrections in DE: normal")
            else:
                Miscellaneous.protocol("Direction for corrections in DE: reversed")

    def slew_to(self, ra, de):
        """
        Move the telescope to a given position (ra, de) in the sky. This method blocks until the
        position is reached.

        :param ra: Target right ascension (radians)
        :param de: Target declination (radians)
        :return: -
        """

        # Convert coordinates into hours and degrees, fill parameters into instruction fields and
        # put the instruction into the queue.
        rect = degrees(ra) / 15.
        decl = degrees(de)
        slew_to_instruction = self.optel.slew_to
        slew_to_instruction['rect'] = rect
        slew_to_instruction['decl'] = decl
        self.optel.instructions.insert(0, slew_to_instruction)
        # Look up the position where the telescope went.
        (rect_lookup, decl_lookup) = self.lookup_tel_position_uncorrected()
        # For some mounts there is a systematic difference between target and the position
        # looked-up. Compute the difference. It will be used to correct future look-ups.
        self.readout_correction_ra = ra - rect_lookup
        self.readout_correction_de = de - decl_lookup
        # Write the corrections to the protocol file.
        if self.configuration.protocol_level > 2:
            Miscellaneous.protocol("New coordinate read-out correction computed (deg.): RA: " +
                                   str(round(degrees(self.readout_correction_ra), 5)) + ", DE: " +
                                   str(round(degrees(self.readout_correction_de), 5)) + " (degrees)")

    def lookup_tel_position_uncorrected(self):
        """
        Look up the current telescope position. Block until the low-level instruction is finished
        and return its results. The result is not corrected for the potential mismatch between
        slew-to and look-up coordinates.

        :return: (RA, DE) where the telescope is currently pointing (coordinates in radians).
        """

        lookup_tel_position_instruction = self.optel.lookup_tel_position
        lookup_tel_position_instruction['finished'] = False
        self.optel.instructions.insert(0, lookup_tel_position_instruction)
        while not lookup_tel_position_instruction['finished']:
            time.sleep(self.lookup_polling_interval)
        return (lookup_tel_position_instruction['ra'], lookup_tel_position_instruction['de'])

    def lookup_tel_position(self):
        """
        Look up the current telescope position. Block until the low-level instruction is
        finished and return its results. If a slew-to operation was performed before calling this
        method, the result is corrected for the potential mismatch between slew-to and look-up
        coordinates.

        :return: (RA, DE) where the telescope is currently pointing (coordinates in radians).
        """

        (tel_ra_uncorrected, tel_de_uncorrected) = self.lookup_tel_position_uncorrected()
        # Apply the correction as measured during the last slew-to operation.
        return (tel_ra_uncorrected + self.readout_correction_ra,
                tel_de_uncorrected + self.readout_correction_de)

    def start_guiding(self, rate_ra, rate_de):
        """
        Start guiding a moving target with given rates in (RA, DE). This method does not block.

        :param rate_ra: speed of the object in right ascension (in radians/sec.)
        :param rate_de: speed of the object in declination (in radians/sec.)
        :return: -
        """

        # Fill the guiding rates into the instruction fields.
        start_guiding_instruction = self.optel.start_guiding
        start_guiding_instruction['rate_ra'] = rate_ra
        start_guiding_instruction['rate_de'] = rate_de
        if self.configuration.protocol_level > 2:
            Miscellaneous.protocol("Start guiding, Rate(RA): " + str(round(degrees(
                start_guiding_instruction['rate_ra']) * 216000., 3)) + ", Rate(DE): " + str(round(
                degrees(start_guiding_instruction['rate_de']) * 216000., 3)) + " (arc min. / hour)")
        # Insert the instruction into the queue.
        self.optel.instructions.insert(0, start_guiding_instruction)
        # Set the "guiding_active" flag to True.
        self.guiding_active = True

    def stop_guiding(self):
        """
        Stop guiding the moving target. This method blocks until an acknowledgement is received
        from the OperateTelescope thread.

        :return: -
        """

        if self.configuration.protocol_level > 2:
            Miscellaneous.protocol("Stop guiding")
        # Insert the instruction into the low-level queue and wait until it is finished.
        stop_guiding_instruction = self.optel.stop_guiding
        stop_guiding_instruction['finished'] = False
        self.optel.instructions.insert(0, stop_guiding_instruction)
        while not stop_guiding_instruction['finished']:
            time.sleep(self.lookup_polling_interval)
        # Reset the "guiding_active" flag.
        self.guiding_active = False

    def move_north(self):
        """
        Start to move the telescope north. This method is non-blocking. The motion will end only
        when the "stop_move_north" method is called.

        :return: -
        """

        self.optel.instructions.insert(0, self.optel.start_moving_north)

    def stop_move_north(self):
        """
        Stop moving the telescope north. This method blocks until the motion is ended.

        :return: -
        """

        stop_moving_north_instruction = self.optel.stop_moving_north
        stop_moving_north_instruction['finished'] = False
        # self.optel.instructions.insert(0, stop_moving_north_instruction)
        self.optel.instructions.append(stop_moving_north_instruction)
        while not stop_moving_north_instruction['finished']:
            time.sleep(self.lookup_polling_interval)

    def move_south(self):
        """
        Start to move the telescope south. This method is non-blocking. The motion will
        end only when the "stop_move_south" method is called.

        :return: -
        """

        self.optel.instructions.insert(0, self.optel.start_moving_south)

    def stop_move_south(self):
        """
        Stop moving the telescope south. This method blocks until the motion is ended.

        :return: -
        """

        stop_moving_south_instruction = self.optel.stop_moving_south
        stop_moving_south_instruction['finished'] = False
        # self.optel.instructions.insert(0, stop_moving_south_instruction)
        self.optel.instructions.append(stop_moving_south_instruction)
        while not stop_moving_south_instruction['finished']:
            time.sleep(self.lookup_polling_interval)

    def move_east(self):
        """
        Start to move the telescope east. This method is non-blocking. The motion will
        end only when the "stop_move_east" method is called.

        :return: -
        """

        self.optel.instructions.insert(0, self.optel.start_moving_east)

    def stop_move_east(self):
        """
        Stop moving the telescope east. This method blocks until the motion is ended.

        :return: -
        """

        stop_moving_east_instruction = self.optel.stop_moving_east
        stop_moving_east_instruction['finished'] = False
        # self.optel.instructions.insert(0, stop_moving_east_instruction)
        self.optel.instructions.append(stop_moving_east_instruction)
        while not stop_moving_east_instruction['finished']:
            time.sleep(self.lookup_polling_interval)

    def move_west(self):
        """
        Start to move the telescope west. This method is non-blocking. The motion will
        end only when the "stop_move_west" method is called.

        :return: -
        """

        self.optel.instructions.insert(0, self.optel.start_moving_west)

    def stop_move_west(self):
        """
        Stop moving the telescope west. This method blocks until the motion is ended.

        :return: -
        """

        stop_moving_west_instruction = self.optel.stop_moving_west
        stop_moving_west_instruction['finished'] = False
        # self.optel.instructions.insert(0, stop_moving_west_instruction)
        self.optel.instructions.append(stop_moving_west_instruction)
        while not stop_moving_west_instruction['finished']:
            time.sleep(self.lookup_polling_interval)

    def pulse_correction(self, direction, pulse_length):
        """
        Issue a pulse correction of given length into a given direction. If the "calibrate" method
        was called before, the direction is corrected for a potential mirror-reversal in the mount.
        The method blocks until the pulse correction is finished.

        :param direction: one of 0, 1 ,2, 3 for north, south, east, west
        :param pulse_length: length (in milliseconds)
        :return: -
        """

        pulse_correction_instruction = self.optel.pulse_correction
        pulse_correction_instruction['direction'] = direction
        pulse_correction_instruction['pulse_length'] = pulse_length
        pulse_correction_instruction['finished'] = False
        self.optel.instructions.append(pulse_correction_instruction)
        while not pulse_correction_instruction['finished']:
            time.sleep(self.lookup_polling_interval)

    def terminate(self):
        """
        Insert a "terminate" instruction into the queue, wait for the OperateTelescope thread to
        finish and write a message to the protocol file.

        :return:
        """

        if self.configuration.protocol_level > 0:
            Miscellaneous.protocol("Terminating telescope")
        self.optel.instructions.insert(0, self.optel.terminate)
        self.optel.join()
        if self.configuration.protocol_level > 0:
            Miscellaneous.protocol("Telescope terminated")
