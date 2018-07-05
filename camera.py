# -*- coding: utf-8 -*-
"""

"""


import cv2
import numpy as np
import matplotlib.pyplot as plt

from imutils import contours
from skimage import measure


class Camera(object):
    """

    """

    def __init__(self, camera=1):
        self._camera = cv2.VideoCapture(camera)
        if not self._camera.isOpened():
            raise RuntimeError('Device not available')

        self._height = self._camera.get(cv2.CAP_PROP_FRAME_HEIGHT)
        self._width = self._camera.get(cv2.CAP_PROP_FRAME_WIDTH)

        self._points = list()

        self._current_xy = 0, 0

        self._dim_x = None
        self._dim_y = None
        self._src = None
        self._dst = None
        self._homography = None

    @property
    def connected(self):
        return self._camera.isOpened()

    def current_image(self):
        for i in range(5):
            self._camera.read()
        return self._camera.read()[1]

    def set_plane(self, dim_x=1.0, dim_y=1.0, points=None, center=False):

        if center:
            x0, x1 = - dim_x / 2, dim_x / 2
            y0, y1 = - dim_y / 2, dim_y / 2
        else:
            x0, y0 = 0, 0
            x1, y1 = dim_x, dim_y

        self._dim_x = [x0, x1]
        self._dim_y = [y0, y1]

        if points is None:
            points = self._select_points()

        dst = [(0, 0),
               (self._width, 0),
               (self._width, self._height),
               (0, self._height)]

        self._setHomography(points, dst)

    def _click_points(self, event, x, y, flags, *args):

        if event == cv2.EVENT_LBUTTONUP:
            if len(self._points) < 5:
                self._points.append((x, y))

        if event == cv2.EVENT_MOUSEMOVE:
            self._current_xy = x, y

    def _select_points(self, color=(255, 0, 0)):
        self._points = list()
        cv2.namedWindow('Calibrate')
        cv2.setMouseCallback('Calibrate', self._click_points)

        while len(self._points) < 4:
            _, image = self._camera.read()

            if cv2.waitKey(1) & 0xFF == 27:
                cv2.destroyWindow('Calibrate')
                self._points.clear
                raise KeyboardInterrupt('Aborted')

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
        self._points = np.float32(self._points[0:4])
        return self._points

    def _setHomography(self, src, dst):

        src_f32 = np.float32(src)
        dst_f32 = np.float32(dst)

        M = cv2.getPerspectiveTransform(src_f32, dst_f32)

        self._src = src_f32
        self._dst = dst_f32
        self._homography = M

    def _apply_homography(self, img=None):
        if img is None:
            img = self.current_image()
        M = self._homography
        h, w = img.shape[:2]
        return cv2.warpPerspective(img, M, (w, h),
                                   flags=cv2.INTER_LINEAR)

    def _test_homography(self, img=None):

        if img is None:
            img = self.current_image()

        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        img[:, :, 1] = 0
        img[:, :, 2] = 0
        warped = self._apply_homography(img)

        f, (ax1, ax2) = plt.subplots(1, 2, figsize=(20, 10))
        f.subplots_adjust(hspace=.2, wspace=.05)
        ax1.imshow(img)

        x_src = [self._src[:][0]]
        y_src = [self._src[:][1]]

        ax1.set_title('Original Image', fontsize=30)
        ax1.set_xlim([0, self._width])
        ax1.set_ylim([0, self._height])

        ax1.plot(x_src, y_src, color='red', alpha=0.4, linewidth=3,
                 solid_capstyle='round', zorder=2)

        ax2.set_title('Unwarped Image', fontsize=30)

        x0, x1 = self._dim_x
        y0, y1 = self._dim_y
        ax2.imshow(warped, extent=[x0, x1, y1, y0])
        plt.show()


if __name__ == "__main__":
    c1 = Camera(0)
    if c1.connected:
        print('Camera 1 (internal) connected as c1')
    c2 = Camera(1)
    if c2.connected:
        print('Camera 2 (webcam) connected as c2')
