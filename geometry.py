# -*- coding: utf-8 -*-
""" File geometry.py

"""

import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D


class Geometry(object):

    def __init__(self, direction=[0, 0, 1], point=[0, 0, 0], ax=None,
                 auto_update=True):
        self._direction = np.asarray(direction, dtype=float)
        self._point = np.asarray(point, dtype=float)
        self._ax = ax
        self._plot = None
        self._auto_update = auto_update
        self._cascade = list()
        if ax is not None:
            self._update_plot()

    @property
    def point(self):
        return self._point

    @point.setter
    def point(self, point):
        self._point = np.asarray(point, dtype=float)
        self.update()

    @property
    def z(self):
        return self.point[2]

    @z.setter
    def z(self, z):
        px, py, pz = self.point
        self.point = np.asarray([px, py, z])

    @property
    def direction(self):
        return self._direction

    @direction.setter
    def direction(self, direction):
        n = np.asarray(direction, dtype=float)
        self._direction = n / np.sqrt(np.dot(n, n))
        self.update()

    @property
    def phi(self):
        return self._cart2sph(self.direction)[1]

    @phi.setter
    def phi(self, phi):
        self.direction = self._sph2cart(self.theta, phi)

    @property
    def theta(self):
        return self._cart2sph(self.direction)[0]

    @theta.setter
    def theta(self, theta):
        self.direction = self._sph2cart(theta, self.phi)

    def _cart2sph(self, direction):
        theta = np.arctan2(self._direction[1], self._direction[0])
        phi = np.arccos(self._direction[2])
        return np.degrees(theta), np.degrees(phi)

    def _sph2cart(self, theta, phi):
        t = np.radians(theta)
        p = np.radians(phi)

        ct = np.cos(t)
        st = np.sin(t)
        cp = np.cos(p)
        sp = np.sin(p)

        return np.asarray([sp * ct, sp * st, cp], dtype=float)

    def _xy_limits(self):
        box = self._ax.axes.xy_viewLim
        return box.x0, box.x1, box.y0, box.y1

    def _meshgrid(self, N=10):
        x0, x1, y0, y1 = self._xy_limits()
        x = np.linspace(x0, x1, N)
        y = np.linspace(y0, y1, N)
        return np.meshgrid(x, y)

    def update(self):
        for element in self._cascade:
            element.update()
        self._update_plot()

    def _update_plot(self):
        pass

    def remove(self):
        if self._ax is not None:
            if self._plot is not None:
                self._plot.remove()


class Plane(Geometry):
    """

    """

    def __init__(self, direction=[0, 0, 1], point=[0, 0, 0], ax=None,
                 auto_update=True):

        super().__init__(direction, point, ax, auto_update)

    def calculate_z(self, x, y):
        x = np.asarray(x, dtype=float)
        y = np.asarray(y, dtype=float)
        n = self.direction
        p = -np.dot(self.point, n)
        return (-n[0] * x - n[1] * y - p) * 1. / n[2]

    def _update_plot(self):
        if self._ax is not None and self._auto_update:
            if self._plot is not None:
                self._plot.remove()
            xx, yy = self._meshgrid()
            z = self.calculate_z(xx, yy)
            self._plot = ax.plot_surface(xx, yy, z, alpha=0.2)


class Ray(Geometry):
    """

    """

    def __init__(self, direction=[0, 0, 1], point=[0, 0, 0], ax=None,
                 auto_update=True):
        self._large = 1000
        super().__init__(direction, point, ax, auto_update)

    def plane_collision(self, plane):
        n = np.dot(plane.direction, self.direction)
        if abs(n) < 1e-6:
            raise RuntimeError('No intersection or line is within plane')
        w = self.point - plane.point
        s = -np.dot(plane.direction, w) / n
        return self.direction * s + self.point

    def calculate_reflection(self, plane):
        d = self.direction
        n = plane.direction
        r = d - (2 * np.dot(d, n) * n) / np.dot(n, n)
        p = self.plane_collision(plane)
        return r, p

    def _update_plot(self):
        if self._ax is not None and self._auto_update:
            if self._plot is not None:
                self._plot.remove()
            n = self.direction
            p0 = self.point
            t = np.linspace(0, self._large, 100)
            x = p0[0] + t * n[0]
            y = p0[1] + t * n[1]
            z = p0[2] + t * n[2]
            self._plot, = ax.plot(x, y, z, alpha=0.8)


class Reflection(Ray):
    """

    """

    def __init__(self, ray, plane, ax=None, auto_update=True):
        self._ray = ray
        self._plane = plane
        r, p = ray.calculate_reflection(plane)
        if ax is None and ray._ax is not None:
            ax = ray._ax
        super().__init__(r, p, ax, auto_update)
        ray._cascade.append(self)
        plane._cascade.append(self)

    @property
    def direction(self):
        return self._direction

    @property
    def point(self):
        return self._point

    @property
    def z(self):
        return self.point[2]

    def update(self):
        r, p = self._ray.calculate_reflection(self._plane)
        self._direction = r
        self._point = p
        super().update()


class Point(Ray):
    """

    """

    def __init__(self, point=[0, 0, 0], ax=None,
                 auto_update=True):

        super().__init__([0, 0, 1], point, ax, auto_update)

    def _update_plot(self):
        if self._ax is not None and self._auto_update:
            if self._plot is not None:
                self._plot.remove()
            x, y, z = self.point
            x0, x1, y0, y1 = self._xy_limits()
            if x0 < x < x1 and y0 < y < y1:
                self._plot, = ax.plot([x], [y], [z], alpha=0.8,
                                      ls=' ', marker='o')
            else:
                self._plot, = ax.plot([x], [y], [z], alpha=0.8,
                                      ls=' ', marker=' ')


class Intersection(Point):
    """

    """

    def __init__(self, ray, plane, ax=None, auto_update=True):
        self._ray = ray
        self._plane = plane
        p = ray.plane_collision(self._plane)
        if ax is None and ray._ax is not None:
            ax = ray._ax
        super().__init__(p, ax, auto_update)
        ray._cascade.append(self)
        plane._cascade.append(self)

    @property
    def direction(self):
        return self._direction

    @property
    def point(self):
        return self._point

    @property
    def z(self):
        return self.point[2]

    def update(self):
        p = self._ray.plane_collision(self._plane)
        self._point = p
        super().update()


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
