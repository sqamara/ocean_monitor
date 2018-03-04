'''
SMOOTH
https://www.megunolink.com/articles/3-methods-filter-noisy-arduino-measurements/
Averaging
Running average
Expotential filter
Exponentially Weighted Moving Average (EWMA)

OUTLIERS
https://ocefpaf.github.io/python4oceanographers/blog/2015/03/16/outlier_detection/
FFT
median filtering
Gaussian processes
MCMC
'''

import numpy as np

'''
OUTLIERS
'''
def get_median_filtered(signal, threshold=3):
    difference = np.abs(signal - np.median(signal))
    median_difference = np.median(difference)
    if median_difference == 0:
        s = 0
    else:
        s = difference / float(median_difference)
    mask = s > threshold
    signal[mask] = np.median(signal)

    return signal


def get_median_filtered_nearest_replacement(signal, threshold=3):
    difference = np.abs(signal - np.median(signal))
    median_difference = np.median(difference)
    if median_difference == 0:
        s = 0
    else:
        s = difference / float(median_difference)
    mask = s > threshold


    not_found_replacement_val = np.median(signal)    
    for i in range(len(signal)):
        if mask[i] == 1:
            # find prev value that was not identified as an outlier
            found = False
            for j in range(i-1,-1, -1):
                if mask[j] == 0:
                    signal[i] = signal[j]
                    found = True
                    break
            if found == False:
                signal[i] = not_found_replacement_val    

    return signal


def get_rolling_median_filtered(signal, window=10, threshold=3, replace_with='median'):

    for i in range(window, len(signal)):
        subsignal = signal[i+1-window:i+1]
        difference = np.abs(subsignal - np.median(subsignal))
        median_difference = np.median(difference)
        if median_difference == 0:
            s = 0
        else:
            s = difference[-1] / float(median_difference)
        if s > threshold:
            if (replace_with == 'median'):
                signal[i] = np.median(subsignal)
            elif (replace_with == 'slope'):
                signal[i] = signal[i-1] + signal[i-1] - signal[i-2]
            elif (replace_with == 'last'):
                signal[i] = signal[i-1]
    return signal

def peak_detector_rolling_median(signal, window=10, threshold=3):
    indixes = []
    values = []

    for i in range(window, len(signal)):
        subsignal = signal[i+1-window:i+1]
        difference = np.abs(subsignal - np.median(subsignal))
        median_difference = np.median(difference)
        if median_difference == 0:
            s = 0
        else:
            s = difference[-1] / float(median_difference)
        if s > threshold:
            indixes.append(i)
            values.append(signal[i])        

    return indixes, values

def peak_detector_left_right(signal, lag=10):
    indixes = []
    values = []

    for i in range(lag, len(signal)-lag):
        left_mean = np.mean(signal[i-lag:i])
        right_mean = np.mean(signal[i+1:i+1+lag])
        if signal[i] > left_mean and signal[i] > right_mean or (signal[i] < left_mean and signal[i] < right_mean):
            indixes.append(i)
            values.append(signal[i])

    return indixes, values