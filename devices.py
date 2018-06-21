# -*- coding: utf-8 -*-
""" File geometry.py

"""

import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from geometry import Ray, Plane, Intersection, Reflection


class Chanosat(Ray):
    """ 

    """

    def __init__(self, theta=0.0, phi=0.0, shift=0.0,
                 ax=None, auto_update=True):
        self._theta = theta
        self._phi = phi
        self._shift = shift
        self._height = 90
        self._radius = 100
        direction, point = self._update_ray()
        super().__init__(direction, point, ax, auto_update)

    @property
    def direction(self):
        return self._direction

    @property
    def point(self):
        return self._point

    @property
    def phi(self):
        return self._phi

    @phi.setter
    def phi(self, phi):
        self._phi = phi
        self.update()

    @property
    def theta(self):
        return self._theta

    @theta.setter
    def theta(self, theta):
        self._theta = theta
        self.update()

    @property
    def shift(self):
        return self._shift

    @shift.setter
    def shift(self, shift):
        self._shift = shift
        self.update()

    @property
    def pos(self):
        return [self._shift, self._theta, self._phi]

    @pos.setter
    def pos(self, pos):
        self.shift = pos[0]
        self.theta = pos[1]
        self.phi = pos[2]

    def _update_ray(self):
        radius = self.shift
        theta = self.theta
        phi = self.phi

        x0 = radius * np.cos(np.radians(theta))
        y0 = radius * np.sin(np.radians(theta))
        z0 = self._height

        direction = self._sph2cart(theta, phi)
        point = np.asarray([x0, y0, z0], dtype=float)

        return direction, point

    def update(self):
        direction, point = self._update_ray()
        self._direction = direction
        self._point = point
        super().update()


plt.ion()
fig = plt.figure()
ax = fig.gca(projection='3d')
ax.set_xlim(-100, 100)
ax.set_ylim(-90, 90)
ax.set_zlim(0, 600)


p1, p2 = Plane(ax=ax), Plane(ax=ax)
p1.z, p2.z = 300, 500
p1.phi, p2.phi = 45, 45

r1 = Chanosat(ax=ax)

r2, r3 = Reflection(r1, p1), Reflection(r1, p2)
a = Intersection(r1, p1)
b = Intersection(r1, p2)
c = Intersection(r3, p1)
