# -*- coding: utf-8 -*-
"""

"""

import cv2
import numpy as np
import matplotlib.pyplot as plt


class Camera(object):
    """

    """

    def __init__(self, camera=1):
        self._camera = cv2.VideoCapture(camera)
        if not self._camera.isOpened():
            raise RuntimeError('Device not available')

        self._height = self._camera.get(cv2.CAP_PROP_FRAME_HEIGHT)
        self._widht = self._camera.get(cv2.CAP_PROP_FRAME_WIDTH)

        self._image = None
        self._points = list()

    def _take_points(self, event, x, y, flags, *args):

        if event == cv2.EVENT_LBUTTONUP:
            self._points.append((x, y))

        if event == cv2.EVENT_MOUSEMOVE:
            for i, point in enumerate(self._points):
                if i > 0:
                    cv2.line(img=self._image,
                             pt1=self._points[i - 1],
                             pt2=self._points[i],
                             color=(0, 0, 255), thickness=1)

                cv2.circle(img=self._image, center=(point[0], point[1]),
                           radius=5, color=(0, 0, 255), thickness=-1)
            if 0 < len(self._points) < 4:
                cv2.line(img=self._image,
                         pt1=self._points[-1], pt2=(x, y),
                         color=(0, 0, 255), thickness=1)
            if len(self._points) == 4:
                cv2.line(img=self._image,
                         pt1=self._points[-1], pt2=self._points[0],
                         color=(0, 0, 255), thickness=1)

    def calibrate(self):
        self._points.clear()
        cv2.namedWindow('Calibrate')
        cv2.setMouseCallback('Calibrate', self._take_points)

        while len(self._points) < 5:
            _, self._image = self._camera.read()

            if cv2.waitKey(1) & 0xFF == 27:
                break

            cv2.imshow('Calibrate', self._image)

        cv2.destroyWindow('Calibrate')
        return self._points
