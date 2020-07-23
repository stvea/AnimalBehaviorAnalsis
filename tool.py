import numpy as np


def point2line(point, line):
    distance = np.abs(line[0]*point[:, 0]-point[:, 1]+line[1])/np.sqrt(line[0]**2+1)
    return distance


def direction_vector(line):
    x = 1.0/np.sqrt(line[:, 0]**2+1)
    y = line[:, 0]/np.sqrt(line[:, 0]**2+1)
    return np.vstack((x, y)).transpose()


def line_intersection(line1, line2):
    x = (line2[1]-line1[1])/(line1[0]-line2[0])
    y = (line1[0]*line2[1]-line1[1]*line2[0])/(line1[0]-line2[0])
    return np.array([x, y])


if __name__ == '__main__':
    line1 = [1, 2]
    line2 = [4, 4]
    print(line_intersection(line1, line2))