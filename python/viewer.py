import numpy as np
import matplotlib.pyplot as plt

plt.ion()

mask = ('Max: {:4d} '
        'Exposure: {:6d} '
        'Theta: {:6.2f} '
        'Shift: {:6.2f} '
        'Phi: {:6.2f}')

current = 0


def view(path='../data/', name='test{i}.npz', **kwargs):
    filename = (path + name).format(**kwargs)
    try:
        a = np.load(filename)
        plt.imshow(a['image'], cmap='gray', vmin=0, vmax=2**12)
        plt.title(mask.format(np.max(a['image']),
                              int(a['exposure']),
                              a['chanosat_pos'][0],
                              a['chanosat_pos'][1],
                              a['chanosat_pos'][2]))
    except FileNotFoundError:
        print('File {} not found'.format(filename))


def next():
    global current
    current += 1
    view(i=current)


def last():
    global current
    current -= 1
    view(i=current)
