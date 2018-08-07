# -*- coding: utf-8 -*-
""" File v4l2_python.py

"""

# Deponia

import ctypes as C
import numpy as np
import v4l2
import time
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import select
import os

plt.style.use('dark_background')

EXPOSURE = v4l2.V4L2_CID_EXPOSURE
EXPOSURE_MODE = v4l2.V4L2_CID_PRIVATE_BASE + 15
EXPOSURE_MODE_OFF = 0
EXPOSURE_MODE_TIMED = 1
EXPOSURE_MODE_TRIGGER_WIDTH = 2
EXPOSURE_MODE_TRIGGER_CONTROLLED = 3

CLIB = C.CDLL('../lib/libv4l2py.so')

clock_exposures = [1, 10, 100, 1000, 10000, 100000, 1000000]
time_exposures = [27.14e-6, 147.9e-6, 1.355e-3,
                  13.43e-3, 134.2e-3, 1.341, 13.41]

exp_clock2time = np.poly1d(np.polyfit(clock_exposures, time_exposures, 1))
exp_time2clock = np.poly1d(np.polyfit(time_exposures, clock_exposures, 1))


class Buffer(C.Structure):
    _fields_ = [("start", C.c_void_p),
                ("length", C.c_size_t)]

    def __init__(self):
        pass


class Device(C.Structure):
    _fields_ = [("fd", C.c_int),
                ("dev_name", C.c_char_p),
                ("width", C.c_int),
                ("height", C.c_int),
                ("fourcc", C.c_char * 4),
                ("buffer", Buffer),
                ("n_buffers", C.c_int)]

    def __init__(self, dev_name='/dev/video1',
                 width=2448, height=2048, fourcc='Y12 '):

        self.dev_name = dev_name.encode('utf-8')
        self._dev = C.pointer(self)
        self._width = width
        self._height = height
        self._fourcc = fourcc
        self._out_type = np.uint16
        self._b = 2
        self._try_max = 5
        self._timeout = 5
        self._fig = None
        self._exposure = 1
        self._save_path = os.path.normpath('./')
        self._vmin = 0
        self._vmax = 2**12
        cw = C.c_int(width)
        ch = C.c_int(height)
        fcc = fourcc.encode('utf-8')

        message = ['Opening...',
                   'Setting pixel format {}-{}x{}. '.format(fourcc,
                                                            width,
                                                            height),
                   'Memory mapping...',
                   'Starting capture...',
                   'Testing device...',
                   '\nCamera ready to use\n']

        print(message[0], end='')
        if CLIB.open_device(self._dev):
            print('Failed\n\n')
            raise RuntimeError('')
        else:
            print('Done')

        print(message[1], end='')
        if CLIB.set_pixelformat(self._dev, cw, ch, fcc):
            print('Failed\n\n')
            raise RuntimeError('')
        else:
            print('Done')

        print(message[2], end='')
        if CLIB.init_mmap(self._dev):
            print('Failed\n\n')
            raise RuntimeError('')
        else:
            print('Done')

        print(message[3], end='')
        if CLIB.start_capturing(self._dev):
            print('Failed\n\n')
            raise RuntimeError('')
        else:
            print('Done')

        self.setDriverCtrlValue(EXPOSURE_MODE, 0)
        self.setDriverCtrlValue(EXPOSURE, 1)

        print(message[4], end='')
        select.select((self.fd,), (), ())
        if CLIB.disconnect_buffer(self._dev):
            print('Failed\n\n')
            raise RuntimeError('')
        else:
            print('Done')

        print(message[5])

    @property
    def exposure(self):
        return self.getDriverCtrlValue(EXPOSURE)

    @exposure.setter
    def exposure(self, value):
        assert(0 <= value < 4192304)
        self._exposure = value
        self.setDriverCtrlValue(EXPOSURE, int(value))

    @property
    def exposure_time(self):
        clock = self.exposure
        return exp_clock2time(clock)

    @exposure_time.setter
    def exposure_time(self, value):
        clock = int(exp_time2clock(value))
        self.exposure = clock

    def print_caps(self):
        CLIB.print_caps(self._dev)

    def setDriverCtrlValue(self, id_ctrl, value):
        r = CLIB.setDriverCtrlValue(self._dev,
                                    C.c_uint(id_ctrl),
                                    C.c_ulong(value))
        if r != 0:
            print("Failed to set driver control value"
                  "with id {}".format(id_ctrl))

    def getDriverCtrlValue(self, id_ctrl):
        c = C.c_ulong(0)
        r = CLIB.getDriverCtrlValue(self._dev,
                                    C.c_uint(id_ctrl),
                                    C.byref(c))
        if r != 0:
            print("Failed to get driver control value")
        return c.value

    def capture(self, print_time=False):
        start_time = time.time()
        if CLIB.reconnect_buffer(self._dev):
            raise RuntimeError("Failed to reconnect buffer")

        select.select((self.fd,), (), ())
        if print_time:
            end_time = time.time() - start_time
            print("{:6.3f}s".format(end_time))
        if CLIB.disconnect_buffer(self._dev):
            raise RuntimeError("Failed to disconnect buffer")

        start = self.buffer.start
        buf_type = (self.buffer.length // self._b) * C.c_uint8
        raw = np.ctypeslib.as_array(buf_type.from_address(start))
        raw_cast = np.frombuffer(raw, dtype=self._out_type)
        raw_copy = np.copy(raw_cast)

        return raw_copy.reshape(self._height, self._width)

    def save_png(self, name_base='test'):
        name = '{}_exp_{}'.format(name_base, self._exposure)
        filename = os.path.normpath(self._save_path + '/' + name + '.png')
        image = self.capture()
        plt.imsave(filename, image, cmap='gray',
                   vmin=self._vmin, vmax=self._vmax)

    def view(self):

        image = self.capture()
        plt.imshow(image, cmap='gray', vmin=self._vmin, vmax=self._vmax)
        mask = 'Exposure: {:7d}\nMin: {:4d} - Max: {:4d}'

        plt.title(mask.format(self._exposure,
                              np.min(image),
                              np.max(image)))

    def view_hist(self):
        image = self.capture()
        plt.hist(image.flatten())
        mask = 'Exposure: {:7d}\nMin: {:4d} - Max: {:4d}'

        plt.title(mask.format(self._exposure,
                              np.min(image),
                              np.max(image)))

    def live_view(self, print_time=False, center_line=True):
        fig = plt.figure()
        image = self.capture()
        im_data = plt.imshow(image, animated=True,
                             cmap='gray', vmin=self._vmin, vmax=self._vmax)
        if center_line:
            plt.axvline(self._width / 2, alpha=0.5)
            plt.axhline(self._height / 2, alpha=0.5)

        def update(*args):
            image = self.capture(print_time=print_time)
            im_data.set_array(image)

        animacion = animation.FuncAnimation(fig, update, interval=1)
        # plt.show()
        return animacion

    def __del__(self):
        self.exposure = 1
        CLIB.stop_capturing(self._dev)
        CLIB.uninit_device(self._dev)
        CLIB.close_device(self._dev)


plt.ion()
