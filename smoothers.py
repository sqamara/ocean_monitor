import numpy as np

'''
SMOOTHING
'''
def averaging(*args):
    points_len = len(args[0])
    samples_per_point = len(args)
    res = np.zeros(points_len)

    for arg in args:
        for i in range(points_len):
            res[i] += arg[i]
    for i in range(points_len):
        res[i] /= samples_per_point

    return res

def running_average(points, window=10):
    points_len = len(points)
    res = np.empty(points_len)

    for i in range(0, window):
        res[i] = points[i]

    for i in range(window, points_len):
        res[i] = np.mean(points[i-window+1:i+1])

    return res

def exponential_filter(points, weight=.3):
    points_len = len(points)
    res = np.empty(points_len)
    res[0] = points[0]

    for i in range(1, points_len):
        res[i] = weight*res[i-1] + (1-weight)*points[i]

    return res