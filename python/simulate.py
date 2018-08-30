import numpy as np
import matplotlib.pyplot as plt
from devices import Chanosat
from geometry import Plane, Intersection
from measure import arange

phi_range = arange(-50, 70, 2)
shift_range = arange(0, 28, 0.5)
theta_range = arange(0, 90, 5)

chano = Chanosat(xyz=[-21, -21, 0])
plane = Plane()
plane.z = 20
r = 21
r2 = r**2


data = list()
i = 0
for theta in theta_range:
    print('.', end='')
    for phi in phi_range:
        for shift in shift_range:
            chano.pos = [shift, theta, phi]
            target = Intersection(ray=chano, plane=plane)

            x, y, z = target.point
            rho = np.sqrt(x**2 + y**2)
            angle = np.arctan2(y, x)

            angle2 = np.deg2rad(theta) - angle
            alpha = phi * np.cos(angle2)
            beta = phi * np.sin(angle2)

            if rho < r:
                i += 1
                data.append([angle, rho, alpha, beta, theta, shift, phi])

            # print('{:4}, {:4}, {:4}, {:8}'.format(theta, shift, phi, i),
            #      end='\r')
        #print(' ' * 30, end='')


data = np.array(data)

plt.ion()
fig1 = plt.figure()
plt.polar(5 / 4 * np.pi, np.sqrt(chano.x**2 + chano.y**2), marker='*')
plt.polar(data[:, 0], data[:, 1], ls='', marker='o')

fig2, ax2 = plt.subplots()
ax2.plot(data[:, 1], data[:, 3], ls='', marker='o')
ax2.set_xlabel('rho', fontsize=14)
ax2.set_ylabel('beta', fontsize=14)

fig3, ax3 = plt.subplots()
ax3.plot(data[:, 1], data[:, 2], ls='', marker='o')
ax3.set_xlabel('rho', fontsize=14)
ax3.set_ylabel('alpha', fontsize=14)
