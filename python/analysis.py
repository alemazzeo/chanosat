import matplotlib as mpl
mpl.rcParams['keymap.back'].remove('left')
mpl.rcParams['keymap.forward'].remove('right')

import numpy as np
import argparse
import matplotlib.pyplot as plt
import os
import sys
import fnmatch

plt.style.use('dark_background')

parser = argparse.ArgumentParser()
parser.add_argument('-name', type=str, default='theta_0_{}.npz')
parser.add_argument('-path', type=str, default='../data/shift_sweep/')

clock_exposures = [1, 10, 100, 1000, 10000, 100000, 1000000]
time_exposures = [27.14e-6, 147.9e-6, 1.355e-3,
                  13.43e-3, 134.2e-3, 1.341, 13.41]

exp_clock2time = np.poly1d(np.polyfit(clock_exposures, time_exposures, 1))
exp_time2clock = np.poly1d(np.polyfit(time_exposures, clock_exposures, 1))

mask = ('Exposure: {:6.2f}s '
        '({:7d})'
        'Shift: {:6.2f} '
        'Theta: {:6.2f} '
        'Phi: {:6.2f}')


class Viewer():
    def __init__(self, name='theta_0_{}.npz', path='../data/shift_sweep/'):

        self._filename = os.path.join(path, name)
        dir_list = os.listdir(path)
        self._list = fnmatch.filter(dir_list, name.format('*'))

        def getint(name):
            basename = name.partition('.')[0]
            num = basename.split('_')[-1]
            return int(num)

        self._list.sort(key=getint)
        self._filenames = [os.path.join(path, name)
                           for name in self._list]
        self._n = len(self._list)
        self._n_exposures = None

        self._fig, self._image_ax = plt.subplots(1)

        self._current_file = None
        self._current = 0
        self._exposure = 0

        self._vmin, self._vmax = 0, 2**12

        self._event = self._fig.canvas.mpl_connect('key_press_event',
                                                   self._on_key)

        images, info = self._load(0)
        self._image_data = self._image_ax.imshow(images[0],
                                                 cmap='gray',
                                                 vmin=self._vmin,
                                                 vmax=self._vmax)
        self._title = self._image_ax.set_title('')
        self._update_plot()

    def _load(self, i):
        self._current_file = np.load(self._filenames[i])
        images = self._current_file['raw_image']
        exposures = self._current_file['raw_exps']
        shift, theta, phi = self._current_file['raw_pos']

        self._n_exposures = len(exposures)

        info = [exposures, shift, theta, phi]
        return images, info

    def _update_plot(self):
        images, info = self._load(self._current)
        exposures, shift, theta, phi = info
        if len(exposures) <= self._exposure:
            self._exposure = len(exposures) - 1
        self._image_data.set_data(images[self._exposure])
        exposure = exposures[self._exposure]
        title = mask.format(exp_clock2time(exposure),
                            exposure,
                            shift,
                            theta,
                            phi)
        self._title.set_text(title)
        plt.draw()

    def _on_key(self, event):
        sys.stdout.flush()
        if event.key == 'left':
            if self._current > 0:
                self._current -= 1
                self._update_plot()
        elif event.key == 'right':
            if self._current <= self._n:
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


if __name__ == '__main__':
    params = parser.parse_args()
    dataview = Viewer(params.name, params.path)
    plt.show()
