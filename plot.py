import pickle
import matplotlib.pyplot as plt
import numpy as np

def reject_outliers(data):
    print(np.median(data))
    
    res = []
    for i in range(len(data)):
        if abs(data[i] - np.median(data)) < 5: 
            res.append(data[i])
        else:
            res.append(res[-1])

    return res


def main():
    with open('results.pickle', 'rb') as file:
        results1, results2 = pickle.load(file)

    results1 = reject_outliers(results1)
    results2 = reject_outliers(results2)
    
    plt.subplot(2, 1, 1)
    plt.plot(range(len(results1)), results1)
    plt.ylabel('distance [cm]')
    plt.xlabel('time [s]')

    plt.subplot(2, 1, 2)
    plt.plot(range(len(results2)), results2)
    plt.ylabel('distance [cm]')
    plt.xlabel('time [s]')

    plt.show()


if __name__ == '__main__':
    main()
