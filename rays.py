import numpy as np
import matplotlib.pyplot as plt
import explore5

pcurves = list()
curves = list()
for s in explore5.data:
    for i, p in enumerate(s):
        y0 = p[1] - 5.8
        m0 = np.tan(-np.deg2rad(p[3] + 5.2))
        if i == 0 or i == len(s) - 1:
            pcurves.append(np.poly1d([m0, y0]))
        else:
            curves.append(np.poly1d([m0, y0]))

x = np.linspace(0, 1000)

for curve in curves:
    y = curve(x)
    plt.plot(x, y, ls='-', lw=0.5)

for curve in pcurves:
    y = curve(x)
    plt.plot(x, y, ls='-', lw=2)

plt.show()
