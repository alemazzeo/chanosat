#!/usr/bin/python
# -*- coding: utf-8 -*-
""" File driver.py

"""

import numpy as np
import matplotlib.pyplot as plt
from devices import Chanosat
import serial
import time


class Chanosat_Driver(Chanosat):
    """ 

    """

    def __init__(self, port='/dev/ttyACM0', *args, **kwargs):
        self._serial = serial.Serial(port, baudrate=9600, timeout=5)
        self._shift_motor = 1
        self._theta_motor = 2
        self._phi_motor = 3
        self._phi_goto_secure = True
        self._theta_goto_secure = True
        self._phi_secure = 10
        self._theta_secure = 5
        self._theta_step = 360 / 7680
        self._phi_step = 360 / 2048
        self._shift_step = 0.0188
        self._last_shift = 0
        self._last_theta = 0
        self._last_phi = 0
        super().__init__(*args, **kwargs)

    @property
    def phi_secure(self):
        return self._phi_secure

    @phi_secure.setter
    def phi_secure(self, value):
        self._phi_secure = value

    @property
    def theta_secure(self):
        return self._theta_secure

    @theta_secure.setter
    def theta_secure(self, value):
        self._theta_secure = value

    def update(self):
        super().update()
        shift = self.shift // self._shift_step
        theta = self.theta // self._theta_step
        phi = self.phi // self._phi_step
        phi_secure = (self.phi + self._phi_secure) // self._phi_step
        theta_secure = (self.theta + self._theta_secure) // self._theta_step

        if self._last_shift != self.shift:
            self.move_motor(self._shift_motor, shift)

        if self._last_theta != self.theta:
            if self._theta_secure != 0 and not self._manual:
                self.move_motor(self._theta_motor, theta_secure)
            self.move_motor(self._theta_motor, theta)

        if self._last_phi != self.phi:
            if self._phi_secure != 0 and not self._manual:
                self.move_motor(self._phi_motor, phi_secure)
            self.move_motor(self._phi_motor, phi)

        self._last_shift = self.shift
        self._last_theta = self.theta
        self._last_phi = self.phi

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
        if out == b'':
            raise TimeoutError('Arduino serial not respond')

    def __del__(self):
        self._pos = [0, 0, 0]
        self._serial.close()


if __name__ == "__main__":

    import matplotlib.pyplot as plt
    from mpl_toolkits.mplot3d import Axes3D
    from geometry import Ray, Plane, Intersection, Reflection

    plt.ion()
    fig = plt.figure()
    ax = fig.gca(projection='3d')
    ax.set_xlim(-30, 30)
    ax.set_ylim(-30, 30)
    ax.set_zlim(0, 100)

    p1 = Plane(ax=ax)
    p1.z = 20
    p1.phi = 0

    c = Chanosat_Driver(ax=ax)
    a = Intersection(c, p1)

    c.manual_controls = True
