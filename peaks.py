def is_peak(indx,signal):
    if signal[indx] > signal[indx-1] and signal[indx] > signal[indx+1]:
        return 1
    elif signal[indx] < signal[indx-1] and signal[indx] < signal[indx+1]:
        return -1
    else:
        return 0

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
