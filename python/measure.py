from driver import Chanosat_Driver
from devices import Chanosat
from v4l2_python import Device
from tools import FileTools
import matplotlib.pyplot as plt
from analysis import exp_clock2time

import argparse
import numpy as np
import os
import time
import fnmatch
import yaml

parser = argparse.ArgumentParser()
parser.add_argument('-name', type=str, default='test')
parser.add_argument('-path', type=str, default='../data/test/')
parser.add_argument('-chano', type=str, default='/dev/ttyACM0')
parser.add_argument('-stc', type=str, default='/dev/video1')
parser.add_argument('-mov', type=str, default='phi')
parser.add_argument('-sim', action='store_true')


def arange(start, end, step):
    n = int(end - start) / abs(step) + 1
    if end > start:
        step = abs(step)
    else:
        step = -abs(step)
    values = np.arange(n) * step + start
    return values


def newfile(basename, start=0):
    i = start
    while True:
        if os.path.isfile(basename.format(i)):
            i += 1
        else:
            yield basename.format(i)


class FalseStc():
    def __init__(self, *args, **kwargs):
        self._exposure = 1
        self._vmin = 0
        self._vmax = 2**12

    def capture(self):
        return np.random.randint(0, 2**12, size=(10, 10))

    def view(self):

        image = self.capture()
        plt.imshow(image, cmap='gray', vmin=self._vmin, vmax=self._vmax)
        mask = 'Exposure: {:7d}\nMin: {:4d} - Max: {:4d}'

        plt.title(mask.format(self._exposure,
                              np.min(image),
                              np.max(image)))

    @property
    def exposure(self):
        return self._exposure

    @exposure.setter
    def exposure(self, value):
        self._exposure = value


class Measure():
    def __init__(self, chano=None, stc=None):
        self._filename = None
        self._threshold = 300

        if (isinstance(chano, Chanosat_Driver) or
                isinstance(chano, Chanosat)):
            self._chano = chano
        elif isinstance(chano, str):
            self._chano = Chanosat_Driver(port=chano)
        else:
            self._chano = Chanosat_Driver(port='/dev/ttyACM0')

        if isinstance(stc, Device) or isinstance(stc, FalseStc):
            self._stc = stc
        elif isinstance(stc, str):
            self._stc = Device(dev_name=stc)
        else:
            self._stc = Device(dev_name='/dev/video1')

        self._exposures = [10, 100, 1000, 10000]
        self._threshold = 1000
        self._tasks = list()

    @property
    def exposures(self):
        return self._exposures

    @property
    def threshold(self):
        return self._threshold

    @property
    def filename(self):
        if self._filename is not None:
            return next(self._filename)
        else:
            return None

    @property
    def path(self):
        return self._path

    @exposures.setter
    def exposures(self, values):
        self._exposures = values

    @threshold.setter
    def threshold(self, value):
        self._threshold = value

    @filename.setter
    def filename(self, filename):
        path, name = os.path.split(filename)
        os.makedirs(path, exist_ok=True)
        print(path)
        self._filename = newfile(filename)

    def load_cfg(self, filename, group=None):
        self._cfg = yaml.load(open(filename, 'r'))
        if group is None:
            task_groups = [key for key, value in self._cfg.items()]
        else:
            task_groups = [group, ]
        for task_group in task_groups:
            for task in self._cfg[task_group]:
                for key, value in task.items():
                    action, target = key.split(' ')
                    if isinstance(value, dict):
                        x = arange(value['start'],
                                   value['end'],
                                   value['step'])
                        prompt = '{} {} {} : {} : {}'.format(action,
                                                             target,
                                                             value['start'],
                                                             value['end'],
                                                             value['step'])
                    elif isinstance(value, list):
                        x = np.asarray(value)
                        if len(x) > 6:
                            prompt = '{} {} [{}, {},..., {}]'.format(action,
                                                                     target,
                                                                     x[0],
                                                                     x[1],
                                                                     x[-1])
                        else:
                            prompt = '{} {} {}'.format(action, target, x)

                    else:
                        x = value
                        prompt = '{} {} {}'.format(action, target, x)
                    print(prompt)
                    self.add_run_task(action, target, x, prompt)

    def add_run_task(self, action, target, value, prompt):

        action = action.lower()
        target = target.lower()

        assert action in ['move', 'sweep', 'set']
        assert target in ['shift', 'theta', 'phi', 'pos',
                          'exposures', 'filename']

        self._tasks.append([action, target, value, prompt])

    def run(self, verbose=True):
        for action, target, value, prompt in self._tasks:
            print(prompt)
            self.do_task(action, target, value)

    def do_task(self, action, target, value):

        if action == 'move':
            setattr(self._chano, target, value)

        elif action == 'set':
            setattr(self, target, value)

        elif action == 'sweep':

            for x in value:
                setattr(self._chano, target, x)
                images = list()
                self._stc.exposure = self._exposures[-1]
                image = self._stc.capture()

                if image.max() > self._threshold:
                    self._stc.exposure = self._exposures[0]
                    self._stc.capture()
                    time.sleep(exp_clock2time(self._exposures[0]))
                    for exposure in self._exposures[:-1]:
                        self._stc.exposure = exposure
                        self._stc.capture()
                        images.append(self._stc.capture())
                    images.append(image)
                    data = {'raw_pos': self._chano.pos,
                            'raw_exps': self._exposures,
                            'raw_image': images}
                else:
                    images.append(image)
                    data = {'raw_pos': self._chano.pos,
                            'raw_exps': self._exposures[-1],
                            'raw_image': images}

                filename = self.filename
                if filename is None:
                    raise FileNotFoundError('Missing filename')
                np.savez_compressed(filename, **data)

        else:
            print('Task <{} {}> not available'.format(action, target))


def find_background(n):
    exps = np.array([10, 100, 1000, 2000, 5000, 10000, 20000])
    maxs = np.zeros(len(exps))
    means = np.zeros(len(exps))
    stds = np.zeros(len(exps))
    for j, exp in enumerate(exps):
        stc.exposure = exp
        stc.capture()
        m = np.zeros((3, n))
        for i in range(n):
            image = stc.capture()
            m[0][i] = image.max()
            m[1][i] = image.mean()
            m[2][i] = image.std()
        maxs[j] = np.mean(m[0])
        means[j] = np.mean(m[1])
        stds[j] = np.std(m[2])
    return exps, maxs, means, stds


if __name__ == '__main__':
    params = parser.parse_args()

    if params.sim:
        chano = Chanosat()
        stc = FalseStc()
    else:
        chano = Chanosat_Driver(port=params.chano)
        stc = Device(dev_name=params.stc)

    measure = Measure(chano, stc)
    # measure.load_cfg('../etc/measure.yaml', 'calibrate')
