import numpy as np
import matplotlib.pyplot as plt

plt.ion()
path = '../data/'
name = 'test{}.npz'

mask = ('Max: {:4d} '
        'Exposure: {:6d} '
        'Theta: {:6.2f} '
        'Shift: {:6.2f} '
        'Phi: {:6.2f}')

current = 0


def view(i):
    try:
        a = np.load((path + name).format(i))
        plt.imshow(a['image'], cmap='gray', vmin=0, vmax=2**12)
        plt.title(mask.format(np.max(a['image']),
                              int(a['exposure']),
                              a['chanosat_pos'][0],
                              a['chanosat_pos'][1],
                              a['chanosat_pos'][2]))
    except FileNotFoundError:
        print('File {} not found')


def next():
    global current
    current += 1
    view(current)


def last():
    global current
    current -= 1
    view(current)
