from driver import Chanosat_Driver
from v4l2_python import Device
from tools import FileTools
import matplotlib.pyplot as plt

import argparse
import numpy as np
import os
import time

parser = argparse.ArgumentParser()
parser.add_argument('-name', type=str, default='test')
parser.add_argument('-path', type=str, default='../data/')
parser.add_argument('-chano', type=str, default='/dev/ttyACM0')
parser.add_argument('-stc', type=str, default='/dev/video1')
parser.add_argument('-mov', type=str, default='phi')


class Measure():
    def __init__(self, name, path, chano=None, stc=None):
        self._name = name
        self._path = path

        if isinstance(chano, Chanosat_Driver):
            self._chano = chano
        elif isinstance(chano, str):
            self._chano = Chanosat_Driver(port=chano)
        else:
            self._chano = Chanosat_Driver(port='/dev/ttyACM0')

        if isinstance(stc, Device):
            self._stc = stc
        elif isinstance(stc, str):
            self._stc = Device(dev_name=stc)
        else:
            self._stc = Device(dev_name='/dev/video1')

        self._default_pos = self._chano.pos
        self._default_exposure = self._stc.exposure
        self._exposures = [100, 1000, 10000]
        self._sequence = list()

    def add_run_task(self, task, mode,
                     values=None, start=None, end=None, step=None,
                     save=True, name=None, path=None):

        if name is None:
            if path is None:
                os.makedirs(self._path, exist_ok=True)
                base_name = os.path.join(self._path, self._name)
            else:
                os.makedirs(path, exist_ok=True)
                base_name = os.path.join(path, self._name)
        else:
            if path is None:
                os.makedirs(path, exist_ok=True)
                base_name = os.path.join(self._path, name)
            else:
                os.makedirs(path, exist_ok=True)
                base_name = os.path.join(path, name)

        assert task.lower() in ['shift', 'theta', 'phi', 'exposures']
        assert mode.lower() in ['absolute', 'relative']

        if values is None:
            n = int(end - start) / abs(step) + 1
            values = np.arange(n) * step - start
        else:
            if not isinstance(values, list):
                if isinstance(values, int) or isinstance(values, float):
                    values = [values, ]
                else:
                    raise ValueError('Valid input: list, int or float')

        self._sequence.append({'task': task,
                               'mode': mode,
                               'values': values,
                               'todo': True,
                               'save': save,
                               'file': base_name})

    def set_as_default(self):
        self._default_pos = self._chano.pos
        self._default_exposure = self._stc.exposure

    def run(self, verbose=True):
        self._stc.view()
        plt.pause(0.001)
        try:
            for i, task in enumerate(self._sequence):
                if verbose:
                    str_format = '{:>8}({:>10}) - {} to {}'
                    print(str_format.format(task['task'],
                                            task['mode'],
                                            task['values'][0],
                                            task['values'][-1]))
                if task['todo']:
                    if task['task'] == 'exposures':
                        self._exposures = task['values']
                        if verbose:
                            print('  Set exposures:', self._exposures)

                    else:
                        if task['mode'] == 'absolute':
                            x0 = 0
                        if task['mode'] == 'relative':
                            x0 = getattr(self._chano, task['task'])

                        for x in task['values']:
                            setattr(self._chano, task['task'], x0 + x)
                            print('  Set chanosat property',
                                  task['task'], 'to', x)
                            if task['save'] is True:
                                images = list()
                                for exposure in self._exposures:
                                    stc.exposure = exposure
                                    if verbose:
                                        print('    Set exposure:', exposure)
                                        self._stc.view()
                                        plt.pause(0.001)
                                    images.append(self._stc.capture())
                                    if verbose:
                                        print('    Image captured')
                                    filename = FileTools.newname(task['file'])
                                    data = {'raw_pos': self._chano.pos,
                                            'raw_exps': self._exposures,
                                            'raw_image': images}
                                    np.savez_compressed(filename,
                                                        **data)
                                    if verbose:
                                        print('    File saved as:', i)
                    self._sequence[i]['todo'] = False
                else:
                    if verbose:
                        print('  Yet done:', self._exposures)

        except:
            self._chano.pos = self._default_pos
            time.sleep(5)
            raise


if __name__ == '__main__':
    params = parser.parse_args()

    chano = Chanosat_Driver(port=params.chano)
    stc = Device(dev_name=params.stc)

    measure = Measure('calibrate.npz', '../data/calibrate/', chano, stc)

    measure.add_run_task('exposures', 'absolute', [2, 1000])
    measure.add_run_task('phi', 'absolute', values=-5, save=False)

    for theta in [-10, 5, 0, 5, 10]:

        measure.add_run_task('shift', 'absolute', values=0, save=False)
        measure.add_run_task('theta', 'absolute', values=theta, save=False)
        measure.add_run_task('shift', 'absolute', start=0, end=10, step=0.2)

    measure.add_run_task('shift', 'absolute', values=0, save=False)
    measure.add_run_task('theta', 'absolute', values=0, save=False)

    measure.add_run_task('exposures', 'absolute', [2, 10, 100, 1000])

    for shift in (np.arange(6) * 5):

        measure.add_run_task('shift', 'absolute', values=float(shift),
                             save=False)
        measure.add_run_task('phi', 'absolute', start=0, end=20, step=1,
                             name='explore.npz', path='../data/explore')

    measure.add_run_task('shift', 'absolute', values=0, save=False)
    measure.add_run_task('theta', 'absolute', values=0, save=False)
    measure.add_run_task('phi', 'absolute', values=-5, save=False)
