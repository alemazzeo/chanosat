import numpy as np
import matplotlib.pyplot as plt
from matplotlib import patches

import argparse

import explore5
import explore6
import explore7

import explore8
import explore10

import explore11
import explore12

import explore14
import explore15
import explore16

parser = argparse.ArgumentParser()
parser.add_argument('-serie1', action='store_true')
parser.add_argument('-serie2', action='store_true')
parser.add_argument('-serie3', action='store_true')
parser.add_argument('-serie4', action='store_true')
parser.add_argument('-serie5', action='store_true')
parser.add_argument('-curves', action='store_true')
parser.add_argument('-show', action='store_false')


def plots(explores, curves=False, show=True):

    fig, ax = plt.subplots(subplot_kw={'aspect': 'equal'})

    data = list()
    fits = list()
    angles = list()
    for explore in explores:
        xs = list()
        ys = list()
        for serie in explore.data:
            for e, s, t, p, x, y in serie:
                xs.append(x)
                ys.append(y)
        data.append([xs, ys])
        p = np.poly1d(np.polyfit(xs, ys, 1))
        angle = np.rad2deg(np.arctan(p.c[0]))
        fits.append(p)
        angles.append(angle)

    x = np.arange(2448, dtype=int)
    y0 = fits[0](x)
    y1 = fits[1](x)
    if len(explores) == 3:
        y2 = fits[2](x)
        diff = abs(y0 - y1) + abs(y0 - y2)
        min_x = x[np.argmin(diff)]
        min_y = (fits[0](min_x) + fits[1](min_x) + fits[2](min_x)) / 3

    elif len(explores) == 2:
        diff = abs(y0 - y1)
        min_x = x[np.argmin(diff)]
        min_y = (fits[0](min_x) + fits[1](min_x)) / 2

    plt.plot(min_x, min_y, ls='', marker='o', markersize=15, alpha=0.5)
    plt.axvline(2448 / 2, ls=':')
    plt.axhline(2048 / 2, ls=':')

    for i in range(len(explores)):
        x, y = data[i]
        fit = fits[i]
        angle = angles[i]
        plt.plot(x, y, ls='', marker='.', markersize=10)
        plt.plot(np.unique(x), fit(np.unique(x)))
        arc = patches.Arc([2448 / 2, 2048 / 2], 1000, 1000,
                          theta1=180 + angle, theta2=180)
        plt.gca().add_patch(arc)

        plt.annotate('{:.3f}°'.format(angle),
                     xy=(x[-1], y[-1]),
                     xytext=(x[-1] - 50, y[-1]),
                     fontsize=14,
                     horizontalalignment='right')

    if show is True:
        plt.show()

    if curves is True:
        for i in range(len(data)):
            x, y = data[i]
            plt.plot(x, y, ls=':', marker='o')

            plt.axvline(2448 / 2, ls=':')
            plt.axhline(2048 / 2, ls=':')
            plt.show()


if __name__ == "__main__":
    params = parser.parse_args()
    if params.serie1 is True:
        plots([explore5, explore6, explore7], params.curves, params.show)
    if params.serie2 is True:
        plots([explore8, explore10], params.curves, params.show)
    if params.serie3 is True:
        plots([explore11, explore12], params.curves, params.show)
    if params.serie4 is True:
        plots([explore14, explore15, explore16], params.curves, params.show)

    if not params.show:
        plt.show()
