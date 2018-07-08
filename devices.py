# -*- coding: utf-8 -*-
""" File devices.py

"""

import numpy as np
from geometry import Ray, Plane, Point, Trace, Intersection, Reflection


class Chanosat(Ray):
    """ 

    """

    def __init__(self, theta=0.0, phi=0.0, shift=0.0, *args, **kwargs):
        self._theta = theta
        self._phi = phi
        self._shift = shift
        self._height = 90
        self._radius = 100
        self._trace = Trace(self)
        direction, point = self._update_ray()
        super().__init__(direction, point, *args, **kwargs)

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
        radius = self._shift
        theta = self._theta
        phi = self._phi
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

    def add_trace_plane(self, plane):
        self._trace.add_plane(plane)

    def remove_trace_plane(self, plane):
        self._trace.remove_plane(plane)

    def make_trace(self, points=100, **kwargs):
        for key, value in kwargs.items():
            start = getattr(self, key)
            if start != value:
                sweep = np.linspace(start, value, points)
                for x in sweep:
                    setattr(self, key, x)
                    self._trace.add_point()

    def clear_trace(self):
        self._trace.clear()


if __name__ == "__main__":

    import matplotlib.pyplot as plt
    from mpl_toolkits.mplot3d import Axes3D

    plt.ion()
    fig = plt.figure()
    ax = fig.gca(projection='3d')
    ax.set_xlim(-100, 100)
    ax.set_ylim(-90, 90)
    ax.set_zlim(0, 600)

    p1, p2 = Plane(ax=ax), Plane(ax=ax)
    p1.z, p2.z = 200, 400
    p1.phi, p2.phi = 0, 0

    r1 = Chanosat(ax=ax)
    r2 = Reflection(r1, p1)
    a = Intersection(r1, p1)

    r2, r3 = Reflection(r1, p1), Reflection(r1, p2)
    c = Intersection(r3, p1)
    b = Intersection(r1, p2)
