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

import time
from math import degrees

from miscellaneous import Miscellaneous


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

        # Instantiate the OperateTelescope object and start the thread.
        try:
            from telescope_ascom import OperateTelescopeASCOM
            self.optel = OperateTelescopeASCOM(self.configuration)
        except ImportError:
            from telescope_indi import OperateTelescopeINDI
            self.optel = OperateTelescopeINDI(self.configuration)

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
        self.calibrate_pulse_length = self.optel.confgetfloat("wait interval") * 1000
        if self.configuration.protocol_level > 2:
            Miscellaneous.protocol("Calibrating guiding direction, time interval (ms): " + str(
                self.calibrate_pulse_length))
        # Choose the instruction, and set the pulse length.
        calibrate_instruction = self.optel.calibrate
        calibrate_instruction['calibrate_pulse_length'] = self.calibrate_pulse_length
        # Initialize the "finished" field to False, and insert the instruction into the queue.
        calibrate_instruction['finished'] = False
        self.optel.instructions.insert(0, calibrate_instruction)
        # Idle loop until the calibration is finished. Write out the results.
        while not calibrate_instruction['finished']:
            time.sleep(self.optel.confgetfloat("polling interval"))
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
            Miscellaneous.protocol("New coordinate read-out correction computed (deg.): RA: " + str(
                round(degrees(self.readout_correction_ra), 5)) + ", DE: " + str(
                round(degrees(self.readout_correction_de), 5)) + " (degrees)")

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
            time.sleep(self.optel.confgetfloat("polling interval"))
        return lookup_tel_position_instruction['ra'], lookup_tel_position_instruction['de']

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
            Miscellaneous.protocol("Start guiding, Rate(RA): " + str(
                round(degrees(start_guiding_instruction['rate_ra']) * 216000.,
                      3)) + ", Rate(DE): " + str(
                round(degrees(start_guiding_instruction['rate_de']) * 216000.,
                      3)) + " (arc min. / hour)")
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
            time.sleep(self.optel.confgetfloat("polling interval"))
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
            time.sleep(self.optel.confgetfloat("polling interval"))

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
            time.sleep(self.optel.confgetfloat("polling interval"))

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
            time.sleep(self.optel.confgetfloat("polling interval"))

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
            time.sleep(self.optel.confgetfloat("polling interval"))

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
            time.sleep(self.optel.confgetfloat("polling interval"))

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
