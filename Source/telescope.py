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


This module contains three classes: This class "OperateTelescopeASCOM" provides the low-level
interface to the ASCOM driver of the telescope mount. It keeps a queue of instructions which is
handled by an independent thread.

The class "OperateTelescopeINDI" has the same external interface as "OperateTelescopeASCOM". It
uses the INDI telescope interface instead of ASCOM.

Class "Telescope" provides the interface to the outside world. Its methods put instructions into
the OperateTelescopeASCOM/INDI queue. Some of its methods block until the OperateTelescopeASCOM/
INDI thread has acknowledged completion. Others are non-blocking.

"""

import threading
import time
from datetime import datetime
from enum import IntEnum
from math import degrees, radians, pi

import numpy
from exceptions import TelescopeException, ASCOMImportException, ASCOMConnectException, \
    ASCOMPropertyException, INDIImportException, INDIConnectException, INDIPropertyException
from miscellaneous import Miscellaneous


class OperateTelescopeASCOM(threading.Thread):
    """
    This class provides the low-level interface to the ASCOM driver of the telescope mount. It
    keeps a queue of instructions which is handled by an independent thread.

    """

    def __init__(self, configuration):
        """
        Initialize the instruction queue and define instruction types.

        :param configuration: object containing parameters set by the user
        """

        threading.Thread.__init__(self)

        # Copy location of configuration object.
        self.configuration = configuration

        # The following flag is set to True at the end of the driver initialization phase. If during
        # initialization an error occurs, the message is stored as "self.initialization_error".
        self.initialized = False
        self.initialization_error = ""

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

        # Initialize instance variables.
        self.tel = None

        if self.configuration.protocol_level > 0:
            Miscellaneous.protocol("OperateTelescopeASCOM thread initialized.")

    def connect_and_test_telescope(self, driver_name):
        """
        Access the telescope driver as a Win32Com object, connect to it, and find out if it supports
        the functions required by MoonPanoramaMaker.

        :param driver_name: Name of the telescope driver, as returned by the ASCOM chooser.
        :return: telescope driver object supporting ASCOM methods and properties.
        """

        try:
            import win32com.client
        except ImportError:
            raise ASCOMImportException("Unable to import Win32com client. "
                                       "Is this a Windows system?")

        # Try to get access to the Win32Com object.
        try:
            telescope_driver = win32com.client.Dispatch(driver_name)
        except:
            raise ASCOMConnectException("ASCOM: Unable to access telescope driver.")

        # Check if the driver is already connected to the telescope. If not, try to establish the
        # connection.
        try:
            if telescope_driver.Connected:
                if self.configuration.protocol_level > 1:
                    Miscellaneous.protocol(
                        "OperateTelescopeASCOM: The telescope was already connected.")
            else:
                telescope_driver.Connected = True
                if telescope_driver.Connected:
                    if self.configuration.protocol_level > 1:
                        Miscellaneous.protocol(
                            "OperateTelescopeASCOM: The telescope is connected now.")
                else:
                    raise ASCOMConnectException("ASCOM: Unable to connect to telescope driver.")
        except:
            # The "Connected" property of the driver cannot be accessed properly.
            raise ASCOMPropertyException(
                "ASCOM: Unable to access the 'Connected' property of the telescope driver.")

        # Check the availability of fundamental driver properties needed by MoonPanoramaMaker. Raise
        # an exception if one property is missing.
        try:
            can_slew = telescope_driver.CanSlew
            can_set_tracking = telescope_driver.CanSetTracking
            can_pulse_guide = telescope_driver.CanPulseGuide
            can_set_guide_rates = telescope_driver.CanSetGuideRates
        except:
            raise ASCOMConnectException(
                "ASCOM: The telescope driver does not support required property lookups.")

        if not can_slew:
            raise ASCOMPropertyException(
                "ASCOM: The telescope driver is not able to slew to RA/DE.")
        elif not can_set_tracking:
            raise ASCOMPropertyException(
                "ASCOM: The telescope driver cannot be set to track in RA/DE.")
        elif not can_pulse_guide:
            raise ASCOMPropertyException(
                "ASCOM: The telescope driver is not able to do pulse guide corrections.")
        elif not can_set_guide_rates:
            raise ASCOMPropertyException(
                "ASCOM: The telescope driver is not able to set guide rates.")

        # Return a reference to the driver object.
        return telescope_driver

    def switch_on_tracking(self):
        """
        Try to switch on tracking. If the telescope driver responds with an error, raise an
        exception and set a human-readable error message.

        :return:
        """

        try:
            # Switch on tracking, if not yet done.
            if not self.tel.Tracking:
                self.tel.Tracking = True
                if self.configuration.protocol_level > 1:
                    Miscellaneous.protocol("OperateTelescopeASCOM: telescope tracking has been "
                                           "switched on.")
        except:
            raise ASCOMPropertyException("ASCOM: Telescope tracking could not be switched on.")

    def set_pulse_guide_speed(self):
        """
        Set the PulseGuide speed (in units of deg/sec). This operation can fail if the user has
        specified an out-of-range value in the configuration dialog. In this case it is important to
        point the user at the concrete problem and tell him/her how to resolve it.

        :return:
        """

        try:
            self.tel.GuideRateRightAscension = \
                self.configuration.conf.getfloat("ASCOM", "pulse guide speed RA")
            self.tel.GuideRateDeclination = \
                self.configuration.conf.getfloat("ASCOM", "pulse guide speed DE")
            if self.configuration.protocol_level > 1:
                Miscellaneous.protocol(
                    "OperateTelescopeASCOM: pulse guide speed in RA set to " + str(
                        self.configuration.conf.get("ASCOM",
                                                    "pulse guide speed RA")) + ", in DE to " + str(
                        self.configuration.conf.get("ASCOM", "pulse guide speed DE")) + ".")
        except:
            raise ASCOMPropertyException(
                "ASCOM: The 'pulse guide speed' value set by the user in the "
                "configuration dialog cannot be handled by the telescope "
                "driver. Most likely it is too large. Try again with a "
                "smaller value.")

    def run(self):
        """
        Execute the thread which serves the telescope instruction queue.

        :return: -
        """

        try:
            import pythoncom
        except ImportError:
            # Save the error message to be looked up by high-level telescope thread.
            self.initialization_error = "Pythoncom module could not be imported. " \
                                        "Is this a Windows system?"
            if self.configuration.protocol_level > 0:
                Miscellaneous.protocol("Ending OperateTelescopeASCOM thread.")
            return
        # This is necessary because Windows COM objects are shared between threads.
        pythoncom.CoInitialize()

        # Connect to the ASCOM telescope driver and check if it is working properly.
        try:
            self.tel = self.connect_and_test_telescope(
                self.configuration.conf.get("ASCOM", "telescope driver"))
            # Switch on tracking, if not yet done.
            self.switch_on_tracking()
            # Set the PulseGuide speed.
            self.set_pulse_guide_speed()
        except Exception as e:
            # Save the error message to be looked up by high-level telescope thread.
            self.initialization_error = str(e)
            # Clean up the low-level telescope thread and exit.
            pythoncom.CoUninitialize()
            if self.configuration.protocol_level > 0:
                Miscellaneous.protocol("Ending OperateTelescopeASCOM thread.")
            return

        # After successful connection to the telescope driver, mark the interface initialized.
        if self.configuration.protocol_level > 0:
            Miscellaneous.protocol("OperateTelescopeASCOM: telescope driver is working properly.")
        self.initialized = True

        # Serve the instruction queue, until the "terminate" instruction is encountered.
        while True:
            if len(self.instructions) > 0:
                # Get the next instruction from the queue, look up its type (name), and execute it.
                instruction = self.instructions.pop()

                # Slew the telescope to a given (RA, DE) position.
                if instruction['name'] == "slew to":
                    if self.configuration.protocol_level > 1:
                        Miscellaneous.protocol("ASCOM: Slewing telescope to RA " + str(
                            round(instruction['rect'] * 15., 5)) + ", DE " + str(
                            round(instruction['decl'], 5)) + " (degrees).")
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
                    while (abs(self.tel.RightAscension - rect) > self.configuration.conf.getfloat(
                            "ASCOM", "telescope lookup precision") / 54000. or abs(
                        self.tel.Declination - decl) > self.configuration.conf.getfloat(
                            "ASCOM", "telescope lookup precision") / 3600.):
                        rect = self.tel.RightAscension
                        decl = self.tel.Declination
                        iter_count += 1
                        time.sleep(self.configuration.conf.getfloat("ASCOM", "wait interval"))
                    # Stationary state reached, copy measured position (in radians) into dict.
                    instruction['ra'] = radians(rect * 15.)
                    instruction['de'] = radians(decl)
                    # Signal that the instruction is finished.
                    instruction['finished'] = True
                    if self.configuration.protocol_level > 2:
                        Miscellaneous.protocol(
                            "OperateTelescopeASCOM: Position looked-up, RA " + str(
                                round(rect * 15., 5)) + ", DE " + str(
                                round(decl, 5)) + " (degrees), iterations: " + str(
                                iter_count) + ".")

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
                            Miscellaneous.protocol("OperateTelescopeASCOM: Pulse guide in RA.")
                        self.tel.PulseGuide(direction_ra, int(
                            self.configuration.conf.getfloat("ASCOM", "guiding interval") * 1000.))
                    # The telescope has been moved too little in DE. Issue a PulseGuide.
                    if abs(target_de - start_de) > abs(current_de - start_de):
                        if self.configuration.protocol_level > 2:
                            Miscellaneous.protocol("OperateTelescopeASCOM: Pulse guide in DE.")
                        self.tel.PulseGuide(direction_de, int(
                            self.configuration.conf.getfloat("ASCOM", "guiding interval") * 1000.))
                    # Re-insert this instruction into the queue.
                    self.instructions.insert(0, instruction)
                    time.sleep(self.configuration.conf.getfloat("ASCOM", "guiding interval"))

                # Stop guiding by removing all instructions of type "continue guiding" from the
                # queue.
                elif instruction['name'] == "stop guiding":
                    self.remove_instruction(self.continue_guiding)
                    instruction['finished'] = True

                # These instructions are used when the user presses one of the arrow keys.
                elif instruction['name'] == "start moving north":
                    # Issue a PulseGuide in the specified direction.
                    self.tel.PulseGuide(self.direction_north,
                                        int(self.configuration.polling_interval * 1000.))
                    # Re-insert this instruction into the queue, and wait a short time.
                    self.instructions.insert(0, instruction)
                    time.sleep(self.configuration.polling_interval)

                # This instruction is used when the "arrow up" key is released.
                elif instruction['name'] == "stop moving north":
                    # Remove all "start moving north" instructions from the queue.
                    self.remove_instruction(self.start_moving_north)
                    instruction['finished'] = True

                # The following instructions are analog to the two above. They handle the three
                # other coordinate directions.
                elif instruction['name'] == "start moving south":
                    self.tel.PulseGuide(self.direction_south,
                                        int(self.configuration.polling_interval * 1000.))
                    self.instructions.insert(0, instruction)
                    time.sleep(self.configuration.polling_interval)

                elif instruction['name'] == "stop moving south":
                    self.remove_instruction(self.start_moving_south)
                    instruction['finished'] = True

                elif instruction['name'] == "start moving east":
                    self.tel.PulseGuide(self.direction_east,
                                        int(self.configuration.polling_interval * 1000.))
                    self.instructions.insert(0, instruction)
                    time.sleep(self.configuration.polling_interval)

                elif instruction['name'] == "stop moving east":
                    self.remove_instruction(self.start_moving_east)
                    instruction['finished'] = True

                elif instruction['name'] == "start moving west":
                    self.tel.PulseGuide(self.direction_west,
                                        int(self.configuration.polling_interval * 1000.))
                    self.instructions.insert(0, instruction)
                    time.sleep(self.configuration.polling_interval)

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
                time.sleep(self.configuration.polling_interval)

        # See comment at the beginning of this method.
        pythoncom.CoUninitialize()
        if self.configuration.protocol_level > 0:
            Miscellaneous.protocol("Ending OperateTelescopeASCOM thread.")

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


class interfaceType(IntEnum):
    """
    This enumeration defines the interface types used by INDI to characterize drivers. It
    serves to select those drivers connected to an INDI server that implement the telescope
    interface.
    """
    TELESCOPE_INTERFACE = (1 << 0)
    CCD_INTERFACE = (1 << 1)
    GUIDER_INTERFACE = (1 << 2)
    FOCUSER_INTERFACE = (1 << 3)
    FILTER_INTERFACE = (1 << 4)
    DOME_INTERFACE = (1 << 5)
    GPS_INTERFACE = (1 << 6)
    WEATHER_INTERFACE = (1 << 7)
    AO_INTERFACE = (1 << 8)
    DUSTCAP_INTERFACE = (1 << 9)
    LIGHTBOX_INTERFACE = (1 << 10)
    DETECTOR_INTERFACE = (1 << 11)
    ROTATOR_INTERFACE = (1 << 12)
    AUX_INTERFACE = (1 << 15)


class OperateTelescopeINDI(threading.Thread):
    """
    This class has the same external interface as "OperateTelescopeASCOM". It uses the INDI
    telescope interface instead of ASCOM.

    """

    def __init__(self, configuration):
        """
        Initialize the instruction queue and define instruction types.

        :param configuration: object containing parameters set by the user
        """

        threading.Thread.__init__(self)

        # Copy location of configuration object.
        self.configuration = configuration

        # The following flag is set to True at the end of the driver initialization phase. If during
        # initialization an error occurs, the message is stored as "self.initialization_error".
        self.initialized = False
        self.initialization_error = ""
        self.instruction_error = ""

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

        # Initialize default directions for the "PulseGuide" instructions
        self.direction_north = 0
        self.direction_south = 1
        self.direction_east = 2
        self.direction_west = 3

        self.indiclnt = None
        self.device_list = []
        self.device_name_list = []
        self.telescope = None
        self.device_telescope = None
        self.telescope_on_coord_set = None
        self.telescope_connect = None
        self.telescope_radec = None
        self.telescope_guideNS = None
        self.telescope_guideWE = None

        if self.configuration.protocol_level > 0:
            Miscellaneous.protocol("OperateTelescopeINDI thread initialized.")

    def connect_and_test_telescope(self):
        """
        Access the telescope driver via the INDI server, connect to it, and find out if it supports
        the functions required by MoonPanoramaMaker.

        :return: -
        """

        # Try to import PyIndi. If this fails, the program most likely runs on a Windows computer.
        try:
            import PyIndi
            from indi_client import IndiClient
        except ImportError:
            raise INDIImportException(
                "Unable to import INDI client. Is INDI installed on this system?")

        # Try to get access to the INDI client.
        try:
            self.indiclnt = IndiClient(self.device_list, self.device_name_list)
            server_address = self.configuration.conf.get("INDI", "server url")
            server_port = self.configuration.indi_port_number
            self.indiclnt.setServer(server_address, server_port)
        except:
            raise INDIConnectException("Unable to connect to INDI client.")

        # Try to connect to the INDI server.
        if not (self.indiclnt.connectServer()):
            raise INDIConnectException(
                "No INDI server running on " + self.indiclnt.getHost() + ":" + str(
                    self.indiclnt.getPort()) + ".")

        # Get the list of available devices.
        for iteration in range(self.configuration.polling_time_out_count):
            time.sleep(self.configuration.polling_interval)
            if len(self.device_list) > 0:
                break
        if len(self.device_list) == 0:
            raise INDIConnectException("INDI: Unable to get the device list.")

        # Look for a device which implements the TELESCOPE_INTERFACE. Exit the
        # loop when the first such driver is found.
        self.device_telescope = None
        for device in self.device_list:
            driver_info = device.getText("DRIVER_INFO")
            for iteration in range(self.configuration.polling_time_out_count):
                time.sleep(self.configuration.polling_interval)
                if driver_info:
                    break
                driver_info = device.getText("DRIVER_INFO")
            if not driver_info:
                raise INDIConnectException("INDI: Unable to get driver info.")
            # The driver info is available, check the interface types it implements.
            if int(driver_info[3].text) & interfaceType.TELESCOPE_INTERFACE:
                if self.configuration.protocol_level > 0:
                    Miscellaneous.protocol(
                        "OperateTelescopeINDI: Telescope driver found: " + driver_info[
                            0].text + ".")
                self.device_telescope = device
                break
        # There is no device which implements the TELESCOPE_INTERFACE. Raise an exception.
        if not self.device_telescope:
            raise INDIConnectException("INDI: Unable to find a driver of type 'telescope'.")

        # Wait for the CONNECTION property be defined for telescope.
        for iteration in range(self.configuration.polling_time_out_count):
            time.sleep(self.configuration.polling_interval)
            self.telescope_connect = self.device_telescope.getSwitch("CONNECTION")
            if self.telescope_connect:
                break
        if not self.telescope_connect:
            raise INDIConnectException("INDI: Unable to get the telescope connection switch.")

        # Check if the telescope device is already connected to the telescope. If not, try to
        # establish the connection.
        if not self.device_telescope.isConnected():
            # Property vectors are mapped to iterable Python objects. Hence we can access each
            # element of the vector using Python indexing. Each element of the "CONNECTION" vector
            # is an ISwitch.
            self.telescope_connect[0].s = PyIndi.ISS_ON  # the "CONNECT" switch
            self.telescope_connect[1].s = PyIndi.ISS_OFF  # the "DISCONNECT" switch
            self.indiclnt.sendNewSwitch(self.telescope_connect)  # send this new value to the device

        # Wait for the CONNECTION property be defined for telescope.
        for iteration in range(self.configuration.polling_time_out_count):
            time.sleep(self.configuration.polling_interval)
            if self.device_telescope.isConnected():
                break
        if not self.device_telescope.isConnected():
            raise INDIConnectException("INDI: Unable to connect with the telescope.")

        # Get the RA/DE coordinate object.
        for iteration in range(self.configuration.polling_time_out_count):
            self.telescope_radec = self.device_telescope.getNumber("EQUATORIAL_EOD_COORD")
            time.sleep(self.configuration.polling_interval)
            if self.telescope_radec:
                break
        if not self.telescope_radec:
            raise INDIConnectException("INDI: Unable to get the RA/DE coordinate object.")
        if self.configuration.protocol_level > 2:
            Miscellaneous.protocol("OperateTelescopeINDI: Scope init done, RA " + str(
                round(self.telescope_radec[0].value * 15., 5)) + ", DE " + str(
                round(self.telescope_radec[1].value, 5)) + " (degrees).")

        # Get pulse guide objects.
        for iteration in range(self.configuration.polling_time_out_count):
            self.telescope_guideNS = self.device_telescope.getNumber("TELESCOPE_TIMED_GUIDE_NS")
            time.sleep(self.configuration.polling_interval)
            if self.telescope_guideNS:
                break
        if not self.telescope_guideNS:
            raise INDIConnectException("INDI: Unable to get the guideNS object.")
        for iteration in range(self.configuration.polling_time_out_count):
            self.telescope_guideWE = self.device_telescope.getNumber("TELESCOPE_TIMED_GUIDE_WE")
            time.sleep(self.configuration.polling_interval)
            if self.telescope_guideWE:
                break
        if not self.telescope_guideWE:
            raise INDIConnectException("INDI: Unable to get the guideWE object.")

    def switch_on_tracking(self):
        """
        Try to switch on tracking. If the telescope driver responds with an error, raise an
        exception and set a human-readable error message.

        :return:
        """

        import PyIndi
        # We want to set the ON_COORD_SET switch to engage tracking after goto. "device.getSwitch"
        # is a helper to retrieve a property vector.
        for iteration in range(self.configuration.polling_time_out_count):
            self.telescope_on_coord_set = self.device_telescope.getSwitch("ON_COORD_SET")
            if self.telescope_on_coord_set:
                break
            time.sleep(self.configuration.polling_interval)
        if not self.telescope_on_coord_set:
            raise INDIPropertyException("INDI: Unable to get the 'ON_COORD_SET' switch.")

        try:
            # The order below is defined in the property vector, look at the standard Properties
            # page, or enumerate them in the Python shell when you're developing your program.
            self.telescope_on_coord_set[0].s = PyIndi.ISS_ON  # TRACK
            self.telescope_on_coord_set[1].s = PyIndi.ISS_OFF  # SLEW
            self.telescope_on_coord_set[2].s = PyIndi.ISS_OFF  # SYNC
            self.indiclnt.sendNewSwitch(self.telescope_on_coord_set)
            if self.configuration.protocol_level > 1:
                Miscellaneous.protocol("OperateTelescopeINDI: telescope tracking has been "
                                       "switched on.")
        except:
            raise INDIPropertyException("INDI: Telescope tracking could not be switched on.")

    def set_pulse_guide_speed(self):
        """
        Set the PulseGuide speed. Normally, the telescope driver should provide the four basic
        slew speeds which the user can have selected via the INDI configuration GUI. If this
        is not the case, an exception is raised and a human-readable error message is printed.

        :return: -
        """

        import PyIndi
        pulse_guide_speed_index = self.configuration.conf.getint("INDI", "pulse guide speed index")
        pulse_guide_speed = ['SLEW_GUIDE', 'SLEW_CENTERING', 'SLEW_FIND', 'SLEW_MAX'][
            pulse_guide_speed_index]
        prate = self.device_telescope.getSwitch("TELESCOPE_SLEW_RATE")
        while not prate or type(prate) != PyIndi.ISwitchVectorProperty:
            prate = self.device_telescope.getSwitch("TELESCOPE_SLEW_RATE")
            time.sleep(0.2)
        if len(prate) < 1:  # no slew rate
            if self.configuration.protocol_level > 0:
                Miscellaneous.protocol(
                    "OperateTelescopeINDI: The telescope driver provides zero slew rates.")
            raise INDIPropertyException("INDI: No slew rate provided by telescope driver.")
        else:
            if self.configuration.protocol_level > 2:
                Miscellaneous.protocol(
                    "OperateTelescopeINDI: There are " + str(len(prate)) + " slew rates.")
            speed_set = False
            for p in prate:
                if p.name == pulse_guide_speed:
                    p.s = PyIndi.ISS_ON
                    speed_set = True
                else:
                    p.s = PyIndi.ISS_OFF
            if speed_set:
                self.indiclnt.sendNewSwitch(prate)
            else:
                # The selected slew rate is not among the rates provided by the driver.
                raise INDIPropertyException("INDI: The user selected a pulse guide "
                                            "speed not supporded by telescope driver.")
            if self.configuration.protocol_level > 1:
                Miscellaneous.protocol(
                    "OperateTelescopeINDI: pulse guide speed set to " + pulse_guide_speed + ".")
        return

    def run(self):
        """
        Execute the thread which serves the telescope instruction queue.

        :return: -
        """

        # Connect to the INDI telescope driver and check if it is working properly.
        try:
            self.connect_and_test_telescope()
            # Switch on tracking, if not yet done.
            self.switch_on_tracking()
            # Set the pulse guide speed.
            self.set_pulse_guide_speed()
        except Exception as e:
            # Save the error message to be looked up by high-level telescope thread.
            self.initialization_error = str(e)
            # Clean up the low-level telescope thread and exit.
            if self.configuration.protocol_level > 0:
                Miscellaneous.protocol("Ending OperateTelescopeINDI thread.")
            return

        # After successful connection to the telescope driver, mark the interface initialized.
        if self.configuration.protocol_level > 0:
            Miscellaneous.protocol("OperateTelescopeINDI: telescope driver is working properly.")
        self.initialized = True

        # Serve the instruction queue, until the "terminate" instruction is encountered.
        while True:
            if len(self.instructions) > 0:
                # Get the next instruction from the queue, look up its type (name), and execute it.
                instruction = self.instructions.pop()

                # Slew the telescope to a given (RA, DE) position.
                if instruction['name'] == "slew to":
                    if self.configuration.protocol_level > 1:
                        Miscellaneous.protocol(
                            "OperateTelescopeINDI: Slewing telescope to: RA " + str(
                                round(instruction['rect'] * 15., 5)) + ", DE " + str(
                                round(instruction['decl'], 5)) + " (degrees).")
                    # Instruct the INDI driver to execute the SlewToCoordinates instruction.
                    # Please note that coordinates are in hours (RA) and degrees (DE).
                    self.telescope_radec[0].value = instruction['rect']
                    self.telescope_radec[1].value = instruction['decl']
                    self.indiclnt.sendNewNumber(self.telescope_radec)

                # Wait until the mount is standing still, then look up the current mount position.
                elif instruction['name'] == "lookup tel position":
                    # Initialize (rect, decl) with impossible coordinates, and iteration count to 0.
                    rect = 25.
                    decl = 91.
                    iter_count = 0
                    # Idle loop until changes in RA,DE are smaller than specified threshold.
                    while (abs(self.telescope_radec[
                                   0].value - rect) > self.configuration.conf.getfloat("INDI",
                            "telescope lookup precision") / 54000. or abs(
                        self.telescope_radec[1].value - decl) > self.configuration.conf.getfloat(
                        "INDI", "telescope lookup precision") / 3600.):
                        rect = self.telescope_radec[0].value
                        decl = self.telescope_radec[1].value
                        iter_count += 1
                        time.sleep(self.configuration.conf.getfloat("INDI", "wait interval"))

                    # Stationary state reached, copy measured position (in radians) into dict.
                    instruction['ra'] = radians(self.telescope_radec[0].value * 15)
                    instruction['de'] = radians(self.telescope_radec[1].value)
                    if self.configuration.protocol_level > 2:
                        Miscellaneous.protocol(
                            "OperateTelescopeINDI: Position looked-up: RA " + str(
                                round(self.telescope_radec[0].value * 15., 5)) + ", DE " + str(
                                round(self.telescope_radec[1].value,
                                      5)) + " (degrees), iterations: " + str(iter_count) + ".")
                    # Signal that the instruction is finished.
                    instruction['finished'] = True

                # Find out which INDI directions correspond to directions in the sky.
                elif instruction['name'] == "calibrate":
                    # Look up the current RA position of the mount.
                    ra_begin = self.telescope_radec[0].value * 15.
                    # Look up the specified length of the test movements in RA, DE.
                    calibrate_pulse_length = instruction['calibrate_pulse_length']
                    # Issue an INDI "move east" instruction and wait a short time.
                    self.telescope_guideWE[0].value = 0
                    self.telescope_guideWE[1].value = calibrate_pulse_length
                    self.indiclnt.sendNewNumber(self.telescope_guideWE)
                    time.sleep(calibrate_pulse_length / 500.)
                    # Look up resulting mount position (RA) in the sky.
                    ra_end = self.telescope_radec[0].value * 15.

                    # The end point was west of the initial point. Flip the RA directions.
                    if ra_end < ra_begin:
                        self.direction_east = 3
                        self.direction_west = 2
                    # Do the same in declination.
                    de_begin = self.telescope_radec[1].value
                    # Issue an INDI "move north" instruction and wait a short time.
                    self.telescope_guideNS[0].value = calibrate_pulse_length
                    self.telescope_guideNS[1].value = 0
                    self.indiclnt.sendNewNumber(self.telescope_guideNS)
                    time.sleep(calibrate_pulse_length / 500.)
                    # Look up resulting mount position (DE) in the sky.
                    de_end = self.telescope_radec[1].value
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
                # If it is behind, an INDI PulseGuide instruction of specified length is issued.
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
                            Miscellaneous.protocol("OperateTelescopeINDI: Pulse guide in RA.")
                        if direction_ra == 2:
                            self.telescope_guideWE[0].value = 0
                            self.telescope_guideWE[1].value = int(
                                self.configuration.conf.getfloat("INDI",
                                                                 "guiding interval") * 1000.)
                        else:
                            self.telescope_guideWE[0].value = int(
                                self.configuration.conf.getfloat("INDI",
                                                                 "guiding interval") * 1000.)
                            self.telescope_guideWE[1].value = 0
                        self.indiclnt.sendNewNumber(self.telescope_guideWE)

                    # The telescope has been moved too little in DE. Issue a PulseGuide.
                    if abs(target_de - start_de) > abs(current_de - start_de):
                        if self.configuration.protocol_level > 2:
                            Miscellaneous.protocol("OperateTelescopeINDI: Pulse guide in DE.")
                        if direction_de == 1:
                            self.telescope_guideNS[0].value = 0
                            self.telescope_guideNS[1].value = int(
                                self.configuration.conf.getfloat("INDI",
                                                                 "guiding interval") * 1000.)
                        else:
                            self.telescope_guideNS[0].value = int(
                                self.configuration.conf.getfloat("INDI",
                                                                 "guiding interval") * 1000.)
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
                    # Issue a PulseGuide in the specified direction.
                    if self.direction_north == 0:
                        self.telescope_guideNS[
                            0].value = self.configuration.polling_interval * 1000.
                        self.telescope_guideNS[1].value = 0.
                    else:
                        self.telescope_guideNS[0].value = 0.
                        self.telescope_guideNS[
                            1].value = self.configuration.polling_interval * 1000.
                    self.indiclnt.sendNewNumber(self.telescope_guideNS)
                    # Re-insert this instruction into the queue, and wait a short time.
                    self.instructions.insert(0, instruction)
                    time.sleep(self.configuration.polling_interval)

                # This instruction is used when the "arrow up" key is released.
                elif instruction['name'] == "stop moving north":
                    # Remove all "start moving north" instructions from the queue.
                    self.remove_instruction(self.start_moving_north)
                    instruction['finished'] = True

                # The following instructions are analog to the two above. They handle the three
                # other coordinate directions.
                elif instruction['name'] == "start moving south":
                    if self.direction_south == 1:
                        self.telescope_guideNS[0].value = 0.
                        self.telescope_guideNS[
                            1].value = self.configuration.polling_interval * 1000.
                    else:
                        self.telescope_guideNS[
                            0].value = self.configuration.polling_interval * 1000.
                        self.telescope_guideNS[1].value = 0.
                    self.indiclnt.sendNewNumber(self.telescope_guideNS)
                    self.instructions.insert(0, instruction)
                    time.sleep(self.configuration.polling_interval)

                elif instruction['name'] == "stop moving south":
                    self.remove_instruction(self.start_moving_south)
                    instruction['finished'] = True

                elif instruction['name'] == "start moving east":
                    if self.direction_east == 2:
                        self.telescope_guideWE[0].value = 0.
                        self.telescope_guideWE[
                            1].value = self.configuration.polling_interval * 1000.
                    else:
                        self.telescope_guideWE[
                            0].value = self.configuration.polling_interval * 1000.
                        self.telescope_guideWE[1].value = 0.
                    self.indiclnt.sendNewNumber(self.telescope_guideWE)
                    self.instructions.insert(0, instruction)
                    time.sleep(self.configuration.polling_interval)

                elif instruction['name'] == "stop moving east":
                    self.remove_instruction(self.start_moving_east)
                    instruction['finished'] = True

                elif instruction['name'] == "start moving west":
                    if self.direction_west == 3:
                        self.telescope_guideWE[
                            0].value = self.configuration.polling_interval * 1000.
                        self.telescope_guideWE[1].value = 0.
                    else:
                        self.telescope_guideWE[0].value = 0.
                        self.telescope_guideWE[
                            1].value = self.configuration.polling_interval * 1000.
                    self.indiclnt.sendNewNumber(self.telescope_guideWE)
                    self.instructions.insert(0, instruction)
                    time.sleep(self.configuration.polling_interval)

                elif instruction['name'] == "stop moving west":
                    self.remove_instruction(self.start_moving_west)
                    instruction['finished'] = True

                # Issue an PulseGuide instruction with given direction and length.
                elif instruction['name'] == "pulse correction":
                    # If a "calibrate" instruction was executed, correct the ASCOM direction values
                    # (0,1,2,3) to reflect the real motion of the telescope.
                    direction = [self.direction_north, self.direction_south, self.direction_east,
                                 self.direction_west][instruction['direction']]
                    # The pulse_length is counted in milliseconds.
                    pulse_length = instruction['pulse_length']
                    # Perform the ASCOM PulseGuide instruction.
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
                time.sleep(self.configuration.polling_interval)

        # Terminate the main loop (after executing the "terminate" instruction).
        # Disconnect all INDI devices and the server from the INDI client first.
        if self.configuration.protocol_level > 0:
            Miscellaneous.protocol("Disconnecting INDI devices.")
        for name in self.device_name_list:
            self.indiclnt.disconnectDevice(name)
        if self.configuration.protocol_level > 0:
            Miscellaneous.protocol("Disconnecting INDI server.")
        self.indiclnt.disconnectServer()
        if self.configuration.protocol_level > 0:
            Miscellaneous.protocol("Ending OperateTelescopeINDI thread.")

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

        # Instantiate the OperateTelescope object and start the thread.
        if self.configuration.conf.get("Telescope", "interface type") == "ASCOM":
            self.optel = OperateTelescopeASCOM(self.configuration)
        elif self.configuration.conf.get("Telescope", "interface type") == "INDI":
            self.optel = OperateTelescopeINDI(self.configuration)
        else:
            raise TelescopeException(
                "Invalid telescope interface type " + self.configuration.conf.get(
                "Telescope", "interface type") + " specified")

        self.optel.start()

        # Wait for the low-level thread to be initialized. Meanwhile check for error messages.
        for iteration in range(4 * self.configuration.polling_time_out_count):
            # An error occurred in low-level initialization. Raise an exception.
            if self.optel.initialization_error != "":
                raise TelescopeException(self.optel.initialization_error)
            if self.optel.initialized:
                # The low-level interface was initialized successfully. Exit the loop.
                break
            time.sleep(self.configuration.polling_interval)
        if not self.optel.initialized:
            raise TelescopeException("Timeout in connecting to telescope driver.")

        if self.configuration.protocol_level > 2:
            Miscellaneous.protocol("High-level telescope interface initialized properly.")

        self.readout_correction_ra = 0.
        self.readout_correction_de = 0.
        self.guiding_active = False

    def calibrate(self):
        """
        Check if movements in RA,DE are mirror-reversed. Directions will be corrected in future
        instructions. This method blocks until the low-level instruction is finished.

        :return: -
        """

        if self.configuration.protocol_level > 2:
            Miscellaneous.protocol("Calibrating guiding direction, time interval (ms): " + str(
                self.configuration.calibrate_pulse_length) + ".")
        # Choose the instruction, and set the pulse length.
        calibrate_instruction = self.optel.calibrate
        calibrate_instruction['calibrate_pulse_length'] = self.configuration.calibrate_pulse_length
        # Initialize the "finished" field to False, and insert the instruction into the queue.
        calibrate_instruction['finished'] = False
        self.optel.instructions.insert(0, calibrate_instruction)
        # Idle loop until the calibration is finished. Write out the results.
        while not calibrate_instruction['finished']:
            time.sleep(self.configuration.polling_interval)
        if self.configuration.protocol_level > 2:
            if self.optel.direction_east == 2:
                Miscellaneous.protocol("Direction for corrections in RA: normal.")
            else:
                Miscellaneous.protocol("Direction for corrections in RA: reversed.")
            if self.optel.direction_north == 0:
                Miscellaneous.protocol("Direction for corrections in DE: normal.")
            else:
                Miscellaneous.protocol("Direction for corrections in DE: reversed.")

    def slew_to(self, ra, de):
        """
        Move the telescope to a given position (ra, de) in the sky. This method blocks until the
        position is reached.

        :param ra: Target right ascension (radians)
        :param de: Target declination (radians)
        :return: -
        """

        # Convert coordinates into hours and degrees, fill parameters into instruction fields and
        # put the instruction into the queue. Make sure the RA value is between 0 and 24 hours.
        rect = (degrees(ra) / 15.) % 24.
        decl = degrees(de)
        slew_to_instruction = self.optel.slew_to
        slew_to_instruction['rect'] = rect
        slew_to_instruction['decl'] = decl
        self.optel.instructions.insert(0, slew_to_instruction)
        # Look up the position where the telescope went.
        (rect_lookup, decl_lookup) = self.lookup_tel_position_uncorrected()
        # For some mounts there is a systematic difference between target and the position
        # looked-up. Compute the difference. It will be used to correct future look-ups.
        # Bring the RA correction as close to zero as possible (full circle ambiguity).
        self.readout_correction_ra = (ra - rect_lookup + pi) % (2. * pi) - pi
        self.readout_correction_de = de - decl_lookup
        # Write the corrections to the protocol file.
        if self.configuration.protocol_level > 2:
            Miscellaneous.protocol("New coordinate read-out correction computed (deg.): RA: " + str(
                round(degrees(self.readout_correction_ra), 5)) + ", DE: " + str(
                round(degrees(self.readout_correction_de), 5)) + " (degrees).")

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
            time.sleep(self.configuration.polling_interval)
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
                      3)) + " (arc min. / hour).")
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
            Miscellaneous.protocol("Stop guiding.")
        # Insert the instruction into the low-level queue and wait until it is finished.
        stop_guiding_instruction = self.optel.stop_guiding
        stop_guiding_instruction['finished'] = False
        self.optel.instructions.insert(0, stop_guiding_instruction)
        while not stop_guiding_instruction['finished']:
            time.sleep(self.configuration.polling_interval)
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
            time.sleep(self.configuration.polling_interval)

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
            time.sleep(self.configuration.polling_interval)

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
            time.sleep(self.configuration.polling_interval)

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
            time.sleep(self.configuration.polling_interval)

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
            time.sleep(self.configuration.polling_interval)

    def terminate(self):
        """
        Insert a "terminate" instruction into the queue, wait for the OperateTelescope thread to
        finish and write a message to the protocol file.

        :return:
        """

        if self.configuration.protocol_level > 0:
            Miscellaneous.protocol("High-level telescope interface: "
                                   "Terminating OperateTelescope thread.")
        self.optel.instructions.insert(0, self.optel.terminate)
        self.optel.join()
        if self.configuration.protocol_level > 0:
            Miscellaneous.protocol("High-level telescope interface: "
                                   "OperateTelescope thread terminated.")
