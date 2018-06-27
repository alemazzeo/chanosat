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

        self._points = list()

        self._current_x = 0
        self._current_y = 0

        self.last_image = None

    @property
    def connected(self):
        return self._camera.isOpened()

    def _take_points(self, event, x, y, flags, *args):

        if event == cv2.EVENT_LBUTTONUP:
            if len(self._points) < 5:
                self._points.append((x, y))

        if event == cv2.EVENT_MOUSEMOVE:
            self._current_x = x
            self._current_y = y

    def calibrate(self):
        self._points.clear()
        cv2.namedWindow('Calibrate')
        cv2.setMouseCallback('Calibrate', self._take_points)

        while len(self._points) < 5:
            _, image = self._camera.read()

            if cv2.waitKey(1) & 0xFF == 27:
                break

            for i, point in enumerate(self._points):
                if i > 0:
                    cv2.line(img=image,
                             pt1=self._points[i - 1],
                             pt2=self._points[i],
                             color=(0, 0, 255), thickness=1)

                cv2.circle(img=image, center=(point[0], point[1]),
                           radius=5, color=(0, 0, 255), thickness=-1)

            if 0 < len(self._points) < 4:
                cv2.line(img=image,
                         pt1=self._points[-1],
                         pt2=(self._current_x, self._current_y),
                         color=(0, 0, 255), thickness=1)
            if len(self._points) == 4:
                cv2.line(img=image,
                         pt1=self._points[-1], pt2=self._points[0],
                         color=(0, 0, 255), thickness=1)

            cv2.imshow('Calibrate', image)

        cv2.destroyWindow('Calibrate')
        self._last_image = image
        return np.float32(self._points[0:4])

    def unwarp(self, img=None, src=None, dst=None, testing=True):

        if img is None and self._last_image is not None:
            img = self._last_image

        if src is None and len(self._points) == 4:
            src = self._points

        if dst is None:
            dst = np.float32([(0, 0),
                              (0, self._height),
                              (self._widht, self._height),
                              (self._height, 0)])

        h, w = img.shape[:2]
        M = cv2.getPerspectiveTransform(src, dst)
        warped = cv2.warpPerspective(img, M, (w, h), flags=cv2.INTER_LINEAR)

        if testing:
            f, (ax1, ax2) = plt.subplots(1, 2, figsize=(20, 10))
            f.subplots_adjust(hspace=.2, wspace=.05)
            ax1.imshow(img)
            x = [src[0][0], src[2][0], src[3][0], src[1][0], src[0][0]]
            y = [src[0][1], src[2][1], src[3][1], src[1][1], src[0][1]]
            ax1.plot(x, y, color='red', alpha=0.4, linewidth=3,
                     solid_capstyle='round', zorder=2)
            ax1.set_ylim([h, 0])
            ax1.set_xlim([0, w])
            ax1.set_title('Original Image', fontsize=30)
            ax2.imshow(cv2.flip(warped, 1))
            ax2.set_title('Unwarped Image', fontsize=30)
            plt.show()
        else:
            return warped, M


if __name__ == "__main__":
    c1 = Camera(0)
    if c1.connected:
        print('Camera 1 connected as c1')
    c2 = Camera(1)
    if c2.connected:
        print('Camera 1 connected as c2')
