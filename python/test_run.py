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


def start(chano, stc, name='test', path='../data/',
          exposures=[10, 100, 1000, 10000],
          mov={'shift': [0, 1, 2, 3, 4, 5]}):

    normalized_name = os.path.normpath(path + '/' + name)
    path, name, extension = FileTools.splitname(normalized_name)
    base_name = os.path.normpath(path + "/" + name)

    mask = 'Exposure: {:6d} Theta: {:6.2f} Shift: {:6.2f} Phi: {:6.2f}'

    time.sleep(5)
    print("\n\n")

    try:
        for motor, sweep in mov.items():
            for x in sweep:

                setattr(chano, motor, x)
                for exposure in exposures:
                    stc.exposure = exposure
                    image = stc.capture()
                    newname = FileTools.newname(base_name + '.npz')

                    np.savez(newname,
                             image=image,
                             exposure=exposure,
                             chanosat_pos=chano.pos)

                    print(mask.format(exposure,
                                      chano.theta,
                                      chano.shift,
                                      chano.phi))

                    time_now = time.gmtime(time.time())
                    print("\n" + time.strftime("%X", time_now), end='')
                    print(' - Saved as: {}'.format(os.path.relpath(newname)))
                    time.sleep(1)

    except:
        print('\n\nUnexpected error.'
              ' Trying to reset chanosat to zero position\n\n')
        chano.pos = [0, 0, 0]
        time.sleep(1)
        raise


if __name__ == '__main__':
    params = parser.parse_args()

    chano = Chanosat_Driver(port=params.chano)
    stc = Device(dev_name=params.stc)

    start(chano, stc, params.name, params.path)
