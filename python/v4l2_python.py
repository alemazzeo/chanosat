# -*- coding: utf-8 -*-
""" File v4l2_python.py

"""


import ctypes as C
import numpy as np
import cv2

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

    def __init__(self, dev_name, width, height, fourcc, buffers=4):
        self.dev_name = "/dev/video0".encode('utf-8')
        self._dev = C.pointer(self)
        cw = C.c_int(width)
        ch = C.c_int(height)
        fcc = fourcc.encode('utf-8')
        CLIB.open_device(self._dev)
        CLIB.set_pixelformat(self._dev, cw, ch, fcc)
        CLIB.init_mmap(self._dev)
        CLIB.start_capturing(self._dev)

    def print_caps(self):
        CLIB.print_caps(self._dev)

    def capture_raw(self):

        print(CLIB.wait_for_frame(self._dev))
        CLIB.disconnect_buffer(self._dev)

        start = self.buffers[0].start
        buf_type = self.buffers[0].length * C.c_uint8
        raw = np.ctypeslib.as_array(buf_type.from_address(start))

        CLIB.reconnect_buffer(self._dev)
        return raw

    def convert(self, raw, cs):
        reshaped = raw.reshape(480, 640, 2)
        image = cv2.cvtColor(reshaped, cs)

        return image

    def capture(self, dst='test.jpg'):
        c = self.capture_raw()
        image = self.convert(c, cv2.COLOR_YUV2BGR_YUYV)
        cv2.imwrite('test.jpg', image)

    def __del__(self):
        CLIB.stop_capturing(self._dev)
        CLIB.uninit_device(self._dev)
        CLIB.close_device(self._dev)
