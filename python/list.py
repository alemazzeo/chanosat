import numpy as np
import os

filename = '../data/test{}.npz'
start = 0
end = 220
line = '{:5d}, {:7d}, {:10.6f}, {:10.6f}, {:10.6f}'

with open('../data/list.txt', 'w') as f:
    for i in range(start, end):
        npz = np.load(filename.format(i))
        f.write(line.format(i, int(npz['exposure']), *npz['chanosat_pos']))
        f.write('\n')
