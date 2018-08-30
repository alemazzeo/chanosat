import numpy as np
import matplotlib.pyplot as plt

simulation = np.load('simulate.npz')

_angle = simulation['angle']
_rho = simulation['rho']
_alpha = simulation['alpha']
_beta = simulation['beta']
_theta = simulation['theta']
_shift = simulation['shift']
_phi = simulation['phi']

order = np.argsort(_rho)

rho = _rho[order]
alpha = _alpha[order]
beta = _beta[order]
plt.ion()

x = np.arange(80) * 0.25
alphas = list()
betas = list()
for i in range(79):
    b = np.argwhere(rho < x[i + 1])
    a = np.argwhere(rho > x[i])
    alphas.append(alpha[a.min():b.max()])
    betas.append(beta[a.min():b.max()])

mins = list()
maxs = list()
for angle in alphas:
    angle.sort()
    diff = np.diff(angle)
    mins.append(diff.min())
    maxs.append(diff.max())

plt.figure()
plt.plot(x[:-1], mins)
plt.plot(x[:-1], maxs)

mins = list()
maxs = list()
for angle in betas:
    angle.sort()
    diff = np.diff(angle)
    mins.append(diff.min())
    maxs.append(diff.max())

plt.figure()
plt.plot(x[:-1], mins)
plt.plot(x[:-1], maxs)
