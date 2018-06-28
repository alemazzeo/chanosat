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

        self._current_xy = 0, 0

        self.last_image = None

        self._homography = None

    @property
    def connected(self):
        return self._camera.isOpened()

    @property
    def current_image(self):
        return self._camera.read()[1]

    def _take_points(self, event, x, y, flags, *args):

        if event == cv2.EVENT_LBUTTONUP:
            if len(self._points) < 5:
                self._points.append((x, y))

        if event == cv2.EVENT_MOUSEMOVE:
            self._current_xy = x, y

    def calibrate(self, color=(255, 0, 0), testing=False):
        self._points = list()
        cv2.namedWindow('Calibrate')
        cv2.setMouseCallback('Calibrate', self._take_points)

        while len(self._points) < 4:
            _, image = self._camera.read()

            if cv2.waitKey(1) & 0xFF == 27:
                cv2.destroyWindow('Calibrate')
                self._points.clear
                return False

            cv2.circle(img=image, center=self._current_xy,
                       radius=5, color=color, thickness=-1)

            for i, point in enumerate(self._points):
                if i > 0:
                    cv2.line(img=image,
                             pt1=self._points[i - 1],
                             pt2=self._points[i],
                             color=color, thickness=2)

                cv2.circle(img=image, center=(point[0], point[1]),
                           radius=5, color=color, thickness=-1)

            if 0 < len(self._points) < 4:
                cv2.line(img=image,
                         pt1=self._points[-1],
                         pt2=self._current_xy,
                         color=color, thickness=2)
            if len(self._points) == 3:
                cv2.line(img=image,
                         pt1=self._current_xy, pt2=self._points[0],
                         color=color, thickness=2)

            cv2.imshow('Calibrate', image)

        cv2.destroyWindow('Calibrate')
        _, image = self._camera.read()
        self._last_image = image
        self._points = np.float32(self._points[0:4])
        self._warpPerspective(img=image, testing=testing, save=True)
        return self._points

    def _warpPerspective(self, img=None, src=None, dst=None,
                         testing=True, save=False):

        if img is None:
            img = self.current_image

        if src is None:
            if len(self._points) != 4:
                if self.calibrate() is False:
                    raise RuntimeError(
                        'Missing calibration points to unwrap')
            src = np.float32(self._points)

        if dst is None:
            dst = np.float32([(0, 0),
                              (self._widht, 0),
                              (self._widht, self._height),
                              (0, self._height)])

        h, w = img.shape[:2]
        M = cv2.getPerspectiveTransform(src, dst)
        warped = cv2.warpPerspective(img, M, (w, h), flags=cv2.INTER_LINEAR)

        if testing:
            f, (ax1, ax2) = plt.subplots(1, 2, figsize=(20, 10))
            f.subplots_adjust(hspace=.2, wspace=.05)
            ax1.imshow(img)
            x_src = [src[:][0]]
            y_src = [src[:][1]]
            ax1.plot(x_src, y_src, color='red', alpha=0.4, linewidth=3,
                     solid_capstyle='round', zorder=2)
            ax1.set_ylim([h, 0])
            ax1.set_xlim([0, w])
            ax1.set_title('Original Image', fontsize=30)
            ax2.imshow(warped)
            ax2.set_title('Unwarped Image', fontsize=30)
            plt.show()
        else:
            if save:
                self._homography = M
            return warped, M


if __name__ == "__main__":
    c1 = Camera(0)
    if c1.connected:
        print('Camera 1 (internal) connected as c1')
    c2 = Camera(1)
    if c2.connected:
        print('Camera 2 (webcam) connected as c2')
        c2._warpPerspective()
