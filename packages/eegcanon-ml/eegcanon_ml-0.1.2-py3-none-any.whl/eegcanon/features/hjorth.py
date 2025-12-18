import numpy as np


def hjorth_parameters(epoch):
    """
    Compute Hjorth Activity, Mobility, Complexity
    epoch shape: (channels, time)
    """
    activity = np.var(epoch, axis=1)

    diff1 = np.diff(epoch, axis=1)
    mobility = np.sqrt(np.var(diff1, axis=1) / activity)

    diff2 = np.diff(diff1, axis=1)
    complexity = np.sqrt(
        np.var(diff2, axis=1) / np.var(diff1, axis=1)
    ) / mobility

    return activity, mobility, complexity