# -*- coding: utf-8 -*-
""" File devices.py

"""

import numpy as np
import matplotlib.pyplot as plt
import sys
from config import load_config
from geometry import Ray, Plane, Point, Trace, Intersection, Reflection

cfg = load_config('devices')


class Chanosat(Ray):
    """ 

    """

    def __init__(self, theta=0.0, phi=0.0, shift=0.0,
                 xyz=[0, 0, 0], *args, **kwargs):
        self._theta = theta
        self._phi = phi
        self._shift = shift
        self._height = 90
        self._radius = 100
        self._trace = Trace(self)

        self._manual = False
        self._target = 'phi'
        self._mpl_keys = list()

        self._x = xyz[0]
        self._y = xyz[1]
        self._z = xyz[2]

        direction, point = self._update_ray()
        super().__init__(direction, point, *args, **kwargs)

    @property
    def direction(self):
        return self._direction

    @property
    def point(self):
        return self._point

    @property
    def x(self):
        return self._x

    @property
    def y(self):
        return self._y

    @property
    def z(self):
        return self._z

    @x.setter
    def x(self, x):
        self._x = x

    @y.setter
    def y(self, y):
        self._y = y

    @z.setter
    def z(self, z):
        self._z = z

    @property
    def phi(self):
        return self._phi

    @phi.setter
    def phi(self, phi):
        if cfg.phi['min'] <= phi <= cfg.phi['max']:
            self._phi = phi
            self.update()

    @property
    def theta(self):
        return self._theta

    @theta.setter
    def theta(self, theta):
        if cfg.theta['min'] <= theta <= cfg.theta['max']:
            self._theta = theta
            self.update()

    @property
    def shift(self):
        return self._shift

    @shift.setter
    def shift(self, shift):
        if cfg.shift['min'] <= shift <= cfg.shift['max']:
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

    @property
    def manual_controls(self):
        return self._manual

    @manual_controls.setter
    def manual_controls(self, enable):
        if self._manual != enable:
            self._set_controls(enable)

    def _update_ray(self):
        radius = self._shift
        theta = self._theta
        phi = self._phi
        x, y, z = self._x, self._y, self._z
        x0 = x + radius * np.cos(np.radians(theta))
        y0 = y + radius * np.sin(np.radians(theta))
        z0 = z

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

    def _set_controls(self, enable):
        if self._ax is not None:
            disconnect = self._ax.figure.canvas.mpl_disconnect
            connect = self._ax.figure.canvas.mpl_connect
            manager = self._ax.figure.canvas.manager
            disconnect(manager.key_press_handler_id)
        if enable is True:
            connect('key_release_event', self._on_key)
            self._manual = True
        else:
            disconnect(manager.key_press_handler_id)
            self._manual = False

    def _on_key(self, event):
        sys.stdout.flush()
        if event.key == 's':
            self._target = 'shift'
        elif event.key == 'p':
            self._target = 'phi'
        elif event.key == 't':
            self._target = 'theta'
        elif event.key == 'left':
            self._move(step='-raw')
        elif event.key == 'right':
            self._move(step='+raw')
        elif event.key == 'up':
            self._move(step='+fine')
        elif event.key == 'down':
            self._move(step='-fine')

    def _move(self, step, target=None):
        if target is None:
            target = self._target
        config = getattr(cfg, target)
        if isinstance(step, str):
            if step == '+raw':
                step = config['raw']
            if step == '-raw':
                step = -config['raw']
            elif step == '+fine':
                step = config['fine']
            elif step == '-fine':
                step = -config['fine']

        setattr(self, target, getattr(self, target) + step)
        plt.pause(0.0001)


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

    r1.manual_controls = True
