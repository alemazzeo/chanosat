# -*- coding: utf-8 -*-
""" File v4l2_python.py

"""

# Deponia

import ctypes as C
import numpy as np
import v4l2
import time
import matplotlib.pyplot as plt
from subprocess import call

EXPOSURE = v4l2.V4L2_CID_EXPOSURE
EXPOSURE_MODE = v4l2.V4L2_CID_PRIVATE_BASE + 15
EXPOSURE_MODE_OFF = 0
EXPOSURE_MODE_TIMED = 1
EXPOSURE_MODE_TRIGGER_WIDTH = 2
EXPOSURE_MODE_TRIGGER_CONTROLLED = 3

CLIB = C.CDLL('../bin/libv4l2py.so')


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
                ("buffers", C.POINTER(Buffer)),
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
        cw = C.c_int(width)
        ch = C.c_int(height)
        fcc = fourcc.encode('utf-8')
        CLIB.open_device(self._dev)
        CLIB.set_pixelformat(self._dev, cw, ch, fcc)
        CLIB.init_mmap(self._dev)
        CLIB.start_capturing(self._dev)
        self.setDriverCtrlValue(EXPOSURE, 1, captures=0)
        self.setDriverCtrlValue(EXPOSURE_MODE, 0, captures=0)

    @property
    def exposure(self):
        return self.getDriverCtrlValue(EXPOSURE)

    @exposure.setter
    def exposure(self, value):
        assert(0 <= value < 4192304)
        self.setDriverCtrlValue(EXPOSURE, int(value))

    def print_caps(self):
        CLIB.print_caps(self._dev)

    def setDriverCtrlValue(self, id_ctrl, value, captures=2):
        r = CLIB.setDriverCtrlValue(self._dev,
                                    C.c_uint(id_ctrl),
                                    C.c_int(value))
        if r != 0:
            raise RuntimeWarning("Failed to set driver control value"
                                 "with id {}".format(id_ctrl))
        for i in range(captures):
            self.capture()
            time.sleep(1)

    def getDriverCtrlValue(self, id_ctrl):
        c = C.c_int(0)
        r = CLIB.getDriverCtrlValue(self._dev,
                                    C.c_uint(id_ctrl),
                                    C.byref(c))
        if r != 0:
            raise RuntimeWarning("Failed to get driver control value")
        return c.value

    def capture(self):

        if CLIB.wait_for_frame(self._dev):
            i = self._try_max - 1
            time.sleep(self._timeout)
            while i > 0 and CLIB.wait_for_frame(self._dev):
                time.sleep(self._timeout)
                i -= 1
            raise TimeoutError("Device not respond")

        if CLIB.disconnect_buffer(self._dev):
            raise RuntimeError("Failed to disconnect buffer")

        start = self.buffers[0].start
        buf_type = (self.buffers[0].length // self._b) * C.c_uint8
        raw = np.ctypeslib.as_array(buf_type.from_address(start))
        raw_cast = np.frombuffer(raw, dtype=self._out_type)
        raw_copy = np.copy(raw_cast)

        if CLIB.reconnect_buffer(self._dev):
            i = self._try_max - 1
            time.sleep(self._timeout)
            while i > 0 and CLIB.reconnect_buffer(self._dev):
                i -= 1
                time.sleep(self._timeout)
            raise TimeoutError("Failed to reconnect buffer")

        return raw_copy.reshape(self._height, self._width)

    def save_png(self, dst='test.png'):
        image = self.capture()
        plt.imsave('test.png', image, cmap='gray', vmin=0, vmax=2**12)

    def view(self):
        image = self.capture()
        plt.imshow(image, cmap='gray', vmin=0, vmax=2**12)
        plt.title('%d - %d' % (np.min(image), np.max(image)))

    def __del__(self):
        CLIB.stop_capturing(self._dev)
        CLIB.uninit_device(self._dev)
        CLIB.close_device(self._dev)


plt.ion()
