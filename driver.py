#!/usr/bin/python
# -*- coding: utf-8 -*-
""" File driver.py

"""

from geometry import Chanosat
import serial


class Chanosat_Driver(Chanosat):
    """ 

    """

    def __init__(self, port=None, theta=None, phi=None, shift=None):
        self._serial = serial.Serial(port, baudrate=9600, timeout=1)
        self._shift_motor = 1
        self._theta_motor = 2
        self._phi_motor = 3
        super().__init__(theta, phi, shift)

    def update(self):
        super().update()
        self.move_motor(self._shift_motor, self.shift)
        self.move_motor(self._theta_motor, self.theta)
        self.move_motor(self._phi_motor, self.phi)

    def move_motor(self, number, pos):
        command = 'STMOV {} {}'.format(number, pos)
        self._send_command(command)

    def _send_command(self, command, verbose=False):
        self._serial.reset_input_buffer()
        self._serial.write((command + '\r').encode())
        if verbose:
            print(command)
        out = self._serial.readline()
        if out != b'0\r\n':
            print(out)

    def __del__(self):
        self._serial.close()


c = Chanosat(port='COM22')
