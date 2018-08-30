import argparse
import numpy as np
import matplotlib.pyplot as plt
from camera import Camera
from driver import Chanosat_Driver

plt.style.use('dark_background')


def arange(start, end, step):
    n = int(end - start) / abs(step) + 1
    if end > start:
        step = abs(step)
    else:
        step = -abs(step)
    values = np.arange(n) * step + start
    return values


def find_border(camera, chano, phis, shifts):
    result = list()
    for phi in phis:
        chano.phi = phi
        curve, = plt.plot([], [], ls='', marker='o')
        plt.axis((shifts[0], shifts[-1], 0, 255))
        y = np.zeros(len(shifts))
        for i, shift in enumerate(shifts):
            chano.shift = shift
            y[i] = camera.current_plane().max()
            curve.set_data(shifts[0:i], y[0:i])
            plt.pause(0.001)
            plt.draw()
        result.append(y)
    return result


def find_border_fit(camera, chano, phis, shift_centers, offset=1.5, step=0.1):
    result = list()
    plt.figure()
    plt.axis((0, 25, 0, 255))
    for j, phi in enumerate(phis):
        chano.phi = phi
        sl = shift_centers[j] - offset
        sr = shift_centers[j] + offset
        shifts = arange(sl, sr, step)
        curve, = plt.plot([], [], ls='', marker='o')
        y = np.zeros(len(shifts))
        for i, shift in enumerate(shifts):
            chano.shift = shift
            y[i] = camera.current_plane().max()
            curve.set_data(shifts[0:i], y[0:i])
            plt.pause(0.001)
            plt.draw()
        result.append([shifts, y])
    return result


if __name__ == '__main__':
    camera = Camera(1)
    chano = Chanosat_Driver()

    camera.set_plane()
    plt.ion()

    #phis = arange(15, 25, 1)
    #shifts = arange(0, 25, 1)

    #result = find_border(camera, chano, phis, shifts)

    phis = [15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25]
    shift_centers = [1.2,
                     3.1,
                     5.4,
                     7.0,
                     9.5,
                     11.0,
                     15.0,
                     18.0,
                     22.0,
                     25.0,
                     28.0]

    result = find_border_fit(camera, chano, phis, shift_centers)
