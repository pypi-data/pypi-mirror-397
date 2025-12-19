import matplotlib.pyplot as plt
import numpy as np


def checkerboard(N=int(3e4), C=10, plot=True, noise=0.5):
    X = np.random.uniform(-1, 1, (N, 2))
    F = np.floor
    mask = (F(C * X[:, 0]) + F(C * X[:, 1])) % 2 == 0
    Y = np.where(mask, 1, -1) + np.random.normal(0, noise, N)
    if plot:
        plt.scatter(X[:, 0], X[:, 1], c=Y, s=3)
        plt.show()
    return X, Y
