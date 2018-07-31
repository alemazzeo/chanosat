from driver import Chanosat_Driver
from v4l2_python import Device
from tools import FileTools

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
        os.makedirs(path, exist_ok=True)
        self._base_name = os.path.join(path, name + '.npz')

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
                     values=None, start=None, end=None, step=None):

        assert task.lower() in ['shift', 'theta', 'phi', 'exposures']
        assert mode.lower() in ['absolute', 'relative']
        if values is None:
            n = int(end - start) / abs(step) + 1
            values = np.arange(n) * step - start

        self._sequence.append({'task': task,
                               'mode': mode,
                               'values': values,
                               'todo': True})

    def set_as_default(self):
        self._default_pos = self._chano.pos
        self._default_exposure = self._stc.exposure

    def run(self, verbose=True, delay=3):
        t = time.time()
        dt = delay
        try:
            for i, task in enumerate(self._sequence):
                if verbose:
                    str_format = '{:3d} - {:>10}({:>10}) - {} to {}'
                    print(str_format.format(i,
                                            task['task'],
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
                            x0 = getattr(self._chano, task['task'])
                        if task['mode'] == 'relative':
                            x0 = 0

                        for x in task['values']:
                            dt = time.time() - t
                            if dt < delay:
                                time.sleep(dt)
                                t = time.time()

                            setattr(self._chano, task['task'], x0 + x)
                            print('  Set chanosat property:',
                                  task['task'], 'to', x)
                            images = list()
                            for exposure in self._exposures:
                                stc.exposure = exposure
                                if verbose:
                                    print('    Set exposure:', exposure)
                                images.append(self._stc.capture())
                                if verbose:
                                    print('    Image captured')
                            filename = FileTools.newname(self._base_name)
                            np.savez_compressed(filename,
                                                raw_pos=self._chano.pos,
                                                raw_exps=self._exposures,
                                                raw_image=images)
                            if verbose:
                                print('    File saved as:', i)
                    self._sequence[i]['todo'] = False

        except:
            self._chano.pos = self._default_pos
            time.sleep(5)
            raise


if __name__ == '__main__':
    params = parser.parse_args()

    chano = Chanosat_Driver(port=params.chano)
    stc = Device(dev_name=params.stc)
