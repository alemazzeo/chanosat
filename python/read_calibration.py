import os
import numpy as np
import fnmatch

from hdr import hdr_builder

exposures = [10, 100, 1000, 10000]
bg_npz = np.load('./calibrate_planes2/background.npz')
background = np.array(bg_npz['background'])
datafiles = os.listdir('./calibrate_planes2/')
stacks = fnmatch.filter(datafiles, '*_tps.npz')

hdr = hdr_builder(background, exposures, 0, 2**12)

data = list()
for i, stack in enumerate(stacks):
    npz = np.load(os.path.join('./calibrate_planes2/', stack))
    image = hdr(npz['images'], exposures)
    np.savez('hdr_{:03d}.npz'.format(i), image=image, pos=npz['pos'])
