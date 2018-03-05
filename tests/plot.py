import os,sys,inspect
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0,parentdir) 

import pickle
import matplotlib.pyplot as plt
import numpy as np

from filters import *
from smoothers import *
from peaks import *

def reject_outliers(data):
    print(np.median(data))
    
    res = []
    for i in range(len(data)):
        if abs(data[i] - np.median(data)) < 5: 
            res.append(data[i])
        else:
            res.append(res[-1])

    return res


def add_plot(graphs, index, title, x, y, xlabel, ylabel):
    ax = plt.subplot(graphs, 1, index+1)
    ax.plot(x, y)
    ax.set_ylabel(ylabel)
    ax.set_xlabel(xlabel)
    ax.set_title(title)

'''
rolling median median replacement
rolling median last valid replacement
rolling median slope replcement
X
agveraging
rolling average
exponential filter
'''
def last_running_avg():
    filename = '../data/water_tray.pickle'

    with open(filename, 'rb') as file:
        results1, results2 = pickle.load(file)

    window = 30     # for filters and running smoother
    threshold = 4   # for filters
    weight = .3     # for exponential filter

    peak_detector_window =   30
    peak_detector_threshold = 1

    offset = 0

    lag = 1

    plot1 = results1[:]
    plot2 = results2[:]

    plot1 = get_rolling_median_filtered(np.array(plot1), window=window, threshold=threshold, replace_with='last')
    plot2 = get_rolling_median_filtered(np.array(plot2), window=window, threshold=threshold, replace_with='last')


    # plot1 = running_average(plot1, window=window)
    # plot2 = running_average(plot2, window=window)

    for i in range(1,20):
        plot1 = exponential_filter(plot1, weight=weight)
        plot2 = exponential_filter(plot2, weight=weight)

    filler = np.median(plot1)
    for i in range(0, window):
        plot1[i] = filler
        plot2[i] = filler

    ax = plt.subplot(1,1,1)
    ax.set_ylim([18, 22])
    
    ax.plot(range(len(plot1)), plot1)
    # peaks_index1,peaks_vals1 = peak_detector_rolling_median(plot1, window=peak_detector_window, threshold=peak_detector_threshold)
    peaks_index1,peaks_vals1 = peak_detector_left_right(plot1, lag=lag)
    # peaks_index1,peaks_vals1 = peak_detector_scipy(plot1, lag=lag)
    plt.plot(peaks_index1,peaks_vals1, marker='o', linestyle='none', color='r', alpha=0.3)

    temp = [filler]*offset
    temp = np.array(temp)
    plot2 = np.concatenate((temp,plot2))
    
    ax.plot(range(len(plot2)), plot2)
    # peaks_index2,peaks_vals2 = peak_detector_rolling_median(plot2, window=peak_detector_window, threshold=peak_detector_threshold)
    peaks_index2,peaks_vals2 = peak_detector_left_right(plot2, lag=lag)
    # peaks_index2,peaks_vals2 = peak_detector_scipy(plot2, lag=lag)
    plt.plot(peaks_index2,peaks_vals2, marker='o', linestyle='none', color='r', alpha=0.3)   




    def is_peak(indx,signal):
        if signal[indx] > signal[indx-1] and signal[indx] > signal[indx+1]:
            return 1
        elif signal[indx] < signal[indx-1] and signal[indx] < signal[indx+1]:
            return -1
        else:
            return 0

    # given an index from signal1 the function returns the next indx in signal2 that 
    # matches the peak characteristic of the provided index
    def find_match(indx, other_indxs, signal1, signal2):
        peak = is_peak(indx, signal1)
        for i in range(len(other_indxs)):
            if indx > other_indxs[i]:
                continue

            if peak == is_peak(other_indxs[i], signal2):
                return other_indxs[i]
        return 299+offset

    for indx in peaks_index1:
        next = find_match(indx, peaks_index2,  plot1, plot2)
        x = [indx, next]
        y = [plot1[indx], plot2[next]]
        
        plt.plot(x, y, linestyle=':', color='r')







    plt.tight_layout()
    plt.show()

def rolling_median_x_smoothing(both=False):
    
    filename = '../data/water_tray.pickle'

    with open(filename, 'rb') as file:
        results1, results2 = pickle.load(file)

    window = 30     # for filters and running smoother
    threshold = 4   # for filters
    weight = .3     # for exponential filter

    filters = ['nonfiltered','median', 'slope', 'last']
    smoothers = ['nonsmoothed','averaging', 'running_average', 'exponential_filter']

    subplot_idx = 1
    for f in filters:
        for s in smoothers:
            
            plot1 = results1[:]
            plot2 = results2[:]

            if f is not 'nonfiltered':
                plot1 = get_rolling_median_filtered(np.array(plot1), window=window, threshold=threshold, replace_with=f)
                plot2 = get_rolling_median_filtered(np.array(plot2), window=window, threshold=threshold, replace_with=f)
            
            if s == 'averaging':
                plot1 = averaging(plot1, plot2)
                plot2 = [np.median(plot2)]*len(plot2)
            elif s == 'running_average':
                plot1 = running_average(plot1, window=window)
                plot2 = running_average(plot2, window=window)
            elif s == 'exponential_filter':
                for i in range(10):
                    plot1 = exponential_filter(plot1, weight=weight)
                    plot2 = exponential_filter(plot2, weight=weight)


            # if used a window need to nullify the first set of results
            filler = np.median(plot1)
            if (f != 'nonfiltered' or s == 'running_average'):
                for i in range(0, window):
                    plot1[i] = filler
                    plot2[i] = filler


            ax = plt.subplot(4, 4, subplot_idx)
            # ax.set_ylabel('distance [cm]')
            # ax.set_xlabel('time [s]')
            if f != 'nonfiltered' and s != 'nonsmoothed':
                ax.set_ylim([18, 22])
            ax.set_title(f+" and " +s)
            ax.plot(range(len(plot1)), plot1)

            if both:
                offset = 10
                temp = [filler]*offset
                temp = np.array(temp)
                plot2 = np.concatenate((temp,plot2))
                ax.plot(range(len(plot2)), plot2)


            subplot_idx += 1

    
    plt.tight_layout()
    plt.show()


def main():
    if (len(sys.argv) > 1):
        filename = sys.argv[1]
    else:
        filename = '../data/results.pickle'

    with open(filename, 'rb') as file:
        results1, results2 = pickle.load(file)

    # graphs = [  ("original",results1),
    #             ("running average", running_average(results1, 5)),
    #             ("averaging", averaging(results1, results2)),
    #             ("exponential filter", exponential_filter(results1, .3)),
    #         ]

    # for i in range(len(graphs)):
    #     add_plot(len(graphs),i, graphs[i][0], range(len(graphs[i][1])), graphs[i][1], 'distance [cm]','time [s]')

    # threshold = 2
    # ############# GLOBAL
    # results1_median_filtered = get_median_filtered(np.array(results1), threshold=threshold)
    # outlier_idx = np.where(results1_median_filtered != results1)[0]

    plt.subplot(4, 1, 1)
    plt.plot(range(len(results1)), results1)
    plt.ylabel('distance [cm]')
    plt.xlabel('time [s]')

    # #highlight outliers
    # outlier_idx = np.where(results1_median_filtered != results1)[0]
    # outlier_point = [results1[idx] for idx in outlier_idx]
    # plt.plot(outlier_idx,outlier_point, marker='o', linestyle='none', color='r', alpha=0.3)




    # plt.subplot(3, 1, 2)
    # plt.plot(range(len(results1)), results1_median_filtered)
    # plt.ylabel('distance [cm]')
    # plt.xlabel('time [s]')

    # outlier_point = [results1_median_filtered[idx] for idx in outlier_idx]
    # plt.plot(outlier_idx,outlier_point, marker='o', linestyle='none', color='r', alpha=0.3)



    # results1_median_filtered_nearest_replacement = get_median_filtered_nearest_replacement(np.array(results1), threshold=threshold)

    # plt.subplot(3, 1, 3)
    # plt.plot(range(len(results1)), results1_median_filtered_nearest_replacement)
    # plt.ylabel('distance [cm]')
    # plt.xlabel('time [s]')

    # outlier_point = [results1_median_filtered_nearest_replacement[idx] for idx in outlier_idx]
    # plt.plot(outlier_idx,outlier_point, marker='o', linestyle='none', color='r', alpha=0.3)

    ## windowed
    window = 30
    threshold = 4

    results1_rolling_median_filtered = get_rolling_median_filtered(np.array(results1), window=window, threshold=threshold, replace_with='median')
    plt.subplot(4, 1, 2)
    plt.plot(range(len(results1)), results1_rolling_median_filtered)
    plt.ylabel('distance [cm]')
    plt.xlabel('time [s]')
    
    rolling_outlier_idx = np.where(results1_rolling_median_filtered != results1)[0]
    rolling_outlier_point = [results1_rolling_median_filtered[idx] for idx in rolling_outlier_idx]
    plt.plot(rolling_outlier_idx,rolling_outlier_point, marker='o', linestyle='none', color='r', alpha=0.3)


    results1_rolling_median_filtered = get_rolling_median_filtered(np.array(results1), window=window, threshold=threshold, replace_with='slope')
    plt.subplot(4, 1, 3)
    plt.plot(range(len(results1)), results1_rolling_median_filtered)
    plt.ylabel('distance [cm]')
    plt.xlabel('time [s]')
    
    rolling_outlier_idx = np.where(results1_rolling_median_filtered != results1)[0]
    rolling_outlier_point = [results1_rolling_median_filtered[idx] for idx in rolling_outlier_idx]
    plt.plot(rolling_outlier_idx,rolling_outlier_point, marker='o', linestyle='none', color='r', alpha=0.3)

    results1_rolling_median_filtered = get_rolling_median_filtered(np.array(results1), window=window, threshold=threshold, replace_with='last')
    plt.subplot(4, 1, 4)
    plt.plot(range(len(results1)), results1_rolling_median_filtered)
    plt.ylabel('distance [cm]')
    plt.xlabel('time [s]')
    
    rolling_outlier_idx = np.where(results1_rolling_median_filtered != results1)[0]
    rolling_outlier_point = [results1_rolling_median_filtered[idx] for idx in rolling_outlier_idx]
    plt.plot(rolling_outlier_idx,rolling_outlier_point, marker='o', linestyle='none', color='r', alpha=0.3)



    plt.tight_layout()
    plt.show()


if __name__ == '__main__':
    # main()
    # rolling_median_x_smoothing()
    # rolling_median_x_smoothing(both=True)
    last_running_avg()
