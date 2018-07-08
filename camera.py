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
        self._x = None
        self._y = None
        self._src = None
        self._dst = None
        self._homography = None

    @property
    def connected(self):
        return self._camera.isOpened()

    @property
    def x(self):
        return self._x

    @property
    def y(self):
        return self._y

    def current_image(self, filtered=[1, 2]):
        for i in range(5):
            self._camera.read()

        image = self._camera.read()[1]
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

        for i in range(0, 2):
            if i in filtered:
                image[:, :, i] = 0

        return image

    def current_plane(self):
        image = self.current_image()
        plane = self._apply_homography(image)
        return plane

    def plot_current(self, ax=None, calibration=True, **subplots_kwargs):
        if ax is None:
            fig, ax = plt.subplots(1, **subplots_kwargs)
        ax.imshow(self.current_image())

        ax.set_xlim([0, self._width])
        ax.set_ylim([0, self._height])

        if calibration:

            x_src = [self._src[:][0]]
            y_src = [self._src[:][1]]

            print(x_src, y_src)

            ax.plot(x_src, y_src, color='red', alpha=0.4, linewidth=3,
                    solid_capstyle='round', zorder=2)

    def plot_plane(self, ax=None, **subplots_kwargs):
        if ax is None:
            fig, ax = plt.subplots(1, **subplots_kwargs)

        x0, x1 = self._dim_x
        y0, y1 = self._dim_y

        ax.imshow(self.current_plane(), extent=[x0, x1, y1, y0])

    def set_plane(self, dim_x=1.0, dim_y=1.0, points=None, center=True):

        if center:
            x0, x1 = - dim_x / 2, dim_x / 2
            y0, y1 = - dim_y / 2, dim_y / 2
        else:
            x0, y0 = 0, 0
            x1, y1 = dim_x, dim_y

        self._dim_x = [x0, x1]
        self._dim_y = [y0, y1]

        self._x = np.linspace(x0, x1, self._width)
        self._y = np.linspace(y0, y1, self._height)

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

        f, (ax1, ax2) = plt.subplots(1, 2, figsize=(20, 10))
        f.subplots_adjust(hspace=.2, wspace=.05)

        self.plot_current(ax1)
        self.plot_plane(ax2)

        ax1.set_title('Original Image', fontsize=30)
        ax2.set_title('Unwarped Image', fontsize=30)
        plt.show()


if __name__ == "__main__":
    try:
        c1 = Camera(0)
        if c1.connected:
            print('Camera 1 connected as c1')
    except RuntimeError:
        print('Camera 1 not available')

    try:
        c2 = Camera(1)
        if c2.connected:
            print('Camera 2 connected as c2')
    except RuntimeError:
        print('Camera 2 not available')
