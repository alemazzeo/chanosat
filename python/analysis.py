import matplotlib as mpl
mpl.rcParams['keymap.back'].remove('left')
mpl.rcParams['keymap.forward'].remove('right')

import numpy as np
import argparse
import matplotlib.pyplot as plt
import os
import sys

plt.style.use('dark_background')

parser = argparse.ArgumentParser()
parser.add_argument('-serie', type=int, default=0)
params = parser.parse_args()

mask = ('Exposure: {:6.2f} '
        'Shift: {:6.2f} '
        'Theta: {:6.2f} '
        'Phi: {:6.2f}')

current = 0

series = [0, 18, 60, 180, 220]
exposures = [2, 2, 3, 1, 0]


class Viewer():
    def __init__(self, name='test{}.npz', path='../data/',
                 start=0, end=17, exposures=2):

        self._fig, self._image_ax = plt.subplots(1)
        self._filename = os.path.normpath(path + '/' + name)
        self._current_file = np.load(self._filename.format(start))
        self._start = start
        self._end = end
        self._exposures = exposures
        self._current = [start, 0]
        self._vmin, self._vmax = 0, 2**12

        self._event = self._fig.canvas.mpl_connect('key_press_event',
                                                   self._on_key)

        image, info = self._load(start)
        self._image_data = self._image_ax.imshow(image,
                                                 cmap='gray',
                                                 vmin=self._vmin,
                                                 vmax=self._vmax)
        self._title = self._image_ax.set_title(info)

    def _load(self, i):
        self._current_file = np.load(self._filename.format(i))
        image = self._current_file['image']
        exposure = float(self._current_file['exposure']) / 1000000 * 13.3
        shift, theta, phi = self._current_file['chanosat_pos']
        info = mask.format(exposure, shift, theta, phi)
        return image, info

    def _update_plot(self):
        image, info = self._load(self._current[0])
        self._image_data.set_data(image)
        self._title.set_text(info)
        plt.draw()

    def _on_key(self, event):
        sys.stdout.flush()
        if event.key == 'left':
            if self._current[0] - self._exposures >= self._start:
                self._current[0] -= self._exposures
                self._update_plot()
        elif event.key == 'right':
            if self._current[0] + self._exposures <= self._end:
                self._current[0] += self._exposures
                self._update_plot()
        elif event.key == 'up':
            if self._current[1] < self._exposures - 1:
                self._current[1] += 1
                self._current[0] += 1
                self._update_plot()
        elif event.key == 'down':
            if self._current[1] > 0:
                self._current[1] -= 1
                self._current[0] -= 1
                self._update_plot()


if __name__ == '__main__':
    i = params.serie
    serie = Viewer(start=series[i], end=series[i +
                                               1] - 1, exposures=exposures[i])
    plt.show()
