# -*- coding: utf-8 -*-
""" File v4l2_python.py

"""

# Deponia

import argparse
import ctypes as C
import numpy as np
import cv2
import v4l2
from subprocess import call

EXPOSURE = v4l2.V4L2_CID_PRIVATE_BASE + 15

parser = argparse.ArgumentParser()
parser.add_argument('-exposure', type=int, default=1)
parser.add_argument('-file', type=str, default='image.png')


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

    def __init__(self, dev_name, width, height, fourcc,
                 buffers=4, exposure=None):
        if exposure is not None:
            call('v4l2-ctl -d {} -c exposure=100'.dev_name, shell=True)
        self.dev_name = dev_name.encode('utf-8')
        self._dev = C.pointer(self)
        self._width = width
        self._height = height
        self._fourcc = fourcc
        self._out_type = np.uint16
        self._b = 2
        cw = C.c_int(width)
        ch = C.c_int(height)
        fcc = fourcc.encode('utf-8')
        CLIB.open_device(self._dev)
        CLIB.set_pixelformat(self._dev, cw, ch, fcc)
        CLIB.init_mmap(self._dev)
        CLIB.start_capturing(self._dev)

    def print_caps(self):
        CLIB.print_caps(self._dev)

    def setDriverCtrlValue(self, id_ctrl, value):
        r = CLIB.setDriverCtrlValue(self._dev,
                                    C.c_uint(id_ctrl),
                                    C.c_int(value))
        if r != 0:
            raise RuntimeWarning("Failed to set driver control value"
                                 "with id {}".format(id_ctrl))

    def getDriverCtrlValue(self, id_ctrl):
        c = C.c_int(0)
        r = CLIB.getDriverCtrlValue(self._dev,
                                    C.c_uint(id_ctrl),
                                    C.byref(c))
        if r != 0:
            raise RuntimeWarning("Failed to get driver control value")
        return c.value

    def capture_raw(self):

        print(CLIB.wait_for_frame(self._dev))
        CLIB.disconnect_buffer(self._dev)

        start = self.buffers[0].start
        buf_type = (self.buffers[0].length // self._b) * C.c_uint8
        raw = np.ctypeslib.as_array(buf_type.from_address(start))

        CLIB.reconnect_buffer(self._dev)
        return np.frombuffer(raw, dtype=self._out_type)

    def convert(self, raw, cs=None):
        if cs is None:
            image = raw.reshape(self._height, self._width)
        else:
            image = cv2.cvtColor(raw.reshape(self._height,
                                             self._width), cs)
        return image

    def capture(self, dst='test.png', cvColor=None):
        c = self.capture_raw()
        image = self.convert(c, cvColor)
        cv2.imwrite(dst, image)

    def __del__(self):
        CLIB.stop_capturing(self._dev)
        CLIB.uninit_device(self._dev)
        CLIB.close_device(self._dev)
