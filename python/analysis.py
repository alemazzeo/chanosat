import numpy as np
import argparse
import matplotlib.pyplot as plt
import os
import sys
import fnmatch
from skimage.measure import label, regionprops
from skimage.transform import rotate
from skimage.filters import threshold_otsu
from skimage.morphology import dilation
from skimage.exposure import adjust_gamma
from hdr import hdr_builder


plt.style.use('dark_background')

parser = argparse.ArgumentParser()
parser.add_argument('-name', type=str, default='*_tps.npz')
parser.add_argument('-path', type=str, default='./calibrate_planes2/')
parser.add_argument('-start', type=int, default=0)

clock_exposures = [1, 10, 100, 1000, 10000, 100000, 1000000]
time_exposures = [27.14e-6, 147.9e-6, 1.355e-3,
                  13.43e-3, 134.2e-3, 1.341, 13.41]

exp_clock2time = np.poly1d(np.polyfit(clock_exposures, time_exposures, 1))
exp_time2clock = np.poly1d(np.polyfit(time_exposures, clock_exposures, 1))

exp10 = np.load('../data/dark/dark05_exp_000010.npz')['image']
exp100 = np.load('../data/dark/dark05_exp_000100.npz')['image']
exp1000 = np.load('../data/dark/dark05_exp_001000.npz')['image']
exp10000 = np.load('../data/dark/dark05_exp_010000.npz')['image']

background = np.asarray([exp10, exp100, exp1000, exp10000])

mask = ('{:^67}\n'
        'Exposure({}/{}): {:.6f}s | '
        'Shift: {:6.2f}° | '
        'Theta: {:6.2f}° | '
        'Phi: {:6.2f}°')


class Viewer():
    def __init__(self, name, path, start=0):

        dir_list = os.listdir(path)
        self._list = fnmatch.filter(dir_list, name)

        self._filenames = [os.path.join(path, name)
                           for name in self._list]
        self._filenames.sort(key=lambda x: os.path.getmtime(x))
        self._n = len(self._list)
        self._n_exposures = None

        self._current_file = None
        self._current = start
        self._exposure = 0
        self._current_info = None

        self._vmin, self._vmax = 0, 2**12

        self._fig, self._image_ax = None, None
        self._event = None
        self._image_data = None
        self._title = None

        self._spots = list()

        self._spotted = False

    def init_view(self, i=0, ax=None):
        self._current = i
        images, info = self.load(i)
        if ax is None:
            self._fig, self._image_ax = plt.subplots(1)
        else:
            self._fig, self._image_ax = ax.get_figure(), ax

        self._fig.canvas.mpl_disconnect(
            self._fig.canvas.manager.key_press_handler_id)

        self._event = self._fig.canvas.mpl_connect('key_press_event',
                                                   self._on_key)

        self._image_data = self._image_ax.imshow(images[0],
                                                 cmap='gray',
                                                 vmin=self._vmin,
                                                 vmax=self._vmax)
        self._title = self._image_ax.set_title('')
        self._update_plot()

    @property
    def files(self):
        return self._list

    @property
    def full_files(self):
        return self._filenames

    def load(self, i):
        self._current_file = np.load(self._filenames[i])
        images = self._current_file['images']
        exposures = np.array([10, 100, 1000, 10000])
        shift, theta, phi = self._current_file['pos']

        self._n_exposures = exposures.size

        info = [exposures, shift, theta, phi]
        return images, info

    def _format_info(self, info):
        mask = ('Exposure({}/{}): {:.6f}s | '
                'Shift: {:6.2f}mm | '
                'Theta: {:6.2f}° | '
                'Phi: {:6.2f}°')

        exposures, shift, theta, phi = info
        if exposures.size == 1:
            exposure = int(exposures)
        else:
            exposure = exposures[self._exposure]
        title = mask.format(self._exposure + 1,
                            exposures.size,
                            exp_clock2time(exposure),
                            shift,
                            theta,
                            phi)
        return title

    def _update_plot(self):
        images, info = self.load(self._current)
        exposures, shift, theta, phi = info

        if exposures.size - 1 <= self._exposure:
            self._exposure = exposures.size - 1

        self._image_data.set_data(images[self._exposure])
        self._current_info = self._format_info(info)
        title = '{:^67}\n{}'.format(self._filenames[self._current],
                                    self._current_info)
        self._title.set_text(title)
        plt.draw()

    def _on_key(self, event):
        sys.stdout.flush()
        if event.key == 'left':
            if self._current > 0:
                self._current -= 1
                self._update_plot()
        elif event.key == 'right':
            if self._current < self._n - 1:
                self._current += 1
                self._update_plot()
        elif event.key == 'up':
            if self._exposure <= self._n_exposures:
                self._exposure += 1
                self._update_plot()
        elif event.key == 'down':
            if self._exposure > 0:
                self._exposure -= 1
                self._update_plot()
        elif event.key == 'p':
            print(self._current_info)
        elif event.key == 'e':
            if self._spotted is True:
                print('\rCancelled {}'.format(' ' * 50), end='')
                self._image_ax.lines.pop()
                self._spotted = False
                plt.draw()
        elif event.key == ' ':
            image = self._current_file['images'][self._exposure]
            spot = search_spot(image, ax=self._image_ax, gamma=1)
            y0, x0 = spot.centroid
            shift, theta, phi = self._current_file['pos']
            exposures = np.array([10, 100, 1000, 10000])
            if exposures.size == 1:
                exposure = int(exposures)
            else:
                exposure = exposures[self._exposure]
            print('\n[{}, {}, {}, {:.2f}, {:.2f}, {:.2f}]'.format(exposure,
                                                                  shift,
                                                                  theta,
                                                                  phi,
                                                                  x0, y0),
                  end='')
            self._spotted = True
            plt.draw()
        elif event.key == 'd':
            image = self._current_file['images'][self._exposure]
            search_difraction(image, ax=self._image_ax, length=10)
            plt.draw()


def search_spot(input_image, ax=None, gamma=0.001, dilates=1,
                plot_spot=True):

    image = adjust_gamma(input_image, gamma)
    threshold = threshold_otsu(image)
    binary = image >= threshold

    for i in range(dilates):
        binary = dilation(binary)

    label_img = label(binary)

    regions = regionprops(label_img, image)

    if ax is None:
        fig, ax = plt.subplots()

        ax.imshow(image, cmap='gray')
        ax.imshow(label_img, cmap='gray', alpha=0.5)

    areas = list()
    for props in regions:
        areas.append(props.area)
    spot = regions[np.argmax(np.array(areas))]

    y0, x0 = spot.centroid
    ax.plot(x0, y0, '.g', markersize=15)

    return spot


def search_difraction(image, ax=None, gamma=0.001, dilates=1, length=1,
                      plot_spot=False, plot_axis=False):

    if ax is None:
        fig, ax = plt.subplots()
        ax.imshow(image, cmap='gray')

    spot = search_spot(image, ax, gamma, dilates, plot_spot)

    y0, x0 = spot.centroid
    orientation = spot.orientation
    print('({}, {}, {})'.format(x0, y0, orientation))

    if plot_axis is True:
        x1 = x0 + np.cos(orientation) * 0.5 * spot.major_axis_length
        y1 = y0 - np.sin(orientation) * 0.5 * spot.major_axis_length
        x2 = x0 - np.sin(orientation) * 0.5 * spot.minor_axis_length
        y2 = y0 - np.cos(orientation) * 0.5 * spot.minor_axis_length
        ax.plot((x0, x1), (y0, y1), '-r', linewidth=2.5)
        ax.plot((x0, x2), (y0, y2), '-r', linewidth=2.5)

    x0_ray = x0 + np.cos(orientation) * length * 0.5 * spot.major_axis_length
    y0_ray = y0 - np.sin(orientation) * length * 0.5 * spot.major_axis_length
    x1_ray = x0 - np.cos(orientation) * length * 0.5 * spot.major_axis_length
    y1_ray = y0 + np.sin(orientation) * length * 0.5 * spot.major_axis_length

    ax.plot((x0_ray, x1_ray), (y0_ray, y1_ray), '-g', linewidth=1)

    minr, minc, maxr, maxc = spot.bbox
    # bx = (minc, maxc, maxc, minc, minc)
    # by = (minr, minr, maxr, maxr, minr)
    # ax.plot(bx, by, '-b', linewidth=1)

    # ax.set_xlim(x0 - 2 * (maxc - minc), x0 + 2 * (maxc - minc))
    # ax.set_ylim(y0 - 2 * (maxr - minr), y0 + 2 * (maxr - minr))


if __name__ == '__main__':
    params = parser.parse_args()
    dataview = Viewer(params.name, params.path)
    dataview.init_view(params.start)
    plt.tight_layout()
    plt.show()
