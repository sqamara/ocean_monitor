import pickle
import matplotlib.pyplot as plt

def main():
	with open('results.pickle', 'rb') as file:
		results1, results2 = pickle.load(file)

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