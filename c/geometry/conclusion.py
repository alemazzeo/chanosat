import numpy as np

simulation = np.load('simulate.npz')

angle = simulation['angle']
rho = simulation['rho']
alpha = simulation['alpha']
beta = simulation['beta']
theta = simulation['theta']
shift = simulation['shift']
phi = simulation['phi']

data = np.array(angle, rho, alpha, beta, theta, shift, phi)
