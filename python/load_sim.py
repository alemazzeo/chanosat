import numpy as np
import matplotlib.pyplot as plt


def load_sim():
    _result = np.loadtxt('calibrate.txt', delimiter=',', unpack=True)
    rho, theta, alpha, beta, c_theta, c_phi, c_shift = _result
    np.savez('sim_calibrate.npz',
             rho=rho, theta=theta, alpha=alpha, beta=beta,
             c_theta=c_theta, c_phi=c_phi, c_shift=c_shift)
    return _result


def to_bins(raw_data, bin_centers, bin_size, column=0):
    order = np.argsort(raw_data[column, :])
    data = raw_data[:, order]

    result = list()
    for x in bin_centers:
        b = np.argwhere(data[column] < x + bin_size)
        a = np.argwhere(data[column] > x - bin_size)
        if a.size > 0 and b.size > 0:
            result.append(data[:, a.min():b.max()])
        else:
            result.append(np.zeros([data.shape[0], 0]))
    return result


if __name__ == "__main__":

    _rho, _theta, _alpha, _beta, _c_theta, _c_phi, _c_shift = load_sim()

    plt.ion()

    rho = _rho
    theta = _theta
    alpha = _alpha * 180 / np.pi
    beta = _beta * 180 / np.pi

    data = np.array([rho, theta, alpha, beta, _c_theta, _c_phi, _c_shift])

    r = 21

    d_rho = 1
    n_bin = int(r / d_rho)
    delta_rho = 2
    x_rho = np.arange(n_bin) * d_rho

    by_rho = to_bins(data, x_rho, delta_rho, 0)

    n_alpha = 25
    min_alpha = -40
    max_alpha = 60

    n_beta = 25
    min_beta = -40
    max_beta = 60

    x_alpha = np.linspace(min_alpha, max_alpha, n_alpha)
    x_beta = np.linspace(min_beta, max_beta, n_beta)

    points = list()
    for i in range(len(by_rho)):
        by_alpha = to_bins(by_rho[i], x_alpha, 0.5, 2)
        for j in range(len(by_alpha)):
            by_beta = to_bins(by_alpha[j], x_beta, 0.5, 3)
            for k in range(len(by_beta)):
                points.append(by_beta[k])

    plt.ion()
    plt.figure()

    for i in range(len(points)):
        plt.plot(points[i][2], points[i][3], 'o')
