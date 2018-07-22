from driver import Chanosat_Driver
from v4l2_python import Device
from tools import FileTools

import argparse
import numpy as np
import os
import time

parser = argparse.ArgumentParser()
parser.add_argument('-name', type=str, default='dark')
parser.add_argument('-path', type=str, default='../data/')
parser.add_argument('-stc', type=str, default='/dev/video1')
parser.add_argument('-captures', type=str, default=10)

params = parser.parse_args()

stc = Device(dev_name=params.stc)

exposures = [1, 10, 50, 100, 200, 500, 1000, 2000, 5000, 10000]

normalized_name = os.path.normpath(params.path + '/' + params.name)
path, name, extension = FileTools.splitname(normalized_name)
base_name = os.path.normpath(path + "/" + name)

mask = 'Exposure: {:6d}'

time.sleep(5)
print("\n\n")

for exposure in exposures:
    stc.exposure = exposure
    print(mask.format(exposure))
    for i in range(params.captures):
        image = stc.capture()
        filename = base_name + '{:02d}_exp_{:06}.npz'.format(i, exposure)
        np.savez(filename, image=image)
        time_now = time.gmtime(time.time())
        print("\n    " + time.strftime("%X", time_now), end='')
        print(' - Saved as: {}'.format(os.path.relpath(filename)))
        time.sleep(1)
