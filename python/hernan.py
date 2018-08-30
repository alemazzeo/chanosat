import numpy as np

from skimage.measure import label, regionprops
from skimage.filters import threshold_otsu

from driver import Chanosat_Driver
from v4l2_python import Device
from measure import arange

from hdr import hdr_builder

phis = arange(-5, 5, 0.5)
shifts = -arange(0, 21, 2)

chano = Chanosat_Driver()
chano.theta_secure = 0
chano.phi_secure = 0

std = Device()
std.exposure = 1000

exposures = [10, 100, 1000, 10000]
background = list()


input("Turn OFF laser and press enter")

for exp in exposures:
    std.exposure = exp
    std.capture()
    background.append(std.capture())

input("Turn ON laser and press enter")

chano.pos = [0, 0, 0]
chano.phi = -20

result = list()

for phi in phis:
    chano.phi = phi
    print(phi)
    for shift in shifts:
        print("  {}\r".format(shift), end='')
        chano.shift = shift
        image = std.capture()
        t = threshold_otsu(image)
        bin_image = image > t

        label_image = label(bin_image)
        regions = regionprops(label_image, image)

        areas = list()
        for props in regions:
            areas.append(props.area)
        spot = regions[np.argmax(np.array(areas))]

        y, x = spot.centroid

        result.append([phi, shift, x, y, image.max()])
