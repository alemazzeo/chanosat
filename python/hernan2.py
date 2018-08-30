import numpy as np

from skimage.measure import label, regionprops
from skimage.filters import threshold_otsu

from driver import Chanosat_Driver
from v4l2_python import Device
from measure import arange

from hdr import hdr_builder

phis = arange(-20, 20, 5)
thetas = [-20, -10, 10, 20]
shifts = [0, 21, 25]

chano = Chanosat_Driver()
chano.theta_secure = 0
chano.phi_secure = 0

std = Device()
std.exposure = 1000

exposures = [10, 100, 1000, 10000]
background = list()

# input("\n\nTurn OFF laser and press enter")

# for exp in exposures:
#    std.exposure = exp
#    std.capture()
#    background.append(std.capture())

# np.savez('./calibrate_planes2/background.npz',
#         background=background)

# input("Turn ON laser and press enter\n")

chano.phi = -25
chano.theta = -30
chano.shift = 21

mask = '{:6.2f}, {:6.2f}, {:6.2f}\r'
mask_file = './calibrate_planes2/{}_{}_{}_tps.npz'

try:
    for i, theta in enumerate(thetas):
        chano.theta = theta
        for j, phi in enumerate(phis):
            chano.phi = phi
            for k, shift in enumerate(shifts):
                print(mask.format(theta, phi, shift), end='')
                chano.shift = shift
                images = list()
                for exp in exposures:
                    std.exposure = exp
                    std.capture()
                    images.append(std.capture())
                std.exposure = exposures[0]
                np.savez(mask_file.format(theta, phi, shift),
                         pos=chano.pos, images=images)

except KeyboardInterrupt:
    chano.pos = [0, 0, 0]
    raise

print(' ' * 50)
chano.pos = [0, 0, 0]
