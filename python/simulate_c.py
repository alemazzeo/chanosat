import numpy as np
import matplotlib.pyplot as plt
import ctypes as C

CLIB = C.CDLL('../lib/libgeompy.so')
pd = C.POINTER(C.c_double)


def arange(start, end, step):
    n = int(end - start) / abs(step) + 1
    if end > start:
        step = abs(step)
    else:
        step = -abs(step)
    values = np.arange(n) * step + start
    return values


class Geometry(C.Structure):
    _fields_ = [('point', pd),
                ('normal', pd)]

    def __init__(self, point=[0, 0, 0], normal=[0, 0, 1]):
        self._point = np.asarray(point, dtype=float)
        self._normal = np.asarray(normal, dtype=float)
        self.point = self._point.ctypes.data_as(pd)
        self.normal = self._normal.ctypes.data_as(pd)


class Lens(Geometry):
    def __init__(self, point=[0, 0, 0], normal=[0, 0, 1], radius=21):
        self.radius = C.c_double(radius)
        super().__init__(point, normal)


class Sweep(C.Structure):
    _fields_ = [('theta', pd),
                ('len_theta', C.c_int),
                ('shift', pd),
                ('len_shift', C.c_int),
                ('phi', pd),
                ('len_phi', C.c_int)]

    def __init__(self, theta, shift, phi):

        self._theta = np.asarray(theta) * np.pi / 180
        self._shift = np.asarray(shift)
        self._phi = np.asarray(phi) * np.pi / 180

        self.theta = self._theta.ctypes.data_as(pd)
        self.len_theta = C.c_int(self._theta.size)

        self.shift = self._shift.ctypes.data_as(pd)
        self.len_shift = C.c_int(self._shift.size)

        self.phi = self._phi.ctypes.data_as(pd)
        self.len_phi = C.c_int(self._phi.size)


class Polar(C.Structure):
    _fields_ = [('rho', C.c_double),
                ('theta', C.c_double),
                ('alpha', C.c_double),
                ('beta', C.c_double)]

    def __init__(self):
        self.rho = C.c_double(0)
        self.theta = C.c_double(0)
        self.alpha = C.c_double(0)
        self.beta = C.c_double(0)


class Chano(C.Structure):
    _fields_ = [('shift', C.c_double),
                ('theta', C.c_double),
                ('phi', C.c_double),
                ('x', C.c_double),
                ('y', C.c_double),
                ('z', C.c_double)]

    def __init__(self, x=0, y=0, z=0):
        self.x = C.c_double(x)
        self.y = C.c_double(y)
        self.z = C.c_double(z)
        self.shift = C.c_double(0.0)
        self.theta = C.c_double(0.0)
        self.phi = C.c_double(0.0)


def simulate(theta_range, phi_range, shift_range, x, y, z, r, dr=None):

    sweep = Sweep(theta=theta_range, shift=shift_range, phi=[-30, 60])
    chano = Chano(x=-x, y=-y, z=0)
    lens = Geometry(point=[0, 0, z], normal=[0, 0, 1])

    filename = C.c_char_p(b"calibrate.txt")

    if dr is None:
        CLIB.explore(filename, sweep, chano, lens,
                     C.c_double(0), C.c_double(r))
    else:
        CLIB.explore(filename, sweep, chano, lens,
                     C.c_double(r - dr), C.c_double(r + dr))

    result = np.loadtxt('calibrate.txt', delimiter=',', unpack=True)
    rho, theta, alpha, beta, c_theta, c_phi, c_shift = result
    np.savez('sim_calibrate.npz',
             rho=rho, theta=theta, alpha=alpha, beta=beta,
             c_theta=c_theta, c_phi=c_phi, c_shift=c_shift)
    return result


if __name__ == "__main__":

    # Sweep for chano
    phi_range = arange(-50, 70, 2)
    shift_range = arange(0, 28, 1)
    theta_range = arange(0, 90, 5)

    # Lens coords
    z = 20
    r = 21
    x = 21
    y = 21

    result = simulate(theta_range, phi_range, shift_range,
                      x=r, y=r, z=20, r=r, dr=3)

    rho, theta, alpha, beta, c_theta, c_phi, c_shift = result

    plt.ion()
    plt.polar(theta, rho, 'go')
