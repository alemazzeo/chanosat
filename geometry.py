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
    def direction(self):
        return self._direction

    @direction.setter
    def direction(self, direction):
        n = np.asarray(direction, dtype=float)
        self._direction = n / np.sqrt(np.dot(n, n))
        self.update()

    @property
    def point(self):
        return self._point

    @point.setter
    def point(self, point):
        self._point = np.asarray(point, dtype=float)
        self.update()

    def _meshgrid(self, ax, N=10):
        box = ax.axes.xy_viewLim
        x = np.linspace(box.x0, box.x1, N)
        y = np.linspace(box.y0, box.y1, N)
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
            xx, yy = self._meshgrid(ax)
            z = self.calculate_z(xx, yy)
            self._plot = ax.plot_surface(xx, yy, z, alpha=0.2)


class Ray(Geometry):
    """

    """

    def __init__(self, direction=[0, 0, 1], point=[0, 0, 0], ax=None,
                 auto_update=True):

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
            t = np.linspace(0, 1, 100)
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
            self._plot, = ax.plot([x], [y], [z], alpha=0.8, ls=' ', marker='o')


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

    def update(self):
        p = self._ray.plane_collision(self._plane)
        self._point = p
        super().update()


plt.ion()
fig = plt.figure()
ax = fig.gca(projection='3d')
ax.set_xlim(-1, 1)
ax.set_ylim(-1, 1)

p1 = Plane(point=[0, 0, 0.5], ax=ax)
p2 = Plane(point=[0, 0, 1], ax=ax)
r1 = Ray(point=[0, 0, 0], direction=[0, 0.5, 1], ax=ax)
r2 = Reflection(r1, p1)
r3 = Reflection(r1, p2)
a = Intersection(r1, p1)
b = Intersection(r1, p2)
c = Intersection(r3, p1)
